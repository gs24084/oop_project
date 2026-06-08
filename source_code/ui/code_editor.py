from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import (
    QColor,
    QPainter,
    QTextCursor,
    QFontMetrics,
    QTextFormat,
    QSyntaxHighlighter,
    QTextCharFormat,
)

try:
    from pygments.lexers import CppLexer
    from pygments.token import (
        Keyword,
        Name,
        String,
        Number,
        Comment,
        Operator,
        Punctuation,
        Error,
    )

    PYGMENTS_AVAILABLE = True

except Exception:
    PYGMENTS_AVAILABLE = False


class CppHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.lexer = CppLexer() if PYGMENTS_AVAILABLE else None
        self.formats = self.create_formats()

    def create_formats(self):
        formats = {}

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000aa"))
        keyword_format.setFontWeight(700)
        formats["keyword"] = keyword_format

        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#267f99"))
        type_format.setFontWeight(600)
        formats["type"] = type_format

        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#795e26"))
        formats["function"] = function_format

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#a31515"))
        formats["string"] = string_format

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#098658"))
        formats["number"] = number_format

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#008000"))
        formats["comment"] = comment_format

        preprocessor_format = QTextCharFormat()
        preprocessor_format.setForeground(QColor("#af00db"))
        formats["preprocessor"] = preprocessor_format

        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#333333"))
        formats["operator"] = operator_format

        punctuation_format = QTextCharFormat()
        punctuation_format.setForeground(QColor("#333333"))
        formats["punctuation"] = punctuation_format

        error_format = QTextCharFormat()
        error_format.setUnderlineColor(QColor("#ff0000"))
        error_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
        formats["error"] = error_format

        return formats

    def highlightBlock(self, text):
        if not PYGMENTS_AVAILABLE or self.lexer is None:
            return

        index = 0

        for token_type, value in self.lexer.get_tokens(text):
            if not value:
                continue

            if index >= len(text):
                break

            length = min(len(value), len(text) - index)
            text_format = self.get_format_for_token(token_type)

            if text_format is not None:
                self.setFormat(index, length, text_format)

            index += len(value)

    def get_format_for_token(self, token_type):
        if token_type in Comment.Preproc:
            return self.formats["preprocessor"]

        if token_type in Comment:
            return self.formats["comment"]

        if token_type in Keyword.Type:
            return self.formats["type"]

        if token_type in Keyword:
            return self.formats["keyword"]

        if token_type in Name.Function:
            return self.formats["function"]

        if token_type in Name.Class:
            return self.formats["type"]

        if token_type in String:
            return self.formats["string"]

        if token_type in Number:
            return self.formats["number"]

        if token_type in Operator:
            return self.formats["operator"]

        if token_type in Punctuation:
            return self.formats["punctuation"]

        if token_type in Error:
            return self.formats["error"]

        return None


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None, tab_spaces=4):
        super().__init__(parent)

        self.tab_spaces = tab_spaces
        self.line_number_area = LineNumberArea(self)
        self.highlighter = CppHighlighter(self.document())

        self.open_to_close = {
            "(": ")",
            "[": "]",
            "{": "}",
            '"': '"',
            "'": "'",
        }

        self.close_chars = {
            ")",
            "]",
            "}",
            '"',
            "'",
        }

        self.update_tab_width()

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def update_tab_width(self):
        space_width = QFontMetrics(self.font()).horizontalAdvance(" ")
        self.setTabStopDistance(space_width * self.tab_spaces)

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 12 + self.fontMetrics().horizontalAdvance("9") * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0,
                rect.y(),
                self.line_number_area.width(),
                rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        content_rect = self.contentsRect()

        self.line_number_area.setGeometry(
            QRect(
                content_rect.left(),
                content_rect.top(),
                self.line_number_area_width(),
                content_rect.height()
            )
        )

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#f3f3f3"))
        painter.setPen(QColor("#888888"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()

        top = int(
            self.blockBoundingGeometry(block)
            .translated(self.contentOffset())
            .top()
        )

        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)

                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number
                )

            block = block.next()
            top = bottom

            if block.isValid():
                bottom = top + int(self.blockBoundingRect(block).height())

            block_number += 1

    def highlight_current_line(self):
        selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            line_color = QColor("#fff8dc")
            selection.format.setBackground(line_color)
            selection.format.setProperty(
                QTextFormat.Property.FullWidthSelection,
                True
            )

            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()

            selections.append(selection)

        self.setExtraSelections(selections)

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()

        if key == Qt.Key.Key_Tab:
            self.insertPlainText(" " * self.tab_spaces)
            return

        if key == Qt.Key.Key_Backtab:
            self.remove_indent()
            return

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.handle_enter()
            return

        if key == Qt.Key.Key_Backspace:
            if self.remove_empty_pair():
                return

            super().keyPressEvent(event)
            return

        if text in self.open_to_close:
            self.insert_pair(text)
            return

        if text in self.close_chars:
            if self.skip_existing_close_char(text):
                return

        super().keyPressEvent(event)

    def handle_enter(self):
        cursor = self.textCursor()
        block_text = cursor.block().text()
        position_in_block = cursor.positionInBlock()

        before_cursor = block_text[:position_in_block]
        after_cursor = block_text[position_in_block:]

        current_indent = self.get_line_indent(block_text)
        next_indent = current_indent

        stripped_before = before_cursor.rstrip()
        stripped_after = after_cursor.lstrip()

        if stripped_before.endswith("{"):
            next_indent += " " * self.tab_spaces

        if stripped_before.endswith("{") and stripped_after.startswith("}"):
            insert_text = "\n" + next_indent + "\n" + current_indent
            cursor.insertText(insert_text)

            new_position = cursor.position() - (len(current_indent) + 1)
            cursor.setPosition(new_position)
            self.setTextCursor(cursor)
            return

        cursor.insertText("\n" + next_indent)
        self.setTextCursor(cursor)

    def get_line_indent(self, line_text):
        indent = []

        for ch in line_text:
            if ch == " ":
                indent.append(ch)
            elif ch == "\t":
                indent.append(" " * self.tab_spaces)
            else:
                break

        return "".join(indent)

    def insert_pair(self, open_char):
        close_char = self.open_to_close[open_char]
        cursor = self.textCursor()

        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(open_char + selected_text + close_char)
            self.setTextCursor(cursor)
            return

        cursor.insertText(open_char + close_char)
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        self.setTextCursor(cursor)

    def skip_existing_close_char(self, close_char):
        cursor = self.textCursor()
        next_char = self.get_next_char(cursor)

        if next_char == close_char:
            cursor.movePosition(QTextCursor.MoveOperation.Right)
            self.setTextCursor(cursor)
            return True

        return False

    def remove_empty_pair(self):
        cursor = self.textCursor()

        if cursor.hasSelection():
            return False

        prev_char = self.get_previous_char(cursor)
        next_char = self.get_next_char(cursor)

        if not prev_char or not next_char:
            return False

        if self.open_to_close.get(prev_char) != next_char:
            return False

        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        cursor.movePosition(
            QTextCursor.MoveOperation.Right,
            QTextCursor.MoveMode.KeepAnchor,
            2
        )
        cursor.removeSelectedText()
        cursor.endEditBlock()

        self.setTextCursor(cursor)
        return True

    def get_previous_char(self, cursor):
        if cursor.position() <= 0:
            return ""

        temp_cursor = QTextCursor(cursor)
        temp_cursor.movePosition(QTextCursor.MoveOperation.Left)
        temp_cursor.movePosition(
            QTextCursor.MoveOperation.Right,
            QTextCursor.MoveMode.KeepAnchor
        )

        return temp_cursor.selectedText()

    def get_next_char(self, cursor):
        if cursor.position() >= len(self.toPlainText()):
            return ""

        temp_cursor = QTextCursor(cursor)
        temp_cursor.movePosition(
            QTextCursor.MoveOperation.Right,
            QTextCursor.MoveMode.KeepAnchor
        )

        return temp_cursor.selectedText()

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