from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QFontMetrics


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
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)

        line_text = cursor.selectedText()

        remove_count = 0

        for ch in line_text[:self.tab_spaces]:
            if ch == " ":
                remove_count += 1
            else:
                break

        if remove_count == 0:
            return

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)

        for _ in range(remove_count):
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)

        cursor.removeSelectedText()
        self.setTextCursor(cursor)