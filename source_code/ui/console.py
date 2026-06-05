from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor


class ConsoleBox(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.run_callback = None
        self.prompt = ">>> "
        self.setPlainText(self.prompt)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
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
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

        current = self.toPlainText()

        if not current.endswith("\n"):
            self.insertPlainText("\n")

        if text:
            self.insertPlainText(str(text).rstrip() + "\n")

        self.insertPlainText(self.prompt)

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

    def reset_console(self):
        self.setPlainText(self.prompt)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)