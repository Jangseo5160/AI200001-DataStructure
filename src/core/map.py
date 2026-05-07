# src/core/map.py
import random

class Room:
    """던전 내부의 방을 정의하는 클래스입니다."""
    def __init__(self, x, y, width, height):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    def center(self):
        """방의 중앙 좌표를 반환합니다. (복도 연결 및 플레이어 시작 위치 지정에 사용)"""
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def intersect(self, other):
        """다른 방과 영역이 겹치는지 검사합니다."""
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Floor:
    """
    [자료구조: 2D Array]
    단일 층의 격자 데이터를 관리하고 절차적 미로를 생성합니다.
    """
    def __init__(self, floor_id, width, height, max_rooms=8, min_room_size=4, max_room_size=10):
        self.floor_id = floor_id
        self.width = width
        self.height = height
        
        self.max_rooms = max_rooms
        self.min_room_size = min_room_size
        self.max_room_size = max_room_size
        
        # 1. 맵 전체를 벽('#')으로 채워 초기화
        self.grid = [['#' for _ in range(width)] for _ in range(height)]
        self.rooms = []
        
        # 2. 미로(던전) 생성 알고리즘 실행
        self.generate_dungeon()

    def generate_dungeon(self):
        """방을 무작위로 배치하고 복도로 연결하는 알고리즘"""
        for _ in range(self.max_rooms):
            # 무작위 크기와 위치의 방 생성
            w = random.randint(self.min_room_size, self.max_room_size)
            h = random.randint(self.min_room_size, self.max_room_size)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)
            
            new_room = Room(x, y, w, h)
            
            # 기존 방들과 겹치는지 확인
            failed = False
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break
                    
            if not failed:
                # 겹치지 않는다면 방을 맵에 파내기('.')
                self.create_room(new_room)
                
                # 첫 번째 방이 아니라면, 이전 방과 복도로 연결하기
                if len(self.rooms) > 0:
                    prev_x, prev_y = self.rooms[-1].center()
                    new_x, new_y = new_room.center()
                    
                    # 동전 던지기로 가로 먼저 파낼지 세로 먼저 파낼지 결정 (ㄱ자 또는 ㄴ자 복도)
                    if random.randint(0, 1) == 1:
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)
                        
                self.rooms.append(new_room)

    def create_room(self, room):
        """방 영역을 길('.')로 만듭니다."""
        for y in range(room.y1, room.y2):
            for x in range(room.x1, room.x2):
                self.grid[y][x] = '.'

    def create_h_tunnel(self, x1, x2, y):
        """가로 복도를 뚫습니다."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.grid[y][x] = '.'

    def create_v_tunnel(self, y1, y2, x):
        """세로 복도를 뚫습니다."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.grid[y][x] = '.'

    def is_walkable(self, x, y):
        """특정 좌표로 이동 가능한지 O(1)로 검사합니다."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x] != '#'
        return False