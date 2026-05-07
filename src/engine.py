# src/engine.py
import curses
import time

# 우리가 만든 클래스들 임포트
from src.core.map import Floor
from src.core.entities import Player
from src.ui.renderer import Renderer  # 렌더러 추가!

class GameEngine:
    def __init__(self):
        self.running = True
        self.player = None
        self.current_floor = None
        self.enemies = []
        
        # 화면 우측에 표시될 초기 로그 메시지
        self.log_messages = ["던전에 진입했습니다!", "방향키 또는 WASD로 이동하세요."] 
        
        # 렌더러 인스턴스 생성
        self.renderer = Renderer()

    def setup_game(self):
        """초기 맵 생성 및 플레이어 배치"""
        # 가로 40, 세로 20 크기의 맵 생성
        self.current_floor = Floor(floor_id=1, width=40, height=20)
        
        # x=5, y=5 위치에 플레이어 배치
        self.player = Player(x=5, y=5)

    def handle_input(self, key):
        """사용자의 키 입력을 처리합니다."""
        dx, dy = 0, 0
        
        if key == ord('q'): # 종료
            self.running = False
        elif key in [curses.KEY_UP, ord('w')]:
            dy = -1
        elif key in [curses.KEY_DOWN, ord('s')]:
            dy = 1
        elif key in [curses.KEY_LEFT, ord('a')]:
            dx = -1
        elif key in [curses.KEY_RIGHT, ord('d')]:
            dx = 1

        if dx != 0 or dy != 0:
            return self.try_move_player(dx, dy)
        return False

    def try_move_player(self, dx, dy):
        """플레이어 이동 시도 및 충돌 검사"""
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        # map.py의 is_walkable(2D Array 충돌 판정) 활용
        if self.current_floor.is_walkable(new_x, new_y):
            self.player.move(dx, dy)
            self.log_messages.append(f"이동: ({self.player.x}, {self.player.y})")
            return True
        else:
            self.log_messages.append("벽에 부딪혔습니다!")
            return False

    def run(self, stdscr):
        """메인 게임 루프"""
        curses.curs_set(0)
        stdscr.nodelay(True)
        
        # 반드시 curses.wrapper가 실행된 이후(run 내부)에 색상을 초기화해야 합니다.
        self.renderer.init_colors() 
        
        self.setup_game()

        while self.running:
            # 1. 화면 렌더링 (View 호출)
            self.renderer.render_all(
                stdscr, 
                self.current_floor, 
                self.player, 
                self.enemies, 
                self.log_messages
            )

            # 2. 사용자 입력 처리 (Controller 역할)
            try:
                key = stdscr.getch()
                if key != -1:
                    self.handle_input(key)
            except Exception as e:
                pass

            time.sleep(0.05) # CPU 점유율 조절