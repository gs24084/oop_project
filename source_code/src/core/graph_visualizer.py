import networkx as nx
import matplotlib.pyplot as plt


class GraphVisualizer:

    def __init__(self):
        pass

    def parse_edges(self, text: str):
        """
        입력 예시

        1 2
        1 3
        2 4
        3 5
        """

        edges = []

        lines = text.strip().splitlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            if len(parts) != 2:
                raise ValueError(
                    f"잘못된 간선 형식: {line}"
                )

            u, v = parts

            try:
                u = int(u)
                v = int(v)
            except ValueError:
                raise ValueError(
                    f"정점 번호는 정수여야 합니다: {line}"
                )

            edges.append((u, v))

        return edges

    def build_graph(self, edges):

        graph = nx.Graph()

        graph.add_edges_from(edges)

        return graph

    def visualize(self, edge_text: str):

        edges = self.parse_edges(edge_text)

        graph = self.build_graph(edges)

        plt.figure(figsize=(8, 6))

        pos = nx.spring_layout(
            graph,
            seed=42
        )

        nx.draw(
            graph,
            pos,
            with_labels=True,
            node_size=1000
        )

        plt.title("Graph Visualization")

        plt.show()