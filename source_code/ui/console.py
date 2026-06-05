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
        key = event.key()
        modifiers = event.modifiers()

        if key in (Qt.Key_Return, Qt.Key_Enter):
            if modifiers & Qt.ShiftModifier:
                self.insertPlainText("\n")
                return

            line_text = self.get_current_line()
            self.insertPlainText("\n")

            if self.run_callback:
                self.run_callback(line_text)

            return

        super().keyPressEvent(event)

    def get_current_line(self):
        text = self.toPlainText()
        lines = text.splitlines()

        if not lines:
            return ""

        last_line = lines[-1]

        if last_line.startswith(self.prompt):
            return last_line[len(self.prompt):]

        return last_line

    def get_current_input(self):
        text = self.toPlainText()
        prompt_index = text.rfind(self.prompt)

        if prompt_index == -1:
            input_text = text
        else:
            input_text = text[prompt_index + len(self.prompt):]

        input_text = input_text.rstrip("\n")

        if input_text:
            return input_text + "\n"

        return ""

    def append_process_output(self, text):
        self.move_cursor_to_end()

        if text is None:
            return

        output_text = str(text)

        if not output_text:
            return

        self.insertPlainText(output_text)
        self.move_cursor_to_end()

    def append_output(self, text):
        self.move_cursor_to_end()
        self.remove_last_empty_prompt()

        current = self.toPlainText()

        if not current.endswith("\n"):
            self.insertPlainText("\n")

        if text is not None:
            output_text = str(text).rstrip()
            if output_text:
                self.insertPlainText(output_text + "\n")

        self.insertPlainText(self.prompt)
        self.move_cursor_to_end()

    def append_prompt(self):
        self.move_cursor_to_end()

        current = self.toPlainText()

        if not current.endswith("\n"):
            self.insertPlainText("\n")

        self.insertPlainText(self.prompt)
        self.move_cursor_to_end()

    def ensure_newline(self):
        self.move_cursor_to_end()

        current = self.toPlainText()

        if current and not current.endswith("\n"):
            self.insertPlainText("\n")

    def reset_console(self):
        self.setPlainText(self.prompt)
        self.move_cursor_to_end()

    def move_cursor_to_end(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

    def remove_last_empty_prompt(self):
        current = self.toPlainText()

        if not current.endswith(self.prompt):
            return

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        for _ in range(len(self.prompt)):
            cursor.movePosition(
                QTextCursor.MoveOperation.Left,
                QTextCursor.MoveMode.KeepAnchor
            )

        cursor.removeSelectedText()
        self.setTextCursor(cursor)