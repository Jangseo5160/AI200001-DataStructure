from src.core.entity import Position, Player
from src.features.dungeon_map import DungeonMap
from src.features.turn_manager import TurnManager
from src.features.inventory import Inventory
from src.features.enemy_ai import EnemyAI
from src.features.undo_system import UndoSystem, GameState
from src.features.leaderboard import Leaderboard
from src.ui.renderer import Renderer


class GameEngine:
    def __init__(self):
        self.map = DungeonMap()
        self.turn_manager = TurnManager()
        self.inventory = Inventory()
        self.enemy_ai = EnemyAI()
        self.undo_system = UndoSystem()
        self.leaderboard = Leaderboard()

        self.player = None
        self.running = True
        self.won = False
        self.lost = False
        self.messages = []

    def setup(self):
        self.map.generate()
        self.player = Player(Position(self.map.start_position.y, self.map.start_position.x))
        self.enemy_ai.spawn_enemies(self.map, count=5, player_position=self.player.position)
        self.messages.append("Dungeon generated. Reach G to win.")

    def run(self):
        self.setup()

        while self.running:
            Renderer.render(
                self.map,
                self.player,
                self.enemy_ai,
                self.inventory,
                self.turn_manager,
                self.messages,
            )

            if self.won or self.lost:
                command = input("Press q to quit: ").strip().lower()
                if command == "q":
                    self.running = False
                continue

            if self.turn_manager.current_turn == TurnManager.PLAYER:
                command = input("> ").lower()
                self.handle_player_command(command)
            else:
                self.handle_enemy_turn()

    def handle_player_command(self, command: str):
        if command == "q":
            self.running = False
            return

        if command == "l":
            self.messages.append(self.leaderboard.display())
            return

        if command == "u":
            self.restore_undo()
            return

        if command == "p":
            self.save_undo()
            if self.inventory.use_potion(self.player):
                self.messages.append("Used Potion. HP restored.")
            else:
                self.messages.append("No Potion available.")
            self.turn_manager.switch_turn()
            return

        if command == " ":
            self.save_undo()
            if self.enemy_ai.player_attack(self.player, self.inventory):
                self.messages.append("You attacked an adjacent enemy.")
            else:
                self.messages.append("No adjacent enemy to attack.")
            self.turn_manager.switch_turn()
            return

        movement = {
            "w": (-1, 0),
            "s": (1, 0),
            "a": (0, -1),
            "d": (0, 1),
        }

        if command in movement:
            self.save_undo()
            dy, dx = movement[command]
            self.move_player(dy, dx)
            self.turn_manager.switch_turn()
            return

        self.messages.append("Invalid command.")

    def move_player(self, dy, dx):
        next_position = Position(self.player.position.y + dy, self.player.position.x + dx)

        if not self.map.is_walkable(next_position):
            self.messages.append("You hit a wall.")
            return

        if self.enemy_ai.enemy_at(next_position):
            self.messages.append("Enemy blocks the way. Use SPACE to attack.")
            return

        self.player.position = next_position
        self.check_tile_event()

    def check_tile_event(self):
        tile = self.map.get_tile(self.player.position)

        if tile == DungeonMap.POTION:
            self.inventory.add("Potion")
            self.map.clear_tile(self.player.position)
            self.messages.append("Picked up Potion.")

        elif tile == DungeonMap.SWORD:
            self.inventory.add("Sword")
            self.map.clear_tile(self.player.position)
            self.messages.append("Picked up Sword. Attack damage increased.")

        elif tile == DungeonMap.EXIT:
            self.won = True
            score = self.calculate_score()
            self.leaderboard.add_score("Player", score)
            self.messages.append(f"You escaped! Score: {score}")

    def handle_enemy_turn(self):
        self.enemy_ai.update(self.map, self.player)

        if not self.player.is_alive():
            self.player.hp = 0
            self.lost = True
            self.messages.append("You died. Game over.")

        self.turn_manager.switch_turn()

    def save_undo(self):
        state = GameState(
            player_y=self.player.position.y,
            player_x=self.player.position.x,
            player_hp=self.player.hp,
            inventory_items=self.inventory.copy_items(),
            enemies=self.enemy_ai.copy_enemies(),
            turn_count=self.turn_manager.turn_count,
        )
        self.undo_system.save(state)

    def restore_undo(self):
        state = self.undo_system.undo()

        if state is None:
            self.messages.append("No previous turn to undo.")
            return

        self.player.position = Position(state.player_y, state.player_x)
        self.player.hp = state.player_hp
        self.inventory.restore_items(state.inventory_items)
        self.enemy_ai.restore_enemies(state.enemies)
        self.turn_manager.turn_count = state.turn_count
        self.turn_manager.current_turn = TurnManager.PLAYER
        self.messages.append("Undo complete.")

    def calculate_score(self):
        score = 1000
        score -= self.turn_manager.turn_count * 10
        score += self.player.hp * 20
        score += len(self.enemy_ai.enemies) * 25
        return max(score, 0)
