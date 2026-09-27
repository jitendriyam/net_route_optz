from app.graph.shortest_path import Dijkstra


def test_dijkstra_returns_minimum_latency_path() -> None:
    graph = {
        "A": [("B", 4), ("C", 1)],
        "B": [("D", 1)],
        "C": [("B", 1), ("D", 8)],
        "D": [],
    }

    assert Dijkstra().find_path(graph, "A", "D") == {
        "path": ["A", "C", "B", "D"],
        "total_latency": 3,
    }


def test_dijkstra_returns_none_when_unreachable() -> None:
    assert Dijkstra().find_path({"A": [], "B": []}, "A", "B") is None
