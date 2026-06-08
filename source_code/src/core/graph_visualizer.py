import networkx as nx
import matplotlib.pyplot as plt


class GraphVisualizer:

    def parse_edges(
        self,
        text: str,
        show_edge_weight=False
    ):

        edges = []

        lines = text.strip().splitlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            if show_edge_weight:

                if len(parts) != 3:
                    raise ValueError(
                        f"잘못된 간선 형식: {line}"
                    )

                u, v, w = map(int, parts)

                edges.append(
                    (u, v, w)
                )

            else:

                if len(parts) != 2:
                    raise ValueError(
                        f"잘못된 간선 형식: {line}"
                    )

                u, v = map(int, parts)

                edges.append(
                    (u, v)
                )

        return edges

    def build_graph(
        self,
        edges,
        directed=False,
        show_edge_weight=False
    ):

        graph = (
            nx.DiGraph()
            if directed
            else nx.Graph()
        )

        if show_edge_weight:

            for u, v, w in edges:

                graph.add_edge(
                    u,
                    v,
                    weight=w
                )

        else:

            graph.add_edges_from(edges)

        return graph

    def visualize(
        self,
        edge_text: str,
        directed=False,
        show_node_weight=False,
        show_edge_weight=False,
        node_weights=None
    ):

        edges = self.parse_edges(
            edge_text,
            show_edge_weight
        )

        graph = self.build_graph(
            edges,
            directed,
            show_edge_weight
        )

        plt.figure(
            figsize=(8, 6)
        )

        pos = nx.spring_layout(
            graph,
            seed=42
        )

        # 노드 라벨 생성

        labels = {}

        for node in graph.nodes():

            if (
                show_node_weight
                and node_weights is not None
            ):

                weight = node_weights.get(
                    node,
                    ""
                )

                labels[node] = (
                    f"{node}\n({weight})"
                )

            else:

                labels[node] = str(node)

        # 그래프 그리기

        nx.draw(
            graph,
            pos,
            labels=labels,
            with_labels=True,
            node_size=1000,
            arrows=directed
        )

        # 간선 가중치 표시

        if show_edge_weight:

            edge_labels = nx.get_edge_attributes(
                graph,
                "weight"
            )

            nx.draw_networkx_edge_labels(
                graph,
                pos,
                edge_labels=edge_labels
            )

        plt.title(
            "Graph Visualization"
        )

        plt.show()