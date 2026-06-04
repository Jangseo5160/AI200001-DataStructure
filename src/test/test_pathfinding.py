import unittest

from src.ds_algo.pathfinding import a_star_search, heuristic


class SimpleMap:
    def __init__(self, rows):
        self.rows = rows
        self.height = len(rows)
        self.width = len(rows[0])

    def is_walkable(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height and self.rows[y][x] != "#"


class PathfindingTest(unittest.TestCase):
    def test_heuristic_uses_manhattan_distance(self):
        self.assertEqual(heuristic((1, 2), (4, 6)), 7)

    def test_a_star_finds_shortest_path_around_wall(self):
        dungeon = SimpleMap([
            "...",
            "##.",
            "...",
        ])

        path = a_star_search(dungeon, (0, 0), (0, 2))

        self.assertEqual(path, [(1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2)])

    def test_a_star_returns_empty_list_when_unreachable(self):
        dungeon = SimpleMap([
            ".#.",
            "###",
            ".#.",
        ])

        self.assertEqual(a_star_search(dungeon, (0, 0), (2, 2)), [])


if __name__ == "__main__":
    unittest.main()
