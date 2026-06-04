# src/ui/renderer.py
import curses
import textwrap
import unicodedata

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

    def display_width(self, text):
        """한글처럼 터미널에서 두 칸을 차지하는 문자를 고려해 표시 폭을 계산합니다."""
        width = 0
        for char in text:
            width += 2 if unicodedata.east_asian_width(char) in ("F", "W") else 1
        return width

    def truncate_to_width(self, text, max_width):
        """curses 자동 줄바꿈을 막기 위해 표시 폭 기준으로 문자열을 자릅니다."""
        result = []
        width = 0
        for char in text:
            char_width = 2 if unicodedata.east_asian_width(char) in ("F", "W") else 1
            if width + char_width > max_width:
                break
            result.append(char)
            width += char_width
        return "".join(result)

    def safe_addstr(self, stdscr, y, x, text, attr=0):
        """화면 밖 출력과 자동 줄바꿈을 방지하는 안전한 addstr 래퍼입니다."""
        max_y, max_x = stdscr.getmaxyx()
        if y < 0 or y >= max_y or x < 0 or x >= max_x - 1:
            return

        available_width = max_x - x - 1
        if available_width <= 0:
            return

        stdscr.addstr(y, x, self.truncate_to_width(str(text), available_width), attr)

    def render_map(self, stdscr, floor):
        """2D 배열 기반의 맵을 화면에 그립니다."""
        for y, row in enumerate(floor.grid):
            for x, tile in enumerate(row):
                attr = curses.color_pair(0)
                if tile == '#':
                    attr = curses.color_pair(self.COLOR_WALL)
                
                # curses 좌표계는 (y, x) 순서임에 주의
                try:
                    stdscr.addch(y, x, tile, attr)
                except curses.error:
                    pass

        if floor.ladder:
            try:
                stdscr.addch(
                    floor.ladder.y,
                    floor.ladder.x,
                    floor.ladder.symbol,
                    curses.color_pair(self.COLOR_ITEM) | curses.A_BOLD
                )
            except curses.error:
                pass

    def render_objects(self, stdscr, objects):
        """아이템과 GOAL 같은 오브젝트를 맵 위에 그립니다."""
        for obj in objects:
            try:
                stdscr.addch(obj.y, obj.x, obj.symbol, curses.color_pair(self.COLOR_ITEM) | curses.A_BOLD)
            except curses.error:
                pass

    def render_entities(self, stdscr, player, enemies):
        """플레이어와 적들을 맵 위에 겹쳐서 그립니다."""
        # 적들 렌더링
        for enemy in enemies:
            if enemy.is_alive():
                try:
                    stdscr.addch(enemy.y, enemy.x, enemy.symbol, curses.color_pair(self.COLOR_ENEMY))
                except curses.error:
                    pass
        
        # 플레이어 렌더링 (가장 위에 표시)
        try:
            stdscr.addch(player.y, player.x, player.symbol, curses.color_pair(self.COLOR_PLAYER) | curses.A_BOLD)
        except curses.error:
            pass

    def render_ui(self, stdscr, floor, player, log_messages, screen_width):
        """상태창과 로그를 우측 또는 하단에 그립니다."""
        ui_x = screen_width + 2
        max_y, max_x = stdscr.getmaxyx()
        panel_width = max_x - ui_x - 1

        if panel_width < 24:
            self.render_bottom_ui(stdscr, floor, player, log_messages)
            return
        
        # 1. 상태창 (Status)
        self.safe_addstr(stdscr, 1, ui_x, f"--- {player.name} ---", curses.color_pair(self.COLOR_STATUS))
        self.safe_addstr(stdscr, 2, ui_x, f"HP: {player.hp}/{player.max_hp}")
        
        # 간단한 HP 바 구현
        hp_percent = player.hp / player.max_hp
        bar_len = 10
        filled = int(bar_len * hp_percent)
        hp_bar = "[" + "=" * filled + " " * (bar_len - filled) + "]"
        self.safe_addstr(stdscr, 3, ui_x, hp_bar)
        
        self.safe_addstr(stdscr, 5, ui_x, f"Level: {player.level}")
        self.safe_addstr(stdscr, 6, ui_x, f"EXP: {player.exp}/{player.max_exp}")
        self.safe_addstr(stdscr, 7, ui_x, f"Floor: {floor.floor_id}/{floor.max_floors}")
        self.safe_addstr(stdscr, 8, ui_x, f"ATK: {player.get_total_attack_power()}  DEF: {player.get_total_defense()}")

        # 2. 메시지 로그 (Log)
        self.safe_addstr(stdscr, 10, ui_x, "[ Message Log ]", curses.A_UNDERLINE)
        line_y = 11
        for msg in log_messages[-6:]: # 최신 6개만 표시
            wrapped_lines = textwrap.wrap(f"> {msg}", width=max(1, panel_width // 2)) or [">"]
            for line in wrapped_lines[:2]:
                if line_y >= max_y - 1:
                    return
                self.safe_addstr(stdscr, line_y, ui_x, line)
                line_y += 1

    def render_bottom_ui(self, stdscr, floor, player, log_messages):
        """우측 패널 공간이 부족할 때 맵 아래에 compact UI를 표시합니다."""
        max_y, max_x = stdscr.getmaxyx()
        start_y = floor.height + 1
        if start_y >= max_y - 1:
            return

        status = (
            f"HP {player.hp}/{player.max_hp} | Lv {player.level} | "
            f"Floor {floor.floor_id}/{floor.max_floors} | "
            f"ATK {player.get_total_attack_power()} DEF {player.get_total_defense()}"
        )
        self.safe_addstr(stdscr, start_y, 0, status, curses.color_pair(self.COLOR_STATUS))

        line_y = start_y + 1
        log_width = max(10, max_x - 2)
        for msg in log_messages[-3:]:
            wrapped_lines = textwrap.wrap(f"> {msg}", width=max(1, log_width // 2)) or [">"]
            for line in wrapped_lines[:2]:
                if line_y >= max_y - 1:
                    return
                self.safe_addstr(stdscr, line_y, 0, line)
                line_y += 1

    def render_all(self, stdscr, floor, player, enemies, objects, log_messages):
        """모든 요소를 순서대로 렌더링하고 업데이트합니다."""
        stdscr.erase() # 화면 지우기
        
        # 맵 -> 오브젝트 -> 엔티티 -> UI 순으로 덧그림
        self.render_map(stdscr, floor)
        self.render_objects(stdscr, objects)
        self.render_entities(stdscr, player, enemies)
        self.render_ui(stdscr, floor, player, log_messages, floor.width)
        
        stdscr.refresh() # 물리적 화면 갱신

    def render_leaderboard(self, stdscr, entries):
        """리더보드 화면을 그립니다."""
        stdscr.erase()
        stdscr.addstr(1, 2, "[ Leaderboard ]", curses.color_pair(self.COLOR_STATUS) | curses.A_BOLD)

        if not entries:
            stdscr.addstr(4, 2, "아직 저장된 기록이 없습니다.")
        else:
            header = "Rank  Name       Score  Floor  Lv  HP  Turns  Cleared At"
            stdscr.addstr(3, 2, header, curses.A_UNDERLINE)

            for index, entry in enumerate(entries[:10], start=1):
                line = (
                    f"{index:<5} "
                    f"{entry.get('name', 'Hero')[:10]:<10} "
                    f"{entry.get('score', 0):<6} "
                    f"{entry.get('floor', 0):<5} "
                    f"{entry.get('level', 0):<3} "
                    f"{entry.get('hp', 0):<3} "
                    f"{entry.get('turns', 0):<6} "
                    f"{entry.get('cleared_at', '-')}"
                )
                stdscr.addstr(4 + index, 2, line)

        stdscr.addstr(17, 2, "아무 키나 누르면 게임으로 돌아갑니다.")
        stdscr.refresh()

    def render_inventory(self, stdscr, player):
        """플레이어 인벤토리와 장비 상태를 그립니다."""
        stdscr.erase()
        stdscr.addstr(1, 2, "[ Inventory ]", curses.color_pair(self.COLOR_STATUS) | curses.A_BOLD)

        weapon_name = player.weapon.name if player.weapon else "없음"
        weapon_bonus = player.weapon.attack_bonus if player.weapon else 0
        armor_name = player.armor.name if player.armor else "없음"
        armor_bonus = player.armor.defense_bonus if player.armor else 0

        stdscr.addstr(3, 2, "[ Equipment ]", curses.A_UNDERLINE)
        stdscr.addstr(4, 2, f"Weapon: {weapon_name} (+{weapon_bonus} ATK)")
        stdscr.addstr(5, 2, f"Armor : {armor_name} (+{armor_bonus} DEF)")

        stdscr.addstr(7, 2, "[ Bag ]", curses.A_UNDERLINE)
        if not player.inventory:
            stdscr.addstr(8, 2, "가방에 보관 중인 아이템이 없습니다.")
        else:
            for index, item in enumerate(player.inventory[:10], start=1):
                stdscr.addstr(7 + index, 2, f"{index}. {item.name} ({item.symbol})")

        stdscr.addstr(17, 2, "아무 키나 누르면 게임으로 돌아갑니다.")
        stdscr.refresh()
