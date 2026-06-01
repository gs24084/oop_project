# test_execution.py

from src.core.execution_manager import ExecutionManager

manager = ExecutionManager()

compile_result = manager.compile_code(
    "src/temp/main.cpp",
    "src/temp/main.exe"
)

print("Compile Result")
print(compile_result)

if compile_result["success"]:
    run_result = manager.run_code(
        "src/temp/main.exe",
        "5\n"
    )

    print("\nRun Result")
    print(run_result)