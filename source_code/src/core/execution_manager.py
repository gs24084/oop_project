# src/core/execution_manager.py

import subprocess
import time
from pathlib import Path


class ExecutionManager:
    def __init__(self, compiler=r"C:\Users\deepb\Downloads\winlibs-x86_64-posix-seh-gcc-16.1.0-mingw-w64ucrt-14.0.0-r2\mingw64\bin\g++.exe"
):
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

        command = [
            self.compiler,
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
            result = subprocess.run(
                [str(exe_file)],
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=timeout
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