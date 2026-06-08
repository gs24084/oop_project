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
                "ollama": {
                    "success": False,
                    "response": (
                        "ComplexityAnalyzer를 불러오지 못했습니다.\n\n"
                        + COMPLEXITY_IMPORT_ERROR
                    )
                }
            }


class ComplexityController:
    def __init__(self, use_ollama=True):
        self.use_ollama = use_ollama
        self.analyzer = ComplexityAnalyzer(use_ollama=use_ollama)

    def analyze_code(self, code: str) -> str:
        if not code.strip():
            return "분석할 코드가 없습니다."

        try:
            result = self.analyzer.analyze(code)
            ollama_result = result.get("ollama", {})

            if ollama_result.get("success"):
                return self.format_ollama_success(
                    ollama_response=ollama_result.get("response", "")
                )

            return self.format_ollama_failed(
                ollama_error=ollama_result.get("response", "")
            )

        except Exception as e:
            return "[시간복잡도 분석 오류]\n\n" + str(e)

    def format_ollama_success(self, ollama_response: str) -> str:
        lines = []

        lines.append("[Ollama 시간복잡도 분석 결과]")
        lines.append("")

        if ollama_response and ollama_response.strip():
            lines.append(ollama_response.strip())
        else:
            lines.append("Ollama 응답이 비어 있습니다.")

        return "\n".join(lines)

    def format_ollama_failed(self, ollama_error: str) -> str:
        lines = []

        lines.append("[Ollama 분석 불가]")
        lines.append("")
        lines.append("Ollama가 실행되지 않으면 시간복잡도를 분석할 수 없습니다.")
        lines.append("")

        if ollama_error and str(ollama_error).strip():
            lines.append("[원인]")
            lines.append(str(ollama_error).strip())
        else:
            lines.append("[원인]")
            lines.append("Ollama 분석 중 알 수 없는 오류가 발생했습니다.")

        return "\n".join(lines)