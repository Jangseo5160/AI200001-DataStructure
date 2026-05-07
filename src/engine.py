# src/engine.py
import curses
import time

from src.core.map import Floor
from src.core.entities import Player, Enemy
from src.ui.renderer import Renderer

# [자료구조 & 알고리즘 임포트]
from src.ds_algo.queue import TurnQueue
from src.ds_algo.pathfinding import a_star_search

class GameEngine:
    def __init__(self):
        self.running = True
        self.player = None
        self.current_floor = None
        self.enemies = []
        self.log_messages = ["던전에 진입했습니다!", "방향키: 이동 | 'q': 종료"] 
        self.renderer = Renderer()
        
        # [기능 3] 턴 관리를 위한 우선순위 큐 초기화
        self.turn_queue = TurnQueue()

    def setup_game(self):
        """초기 맵 생성, 플레이어 및 적 배치"""
        # 1. 미로 맵 생성
        self.current_floor = Floor(floor_id=1, width=60, height=20)
        
        # 2. 플레이어를 첫 번째 방에 배치
        start_x, start_y = self.current_floor.rooms[0].center()
        self.player = Player(x=start_x, y=start_y)
        self.turn_queue.enqueue(self.player) # 플레이어를 턴 큐에 등록
        
        # 3. [몬스터 스폰] 나머지 방들에 고블린 배치
        for room in self.current_floor.rooms[1:]:
            ex, ey = room.center()
            # Enemy 속성: (x, y, 이름, hp, speed, 공격력, 심볼, ai타입, 경험치)
            enemy = Enemy(ex, ey, "고블린", 20, speed=8, attack_power=5, symbol='G', ai_type='aggressive', exp_reward=10)
            self.enemies.append(enemy)
            self.turn_queue.enqueue(enemy) # 몬스터도 턴 큐에 등록

    def handle_input(self, key):
        """사용자의 키 입력을 처리합니다."""
        dx, dy = 0, 0
        if key == ord('q'):
            self.running = False
            return False
        elif key in [curses.KEY_UP, ord('w')]: dy = -1
        elif key in [curses.KEY_DOWN, ord('s')]: dy = 1
        elif key in [curses.KEY_LEFT, ord('a')]: dx = -1
        elif key in [curses.KEY_RIGHT, ord('d')]: dx = 1

        if dx != 0 or dy != 0:
            return self.try_move_player(dx, dy)
        return False

    def get_entity_at(self, x, y):
        """특정 좌표에 있는 엔티티(적)를 찾아 반환합니다."""
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y and enemy.is_alive():
                return enemy
        return None

    def try_move_player(self, dx, dy):
        """플레이어 이동 또는 공격 시도"""
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        # 1. 해당 위치에 적이 있는지 확인 (전투 판정)
        target_enemy = self.get_entity_at(new_x, new_y)
        if target_enemy:
            # 플레이어가 적을 공격
            damage = self.player.attack_power
            target_enemy.take_damage(damage)
            self.log_messages.append(f"{target_enemy.name}에게 {damage}의 데미지를 입혔습니다!")
            
            if not target_enemy.is_alive():
                self.log_messages.append(f"{target_enemy.name}을 처치했습니다! (+{target_enemy.exp_reward} EXP)")
                self.player.gain_exp(target_enemy.exp_reward)
            return True # 공격도 턴을 소모함

        # 2. 적이 없다면 이동 가능한지 확인
        if self.current_floor.is_walkable(new_x, new_y):
            self.player.move(dx, dy)
            return True
            
        return False

    def run(self, stdscr):
        """메인 게임 루프 수정"""
        curses.curs_set(0)
        self.renderer.init_colors() 
        self.setup_game()

        while self.running:
            active_entity, action_time = self.turn_queue.dequeue()

            if not active_entity.is_alive():
                continue # 죽은 엔티티는 턴을 건너뜀

            if active_entity == self.player:
                # [플레이어 턴 렌더링 및 입력 받기]
                self.renderer.render_all(stdscr, self.current_floor, self.player, self.enemies, self.log_messages)
                
                stdscr.nodelay(False)
                turn_taken = False
                while not turn_taken and self.running:
                    key = stdscr.getch()
                    turn_taken = self.handle_input(key)
                stdscr.nodelay(True)
                
                if self.running:
                    self.turn_queue.enqueue(self.player, action_time)

            else:
                # [몬스터 턴 로직]
                if active_entity.is_alive():
                    start_pos = (active_entity.x, active_entity.y)
                    goal_pos = (self.player.x, self.player.y)
                    
                    # 플레이어와의 거리 계산 (인접해 있는지 확인)
                    dist = abs(active_entity.x - self.player.x) + abs(active_entity.y - self.player.y)
                    
                    if dist == 1:
                        # 몬스터가 플레이어를 공격
                        damage = active_entity.attack_power
                        self.player.take_damage(damage)
                        self.log_messages.append(f"{active_entity.name}이(가) 당신을 공격했습니다! ({damage} 피해)")
                        
                        if not self.player.is_alive():
                            self.log_messages.append("치명상을 입었습니다... 게임 오버!")
                            # 게임 종료 로직이나 초기화 로직 추가 가능
                    else:
                        # 플레이어를 향해 이동 (A* 알고리즘)
                        path = a_star_search(self.current_floor, start_pos, goal_pos)
                        if path and len(path) > 1:
                            next_x, next_y = path[1]
                            # 이동하려는 칸에 다른 몬스터가 없는지도 체크하면 더 좋습니다.
                            if self.current_floor.is_walkable(next_x, next_y) and not (next_x == self.player.x and next_y == self.player.y):
                                active_entity.x, active_entity.y = next_x, next_y
                            
                    self.turn_queue.enqueue(active_entity, action_time)
        """메인 게임 루프 (턴 시스템 기반)"""
        curses.curs_set(0)
        self.renderer.init_colors() 
        self.setup_game()

        while self.running:
            # 1. 큐에서 이번 턴에 행동할 개체를 꺼냅니다. (우선순위 큐 동작)
            active_entity, action_time = self.turn_queue.dequeue()

            # [플레이어의 턴]
            if active_entity == self.player:
                # 화면을 갱신하고 입력을 기다립니다.
                self.renderer.render_all(stdscr, self.current_floor, self.player, self.enemies, self.log_messages)
                
                stdscr.nodelay(False) # 플레이어 입력 대기 모드 켬
                turn_taken = False
                while not turn_taken and self.running:
                    key = stdscr.getch()
                    turn_taken = self.handle_input(key)
                stdscr.nodelay(True)  # 입력 대기 모드 끔
                
                # 행동을 마친 플레이어를 다시 큐에 넣습니다.
                if self.running:
                    self.turn_queue.enqueue(self.player, action_time)

            # [몬스터의 턴]
            else:
                if active_entity.is_alive():
                    # [기능 5] A* 알고리즘을 이용해 플레이어 추적
                    start_pos = (active_entity.x, active_entity.y)
                    goal_pos = (self.player.x, self.player.y)
                    
                    path = a_star_search(self.current_floor, start_pos, goal_pos)
                    
                    # path[0]은 현재 위치, path[1]이 다음 이동할 목표 타일
                    if path and len(path) > 1:
                        next_x, next_y = path[1]
                        # 몬스터도 벽이 아닌 곳으로만 이동 (플레이어 겹침 방지는 추후 구현)
                        if self.current_floor.is_walkable(next_x, next_y):
                            active_entity.x, active_entity.y = next_x, next_y
                            
                    # 행동을 마친 몬스터를 다시 큐에 넣습니다.
                    self.turn_queue.enqueue(active_entity, action_time)