import sys
import time
import shutil
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
from PySide6.QtCore import Qt, QProcess, QProcessEnvironment

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PS C++ Editor")
        self.resize(1350, 850)

        self.execution_manager = ExecutionManager()
        self.current_file_path = None
        self.floating_windows = []

        self.process = None
        self.process_running = False
        self.process_start_time = 0.0

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

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("C++ 코드를 작성하세요.")
        self.editor.setPlainText(self.load_default_cpp_code())
        self.editor.setStyleSheet(editor_style())

        self.console_box = ConsoleBox()
        self.console_box.setPlaceholderText("Enter: 입력 전송 / Shift+Enter: 줄바꿈")
        self.console_box.setStyleSheet(console_style())

        self.terminal_box = QTextEdit()
        self.terminal_box.setReadOnly(True)
        self.terminal_box.setPlaceholderText("Debug, 컴파일 메시지가 표시됩니다.")
        self.terminal_box.setStyleSheet(console_style())

        upper_splitter = QSplitter(Qt.Horizontal)
        upper_splitter.addWidget(self.create_editor_panel())
        upper_splitter.addWidget(self.create_feature_panel())
        upper_splitter.setSizes([900, 420])

        main_splitter = QSplitter(Qt.Vertical)
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
        self.debug_button = QPushButton("Debug")

        toolbar.addWidget(self.new_button)
        toolbar.addWidget(self.open_button)
        toolbar.addWidget(self.save_button)
        toolbar.addWidget(self.setting_button)

        spacer = QWidget()
        spacer.setFixedWidth(380)
        toolbar.addWidget(spacer)

        toolbar.addWidget(self.run_button)
        toolbar.addWidget(self.debug_button)

        self.addToolBar(Qt.TopToolBarArea, toolbar)

    def create_editor_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
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
        panel.setFrameShape(QFrame.StyledPanel)
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
        panel.setFrameShape(QFrame.StyledPanel)
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
        if self.process_running:
            QMessageBox.warning(self, "실행 중", "프로그램 실행 중에는 새 파일을 만들 수 없습니다.")
            return

        if self.editor.toPlainText().strip():
            answer = QMessageBox.question(
                self,
                "새 파일",
                "현재 코드를 지우고 새 파일을 만들까요?"
            )
            if answer != QMessageBox.Yes:
                return

        self.editor.clear()
        self.current_file_path = None
        self.statusBar().showMessage("새 파일을 만들었습니다.")

    def open_cpp_file(self):
        if self.process_running:
            QMessageBox.warning(self, "실행 중", "프로그램 실행 중에는 파일을 열 수 없습니다.")
            return

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

    def save_editor_code_to_temp(self):
        code = self.editor.toPlainText()

        self.run_cpp_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.run_cpp_path, "w", encoding="utf-8") as f:
            f.write(code)

    def compile_current_editor_code(self):
        code = self.editor.toPlainText()

        if not code.strip():
            return {
                "success": False,
                "type": "compile",
                "message": "코드가 비어 있습니다."
            }

        self.save_editor_code_to_temp()

        compile_result = self.execution_manager.compile_code(
            str(self.run_cpp_path),
            str(self.run_exe_path)
        )

        return {
            "success": compile_result.get("success", False),
            "type": "compile",
            "message": compile_result.get("message", ""),
            "cpp_path": str(self.run_cpp_path),
            "exe_path": str(self.run_exe_path)
        }

    def run_current_editor_code(self, input_text):
        compile_result = self.compile_current_editor_code()

        if not compile_result.get("success"):
            return {
                "success": False,
                "type": "compile",
                "message": compile_result.get("message", ""),
                "stdout": "",
                "stderr": "",
                "execution_time": 0.0,
                "cpp_path": compile_result.get("cpp_path", ""),
                "exe_path": compile_result.get("exe_path", "")
            }

        run_result = self.execution_manager.run_code(
            str(self.run_exe_path),
            stdin_data=input_text,
            timeout=2
        )

        return {
            "success": run_result.get("success", False),
            "type": "run",
            "message": "",
            "stdout": run_result.get("stdout", "") or "",
            "stderr": run_result.get("stderr", "") or "",
            "execution_time": run_result.get("execution_time", 0.0) or 0.0,
            "cpp_path": str(self.run_cpp_path),
            "exe_path": str(self.run_exe_path)
        }

    def run_code_from_console(self, line_text=None):
        if self.process_running:
            self.send_input_to_process(line_text)
            return

        if line_text is None:
            input_text = self.console_box.get_current_input()
            self.console_box.ensure_newline()
        else:
            input_text = line_text

        self.start_interactive_run(input_text)

    def start_interactive_run(self, first_input):
        code = self.editor.toPlainText()

        if not code.strip():
            QMessageBox.warning(self, "실행 불가", "코드가 비어 있습니다.")
            self.console_box.append_prompt()
            return

        compile_result = self.compile_current_editor_code()

        if not compile_result.get("success"):
            self.console_box.append_output("[Compile Error]\n" + compile_result.get("message", ""))
            return

        self.bottom_tabs.setCurrentIndex(0)

        self.process = QProcess(self)
        self.process.setProcessEnvironment(self.create_process_environment())

        self.process.readyReadStandardOutput.connect(self.handle_process_stdout)
        self.process.readyReadStandardError.connect(self.handle_process_stderr)
        self.process.finished.connect(self.handle_process_finished)
        self.process.errorOccurred.connect(self.handle_process_error)

        self.process_start_time = time.perf_counter()
        self.process_running = True

        self.process.start(str(self.run_exe_path))

        if not self.process.waitForStarted(1000):
            self.process_running = False
            self.console_box.append_output("[Run Error]\n실행 파일을 시작하지 못했습니다.")
            self.process = None
            return

        self.send_input_to_process(first_input)

    def create_process_environment(self):
        env = QProcessEnvironment.systemEnvironment()

        compiler_name = getattr(self.execution_manager, "compiler", "g++")
        compiler_path = shutil.which(compiler_name)

        if compiler_path:
            compiler_bin = str(Path(compiler_path).parent)
            old_path = env.value("PATH")
            env.insert("PATH", compiler_bin + ";" + old_path)

        return env

    def send_input_to_process(self, text):
        if not self.process or not self.process_running:
            self.console_box.append_output("[Input Error]\n실행 중인 프로그램이 없습니다.")
            return

        if text is None:
            text = ""

        text = str(text)

        if text and not text.endswith("\n"):
            text += "\n"

        if not text:
            text = "\n"

        self.process.write(text.encode("utf-8"))

    def handle_process_stdout(self):
        if not self.process:
            return

        data = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
        self.console_box.append_process_output(data)

    def handle_process_stderr(self):
        if not self.process:
            return

        data = bytes(self.process.readAllStandardError()).decode("utf-8", errors="replace")
        self.console_box.append_process_output(data)

    def handle_process_finished(self, exit_code, exit_status):
        elapsed = round(time.perf_counter() - self.process_start_time, 6)

        if exit_code != 0:
            self.console_box.append_process_output(f"\n[Runtime Error] exit code: {exit_code}\n")

        self.console_box.append_process_output(f"[실행 시간] {elapsed}s\n")
        self.console_box.append_prompt()

        self.process_running = False

        if self.process:
            self.process.deleteLater()
            self.process = None

    def handle_process_error(self, error):
        self.process_running = False
        self.console_box.append_output("[Process Error]\n" + str(error))

        if self.process:
            self.process.deleteLater()
            self.process = None

    def debug_code(self):
        self.bottom_tabs.setCurrentIndex(1)
        self.terminal_box.clear()

        code = self.editor.toPlainText()
        input_text = self.console_box.get_current_input()

        if not code.strip():
            self.terminal_box.setPlainText("[Debug Failed]\n\n코드가 비어 있습니다.")
            return

        try:
            result = self.run_current_editor_code(input_text)

            stdout = result.get("stdout", "") or ""
            stderr = result.get("stderr", "") or ""
            message = result.get("message", "") or ""

            lines = []
            lines.append("[Debug Info]")
            lines.append("")
            lines.append(f"source file: {result.get('cpp_path', str(self.run_cpp_path))}")
            lines.append(f"executable: {result.get('exe_path', str(self.run_exe_path))}")
            lines.append(f"input: {repr(input_text)}")
            lines.append(f"result type: {result.get('type')}")
            lines.append(f"success: {result.get('success')}")
            lines.append(f"execution time: {result.get('execution_time', 0.0)}s")

            if result.get("type") == "compile":
                lines.append("")
                lines.append("[Compile Message]")
                lines.append(message if message else "(empty)")

            elif result.get("type") == "run":
                lines.append("")
                lines.append("[stdout]")
                lines.append(stdout if stdout else "(empty)")

                lines.append("")
                lines.append("[stderr]")
                lines.append(stderr if stderr else "(empty)")

            self.terminal_box.setPlainText("\n".join(str(x) for x in lines))

        except Exception as e:
            self.terminal_box.setPlainText("[Debug Error]\n\n" + str(e))

    def append_run_result(self, result):
        success = result.get("success", False)
        stdout = result.get("stdout", "") or ""
        stderr = result.get("stderr", "") or ""
        execution_time = result.get("execution_time", 0.0) or 0.0

        if success:
            output = stdout.strip()

            if not output:
                output = "(출력 없음)"

            text = output
            text += f"\n[실행 시간] {execution_time}s"

            self.append_console(text)

        else:
            error_text = stderr.strip() if stderr else "실행 중 오류가 발생했습니다."

            text = "[Runtime Error]\n"
            text += error_text
            text += f"\n[실행 시간] {execution_time}s"

            self.append_console(text)

    def append_console(self, text):
        self.console_box.append_output(text)

    def clear_console(self):
        if self.process_running:
            QMessageBox.warning(self, "실행 중", "프로그램 실행 중에는 콘솔을 지울 수 없습니다.")
            return

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

        for_count = code.count("for")
        while_count = code.count("while")

        self.complexity_result.setPlainText(
            "임시 시간복잡도 분석 결과\n\n"
            f"for 개수: {for_count}\n"
            f"while 개수: {while_count}\n\n"
            "정확한 분석은 추후 연결할 예정입니다."
        )

    def insert_basic_template(self):
        self.editor.setPlainText(default_cpp_code())

    def insert_graph_template(self):
        self.editor.setPlainText(graph_cpp_code())

    def insert_dp_template(self):
        self.editor.setPlainText(dp_cpp_code())

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