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
    QCheckBox,
    QScrollArea,
)

from PySide6.QtCore import Qt

from source_code.ui.ui_styles import small_box_style


def make_scroll_area(content_widget):
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll_area.setWidget(content_widget)

    scroll_area.setMinimumHeight(0)
    scroll_area.setStyleSheet(
        """
        QScrollArea {
            background: transparent;
            border: none;
        }
        """
    )

    return scroll_area


def create_testcase_tab(parent):
    content = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(6, 6, 6, 6)

    label = QLabel("테스트케이스 관리")
    label.setStyleSheet("font-weight: bold;")

    parent.testcase_input = QTextEdit()
    parent.testcase_input.setPlaceholderText("테스트 입력")
    parent.testcase_input.setStyleSheet(small_box_style())
    parent.testcase_input.setMinimumHeight(80)

    parent.expected_output = QTextEdit()
    parent.expected_output.setPlaceholderText("예상 출력")
    parent.expected_output.setStyleSheet(small_box_style())
    parent.expected_output.setMinimumHeight(80)

    parent.run_testcase_button = QPushButton("현재 입력 실행")
    parent.add_testcase_button = QPushButton("테스트케이스 추가")

    top_button_layout = QHBoxLayout()
    top_button_layout.addWidget(parent.run_testcase_button)
    top_button_layout.addWidget(parent.add_testcase_button)

    list_label = QLabel("저장된 테스트케이스")
    list_label.setStyleSheet("font-weight: bold;")

    parent.testcase_list = QListWidget()
    parent.testcase_list.setMinimumHeight(100)

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
    layout.addStretch()

    content.setLayout(layout)
    return make_scroll_area(content)


def create_graph_tab(parent):
    content = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(6, 6, 6, 6)

    label = QLabel("그래프 시각화")
    label.setStyleSheet("font-weight: bold;")

    description = QLabel(
        "간선 입력 형식\n"
        "- 간선 가중치 없음: u v\n"
        "- 간선 가중치 있음: u v w"
    )
    description.setWordWrap(True)

    parent.graph_input = QTextEdit()
    parent.graph_input.setPlaceholderText(
        "간선 입력 예시\n"
        "1 2\n"
        "1 3\n"
        "2 4\n"
        "3 5\n"
        "1 6\n"
        "1 8"
    )
    parent.graph_input.setStyleSheet(small_box_style())
    parent.graph_input.setMinimumHeight(120)

    option_layout = QHBoxLayout()

    parent.graph_directed_checkbox = QCheckBox("유향 그래프")
    parent.graph_edge_weight_checkbox = QCheckBox("간선 가중치")

    option_layout.addWidget(parent.graph_directed_checkbox)
    option_layout.addWidget(parent.graph_edge_weight_checkbox)
    option_layout.addStretch()

    button_layout = QHBoxLayout()

    parent.graph_button = QPushButton("그래프 시각화")
    parent.graph_clear_button = QPushButton("입력 지우기")

    button_layout.addWidget(parent.graph_button)
    button_layout.addWidget(parent.graph_clear_button)

    parent.graph_result = QTextEdit()
    parent.graph_result.setReadOnly(True)
    parent.graph_result.setPlaceholderText("그래프 정보 또는 오류 메시지가 표시됩니다.")
    parent.graph_result.setStyleSheet(small_box_style())
    parent.graph_result.setMinimumHeight(130)

    parent.graph_image_label = QLabel("그래프 이미지가 여기에 표시됩니다.")
    parent.graph_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    parent.graph_image_label.setMinimumHeight(260)
    parent.graph_image_label.setStyleSheet(
        """
        QLabel {
            background-color: #fbfbfb;
            color: #555555;
            border: 1px solid #cccccc;
            border-radius: 6px;
            padding: 6px;
        }
        """
    )

    layout.addWidget(label)
    layout.addWidget(description)

    layout.addWidget(QLabel("간선 입력"))
    layout.addWidget(parent.graph_input)

    layout.addLayout(option_layout)
    layout.addLayout(button_layout)

    layout.addWidget(QLabel("그래프 정보"))
    layout.addWidget(parent.graph_result)

    layout.addWidget(QLabel("그래프 이미지"))
    layout.addWidget(parent.graph_image_label)
    layout.addStretch()

    content.setLayout(layout)
    return make_scroll_area(content)


def create_complexity_tab(parent):
    content = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(6, 6, 6, 6)

    label = QLabel("시간복잡도 분석")
    label.setStyleSheet("font-weight: bold;")

    parent.complexity_result = QTextEdit()
    parent.complexity_result.setReadOnly(True)
    parent.complexity_result.setPlaceholderText("코드 분석 결과")
    parent.complexity_result.setStyleSheet(small_box_style())
    parent.complexity_result.setMinimumHeight(320)

    parent.complexity_button = QPushButton("복잡도 분석")

    layout.addWidget(label)
    layout.addWidget(parent.complexity_button)
    layout.addWidget(parent.complexity_result)
    layout.addStretch()

    content.setLayout(layout)
    return make_scroll_area(content)


def create_template_tab(parent):
    content = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(6, 6, 6, 6)

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

    content.setLayout(layout)
    return make_scroll_area(content)