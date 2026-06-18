from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox

from source_code.ui.cpp_templates import default_cpp_code

# 파일 관련 동작을 제어하는 클래스. 새 파일 생성, C++ 파일 열기, 저장, 기본 코드 불러오기 등 코드 에디터와 연결된 파일 입출력 기능을 처리한다.
class FileController:
    def __init__(self, parent, editor, default_cpp_path: Path):
        self.parent = parent
        self.editor = editor
        self.default_cpp_path = default_cpp_path
        self.current_file_path = None

    def new_file(self):
        if self.editor.toPlainText().strip():
            answer = QMessageBox.question(
                self.parent,
                "새 파일",
                "현재 코드를 지우고 새 파일을 만들까요?"
            )

            if answer != QMessageBox.StandardButton.Yes:
                return

        self.editor.clear()
        self.current_file_path = None
        self.parent.statusBar().showMessage("새 파일을 만들었습니다.")

    def open_cpp_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
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
            self.parent.statusBar().showMessage(f"파일을 열었습니다: {file_path}")

        except Exception as e:
            QMessageBox.critical(self.parent, "열기 실패", str(e))

    def save_cpp_file(self):
        code = self.editor.toPlainText()

        if self.current_file_path:
            try:
                with open(self.current_file_path, "w", encoding="utf-8") as f:
                    f.write(code)

                self.parent.statusBar().showMessage(f"저장 완료: {self.current_file_path}")
                return

            except Exception as e:
                QMessageBox.critical(self.parent, "저장 실패", str(e))
                return

        file_path, _ = QFileDialog.getSaveFileName(
            self.parent,
            "C++ 파일 저장",
            "main.cpp",
            "C++ Files (*.cpp);;All Files (*)"
        )

        if not file_path:
            return

        if not file_path.endswith(".cpp"):
            file_path += ".cpp"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)

            self.current_file_path = file_path
            self.parent.statusBar().showMessage(f"저장 완료: {file_path}")

        except Exception as e:
            QMessageBox.critical(self.parent, "저장 실패", str(e))

    def load_default_cpp_code(self):
        if self.default_cpp_path.exists():
            try:
                with open(self.default_cpp_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                return default_cpp_code()

        return default_cpp_code()