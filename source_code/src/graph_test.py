from core.graph_visualizer import GraphVisualizer

text = """
1 2
1 3
2 4
3 5
"""

visualizer = GraphVisualizer()

visualizer.visualize(
    """
    1 2 5
    1 3 7
    2 4 10
    3 5 4
    """,
    directed=True,
    show_edge_weight=True,
    show_node_weight=True,
    node_weights={
        1: 100,
        2: 30,
        3: 50,
        4: 20,
        5: 10
    }
)