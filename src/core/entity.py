from dataclasses import dataclass


@dataclass
class Position:
    y: int
    x: int


@dataclass
class Player:
    position: Position
    hp: int = 8
    max_hp: int = 8
    attack: int = 2

    def is_alive(self) -> bool:
        return self.hp > 0


@dataclass
class Enemy:
    position: Position
    hp: int = 4
    attack: int = 2

    def is_alive(self) -> bool:
        return self.hp > 0
