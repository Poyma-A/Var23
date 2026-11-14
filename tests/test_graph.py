import unittest

from src.graph import build_graph


class GraphTests(unittest.TestCase):
    def test_shorter_path(self):
        source = {
            "A": ["B", "C"],
            "B": ["C"],
            "C": ["D"],
        }
        graph = build_graph(
            "A", source.__getitem__, 2
        )
        self.assertEqual(
            graph["C"], ["D"]
        )
        self.assertEqual(graph["D"], [])

    def test_cycle(self):
        source = {
            "A": ["B"], "B": ["A"]
        }
        graph = build_graph(
            "A", source.__getitem__, 10
        )
        self.assertEqual(graph, source)

    def test_filter(self):
        source = {"A": ["B", "CC"]}
        graph = build_graph(
            "A", source.__getitem__, 1,
            "C",
        )
        self.assertEqual(
            graph, {"A": ["B"], "B": []}
        )
