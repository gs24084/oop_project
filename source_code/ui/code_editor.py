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