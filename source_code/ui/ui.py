from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QTextEdit,
    QPlainTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
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
    from source_code.ui.function import FileManager, CompilerRunner
except Exception:
    class FileManager:
        def save_file(self, file_path, content):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    class CompilerRunner:
        def run(self, code, input_text):
            return {
                "success": True,
                "output": "아직 실제 실행 기능이 연결되지 않았습니다.\n\n[입력값]\n" + input_text,
                "error": "",
                "time": 0
            }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PS C++ Editor")
        self.resize(1300, 850)

        self.file_manager = FileManager()
        self.runner = CompilerRunner()
        self.current_file_path = None

        self.init_ui()
        self.connect_events()

    def init_ui(self):
        self.setStyleSheet(self.window_style())

        self.create_top_bar()

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("C++ 코드를 작성하세요.")
        self.editor.setPlainText(self.default_cpp_code())
        self.editor.setStyleSheet(self.editor_style())

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setPlaceholderText("입력하고 Enter를 누르면 실행 결과가 이곳에 표시됩니다.")
        self.console_output.setStyleSheet(self.console_output_style())

        self.console_input = QLineEdit()
        self.console_input.setPlaceholderText("입력값을 작성한 뒤 Enter를 누르세요.")
        self.console_input.setStyleSheet(self.console_input_style())

        self.terminal_box = QTextEdit()
        self.terminal_box.setReadOnly(True)
        self.terminal_box.setPlaceholderText("Build, Debug 로그가 표시됩니다.")
        self.terminal_box.setStyleSheet(self.console_output_style())

        upper_splitter = QSplitter(Qt.Horizontal)
        upper_splitter.addWidget(self.create_editor_panel())
        upper_splitter.addWidget(self.create_feature_panel())
        upper_splitter.setSizes([850, 430])

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(upper_splitter)
        main_splitter.addWidget(self.create_bottom_panel())
        main_splitter.setSizes([570, 230])

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
                background-color: #f2f5ff;
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
        spacer.setFixedWidth(360)
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

        layout.addWidget(label)
        layout.addWidget(self.basic_template_button)
        layout.addWidget(self.graph_template_button)
        layout.addWidget(self.dp_template_button)
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
        console_layout.addWidget(self.console_output)
        console_layout.addWidget(self.console_input)

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

        self.console_input.returnPressed.connect(self.run_code_from_console)

        self.run_testcase_button.clicked.connect(self.run_current_testcase)
        self.add_testcase_button.clicked.connect(self.add_testcase)

        self.graph_button.clicked.connect(self.analyze_graph)
        self.complexity_button.clicked.connect(self.analyze_complexity)

        self.basic_template_button.clicked.connect(self.insert_basic_template)
        self.graph_template_button.clicked.connect(self.insert_graph_template)
        self.dp_template_button.clicked.connect(self.insert_dp_template)

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
                self.file_manager.save_file(self.current_file_path, code)
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
            self.file_manager.save_file(file_path, code)
            self.current_file_path = file_path
            self.statusBar().showMessage(f"저장 완료: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "저장 실패", str(e))

    def run_code_from_console(self):
        code = self.editor.toPlainText()
        input_text = self.console_input.text()

        if not code.strip():
            QMessageBox.warning(self, "실행 불가", "코드가 비어 있습니다.")
            return

        self.bottom_tabs.setCurrentIndex(0)

        self.append_console("> " + input_text)
        self.console_input.clear()

        try:
            result = self.runner.run(code, input_text)
            self.append_run_result(result)
        except Exception as e:
            self.append_console("[UI 연결 오류]\n" + str(e))

    def append_run_result(self, result):
        success = result.get("success", False)
        output = result.get("output", "")
        error = result.get("error", "")
        time = result.get("time", None)

        if success:
            text = output.strip()
            if not text:
                text = "(출력 없음)"

            self.append_console(text)

            if time is not None:
                self.append_console(f"[실행 시간] {time}")

        else:
            text = error.strip() if error else "알 수 없는 오류가 발생했습니다."
            self.append_console("[실행 실패]\n" + text)

    def append_console(self, text):
        current = self.console_output.toPlainText()

        if current.strip():
            self.console_output.append(text)
        else:
            self.console_output.setPlainText(text)

        cursor = self.console_output.textCursor()
        cursor.movePosition(cursor.End)
        self.console_output.setTextCursor(cursor)

    def build_code(self):
        self.bottom_tabs.setCurrentIndex(1)
        self.terminal_box.setPlainText(
            "Build 버튼이 눌렸습니다.\n"
            "실제 빌드 기능은 function 담당 코드와 연결될 예정입니다."
        )

    def debug_code(self):
        self.bottom_tabs.setCurrentIndex(1)
        self.terminal_box.setPlainText(
            "Debug 버튼이 눌렸습니다.\n"
            "디버그 기능은 추후 연결될 예정입니다."
        )

    def run_current_testcase(self):
        code = self.editor.toPlainText()
        input_text = self.testcase_input.toPlainText()

        self.bottom_tabs.setCurrentIndex(0)
        self.append_console("[테스트케이스 실행]")
        self.append_console("> " + input_text)

        try:
            result = self.runner.run(code, input_text)
            self.append_run_result(result)
        except Exception as e:
            self.append_console("[테스트케이스 실행 오류]\n" + str(e))

    def add_testcase(self):
        QMessageBox.information(
            self,
            "테스트케이스 추가",
            "테스트케이스 저장 기능은 추후 function 담당 코드와 연결할 예정입니다."
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
            "정확한 복잡도 분석은 추후 function 담당 코드와 연결할 예정입니다."
        )

    def insert_basic_template(self):
        self.editor.setPlainText(self.default_cpp_code())

    def insert_graph_template(self):
        self.editor.setPlainText(self.graph_cpp_code())

    def insert_dp_template(self):
        self.editor.setPlainText(self.dp_cpp_code())

    def show_setting_message(self):
        QMessageBox.information(
            self,
            "설정",
            "설정 기능은 추후 추가할 예정입니다."
        )

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

    def console_output_style(self):
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

    def console_input_style(self):
        return """
            QLineEdit {
                font-family: Consolas;
                font-size: 14px;
                background-color: #ffffff;
                color: #111111;
                border: 1px solid #bdbdbd;
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