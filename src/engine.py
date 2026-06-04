# src/engine.py
import copy
import curses

from src.core.map import Floor
from src.core.entities import Player, Enemy, Goal, Potion, Weapon, Armor
from src.ui.renderer import Renderer
from src.utils.data_handler import add_leaderboard_entry, load_leaderboard

# [자료구조 & 알고리즘 임포트]
from src.ds_algo.queue import TurnQueue
from src.ds_algo.pathfinding import a_star_search
from src.ds_algo.stack import UndoStack


class GameEngine:
    def __init__(self):
        self.running = True
        self.player = None
        self.current_floor = None
        self.enemies = []
        self.objects = []
        self.max_floors = 5
        self.turn_count = 0
        self.floor_changed_this_turn = False
        self.log_messages = ["던전에 진입했습니다!", "WASD/방향키 이동, p 포션, u/r 실행취소/재실행, i 인벤토리, l 리더보드, q 종료"]
        self.renderer = Renderer()

        # [기능 3] 턴 관리를 위한 우선순위 큐 초기화
        self.turn_queue = TurnQueue()
        self.undo_stack = UndoStack()
        self.redo_stack = UndoStack()

    def setup_game(self):
        """초기 맵 생성, 플레이어 및 적 배치"""
        self.player = None
        self.setup_floor(1)

    def setup_floor(self, floor_id):
        """지정한 층을 생성하고 플레이어, 적, 턴 큐를 새로 배치합니다."""
        self.current_floor = Floor(floor_id=floor_id, width=60, height=20, max_floors=self.max_floors)
        self.enemies = []
        self.objects = []
        self.turn_queue = TurnQueue()

        start_x, start_y = self.current_floor.rooms[0].center()
        if self.player is None:
            self.player = Player(x=start_x, y=start_y)
        else:
            self.player.x = start_x
            self.player.y = start_y

        self.turn_queue.enqueue(self.player)
        self.spawn_floor_objects()

        # [몬스터 스폰] 나머지 방들에 고블린 배치
        for room in self.current_floor.rooms[1:]:
            ex, ey = room.center()
            if self.current_floor.get_ladder_at(ex, ey):
                continue
            if self.get_object_at(ex, ey):
                continue

            enemy = self.create_floor_enemy(ex, ey)
            self.enemies.append(enemy)
            self.turn_queue.enqueue(enemy)

    def capture_state(self):
        """Undo/Redo용 현재 게임 상태 스냅샷을 만듭니다."""
        return {
            "player": copy.deepcopy(self.player),
            "current_floor": copy.deepcopy(self.current_floor),
            "enemies": copy.deepcopy(self.enemies),
            "objects": copy.deepcopy(self.objects),
            "turn_count": self.turn_count,
            "floor_changed_this_turn": self.floor_changed_this_turn,
            "log_messages": copy.deepcopy(self.log_messages),
        }

    def restore_state(self, state):
        """저장된 게임 상태 스냅샷을 복원합니다."""
        self.player = copy.deepcopy(state["player"])
        self.current_floor = copy.deepcopy(state["current_floor"])
        self.enemies = copy.deepcopy(state["enemies"])
        self.objects = copy.deepcopy(state["objects"])
        self.turn_count = state["turn_count"]
        self.floor_changed_this_turn = state["floor_changed_this_turn"]
        self.log_messages = copy.deepcopy(state["log_messages"])
        self.rebuild_turn_queue_for_player_turn()

    def rebuild_turn_queue_for_player_turn(self):
        """Undo/Redo 복원 후 현재 적 목록 기준으로 턴 큐를 다시 만듭니다."""
        self.turn_queue = TurnQueue()
        for enemy in self.enemies:
            if enemy.is_alive():
                self.turn_queue.enqueue(enemy)

    def undo(self):
        """이전 플레이어 행동 전 상태로 되돌립니다."""
        state = self.undo_stack.pop()
        if state is None:
            self.log_messages.append("되돌릴 행동이 없습니다.")
            return

        self.redo_stack.push(self.capture_state())
        self.restore_state(state)
        self.log_messages.append("이전 행동으로 되돌렸습니다.")

    def redo(self):
        """Undo로 되돌린 행동을 다시 적용합니다."""
        state = self.redo_stack.pop()
        if state is None:
            self.log_messages.append("다시 실행할 행동이 없습니다.")
            return

        self.undo_stack.push(self.capture_state())
        self.restore_state(state)
        self.log_messages.append("되돌린 행동을 다시 실행했습니다.")

    def create_floor_enemy(self, x, y):
        """층이 깊어질수록 강해지는 고블린을 생성합니다."""
        floor_id = self.current_floor.floor_id
        hp = 15 + floor_id * 10
        attack_power = 3 + floor_id * 3
        speed = 7 + floor_id
        exp_reward = 8 + floor_id * 5

        if floor_id >= 5:
            name = "고블린 대장"
            symbol = "B"
            hp += 20
            attack_power += 4
            exp_reward += 15
        elif floor_id >= 3:
            name = "엘리트 고블린"
            symbol = "G"
        else:
            name = "고블린"
            symbol = "G"

        return Enemy(
            x,
            y,
            name,
            hp,
            speed=speed,
            attack_power=attack_power,
            symbol=symbol,
            ai_type="aggressive",
            exp_reward=exp_reward,
        )

    def spawn_floor_objects(self):
        """각 층에 회복/장비 아이템을 놓고, 마지막 층에는 GOAL을 배치합니다."""
        rooms = self.current_floor.rooms
        if len(rooms) > 1:
            x, y = rooms[1].center()
            self.objects.append(Potion(x + 1, y, heal_amount=20 + self.current_floor.floor_id * 5))

        if len(rooms) > 2:
            x, y = rooms[2].center()
            self.objects.append(Weapon(x + 1, y, f"Floor {self.current_floor.floor_id} Sword", attack_bonus=3 + self.current_floor.floor_id))

        if len(rooms) > 3:
            x, y = rooms[3].center()
            self.objects.append(Armor(x + 1, y, f"Floor {self.current_floor.floor_id} Armor", defense_bonus=1 + self.current_floor.floor_id))

        if self.current_floor.floor_id == self.max_floors and rooms:
            x, y = rooms[-1].center()
            self.objects.append(Goal(x, y))

    def descend_floor(self, ladder):
        """사다리를 사용해 다음 층으로 내려갑니다."""
        next_floor = ladder.use()
        self.floor_changed_this_turn = True
        self.log_messages.append(f"사다리를 타고 {next_floor}층으로 내려갑니다.")
        self.setup_floor(next_floor)

        if next_floor == self.max_floors:
            self.log_messages.append("마지막 층에 도착했습니다. 더 아래로 내려가는 사다리는 없습니다.")

    def handle_input(self, key, stdscr=None):
        """키 입력을 처리합니다."""
        dx, dy = 0, 0
        if key == ord("q"):
            self.running = False
            return False
        elif key == ord("u"):
            self.undo()
            return False
        elif key == ord("r"):
            self.redo()
            return False
        elif key == ord("i"):
            self.show_inventory(stdscr)
            return False
        elif key == ord("p"):
            previous_state = self.capture_state()
            turn_taken = self.use_inventory_potion()
            if turn_taken:
                self.undo_stack.push(previous_state)
                self.redo_stack.clear()
            return turn_taken
        elif key == ord("l"):
            self.show_leaderboard(stdscr)
            return False
        elif key in [curses.KEY_UP, ord("w")]:
            dy = -1
        elif key in [curses.KEY_DOWN, ord("s")]:
            dy = 1
        elif key in [curses.KEY_LEFT, ord("a")]:
            dx = -1
        elif key in [curses.KEY_RIGHT, ord("d")]:
            dx = 1

        if dx != 0 or dy != 0:
            previous_state = self.capture_state()
            turn_taken = self.try_move_player(dx, dy)
            if turn_taken:
                self.undo_stack.push(previous_state)
                self.redo_stack.clear()
            return turn_taken
        return False

    def show_leaderboard(self, stdscr):
        """현재 게임을 잠시 멈추고 리더보드를 보여줍니다."""
        if stdscr is None:
            return

        entries = load_leaderboard()
        self.renderer.render_leaderboard(stdscr, entries)
        stdscr.getch()

    def show_inventory(self, stdscr):
        """현재 장비와 인벤토리를 보여줍니다."""
        if stdscr is None:
            return

        self.renderer.render_inventory(stdscr, self.player)
        stdscr.getch()

    def get_entity_at(self, x, y):
        """특정 좌표에 있는 엔티티(적)를 찾아 반환합니다."""
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y and enemy.is_alive():
                return enemy
        return None

    def get_object_at(self, x, y):
        """특정 좌표에 있는 오브젝트를 찾아 반환합니다."""
        for obj in self.objects:
            if obj.is_at(x, y):
                return obj
        return None

    def use_inventory_potion(self):
        """인벤토리 리스트에서 가장 앞의 포션을 사용합니다."""
        potion = self.player.find_first_item(Potion)
        if potion is None:
            self.log_messages.append("사용할 포션이 없습니다.")
            return False

        before_hp = self.player.hp
        potion.use(self.player)
        self.player.remove_item(potion)
        healed = self.player.hp - before_hp
        self.log_messages.append(f"{potion.name}을 사용했습니다. HP +{healed}")
        return True

    def handle_object_at_player(self):
        """플레이어가 밟은 아이템/GOAL을 처리합니다."""
        obj = self.get_object_at(self.player.x, self.player.y)
        if obj is None:
            return

        if isinstance(obj, Potion):
            self.player.add_item(obj)
            self.log_messages.append(f"{obj.name}을 인벤토리에 넣었습니다. p 키로 사용할 수 있습니다.")
            self.objects.remove(obj)
        elif isinstance(obj, Weapon):
            self.player.add_item(obj)
            obj.equip(self.player)
            self.log_messages.append(f"{obj.name}을 획득하고 장착했습니다. 공격력 +{obj.attack_bonus}")
            self.objects.remove(obj)
        elif isinstance(obj, Armor):
            self.player.add_item(obj)
            obj.equip(self.player)
            self.log_messages.append(f"{obj.name}을 획득하고 장착했습니다. 방어력 +{obj.defense_bonus}")
            self.objects.remove(obj)
        elif isinstance(obj, Goal):
            entry = add_leaderboard_entry(self.player, self.current_floor.floor_id, self.turn_count)
            self.log_messages.append(f"GOAL 도착! 점수 {entry['score']}점이 리더보드에 저장되었습니다.")
            self.running = False

    def try_move_player(self, dx, dy):
        """플레이어 이동 또는 공격 시도"""
        new_x = self.player.x + dx
        new_y = self.player.y + dy

        # 1. 해당 위치에 적이 있는지 확인 (전투 판정)
        target_enemy = self.get_entity_at(new_x, new_y)
        if target_enemy:
            damage = self.player.get_total_attack_power()
            target_enemy.take_damage(damage)
            self.log_messages.append(f"{target_enemy.name}에게 {damage}의 데미지를 입혔습니다!")

            if not target_enemy.is_alive():
                self.log_messages.append(f"{target_enemy.name}을 처치했습니다! (+{target_enemy.exp_reward} EXP)")
                self.player.gain_exp(target_enemy.exp_reward)
            return True

        # 2. 적이 없다면 이동 가능한지 확인
        if self.current_floor.is_walkable(new_x, new_y):
            self.player.move(dx, dy)
            self.handle_object_at_player()
            ladder = self.current_floor.get_ladder_at(self.player.x, self.player.y)
            if ladder:
                self.descend_floor(ladder)
            return True

        return False

    def run(self, stdscr):
        """메인 게임 루프 (턴 시스템 기반)"""
        curses.curs_set(0)
        self.renderer.init_colors()
        self.setup_game()

        while self.running:
            active_entity, action_time = self.turn_queue.dequeue()
            if active_entity is None:
                break

            if not active_entity.is_alive():
                continue

            if active_entity == self.player:
                self.renderer.render_all(stdscr, self.current_floor, self.player, self.enemies, self.objects, self.log_messages)

                stdscr.nodelay(False)
                turn_taken = False
                self.floor_changed_this_turn = False
                while not turn_taken and self.running:
                    key = stdscr.getch()
                    turn_taken = self.handle_input(key, stdscr)
                    if not turn_taken and self.running:
                        self.renderer.render_all(
                            stdscr,
                            self.current_floor,
                            self.player,
                            self.enemies,
                            self.objects,
                            self.log_messages,
                        )
                stdscr.nodelay(True)

                if self.running and not self.floor_changed_this_turn:
                    self.turn_count += 1
                    self.turn_queue.enqueue(self.player, action_time)
            else:
                self.run_enemy_turn(active_entity, action_time)

    def run_enemy_turn(self, active_entity, action_time):
        """몬스터 한 턴을 처리합니다."""
        start_pos = (active_entity.x, active_entity.y)
        goal_pos = (self.player.x, self.player.y)
        dist = abs(active_entity.x - self.player.x) + abs(active_entity.y - self.player.y)

        if dist == 1:
            damage = max(0, active_entity.attack_power - self.player.get_total_defense())
            self.player.take_damage(damage)
            self.log_messages.append(f"{active_entity.name}이(가) 당신을 공격했습니다! ({damage} 피해)")

            if not self.player.is_alive():
                self.log_messages.append("치명상을 입었습니다... 게임 오버!")
                self.running = False
        else:
            path = a_star_search(self.current_floor, start_pos, goal_pos)
            if path:
                next_x, next_y = path[0]
                if self.current_floor.is_walkable(next_x, next_y) and not (next_x == self.player.x and next_y == self.player.y):
                    active_entity.x, active_entity.y = next_x, next_y

        if self.running:
            self.turn_queue.enqueue(active_entity, action_time)
