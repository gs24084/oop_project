from pathlib import Path


try:
    from source_code.src.core.execution_manager import ExecutionManager
except Exception as e:
    IMPORT_ERROR_MESSAGE = str(e)

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


class RunController:
    def __init__(self, source_code_dir: Path):
        self.source_code_dir = source_code_dir
        self.temp_dir = self.source_code_dir / "src" / "temp"

        self.run_cpp_path = self.temp_dir / "editor_run.cpp"
        self.run_exe_path = self.temp_dir / "editor_run.exe"

        self.execution_manager = ExecutionManager()

    def save_editor_code(self, code: str):
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        with open(self.run_cpp_path, "w", encoding="utf-8") as f:
            f.write(code)

    def build(self, code: str) -> dict:
        if not code.strip():
            return {
                "success": False,
                "type": "build",
                "message": "코드가 비어 있습니다."
            }

        self.save_editor_code(code)

        compile_result = self.execution_manager.compile_code(
            str(self.run_cpp_path),
            str(self.run_exe_path)
        )

        return {
            "success": compile_result.get("success", False),
            "type": "build",
            "message": compile_result.get("message", ""),
            "cpp_path": str(self.run_cpp_path),
            "exe_path": str(self.run_exe_path)
        }

    def run(self, code: str, input_text: str, timeout: int = 2) -> dict:
        build_result = self.build(code)

        if not build_result.get("success"):
            return {
                "success": False,
                "type": "compile",
                "message": build_result.get("message", ""),
                "cpp_path": build_result.get("cpp_path", ""),
                "exe_path": build_result.get("exe_path", "")
            }

        run_result = self.execution_manager.run_code(
            str(self.run_exe_path),
            stdin_data=input_text,
            timeout=timeout
        )

        return {
            "success": run_result.get("success", False),
            "type": "run",
            "stdout": run_result.get("stdout", ""),
            "stderr": run_result.get("stderr", ""),
            "execution_time": run_result.get("execution_time", 0.0),
            "cpp_path": str(self.run_cpp_path),
            "exe_path": str(self.run_exe_path)
        }

    def debug(self, code: str, input_text: str, timeout: int = 2) -> dict:
        result = self.run(code, input_text, timeout)

        debug_message = [
            "[Debug Info]",
            f"source file: {self.run_cpp_path}",
            f"executable: {self.run_exe_path}",
            f"input: {repr(input_text)}",
            f"success: {result.get('success')}",
            f"type: {result.get('type')}",
            f"execution_time: {result.get('execution_time', 0.0)}s",
        ]

        if result.get("type") == "compile":
            debug_message.append("\n[Compile Message]")
            debug_message.append(result.get("message", ""))

        else:
            debug_message.append("\n[stdout]")
            debug_message.append(result.get("stdout", ""))

            debug_message.append("\n[stderr]")
            debug_message.append(result.get("stderr", ""))

        return {
            **result,
            "debug_message": "\n".join(debug_message)
        }