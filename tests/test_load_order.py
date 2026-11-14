import unittest

from src.graph import load_order


class LoadOrderTests(unittest.TestCase):
    def test_shared_dependency(self):
        graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }
        self.assertEqual(
            load_order(graph),
            ["D", "B", "C", "A"],
        )

    def test_cycle(self):
        graph = {
            "A": ["B"], "B": ["A"]
        }
        with self.assertRaisesRegex(
            ValueError, "Cycle at A"
        ):
            load_order(graph)
