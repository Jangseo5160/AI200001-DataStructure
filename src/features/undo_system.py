from dataclasses import dataclass
from src.core.entity import Position


@dataclass
class GameState:
    player_y: int
    player_x: int
    player_hp: int
    inventory_items: list
    enemies: list
    turn_count: int


class UndoSystem:
    def __init__(self):
        self.stack = []

    def save(self, state: GameState):
        self.stack.append(state)

    def can_undo(self) -> bool:
        return len(self.stack) > 0

    def undo(self):
        if not self.stack:
            return None
        return self.stack.pop()

    def clear(self):
        self.stack.clear()
