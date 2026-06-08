import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


try:
    from source_code.src.core.graph_visualizer import GraphVisualizer
except Exception as e:
    GRAPH_VISUALIZER_IMPORT_ERROR = str(e)

    class GraphVisualizer:
        def parse_edges(self, text: str, show_edge_weight=False):
            raise ImportError(
                "GraphVisualizer를 불러오지 못했습니다.\n"
                + GRAPH_VISUALIZER_IMPORT_ERROR
            )

        def build_graph(self, edges, directed=False, show_edge_weight=False):
            raise ImportError(
                "GraphVisualizer를 불러오지 못했습니다.\n"
                + GRAPH_VISUALIZER_IMPORT_ERROR
            )


class GraphController:
    def __init__(self, source_code_dir: Path):
        self.source_code_dir = source_code_dir
        self.temp_dir = self.source_code_dir / "src" / "temp"
        self.output_path = self.temp_dir / "graph_visualization.png"

        self.visualizer = GraphVisualizer()

    def visualize_graph(
        self,
        edge_text: str,
        directed: bool = False,
        show_edge_weight: bool = False
    ) -> dict:
        if not edge_text.strip():
            return {
                "success": False,
                "message": "그래프 입력이 비어 있습니다.",
                "image_path": None
            }

        try:
            edges = self.visualizer.parse_edges(
                edge_text,
                show_edge_weight=show_edge_weight
            )

            graph = self.visualizer.build_graph(
                edges=edges,
                directed=directed,
                show_edge_weight=show_edge_weight
            )

            image_path = self.save_graph_image(
                graph=graph,
                directed=directed,
                show_edge_weight=show_edge_weight
            )

            message = self.format_graph_info(
                graph=graph,
                edges=edges,
                directed=directed,
                show_edge_weight=show_edge_weight
            )

            return {
                "success": True,
                "message": message,
                "image_path": str(image_path)
            }

        except Exception as e:
            return {
                "success": False,
                "message": "[그래프 시각화 오류]\n\n" + str(e),
                "image_path": None
            }

    def save_graph_image(
        self,
        graph,
        directed: bool,
        show_edge_weight: bool
    ) -> Path:
        try:
            import matplotlib
            matplotlib.use("Agg")

            import matplotlib.pyplot as plt
            import networkx as nx

        except Exception as e:
            raise ImportError(
                "그래프 시각화를 위해 matplotlib, networkx가 필요합니다.\n"
                "터미널에서 다음 명령어를 실행하세요.\n\n"
                "python -m pip install matplotlib networkx\n\n"
                f"원인: {e}"
            )

        self.temp_dir.mkdir(parents=True, exist_ok=True)

        plt.figure(figsize=(8, 6))

        pos = nx.spring_layout(
            graph,
            seed=42
        )

        labels = {}

        for node in graph.nodes():
            labels[node] = str(node)

        nx.draw(
            graph,
            pos,
            labels=labels,
            with_labels=True,
            node_size=1000,
            arrows=directed,
            arrowsize=18,
            font_size=10
        )

        if show_edge_weight:
            edge_labels = nx.get_edge_attributes(
                graph,
                "weight"
            )

            nx.draw_networkx_edge_labels(
                graph,
                pos,
                edge_labels=edge_labels,
                font_size=9
            )

        plt.title("Graph Visualization")
        plt.axis("off")
        plt.tight_layout()

        plt.savefig(
            self.output_path,
            dpi=160,
            bbox_inches="tight"
        )

        plt.close()

        return self.output_path

    def format_graph_info(
        self,
        graph,
        edges,
        directed: bool,
        show_edge_weight: bool
    ) -> str:
        lines = []

        lines.append("[그래프 시각화 결과]")
        lines.append("")
        lines.append(f"그래프 종류: {'유향 그래프' if directed else '무향 그래프'}")
        lines.append(f"간선 가중치: {'사용' if show_edge_weight else '사용 안 함'}")
        lines.append(f"노드 수: {graph.number_of_nodes()}")
        lines.append(f"간선 수: {graph.number_of_edges()}")
        lines.append("")

        lines.append("[노드 목록]")
        nodes = sorted(list(graph.nodes()))
        lines.append(", ".join(map(str, nodes)))
        lines.append("")

        lines.append("[간선 목록]")
        arrow = "->" if directed else "--"

        if show_edge_weight:
            for u, v, w in edges:
                lines.append(f"{u} {arrow} {v}  weight={w}")
        else:
            for u, v in edges:
                lines.append(f"{u} {arrow} {v}")

        return "\n".join(lines)