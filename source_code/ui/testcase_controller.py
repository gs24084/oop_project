class TestCaseController:
    def __init__(self, execution_controller):
        self.execution_controller = execution_controller
        self.testcases = []

    def add_testcase(self, input_text: str, expected_output: str):
        case = {
            "input": input_text,
            "expected": expected_output,
            "actual": "",
            "status": "not run",
            "message": ""
        }

        self.testcases.append(case)

    def delete_testcase(self, index: int):
        if 0 <= index < len(self.testcases):
            self.testcases.pop(index)

    def clear_testcases(self):
        self.testcases.clear()

    def get_testcases(self):
        return self.testcases

    def run_single(self, code: str, index: int) -> dict:
        if not (0 <= index < len(self.testcases)):
            return {
                "success": False,
                "type": "testcase",
                "status": "error",
                "message": "선택한 테스트케이스가 없습니다."
            }

        case = self.testcases[index]

        result = self.execution_controller.run_code(
            code=code,
            input_text=case["input"],
            timeout=2
        )

        judged = self.judge_result(
            result=result,
            expected_output=case["expected"]
        )

        case["actual"] = judged["actual"]
        case["status"] = judged["status"]
        case["message"] = judged["message"]

        return {
            **result,
            **judged,
            "index": index,
            "input": case["input"],
            "expected": case["expected"]
        }

    def run_all(self, code: str) -> list:
        results = []

        for i in range(len(self.testcases)):
            result = self.run_single(code, i)
            results.append(result)

            if result.get("type") == "compile":
                break

        return results

    def judge_result(self, result: dict, expected_output: str) -> dict:
        if result.get("type") == "compile":
            return {
                "status": "compile error",
                "actual": "",
                "message": result.get("message", "")
            }

        if not result.get("success"):
            stderr = result.get("stderr", "") or "실행 중 오류가 발생했습니다."
            return {
                "status": "runtime error",
                "actual": result.get("stdout", ""),
                "message": stderr
            }

        actual = result.get("stdout", "") or ""
        expected = expected_output or ""

        if not expected.strip():
            return {
                "status": "executed",
                "actual": actual,
                "message": "예상 출력이 없어 정답 여부는 비교하지 않았습니다."
            }

        if self.normalize_output(actual) == self.normalize_output(expected):
            return {
                "status": "accepted",
                "actual": actual,
                "message": "정답"
            }

        return {
            "status": "wrong answer",
            "actual": actual,
            "message": "예상 출력과 실제 출력이 다릅니다."
        }

    def normalize_output(self, text: str) -> str:
        lines = text.strip().splitlines()
        lines = [line.rstrip() for line in lines]
        return "\n".join(lines)

    def format_case_for_list(self, index: int, case: dict) -> str:
        status = case.get("status", "not run")

        input_preview = self.make_preview(case.get("input", ""))
        expected_preview = self.make_preview(case.get("expected", ""))

        return (
            f"{index + 1}. [{status}] "
            f"input: {input_preview} / expected: {expected_preview}"
        )

    def make_preview(self, text: str, max_len: int = 35) -> str:
        text = text.replace("\n", "\\n").strip()

        if not text:
            return "(empty)"

        if len(text) > max_len:
            return text[:max_len] + "..."

        return text

    def format_single_result(self, result: dict) -> str:
        index = result.get("index", 0) + 1

        lines = []
        lines.append(f"[테스트케이스 {index} 실행 결과]")
        lines.append("")
        lines.append("[입력]")
        lines.append(result.get("input", "").rstrip() or "(empty)")
        lines.append("")
        lines.append("[예상 출력]")
        lines.append(result.get("expected", "").rstrip() or "(empty)")
        lines.append("")
        lines.append("[실제 출력]")
        lines.append(result.get("actual", "").rstrip() or "(empty)")
        lines.append("")
        lines.append(f"[판정] {result.get('status', 'unknown')}")
        lines.append(result.get("message", ""))

        if "execution_time" in result:
            lines.append("")
            lines.append(f"[실행 시간] {result.get('execution_time')}s")

        return "\n".join(lines)

    def format_all_results(self, results: list) -> str:
        if not results:
            return "[테스트케이스 전체 실행]\n\n실행할 테스트케이스가 없습니다."

        accepted = 0
        wrong = 0
        runtime_error = 0
        compile_error = 0
        executed = 0

        lines = []
        lines.append("[테스트케이스 전체 실행 결과]")
        lines.append("")

        for result in results:
            status = result.get("status", "unknown")
            index = result.get("index", 0) + 1

            if status == "accepted":
                accepted += 1
            elif status == "wrong answer":
                wrong += 1
            elif status == "runtime error":
                runtime_error += 1
            elif status == "compile error":
                compile_error += 1
            elif status == "executed":
                executed += 1

            lines.append(f"{index}. {status}")

            message = result.get("message", "")
            if message:
                lines.append(f"   {message}")

        lines.append("")
        lines.append("[요약]")
        lines.append(f"정답: {accepted}")
        lines.append(f"오답: {wrong}")
        lines.append(f"실행 완료: {executed}")
        lines.append(f"런타임 에러: {runtime_error}")
        lines.append(f"컴파일 에러: {compile_error}")

        return "\n".join(lines)