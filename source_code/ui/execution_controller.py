import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


try:
    from source_code.src.core.execution_manager import ExecutionManager
except Exception as e:
    IMPORT_ERROR_MESSAGE = str(e)

    # execution_manager.py에서 정의한 class 미작동 시 대체 클래스.
    class ExecutionManager:
        def __init__(self, compiler="g++"):
            self.compiler = compiler

        def compile_code(self, cpp_path: str, output_path: str) -> dict:
            return {
                "success": False,
                "message": "ExecutionManager를 불러오지 못했습니다.\n" + IMPORT_ERROR_MESSAGE
            }

        def run_code(self, executable_path: str, stdin_data: str = "", timeout: int = 2) -> dict:
            return {
                "success": False,
                "stdout": "",
                "stderr": "ExecutionManager를 불러오지 못했습니다.\n" + IMPORT_ERROR_MESSAGE,
                "execution_time": 0.0
            }

# UI와 실행 엔진 사이를 연결하는 클래스. 에디터의 코드를 임시 C++ 파일로 저장한 뒤 ExecutionManager에 실행을 요청하고, 컴파일 및 실행 결과를 콘솔에 표시하기 적절한 형태로 정리한다.
class ExecutionController:
    def __init__(self, source_code_dir: Path):
        self.source_code_dir = source_code_dir

        self.run_cpp_path = self.source_code_dir / "src" / "temp" / "editor_run.cpp"
        self.run_exe_path = self.source_code_dir / "src" / "temp" / "editor_run.exe"

        self.execution_manager = ExecutionManager()

    def save_code_to_temp(self, code: str):
        self.run_cpp_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.run_cpp_path, "w", encoding="utf-8") as f:
            f.write(code)

    def compile_code(self, code: str) -> dict:
        if not code.strip():
            return {
                "success": False,
                "type": "compile",
                "message": "코드가 비어 있습니다.",
                "cpp_path": str(self.run_cpp_path),
                "exe_path": str(self.run_exe_path)
            }

        self.save_code_to_temp(code)

        compile_result = self.execution_manager.compile_code(
            str(self.run_cpp_path),
            str(self.run_exe_path)
        )

        return {
            "success": compile_result.get("success", False),
            "type": "compile",
            "message": compile_result.get("message", ""),
            "cpp_path": str(self.run_cpp_path),
            "exe_path": str(self.run_exe_path)
        }

    def run_code(self, code: str, input_text: str, timeout: int = 2) -> dict:
        compile_result = self.compile_code(code)

        if not compile_result.get("success"):
            return {
                "success": False,
                "type": "compile",
                "message": compile_result.get("message", ""),
                "stdout": "",
                "stderr": "",
                "execution_time": 0.0,
                "cpp_path": compile_result.get("cpp_path", ""),
                "exe_path": compile_result.get("exe_path", "")
            }

        run_result = self.execution_manager.run_code(
            str(self.run_exe_path),
            stdin_data=input_text,
            timeout=timeout
        )

        return {
            "success": run_result.get("success", False),
            "type": "run",
            "message": "",
            "stdout": run_result.get("stdout", "") or "",
            "stderr": run_result.get("stderr", "") or "",
            "execution_time": run_result.get("execution_time", 0.0) or 0.0,
            "cpp_path": str(self.run_cpp_path),
            "exe_path": str(self.run_exe_path)
        }

    def format_build_result(self, result: dict) -> str:
        if result.get("success"):
            text = "[Build Success]\n\n"
            text += result.get("message", "")
            text += "\n\n[Source]\n"
            text += result.get("cpp_path", "")
            text += "\n\n[Executable]\n"
            text += result.get("exe_path", "")
            return text

        text = "[Build Failed]\n\n"
        text += result.get("message", "")
        return text

    def format_debug_result(self, result: dict, input_text: str) -> str:
        stdout = result.get("stdout", "") or ""
        stderr = result.get("stderr", "") or ""
        message = result.get("message", "") or ""

        lines = []
        lines.append("[Debug Info]")
        lines.append("")
        lines.append(f"source file: {result.get('cpp_path', str(self.run_cpp_path))}")

        if result.get("type") == "compile" and not result.get("success"):
            lines.append("executable: 컴파일 실패로 새 실행 파일이 생성되지 않았습니다.")
        else:
            lines.append(f"executable: {result.get('exe_path', str(self.run_exe_path))}")

        lines.append(f"input: {repr(input_text)}")
        lines.append(f"result type: {result.get('type')}")
        lines.append(f"success: {result.get('success')}")
        lines.append(f"execution time: {result.get('execution_time', 0.0)}s")

        if result.get("type") == "compile":
            lines.append("")
            lines.append("[Compile Message]")

            if message:
                lines.append(message)
            else:
                lines.append(
                    "컴파일에 실패했지만 컴파일러 메시지를 받지 못했습니다.\n"
                    "execution_manager.py에서 stderr 또는 stdout 전달을 확인해야 합니다."
                )

        elif result.get("type") == "run":
            lines.append("")
            lines.append("[stdout]")
            lines.append(stdout if stdout else "(empty)")

            lines.append("")
            lines.append("[stderr]")
            lines.append(stderr if stderr else "(empty)")

        return "\n".join(str(x) for x in lines)