# src/ui/renderer.py
import curses

class Renderer:
    def __init__(self):
        # 색상 쌍 ID 정의
        self.COLOR_PLAYER = 1
        self.COLOR_ENEMY = 2
        self.COLOR_WALL = 3
        self.COLOR_ITEM = 4
        self.COLOR_STATUS = 5

    def init_colors(self):
        """터미널 색상을 초기화합니다."""
        curses.start_color()
        # (전경색, 배경색)
        curses.init_pair(self.COLOR_PLAYER, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_ENEMY, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_WALL, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_ITEM, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_STATUS, curses.COLOR_GREEN, curses.COLOR_BLACK)

    def render_map(self, stdscr, floor):
        """2D 배열 기반의 맵을 화면에 그립니다."""
        for y, row in enumerate(floor.grid):
            for x, tile in enumerate(row):
                attr = curses.color_pair(0)
                if tile == '#':
                    attr = curses.color_pair(self.COLOR_WALL)
                
                # curses 좌표계는 (y, x) 순서임에 주의
                stdscr.addch(y, x, tile, attr)

    def render_entities(self, stdscr, player, enemies):
        """플레이어와 적들을 맵 위에 겹쳐서 그립니다."""
        # 적들 렌더링
        for enemy in enemies:
            if enemy.is_alive():
                stdscr.addch(enemy.y, enemy.x, enemy.symbol, curses.color_pair(self.COLOR_ENEMY))
        
        # 플레이어 렌더링 (가장 위에 표시)
        stdscr.addch(player.y, player.x, player.symbol, curses.color_pair(self.COLOR_PLAYER) | curses.A_BOLD)

    def render_ui(self, stdscr, player, log_messages, screen_width):
        """상태창과 로그를 우측 또는 하단에 그립니다."""
        ui_x = screen_width + 2
        
        # 1. 상태창 (Status)
        stdscr.addstr(1, ui_x, f"--- {player.name} ---", curses.color_pair(self.COLOR_STATUS))
        stdscr.addstr(2, ui_x, f"HP: {player.hp}/{player.max_hp}")
        
        # 간단한 HP 바 구현
        hp_percent = player.hp / player.max_hp
        bar_len = 10
        filled = int(bar_len * hp_percent)
        hp_bar = "[" + "=" * filled + " " * (bar_len - filled) + "]"
        stdscr.addstr(3, ui_x, hp_bar)
        
        stdscr.addstr(5, ui_x, f"Level: {player.level}")
        stdscr.addstr(6, ui_x, f"EXP: {player.exp}/{player.max_exp}")

        # 2. 메시지 로그 (Log)
        stdscr.addstr(9, ui_x, "[ Message Log ]", curses.A_UNDERLINE)
        for i, msg in enumerate(log_messages[-10:]): # 최신 10개만 표시
            stdscr.addstr(10 + i, ui_x, f"> {msg}")

    def render_all(self, stdscr, floor, player, enemies, log_messages):
        """모든 요소를 순서대로 렌더링하고 업데이트합니다."""
        stdscr.erase() # 화면 지우기
        
        # 맵 -> 엔티티 -> UI 순으로 덧그림
        self.render_map(stdscr, floor)
        self.render_entities(stdscr, player, enemies)
        self.render_ui(stdscr, player, log_messages, floor.width)
        
        stdscr.refresh() # 물리적 화면 갱신

