import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QWidget,
    QTextEdit,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
)

from source_code.ui.ui_styles import small_box_style


def create_testcase_tab(parent):
    tab = QWidget()
    layout = QVBoxLayout()

    label = QLabel("테스트케이스 관리")
    label.setStyleSheet("font-weight: bold;")

    parent.testcase_input = QTextEdit()
    parent.testcase_input.setPlaceholderText("테스트 입력")
    parent.testcase_input.setStyleSheet(small_box_style())

    parent.expected_output = QTextEdit()
    parent.expected_output.setPlaceholderText("예상 출력")
    parent.expected_output.setStyleSheet(small_box_style())

    parent.run_testcase_button = QPushButton("현재 입력 실행")
    parent.add_testcase_button = QPushButton("테스트케이스 추가")

    top_button_layout = QHBoxLayout()
    top_button_layout.addWidget(parent.run_testcase_button)
    top_button_layout.addWidget(parent.add_testcase_button)

    list_label = QLabel("저장된 테스트케이스")
    list_label.setStyleSheet("font-weight: bold;")

    parent.testcase_list = QListWidget()

    parent.run_all_testcase_button = QPushButton("전체 실행")
    parent.delete_testcase_button = QPushButton("선택 삭제")
    parent.clear_testcase_button = QPushButton("전체 삭제")

    bottom_button_layout = QHBoxLayout()
    bottom_button_layout.addWidget(parent.run_all_testcase_button)
    bottom_button_layout.addWidget(parent.delete_testcase_button)
    bottom_button_layout.addWidget(parent.clear_testcase_button)

    layout.addWidget(label)
    layout.addWidget(QLabel("입력"))
    layout.addWidget(parent.testcase_input)
    layout.addWidget(QLabel("예상 출력"))
    layout.addWidget(parent.expected_output)
    layout.addLayout(top_button_layout)
    layout.addWidget(list_label)
    layout.addWidget(parent.testcase_list)
    layout.addLayout(bottom_button_layout)

    tab.setLayout(layout)
    return tab


def create_graph_tab(parent):
    tab = QWidget()
    layout = QVBoxLayout()

    label = QLabel("그래프 시각화")
    label.setStyleSheet("font-weight: bold;")

    parent.graph_input = QTextEdit()
    parent.graph_input.setPlaceholderText("그래프 입력 예시\n5 4\n1 2\n1 3\n2 4\n3 5")
    parent.graph_input.setStyleSheet(small_box_style())

    parent.graph_result = QTextEdit()
    parent.graph_result.setReadOnly(True)
    parent.graph_result.setPlaceholderText("그래프 분석 결과")
    parent.graph_result.setStyleSheet(small_box_style())

    parent.graph_button = QPushButton("그래프 분석")

    layout.addWidget(label)
    layout.addWidget(parent.graph_input)
    layout.addWidget(parent.graph_button)
    layout.addWidget(parent.graph_result)

    tab.setLayout(layout)
    return tab


def create_complexity_tab(parent):
    tab = QWidget()
    layout = QVBoxLayout()

    label = QLabel("시간복잡도 분석")
    label.setStyleSheet("font-weight: bold;")

    parent.complexity_result = QTextEdit()
    parent.complexity_result.setReadOnly(True)
    parent.complexity_result.setPlaceholderText("코드 분석 결과")
    parent.complexity_result.setStyleSheet(small_box_style())

    parent.complexity_button = QPushButton("복잡도 분석")

    layout.addWidget(label)
    layout.addWidget(parent.complexity_button)
    layout.addWidget(parent.complexity_result)

    tab.setLayout(layout)
    return tab


def create_template_tab(parent):
    tab = QWidget()
    layout = QVBoxLayout()

    label = QLabel("템플릿")
    label.setStyleSheet("font-weight: bold;")

    parent.basic_template_button = QPushButton("기본 C++ 템플릿")
    parent.graph_template_button = QPushButton("그래프 BFS 템플릿")
    parent.dp_template_button = QPushButton("DP 템플릿")
    parent.clear_console_button = QPushButton("콘솔 지우기")

    layout.addWidget(label)
    layout.addWidget(parent.basic_template_button)
    layout.addWidget(parent.graph_template_button)
    layout.addWidget(parent.dp_template_button)
    layout.addWidget(parent.clear_console_button)
    layout.addStretch()

    tab.setLayout(layout)
    return tab