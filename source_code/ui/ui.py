import tempfile
from pathlib import Path

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
    QTabWidget,
    QFrame,
    QToolBar,
    QStatusBar,
)
from PySide6.QtCore import Qt


try:
    from source_code.src.core.execution_manager import ExecutionManager
except Exception:
    class ExecutionManager:
        def __init__(self, compiler="g++"):
            self.compiler = compiler

        def compile_code(self, cpp_path: str, output_path: str) -> dict:
            return {
                "success": False,
                "message": "ExecutionManager를 불러오지 못했습니다."
            }

        def run_code(self, executable_path: str, stdin_data: str = "", timeout: int = 2) -> dict:
            return {
                "success": False,
                "stdout": "",
                "stderr": "ExecutionManager를 불러오지 못했습니다.",
                "execution_time": 0.0
            }


class ConsoleBox(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.run_callback = None
        self.prompt = ">>> "
        self.setPlainText(self.prompt)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
            if self.run_callback:
                self.run_callback()
            return

        super().keyPressEvent(event)

    def get_current_input(self):
        text = self.toPlainText()
        lines = text.splitlines()

        if not lines:
            return ""

        last_line = lines[-1]

        if last_line.startswith(self.prompt):
            return last_line[len(self.prompt):]

        return last_line

    def append_output(self, text):
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        self.setTextCursor(cursor)

        current = self.toPlainText()

        if not current.endswith("\n"):
            self.insertPlainText("\n")

        if text:
            self.insertPlainText(str(text).rstrip() + "\n")

        self.insertPlainText(self.prompt)

        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        self.setTextCursor(cursor)

    def reset_console(self):
        self.setPlainText(self.prompt)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PS C++ Editor")
        self.resize(1350, 850)

        self.execution_manager = ExecutionManager()
        self.current_file_path = None

        self.ui_dir = Path(__file__).resolve().parent
        self.source_code_dir = self.ui_dir.parent
        self.default_cpp_path = self.source_code_dir / "src" / "temp" / "main.cpp"

        self.init_ui()
        self.connect_events()

    def init_ui(self):
        self.setStyleSheet(self.window_style())

        self.create_top_bar()

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("C++ 코드를 작성하세요.")
        self.editor.setPlainText(self.load_default_cpp_code())
        self.editor.setStyleSheet(self.editor_style())

        self.console_box = ConsoleBox()
        self.console_box.setPlaceholderText(">>> 뒤에 입력값을 작성하고 Enter를 누르세요.")
        self.console_box.setStyleSheet(self.console_style())

        self.terminal_box = QTextEdit()
        self.terminal_box.setReadOnly(True)
        self.terminal_box.setPlaceholderText("Build, Debug, 컴파일 메시지가 표시됩니다.")
        self.terminal_box.setStyleSheet(self.console_style())

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
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #ffffff;
                border-bottom: 1px solid #dddddd;
                spacing: 6px;
                padding: 6px;
            }
            QPushButton {
                padding: 6px 13px;
                border: 1px solid #d0d0d0;
                background-color: #ffffff;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #eef3ff;
                border: 1px solid #9bb8ff;
            }
        """)

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

        self.addToolBar(Qt.TopToolBarArea, toolbar)

    def create_editor_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet(self.panel_style())

        title = QLabel("Editor")
        title.setStyleSheet(self.title_style())

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
        panel.setStyleSheet(self.panel_style())

        title = QLabel("Tools")
        title.setStyleSheet(self.title_style())

        self.feature_tabs = QTabWidget()
        self.feature_tabs.setStyleSheet(self.tab_style())

        self.feature_tabs.addTab(self.create_testcase_tab(), "테스트케이스")
        self.feature_tabs.addTab(self.create_graph_tab(), "그래프")
        self.feature_tabs.addTab(self.create_complexity_tab(), "복잡도")
        self.feature_tabs.addTab(self.create_template_tab(), "템플릿")

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(title)
        layout.addWidget(self.feature_tabs)

        panel.setLayout(layout)
        return panel

    def create_testcase_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        label = QLabel("테스트케이스 관리")
        label.setStyleSheet("font-weight: bold;")

        self.testcase_input = QTextEdit()
        self.testcase_input.setPlaceholderText("테스트 입력")
        self.testcase_input.setStyleSheet(self.small_box_style())

        self.expected_output = QTextEdit()
        self.expected_output.setPlaceholderText("예상 출력")
        self.expected_output.setStyleSheet(self.small_box_style())

        self.run_testcase_button = QPushButton("현재 테스트케이스 실행")
        self.add_testcase_button = QPushButton("테스트케이스 추가")

        layout.addWidget(label)
        layout.addWidget(QLabel("입력"))
        layout.addWidget(self.testcase_input)
        layout.addWidget(QLabel("예상 출력"))
        layout.addWidget(self.expected_output)
        layout.addWidget(self.run_testcase_button)
        layout.addWidget(self.add_testcase_button)

        tab.setLayout(layout)
        return tab

    def create_graph_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        label = QLabel("그래프 시각화")
        label.setStyleSheet("font-weight: bold;")

        self.graph_input = QTextEdit()
        self.graph_input.setPlaceholderText("그래프 입력 예시\n5 4\n1 2\n1 3\n2 4\n3 5")
        self.graph_input.setStyleSheet(self.small_box_style())

        self.graph_result = QTextEdit()
        self.graph_result.setReadOnly(True)
        self.graph_result.setPlaceholderText("그래프 분석 결과")
        self.graph_result.setStyleSheet(self.small_box_style())

        self.graph_button = QPushButton("그래프 분석")

        layout.addWidget(label)
        layout.addWidget(self.graph_input)
        layout.addWidget(self.graph_button)
        layout.addWidget(self.graph_result)

        tab.setLayout(layout)
        return tab

    def create_complexity_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        label = QLabel("시간복잡도 분석")
        label.setStyleSheet("font-weight: bold;")

        self.complexity_result = QTextEdit()
        self.complexity_result.setReadOnly(True)
        self.complexity_result.setPlaceholderText("코드 분석 결과")
        self.complexity_result.setStyleSheet(self.small_box_style())

        self.complexity_button = QPushButton("복잡도 분석")

        layout.addWidget(label)
        layout.addWidget(self.complexity_button)
        layout.addWidget(self.complexity_result)

        tab.setLayout(layout)
        return tab

    def create_template_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        label = QLabel("템플릿")
        label.setStyleSheet("font-weight: bold;")

        self.basic_template_button = QPushButton("기본 C++ 템플릿")
        self.graph_template_button = QPushButton("그래프 BFS 템플릿")
        self.dp_template_button = QPushButton("DP 템플릿")
        self.clear_console_button = QPushButton("콘솔 지우기")

        layout.addWidget(label)
        layout.addWidget(self.basic_template_button)
        layout.addWidget(self.graph_template_button)
        layout.addWidget(self.dp_template_button)
        layout.addWidget(self.clear_console_button)
        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def create_bottom_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet(self.panel_style())

        self.bottom_tabs = QTabWidget()
        self.bottom_tabs.setStyleSheet(self.tab_style())

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
            if answer != QMessageBox.Yes:
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

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            cpp_path = temp_dir / "run.cpp"
            exe_path = temp_dir / "run.exe"

            with open(cpp_path, "w", encoding="utf-8") as f:
                f.write(code)

            compile_result = self.execution_manager.compile_code(
                str(cpp_path),
                str(exe_path)
            )

            if not compile_result.get("success"):
                return {
                    "success": False,
                    "type": "compile",
                    "message": compile_result.get("message", "")
                }

            run_result = self.execution_manager.run_code(
                str(exe_path),
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
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)
                cpp_path = temp_dir / "build.cpp"
                exe_path = temp_dir / "build.exe"

                with open(cpp_path, "w", encoding="utf-8") as f:
                    f.write(code)

                result = self.execution_manager.compile_code(
                    str(cpp_path),
                    str(exe_path)
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

        for_count = code.count("for")
        while_count = code.count("while")

        self.complexity_result.setPlainText(
            "임시 시간복잡도 분석 결과\n\n"
            f"for 개수: {for_count}\n"
            f"while 개수: {while_count}\n\n"
            "정확한 분석은 추후 연결할 예정입니다."
        )

    def insert_basic_template(self):
        self.editor.setPlainText(self.default_cpp_code())

    def insert_graph_template(self):
        self.editor.setPlainText(self.graph_cpp_code())

    def insert_dp_template(self):
        self.editor.setPlainText(self.dp_cpp_code())

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
                return self.default_cpp_code()

        return self.default_cpp_code()

    def default_cpp_code(self):
        return """#include <bits/stdc++.h>
using namespace std;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    cout << n << "\\n";

    return 0;
}
"""

    def graph_cpp_code(self):
        return """#include <bits/stdc++.h>
using namespace std;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;

    vector<vector<int>> g(n + 1);

    for(int i = 0; i < m; i++){
        int a, b;
        cin >> a >> b;
        g[a].push_back(b);
        g[b].push_back(a);
    }

    queue<int> q;
    vector<int> visited(n + 1, 0);

    q.push(1);
    visited[1] = 1;

    while(!q.empty()){
        int x = q.front();
        q.pop();

        cout << x << ' ';

        for(int nx : g[x]){
            if(!visited[nx]){
                visited[nx] = 1;
                q.push(nx);
            }
        }
    }

    return 0;
}
"""

    def dp_cpp_code(self):
        return """#include <bits/stdc++.h>
using namespace std;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<int> dp(n + 1, 0);

    dp[0] = 1;

    for(int i = 1; i <= n; i++){
        dp[i] = dp[i - 1];
    }

    cout << dp[n] << "\\n";

    return 0;
}
"""

    def window_style(self):
        return """
            QMainWindow {
                background-color: #f5f6f8;
            }
            QPushButton {
                padding: 7px 10px;
                border: 1px solid #d0d0d0;
                background-color: #ffffff;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #eef3ff;
                border: 1px solid #9bb8ff;
            }
            QLabel {
                color: #222222;
                font-size: 13px;
            }
        """

    def panel_style(self):
        return """
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dddddd;
                border-radius: 8px;
            }
        """

    def title_style(self):
        return """
            QLabel {
                font-size: 15px;
                font-weight: bold;
                padding: 4px;
                border: none;
            }
        """

    def tab_style(self):
        return """
            QTabWidget::pane {
                border: 1px solid #dddddd;
                border-radius: 6px;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f1f2f4;
                border: 1px solid #d0d0d0;
                padding: 7px 13px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #eef3ff;
            }
        """

    def editor_style(self):
        return """
            QPlainTextEdit {
                font-family: Consolas;
                font-size: 15px;
                background-color: #ffffff;
                color: #111111;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 8px;
            }
        """

    def console_style(self):
        return """
            QTextEdit {
                font-family: Consolas;
                font-size: 14px;
                background-color: #fbfbfb;
                color: #111111;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 8px;
            }
        """

    def small_box_style(self):
        return """
            QTextEdit {
                font-family: Consolas;
                font-size: 13px;
                background-color: #fbfbfb;
                color: #111111;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 6px;
            }
        """