import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QTabWidget,
    QDialog,
    QLabel,
    QFrame,
    QVBoxLayout,
)
from PySide6.QtCore import Qt, QPoint

from source_code.ui.ui_styles import (
    floating_header_style,
    floating_container_style,
)


class FloatingTabWindow(QDialog):
    def __init__(self, source_tab_widget, content_widget, title, original_index, parent_window):
        super().__init__(parent_window)

        self.source_tab_widget = source_tab_widget
        self.content_widget = content_widget
        self.title = title
        self.original_index = original_index
        self.parent_window = parent_window
        self.attached = False

        self.dragging = False
        self.drag_offset = QPoint(0, 0)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.resize(520, 360)

        self.header = QLabel(title + "    더블클릭하면 원래 위치로 돌아갑니다")
        self.header.setFixedHeight(32)
        self.header.setStyleSheet(floating_header_style())

        self.header.mousePressEvent = self.header_mouse_press
        self.header.mouseMoveEvent = self.header_mouse_move
        self.header.mouseReleaseEvent = self.header_mouse_release
        self.header.mouseDoubleClickEvent = self.header_mouse_double_click

        self.container = QFrame()
        self.container.setStyleSheet(floating_container_style())

        self.inner_layout = QVBoxLayout()
        self.inner_layout.setContentsMargins(8, 8, 8, 8)

        self.content_widget.setParent(self.container)
        self.inner_layout.addWidget(self.content_widget)
        self.content_widget.setVisible(True)

        self.container.setLayout(self.inner_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.header)
        layout.addWidget(self.container)

        self.setLayout(layout)

    def header_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def header_mouse_move(self, event):
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def header_mouse_release(self, event):
        self.dragging = False

    def header_mouse_double_click(self, event):
        if event.button() == Qt.LeftButton:
            self.attach_to_original_position()

    def attach_to_original_position(self):
        if self.attached:
            return

        self.attached = True

        self.inner_layout.removeWidget(self.content_widget)
        self.content_widget.setParent(None)

        index = min(self.original_index, self.source_tab_widget.count())
        self.source_tab_widget.insertTab(index, self.content_widget, self.title)
        self.source_tab_widget.setCurrentWidget(self.content_widget)
        self.content_widget.setVisible(True)

        if self in self.parent_window.floating_windows:
            self.parent_window.floating_windows.remove(self)

        self.close()

    def closeEvent(self, event):
        if not self.attached:
            self.attach_to_original_position()

        event.accept()


class DetachableTabWidget(QTabWidget):
    def __init__(self, parent_window):
        super().__init__()

        self.parent_window = parent_window

        self.setMovable(True)
        self.tabBar().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.tabBar():
            if event.type() == event.Type.MouseButtonDblClick and event.button() == Qt.LeftButton:
                index = self.tabBar().tabAt(event.pos())

                if index != -1:
                    self.detach_tab(index, event.globalPosition().toPoint())
                    return True

        return super().eventFilter(obj, event)

    def detach_tab(self, index, global_pos):
        if index < 0 or index >= self.count():
            return None

        content_widget = self.widget(index)
        title = self.tabText(index)

        self.removeTab(index)

        floating_window = FloatingTabWindow(
            self,
            content_widget,
            title,
            index,
            self.parent_window
        )

        floating_window.move(global_pos + QPoint(10, 10))
        floating_window.show()
        floating_window.raise_()
        floating_window.activateWindow()

        self.parent_window.floating_windows.append(floating_window)

        return floating_window