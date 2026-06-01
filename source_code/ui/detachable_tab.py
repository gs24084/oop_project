from PySide6.QtWidgets import (
    QApplication,
    QTabWidget,
    QDialog,
    QLabel,
    QFrame,
    QVBoxLayout,
)
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QCursor

from source_code.ui.ui_styles import floating_header_style, floating_container_style


class FloatingTabWindow(QDialog):
    def __init__(self, source_tab_widget, content_widget, title, original_index, parent_window):
        super().__init__(parent_window)

        self.source_tab_widget = source_tab_widget
        self.content_widget = content_widget
        self.title = title
        self.original_index = original_index
        self.parent_window = parent_window

        self.dragging = False
        self.drag_offset = QPoint(40, 18)
        self.attached = False

        self.follow_timer = QTimer(self)
        self.follow_timer.timeout.connect(self.follow_mouse)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.resize(520, 360)

        self.header = QLabel(title + "    원래 탭 위치로 드래그하거나 더블클릭하면 다시 붙습니다")
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

    def start_follow_mouse(self):
        self.dragging = True
        self.follow_timer.start(10)

    def follow_mouse(self):
        if not self.dragging:
            self.follow_timer.stop()
            return

        if not (QApplication.mouseButtons() & Qt.LeftButton):
            self.dragging = False
            self.follow_timer.stop()
            self.try_attach_by_mouse_position()
            return

        self.move_by_global_pos(QCursor.pos())

    def move_by_global_pos(self, global_pos):
        self.move(global_pos - self.drag_offset)

    def header_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def header_mouse_move(self, event):
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def header_mouse_release(self, event):
        self.dragging = False
        self.try_attach_by_mouse_position(event.globalPosition().toPoint())

    def header_mouse_double_click(self, event):
        if event.button() == Qt.LeftButton:
            self.attach_to_original_position()

    def try_attach_by_mouse_position(self, global_pos=None):
        if global_pos is None:
            global_pos = QCursor.pos()

        local_pos = self.source_tab_widget.mapFromGlobal(global_pos)

        if self.source_tab_widget.rect().contains(local_pos):
            self.attach_to_original_position()

    def attach_to_original_position(self):
        if self.attached:
            return

        self.attached = True
        self.follow_timer.stop()

        self.inner_layout.removeWidget(self.content_widget)
        self.content_widget.setParent(self.source_tab_widget)

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
        self.press_index = -1
        self.press_pos = QPoint(0, 0)
        self.drag_started = False
        self.active_floating_window = None

        self.setMovable(True)
        self.tabBar().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.tabBar():
            if event.type() == event.Type.MouseButtonPress and event.button() == Qt.LeftButton:
                self.press_index = self.tabBar().tabAt(event.pos())
                self.press_pos = event.globalPosition().toPoint()
                self.drag_started = False
                self.active_floating_window = None

            elif event.type() == event.Type.MouseMove:
                if self.press_index != -1 and event.buttons() & Qt.LeftButton:
                    global_pos = event.globalPosition().toPoint()
                    distance = (global_pos - self.press_pos).manhattanLength()

                    if distance > QApplication.startDragDistance() and not self.drag_started:
                        self.drag_started = True
                        self.active_floating_window = self.detach_tab(
                            self.press_index,
                            global_pos,
                            drag_mode=True
                        )
                        self.press_index = -1
                        return True

            elif event.type() == event.Type.MouseButtonRelease:
                if self.drag_started and self.active_floating_window:
                    self.active_floating_window.dragging = False
                    self.active_floating_window.try_attach_by_mouse_position(
                        event.globalPosition().toPoint()
                    )

                self.press_index = -1
                self.drag_started = False
                self.active_floating_window = None

            elif event.type() == event.Type.MouseButtonDblClick and event.button() == Qt.LeftButton:
                index = self.tabBar().tabAt(event.pos())

                if index != -1:
                    self.detach_tab(
                        index,
                        event.globalPosition().toPoint(),
                        drag_mode=False
                    )

                    self.press_index = -1
                    self.drag_started = False
                    self.active_floating_window = None
                    return True

        return super().eventFilter(obj, event)

    def detach_tab(self, index, global_pos, drag_mode=False):
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

        floating_window.move_by_global_pos(global_pos)
        floating_window.show()
        floating_window.raise_()
        floating_window.activateWindow()

        if drag_mode:
            floating_window.start_follow_mouse()

        self.parent_window.floating_windows.append(floating_window)

        return floating_window