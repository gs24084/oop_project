import re
import requests


class ComplexityAnalyzer:
#시간복잡도 분석 클래스, ollama 로컬 llm 모델을 이용해서 시간복잡도 분석.
    def __init__(
        self,
        use_ollama=True,
        model="qwen3:0.6b"
    ):
        self.use_ollama = use_ollama
        self.model = model

    def analyze(self, code: str) -> dict:

        result = {
            "static": self._static_analyze(code)
        }

        if self.use_ollama:
            result["ollama"] = (
                self._ollama_analyze(code)
            )

        return result

    def _static_analyze(
        self,
        code: str
    ) -> dict:

        evidence = []

        complexity = "O(1)"

        # sort

        if re.search(
            r"\bsort\s*\(",
            code
        ):
            complexity = "O(n log n)"
            evidence.append(
                "std::sort detected"
            )

        # priority_queue

        if "priority_queue" in code:
            evidence.append(
                "priority_queue detected"
            )

        # map / set

        if re.search(
            r"\b(map|set|multiset|multimap)\b",
            code
        ):
            evidence.append(
                "balanced tree container detected"
            )

        # 반복문 개수

        loop_count = len(
            re.findall(
                r"\bfor\s*\(",
                code
            )
        )

        loop_count += len(
            re.findall(
                r"\bwhile\s*\(",
                code
            )
        )

        evidence.append(
            f"loop count = {loop_count}"
        )

        if complexity == "O(1)":

            if loop_count == 1:
                complexity = "O(n)"

            elif loop_count == 2:
                complexity = "O(n²)"

            elif loop_count == 3:
                complexity = "O(n³)"

        recursion = self._detect_recursion(
            code
        )

        if recursion:
            evidence.append(
                "recursive function detected"
            )

        return {
            "complexity": complexity,
            "evidence": evidence
        }

    def _detect_recursion(
        self,
        code: str
    ) -> bool:

        functions = re.findall(
            r"(?:int|void|long long|bool|string|double)\s+(\w+)\s*\(",
            code
        )

        for func in functions:

            pattern = (
                func
                + r"\s*\("
            )

            calls = len(
                re.findall(
                    pattern,
                    code
                )
            )

            if calls >= 2:
                return True

        return False

    def _ollama_analyze(
        self,
        code: str
    ) -> dict:

        prompt = f"""
You are a competitive programming expert.

Analyze the following C++ code.

Return ONLY the following format.

Complexity: <complexity>

Reason:
- ...
- ...

Do NOT include the original code.
Do NOT repeat the prompt.
Do NOT add markdown.

Code:

{code}
"""

        try:

            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )

            response.raise_for_status()

            return {
                "success": True,
                "response":
                response.json()["response"]
            }

        except Exception as e:

            return {
                "success": False,
                "response": str(e)
            }