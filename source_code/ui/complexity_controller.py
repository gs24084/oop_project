import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


try:
    from source_code.src.core.complexity_analyzer import ComplexityAnalyzer
except Exception as e:
    COMPLEXITY_IMPORT_ERROR = str(e)

    class ComplexityAnalyzer:
        def __init__(self, use_ollama=True, model="qwen3:0.6b"):
            self.use_ollama = use_ollama
            self.model = model

        def analyze(self, code: str) -> dict:
            return {
                "static": {
                    "complexity": "분석 불가",
                    "evidence": [
                        "ComplexityAnalyzer를 불러오지 못했습니다.",
                        COMPLEXITY_IMPORT_ERROR
                    ]
                }
            }


class ComplexityController:
    def __init__(self, use_ollama=True):
        self.analyzer = ComplexityAnalyzer(use_ollama=use_ollama)

    def analyze_code(self, code: str) -> str:
        if not code.strip():
            return "분석할 코드가 없습니다."

        try:
            result = self.analyzer.analyze(code)

            static_result = result.get("static", {})
            complexity = static_result.get("complexity", "알 수 없음")
            evidence = static_result.get("evidence", [])

            lines = []
            lines.append("[시간복잡도 분석 결과]")
            lines.append("")
            lines.append(f"추정 시간복잡도: {complexity}")
            lines.append("")
            lines.append("[근거]")

            if evidence:
                for item in evidence:
                    lines.append(f"- {item}")
            else:
                lines.append("- 근거 없음")

            if "ollama" in result:
                ollama_result = result["ollama"]

                lines.append("")
                lines.append("[Ollama 분석 결과]")

                if ollama_result.get("success"):
                    lines.append(ollama_result.get("response", ""))
                else:
                    lines.append("Ollama 분석 실패")
                    lines.append(ollama_result.get("response", ""))

            return "\n".join(lines)

        except Exception as e:
            return "[시간복잡도 분석 오류]\n\n" + str(e)