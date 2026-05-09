import random
from collections import deque
from src.core.entity import Position, Enemy


class EnemyAI:
    def __init__(self, detection_range=6):
        self.enemies = []
        self.detection_range = detection_range

    def spawn_enemies(self, dungeon_map, count, player_position):
        self.enemies = []
        attempts = 0

        while len(self.enemies) < count and attempts < 1000:
            attempts += 1
            y = random.randint(1, dungeon_map.height - 2)
            x = random.randint(1, dungeon_map.width - 2)
            pos = Position(y, x)

            if not dungeon_map.is_walkable(pos):
                continue
            if dungeon_map.get_tile(pos) != dungeon_map.FLOOR:
                continue
            if self.distance(pos, player_position) < 8:
                continue
            if self.enemy_at(pos):
                continue

            self.enemies.append(Enemy(pos))

    def update(self, dungeon_map, player):
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue

            distance = self.distance(enemy.position, player.position)

            if distance == 1:
                player.hp -= enemy.attack
                continue

            if distance <= self.detection_range:
                next_pos = self._next_step_toward_player(dungeon_map, enemy.position, player.position)
                if next_pos and not self.enemy_at(next_pos):
                    enemy.position = next_pos
            else:
                self._random_move(dungeon_map, enemy, player.position)

        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive()]

    def player_attack(self, player, inventory) -> bool:
        damage = player.attack + (2 if inventory.has("Sword") else 0)

        for enemy in self.enemies:
            if self.distance(enemy.position, player.position) == 1:
                enemy.hp -= damage
                self.enemies = [e for e in self.enemies if e.is_alive()]
                return True

        return False

    def enemy_at(self, pos: Position) -> bool:
        return any(enemy.position.y == pos.y and enemy.position.x == pos.x for enemy in self.enemies)

    def distance(self, a: Position, b: Position) -> int:
        return abs(a.y - b.y) + abs(a.x - b.x)

    def copy_enemies(self):
        return [Enemy(Position(enemy.position.y, enemy.position.x), enemy.hp, enemy.attack) for enemy in self.enemies]

    def restore_enemies(self, enemies):
        self.enemies = [Enemy(Position(enemy.position.y, enemy.position.x), enemy.hp, enemy.attack) for enemy in enemies]

    def _random_move(self, dungeon_map, enemy, player_position):
        candidates = list(dungeon_map.neighbors(enemy.position))
        random.shuffle(candidates)

        for pos in candidates:
            if self.enemy_at(pos):
                continue
            if pos.y == player_position.y and pos.x == player_position.x:
                continue
            enemy.position = pos
            return

    def _next_step_toward_player(self, dungeon_map, start, goal):
        queue = deque([start])
        came_from = {(start.y, start.x): None}

        while queue:
            current = queue.popleft()

            if current.y == goal.y and current.x == goal.x:
                break

            for next_pos in dungeon_map.neighbors(current):
                key = (next_pos.y, next_pos.x)
                if key in came_from:
                    continue

                came_from[key] = current
                queue.append(next_pos)

        goal_key = (goal.y, goal.x)
        if goal_key not in came_from:
            return None

        current = goal
        previous = came_from[goal_key]

        while previous and not (previous.y == start.y and previous.x == start.x):
            current = previous
            previous = came_from[(current.y, current.x)]

        return current
