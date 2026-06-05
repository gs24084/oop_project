import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPlainTextEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QFileDialog,
    QMessageBox,
    QSplitter,
    QFrame,
    QToolBar,
    QStatusBar,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QFontMetrics

from source_code.ui.console import ConsoleBox
from source_code.ui.detachable_tab import DetachableTabWidget
from source_code.ui.panels import (
    create_testcase_tab,
    create_graph_tab,
    create_complexity_tab,
    create_template_tab,
)
from source_code.ui.cpp_templates import (
    default_cpp_code,
    graph_cpp_code,
    dp_cpp_code,
)
from source_code.ui.ui_styles import (
    window_style,
    panel_style,
    title_style,
    tab_style,
    editor_style,
    console_style,
    toolbar_style,
)

try:
    from source_code.src.core.execution_manager import ExecutionManager
except Exception as e:
    IMPORT_ERROR_MESSAGE = str(e)

    class ExecutionManager:
        def __init__(self, compiler="g++"):
            self.compiler = compiler

        def compile_code(self, cpp_path: str, output_path: str) -> dict:
            return {
                "success": False,
                "message": "ExecutionManager를 불러오지 못했습니다.\n" + IMPORT_ERROR_MESSAGE
            }

        def run_code(self, executable_path: str, stdin_data: str = "", timeout: int = 2) -> dict:
            return {
                "success": False,
                "stdout": "",
                "stderr": "ExecutionManager를 불러오지 못했습니다.\n" + IMPORT_ERROR_MESSAGE,
                "execution_time": 0.0
            }


try:
    from source_code.src.core.complexity_analyzer import ComplexityAnalyzer
except Exception as e:
    COMPLEXITY_IMPORT_ERROR = str(e)

    class ComplexityAnalyzer:
        def __init__(self, use_ollama=True, model="qwen3:0.6b"):
            self.use_ollama = use_ollama
            self.model = model

        def analyze(self, code: str) -> dict:
            return {
                "static": {
                    "complexity": "분석 불가",
                    "evidence": [
                        "ComplexityAnalyzer를 불러오지 못했습니다.",
                        COMPLEXITY_IMPORT_ERROR
                    ]
                }
            }


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None, tab_spaces=4):
        super().__init__(parent)

        self.tab_spaces = tab_spaces
        self.update_tab_width()

    def update_tab_width(self):
        space_width = QFontMetrics(self.font()).horizontalAdvance(" ")
        self.setTabStopDistance(space_width * self.tab_spaces)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            self.insertPlainText(" " * self.tab_spaces)
            return

        if event.key() == Qt.Key_Backtab:
            self.remove_indent()
            return

        super().keyPressEvent(event)

    def remove_indent(self):
        cursor = self.textCursor()

        if cursor.hasSelection():
            self.remove_indent_from_selection()
            return

        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(
            QTextCursor.MoveOperation.Right,
            QTextCursor.MoveMode.KeepAnchor,
            self.tab_spaces
        )

        selected = cursor.selectedText()
        remove_count = 0

        for ch in selected:
            if ch == " ":
                remove_count += 1
            else:
                break

        if remove_count == 0:
            return

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)

        cursor.movePosition(
            QTextCursor.MoveOperation.Right,
            QTextCursor.MoveMode.KeepAnchor,
            remove_count
        )

        cursor.removeSelectedText()
        self.setTextCursor(cursor)

    def remove_indent_from_selection(self):
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        cursor.setPosition(start)
        start_block = cursor.blockNumber()

        cursor.setPosition(end)
        end_block = cursor.blockNumber()

        cursor.beginEditBlock()

        for block_number in range(start_block, end_block + 1):
            block = self.document().findBlockByNumber(block_number)

            if not block.isValid():
                continue

            text = block.text()
            remove_count = 0

            for ch in text[:self.tab_spaces]:
                if ch == " ":
                    remove_count += 1
                else:
                    break

            if remove_count == 0:
                continue

            cursor.setPosition(block.position())
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                remove_count
            )
            cursor.removeSelectedText()

        cursor.endEditBlock()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PS C++ Editor")
        self.resize(1350, 850)

        self.execution_manager = ExecutionManager()
        self.complexity_analyzer = ComplexityAnalyzer(use_ollama=True)

        self.current_file_path = None
        self.floating_windows = []

        self.ui_dir = Path(__file__).resolve().parent
        self.source_code_dir = self.ui_dir.parent

        self.default_cpp_path = self.source_code_dir / "src" / "temp" / "main.cpp"
        self.run_cpp_path = self.source_code_dir / "src" / "temp" / "editor_run.cpp"
        self.run_exe_path = self.source_code_dir / "src" / "temp" / "editor_run.exe"

        self.init_ui()
        self.connect_events()

    def init_ui(self):
        self.setStyleSheet(window_style())

        self.create_top_bar()

        self.editor = CodeEditor(tab_spaces=4)
        self.editor.setPlaceholderText("C++ 코드를 작성하세요.")
        self.editor.setPlainText(self.load_default_cpp_code())
        self.editor.setStyleSheet(editor_style())
        self.editor.update_tab_width()

        self.console_box = ConsoleBox()
        self.console_box.setPlaceholderText(">>> 뒤에 입력값을 작성하고 Enter를 누르세요.")
        self.console_box.setStyleSheet(console_style())

        self.terminal_box = QTextEdit()
        self.terminal_box.setReadOnly(True)
        self.terminal_box.setPlaceholderText("Build, Debug, 컴파일 메시지가 표시됩니다.")
        self.terminal_box.setStyleSheet(console_style())

        upper_splitter = QSplitter(Qt.Orientation.Horizontal)
        upper_splitter.addWidget(self.create_editor_panel())
        upper_splitter.addWidget(self.create_feature_panel())
        upper_splitter.setSizes([900, 420])

        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(upper_splitter)
        main_splitter.addWidget(self.create_bottom_panel())
        main_splitter.setSizes([580, 230])

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(main_splitter)
        container.setLayout(layout)

        self.setCentralWidget(container)
        self.setStatusBar(QStatusBar())

    def create_top_bar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setStyleSheet(toolbar_style())

        self.new_button = QPushButton("새 파일")
        self.open_button = QPushButton("열기")
        self.save_button = QPushButton("저장")
        self.setting_button = QPushButton("설정")

        self.run_button = QPushButton("실행")
        self.build_button = QPushButton("Build")
        self.debug_button = QPushButton("Debug")

        toolbar.addWidget(self.new_button)
        toolbar.addWidget(self.open_button)
        toolbar.addWidget(self.save_button)
        toolbar.addWidget(self.setting_button)

        spacer = QWidget()
        spacer.setFixedWidth(380)
        toolbar.addWidget(spacer)

        toolbar.addWidget(self.run_button)
        toolbar.addWidget(self.build_button)
        toolbar.addWidget(self.debug_button)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

    def create_editor_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setStyleSheet(panel_style())

        title = QLabel("Editor")
        title.setStyleSheet(title_style())

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(title)
        layout.addWidget(self.editor)

        panel.setLayout(layout)
        return panel

    def create_feature_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(360)
        panel.setStyleSheet(panel_style())

        title = QLabel("Tools")
        title.setStyleSheet(title_style())

        self.feature_tabs = DetachableTabWidget(self)
        self.feature_tabs.setStyleSheet(tab_style())

        self.feature_tabs.addTab(create_testcase_tab(self), "테스트케이스")
        self.feature_tabs.addTab(create_graph_tab(self), "그래프")
        self.feature_tabs.addTab(create_complexity_tab(self), "복잡도")
        self.feature_tabs.addTab(create_template_tab(self), "템플릿")

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(title)
        layout.addWidget(self.feature_tabs)

        panel.setLayout(layout)
        return panel

    def create_bottom_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setStyleSheet(panel_style())

        self.bottom_tabs = DetachableTabWidget(self)
        self.bottom_tabs.setStyleSheet(tab_style())

        console_tab = QWidget()
        console_layout = QVBoxLayout()
        console_layout.setContentsMargins(6, 6, 6, 6)

        console_title = QLabel("Console")
        console_title.setStyleSheet("font-weight: bold;")

        console_layout.addWidget(console_title)
        console_layout.addWidget(self.console_box)

        console_tab.setLayout(console_layout)

        self.bottom_tabs.addTab(console_tab, "콘솔")
        self.bottom_tabs.addTab(self.terminal_box, "터미널")

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self.bottom_tabs)

        panel.setLayout(layout)
        return panel

    def connect_events(self):
        self.new_button.clicked.connect(self.new_file)
        self.open_button.clicked.connect(self.open_cpp_file)
        self.save_button.clicked.connect(self.save_cpp_file)
        self.setting_button.clicked.connect(self.show_setting_message)

        self.run_button.clicked.connect(self.run_code_from_console)
        self.build_button.clicked.connect(self.build_code)
        self.debug_button.clicked.connect(self.debug_code)

        self.console_box.run_callback = self.run_code_from_console

        self.run_testcase_button.clicked.connect(self.run_current_testcase)
        self.add_testcase_button.clicked.connect(self.add_testcase)

        self.graph_button.clicked.connect(self.analyze_graph)
        self.complexity_button.clicked.connect(self.analyze_complexity)

        self.basic_template_button.clicked.connect(self.insert_basic_template)
        self.graph_template_button.clicked.connect(self.insert_graph_template)
        self.dp_template_button.clicked.connect(self.insert_dp_template)
        self.clear_console_button.clicked.connect(self.clear_console)

    def new_file(self):
        if self.editor.toPlainText().strip():
            answer = QMessageBox.question(
                self,
                "새 파일",
                "현재 코드를 지우고 새 파일을 만들까요?"
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        self.editor.clear()
        self.current_file_path = None
        self.statusBar().showMessage("새 파일을 만들었습니다.")

    def open_cpp_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "C++ 파일 열기",
            "",
            "C++ Files (*.cpp);;All Files (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.editor.setPlainText(f.read())

            self.current_file_path = file_path
            self.statusBar().showMessage(f"파일을 열었습니다: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "열기 실패", str(e))

    def save_cpp_file(self):
        code = self.editor.toPlainText()

        if self.current_file_path:
            try:
                with open(self.current_file_path, "w", encoding="utf-8") as f:
                    f.write(code)

                self.statusBar().showMessage(f"저장 완료: {self.current_file_path}")
                return
            except Exception as e:
                QMessageBox.critical(self, "저장 실패", str(e))
                return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "C++ 파일 저장",
            "main.cpp",
            "C++ Files (*.cpp);;All Files (*)"
        )

        if not file_path:
            return

        if not file_path.endswith(".cpp"):
            file_path += ".cpp"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)

            self.current_file_path = file_path
            self.statusBar().showMessage(f"저장 완료: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "저장 실패", str(e))

    def run_current_editor_code(self, input_text):
        code = self.editor.toPlainText()

        self.run_cpp_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.run_cpp_path, "w", encoding="utf-8") as f:
            f.write(code)

        compile_result = self.execution_manager.compile_code(
            str(self.run_cpp_path),
            str(self.run_exe_path)
        )

        if not compile_result.get("success"):
            return {
                "success": False,
                "type": "compile",
                "message": compile_result.get("message", "")
            }

        run_result = self.execution_manager.run_code(
            str(self.run_exe_path),
            stdin_data=input_text,
            timeout=2
        )

        return {
            "success": run_result.get("success", False),
            "type": "run",
            "stdout": run_result.get("stdout", ""),
            "stderr": run_result.get("stderr", ""),
            "execution_time": run_result.get("execution_time", 0.0)
        }

    def build_code(self):
        self.bottom_tabs.setCurrentIndex(1)
        self.terminal_box.clear()

        code = self.editor.toPlainText()

        if not code.strip():
            self.terminal_box.setPlainText("[Build Failed]\n\n코드가 비어 있습니다.")
            return

        try:
            self.run_cpp_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.run_cpp_path, "w", encoding="utf-8") as f:
                f.write(code)

            result = self.execution_manager.compile_code(
                str(self.run_cpp_path),
                str(self.run_exe_path)
            )

            if result.get("success"):
                self.terminal_box.setPlainText("[Build Success]\n\n" + result.get("message", ""))
            else:
                self.terminal_box.setPlainText("[Build Failed]\n\n" + result.get("message", ""))

        except Exception as e:
            self.terminal_box.setPlainText("[Build Error]\n\n" + str(e))

    def run_code_from_console(self):
        code = self.editor.toPlainText()
        input_text = self.console_box.get_current_input()

        if not code.strip():
            QMessageBox.warning(self, "실행 불가", "코드가 비어 있습니다.")
            return

        self.bottom_tabs.setCurrentIndex(0)

        try:
            result = self.run_current_editor_code(input_text)

            if result.get("type") == "compile":
                self.console_box.append_output("[Compile Error]\n" + result.get("message", ""))
                return

            self.append_run_result(result)

        except Exception as e:
            self.console_box.append_output("[UI Error]\n" + str(e))

    def append_run_result(self, result):
        success = result.get("success", False)
        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")
        execution_time = result.get("execution_time", 0.0)

        if success:
            output = stdout.strip()

            if not output:
                output = "(출력 없음)"

            self.append_console(output)
            self.append_console(f"[실행 시간] {execution_time}s")

        else:
            error_text = stderr.strip() if stderr else "실행 중 오류가 발생했습니다."
            self.append_console("[Runtime Error]\n" + error_text)
            self.append_console(f"[실행 시간] {execution_time}s")

    def append_console(self, text):
        self.console_box.append_output(text)

    def clear_console(self):
        self.console_box.reset_console()

    def run_current_testcase(self):
        code = self.editor.toPlainText()
        input_text = self.testcase_input.toPlainText()
        expected = self.expected_output.toPlainText().strip()

        if not code.strip():
            QMessageBox.warning(self, "실행 불가", "코드가 비어 있습니다.")
            return

        self.bottom_tabs.setCurrentIndex(0)
        self.console_box.append_output("[테스트케이스 실행]\n입력:\n" + input_text.strip())

        try:
            result = self.run_current_editor_code(input_text)

            if result.get("type") == "compile":
                self.console_box.append_output("[Compile Error]\n" + result.get("message", ""))
                return

            self.append_run_result(result)

            actual = result.get("stdout", "").strip()

            if expected:
                if actual == expected:
                    self.append_console("[결과 비교] 정답")
                else:
                    self.append_console("[결과 비교] 오답")
                    self.append_console("[예상 출력]\n" + expected)
                    self.append_console("[실제 출력]\n" + actual)

        except Exception as e:
            self.append_console("[테스트케이스 실행 오류]\n" + str(e))

    def add_testcase(self):
        QMessageBox.information(
            self,
            "테스트케이스 추가",
            "테스트케이스 저장 기능은 추후 연결할 예정입니다."
        )

    def analyze_graph(self):
        text = self.graph_input.toPlainText().strip()

        if not text:
            self.graph_result.setPlainText("그래프 입력이 비어 있습니다.")
            return

        lines = text.splitlines()
        edge_count = max(0, len(lines) - 1)

        self.graph_result.setPlainText(
            "임시 그래프 분석 결과\n\n"
            f"입력 줄 수: {len(lines)}\n"
            f"간선 정보로 추정되는 줄 수: {edge_count}\n\n"
            "실제 시각화 기능은 추후 연결 예정입니다."
        )

    def analyze_complexity(self):
        code = self.editor.toPlainText()

        if not code.strip():
            self.complexity_result.setPlainText("분석할 코드가 없습니다.")
            return

        try:
            result = self.complexity_analyzer.analyze(code)

            static_result = result.get("static", {})
            complexity = static_result.get("complexity", "알 수 없음")
            evidence = static_result.get("evidence", [])

            lines = []
            lines.append("[시간복잡도 분석 결과]")
            lines.append("")
            lines.append(f"추정 시간복잡도: {complexity}")
            lines.append("")
            lines.append("[근거]")

            if evidence:
                for item in evidence:
                    lines.append(f"- {item}")
            else:
                lines.append("- 근거 없음")

            if "ollama" in result:
                ollama_result = result["ollama"]

                lines.append("")
                lines.append("[Ollama 분석 결과]")

                if ollama_result.get("success"):
                    lines.append(ollama_result.get("response", ""))
                else:
                    lines.append("Ollama 분석 실패")
                    lines.append(ollama_result.get("response", ""))

            self.complexity_result.setPlainText("\n".join(lines))

        except Exception as e:
            self.complexity_result.setPlainText(
                "[시간복잡도 분석 오류]\n\n" + str(e)
            )

    def insert_basic_template(self):
        self.editor.setPlainText(default_cpp_code())

    def insert_graph_template(self):
        self.editor.setPlainText(graph_cpp_code())

    def insert_dp_template(self):
        self.editor.setPlainText(dp_cpp_code())

    def debug_code(self):
        self.bottom_tabs.setCurrentIndex(1)
        self.terminal_box.setPlainText(
            "Debug 버튼이 눌렸습니다.\n"
            "디버그 기능은 추후 연결할 예정입니다."
        )

    def show_setting_message(self):
        QMessageBox.information(
            self,
            "설정",
            "설정 기능은 추후 추가할 예정입니다."
        )

    def load_default_cpp_code(self):
        if self.default_cpp_path.exists():
            try:
                with open(self.default_cpp_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                return default_cpp_code()

        return default_cpp_code()