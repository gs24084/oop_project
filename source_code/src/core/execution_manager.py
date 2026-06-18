# src/core/execution_manager.py

import subprocess
import time
from pathlib import Path
import os
import shutil
#코드 실행 담당 클래스. gcc 컴파일러를 사용해 cpp 파일을 실행하고 출력값/리턴값 반환 가능.
class ExecutionManager:
    def __init__(self, compiler="g++"):
        self.compiler = compiler

    def compile_code(
        self,
        cpp_path: str,
        output_path: str = "temp/main.exe"
    ) -> dict:
        """
        C++ 파일 컴파일

        Returns:
        {
            "success": bool,
            "message": str
        }
        """

        cpp_file = Path(cpp_path)

        if not cpp_file.exists():
            return {
                "success": False,
                "message": f"File not found: {cpp_path}"
            }
        compiler_path = shutil.which(self.compiler)

        if compiler_path is None:
            return {
                "success": False,
                "message": "g++ compiler not found. Please install GCC and add it to PATH."
            }
        command = [
            compiler_path,
            str(cpp_file),
            "-std=c++17",
            "-O2",
            "-o",
            output_path
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Compile Success"
                }

            return {
                "success": False,
                "message": result.stderr
            }

        except FileNotFoundError:
            return {
                "success": False,
                "message": "g++ compiler not found"
            }

    def run_code(
        self,
        executable_path: str,
        stdin_data: str = "",
        timeout: int = 2
    ) -> dict:
        """
        실행파일 실행

        Returns:
        {
            "success": bool,
            "stdout": str,
            "stderr": str,
            "execution_time": float
        }
        """

        exe_file = Path(executable_path)

        if not exe_file.exists():
            return {
                "success": False,
                "stdout": "",
                "stderr": "Executable not found",
                "execution_time": 0.0
            }

        start_time = time.perf_counter()

        try:
            compiler_path = shutil.which(self.compiler)

            if compiler_path is None:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "g++ compiler not found",
                    "execution_time": 0.0
                }

            compiler_bin = str(Path(compiler_path).parent)

            env = os.environ.copy()
            env["PATH"] = compiler_bin + ";" + env["PATH"]

            result = subprocess.run(
                [str(exe_file)],
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            print("returncode =", result.returncode)
            print("stdout =", repr(result.stdout))
            print("stderr =", repr(result.stderr))

            end_time = time.perf_counter()

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": round(
                    end_time - start_time,
                    6
                )
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Time Limit Exceeded ({timeout}s)",
                "execution_time": float(timeout)
            }