import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QTextEdit,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QMessageBox,
    QSplitter,
    QFrame,
    QToolBar,
    QStatusBar,
)
from PySide6.QtCore import Qt

from source_code.ui.console import ConsoleBox
from source_code.ui.code_editor import CodeEditor
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
from source_code.ui.file_controller import FileController
from source_code.ui.execution_controller import ExecutionController
from source_code.ui.complexity_controller import ComplexityController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PS C++ Editor")
        self.resize(1350, 850)

        self.floating_windows = []

        self.ui_dir = Path(__file__).resolve().parent
        self.source_code_dir = self.ui_dir.parent
        self.default_cpp_path = self.source_code_dir / "src" / "temp" / "main.cpp"

        self.file_controller = None
        self.execution_controller = ExecutionController(self.source_code_dir)
        self.complexity_controller = ComplexityController(use_ollama=True)

        self.init_ui()
        self.init_controllers()
        self.connect_events()

    def init_ui(self):
        self.setStyleSheet(window_style())

        self.create_top_bar()

        self.editor = CodeEditor(tab_spaces=4)
        self.editor.setPlaceholderText("C++ 코드를 작성하세요.")
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

    def init_controllers(self):
        self.file_controller = FileController(
            parent=self,
            editor=self.editor,
            default_cpp_path=self.default_cpp_path
        )

        self.editor.setPlainText(
            self.file_controller.load_default_cpp_code()
        )

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
        self.file_controller.new_file()

    def open_cpp_file(self):
        self.file_controller.open_cpp_file()

    def save_cpp_file(self):
        self.file_controller.save_cpp_file()

    def run_current_editor_code(self, input_text):
        code = self.editor.toPlainText()

        return self.execution_controller.run_code(
            code=code,
            input_text=input_text,
            timeout=2
        )

    def build_code(self):
        self.bottom_tabs.setCurrentIndex(1)
        self.terminal_box.clear()

        code = self.editor.toPlainText()

        try:
            result = self.execution_controller.compile_code(code)
            text = self.execution_controller.format_build_result(result)
            self.terminal_box.setPlainText(text)

        except Exception as e:
            self.terminal_box.setPlainText("[Build Error]\n\n" + str(e))

    def debug_code(self):
        self.bottom_tabs.setCurrentIndex(1)
        self.terminal_box.clear()

        code = self.editor.toPlainText()
        input_text = self.console_box.get_current_input()

        if not code.strip():
            self.terminal_box.setPlainText("[Debug Failed]\n\n코드가 비어 있습니다.")
            return

        try:
            result = self.execution_controller.run_code(
                code=code,
                input_text=input_text,
                timeout=2
            )

            text = self.execution_controller.format_debug_result(
                result=result,
                input_text=input_text
            )

            self.terminal_box.setPlainText(text)

        except Exception as e:
            self.terminal_box.setPlainText("[Debug Error]\n\n" + str(e))

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
        stdout = result.get("stdout", "") or ""
        stderr = result.get("stderr", "") or ""
        execution_time = result.get("execution_time", 0.0) or 0.0

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
        result_text = self.complexity_controller.analyze_code(code)
        self.complexity_result.setPlainText(result_text)

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