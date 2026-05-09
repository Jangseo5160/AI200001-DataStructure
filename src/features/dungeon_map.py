import random
from collections import deque
from src.core.entity import Position


class DungeonMap:
    WALL = "#"
    FLOOR = "."
    EXIT = "G"
    POTION = "P"
    SWORD = "S"

    def __init__(self, height=15, width=45):
        self.height = height
        self.width = width
        self.grid = []
        self.start_position = Position(1, 1)
        self.exit_position = Position(height - 2, width - 2)

    def generate(self):
        """Create a random but always solvable dungeon map."""
        while True:
            self._generate_once()
            if self.is_reachable(self.start_position, self.exit_position):
                break

    def _generate_once(self):
        self.grid = [[self.FLOOR for _ in range(self.width)] for _ in range(self.height)]

        for y in range(self.height):
            for x in range(self.width):
                if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1:
                    self.grid[y][x] = self.WALL

        self.start_position = Position(1, 1)
        self.exit_position = Position(self.height - 2, self.width - 2)

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if (y, x) in [(1, 1), (self.exit_position.y, self.exit_position.x)]:
                    continue

                if random.random() < 0.16:
                    self.grid[y][x] = self.WALL

        self.grid[self.start_position.y][self.start_position.x] = self.FLOOR
        self.grid[self.exit_position.y][self.exit_position.x] = self.EXIT

        self._place_random_items(self.POTION, 4)
        self._place_random_items(self.SWORD, 1)

    def _place_random_items(self, tile, count):
        placed = 0
        attempts = 0

        while placed < count and attempts < 1000:
            attempts += 1
            y = random.randint(1, self.height - 2)
            x = random.randint(1, self.width - 2)

            if self.grid[y][x] == self.FLOOR and (y, x) != (1, 1):
                self.grid[y][x] = tile
                placed += 1

    def is_inside(self, pos: Position) -> bool:
        return 0 <= pos.y < self.height and 0 <= pos.x < self.width

    def get_tile(self, pos: Position) -> str:
        if not self.is_inside(pos):
            return self.WALL
        return self.grid[pos.y][pos.x]

    def set_tile(self, pos: Position, tile: str):
        if self.is_inside(pos):
            self.grid[pos.y][pos.x] = tile

    def clear_tile(self, pos: Position):
        if self.is_inside(pos) and self.get_tile(pos) != self.EXIT:
            self.grid[pos.y][pos.x] = self.FLOOR

    def is_walkable(self, pos: Position) -> bool:
        return self.is_inside(pos) and self.get_tile(pos) != self.WALL

    def is_reachable(self, start: Position, goal: Position) -> bool:
        visited = set()
        queue = deque([start])
        visited.add((start.y, start.x))

        while queue:
            current = queue.popleft()

            if current.y == goal.y and current.x == goal.x:
                return True

            for next_pos in self.neighbors(current):
                key = (next_pos.y, next_pos.x)
                if key not in visited:
                    visited.add(key)
                    queue.append(next_pos)

        return False

    def neighbors(self, pos: Position):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dy, dx in directions:
            next_pos = Position(pos.y + dy, pos.x + dx)
            if self.is_walkable(next_pos):
                yield next_pos
