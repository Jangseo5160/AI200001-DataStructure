# src/core/map.py
import random

from src.core.entities import Ladder

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
    [자료구조: 2D Array + Adjacency List (Graph)]
    단일 층의 격자 데이터를 관리하고 절차적 미로를 생성합니다.

    두 가지 자료구조를 병행 사용합니다:
    - 2D Array (self.grid): O(1) 타일 조회, 렌더링에 최적
    - Adjacency List (self.graph): 각 이동 가능 타일을 노드, 인접 이동 가능 타일을 간선으로
      표현한 그래프. BFS/DFS 등 그래프 탐색 알고리즘에 직접 사용 가능.

    대안 비교:
    - 2D Array만 사용: 타일 조회는 O(1)이지만, 그래프 알고리즘 적용 시 매번
      4방향 검사 로직을 인라인으로 작성해야 함.
    - Adjacency List: 노드 간 연결 관계를 명시적으로 저장. 이동 가능 경로를
      그래프로 표현해 BFS/DFS/A* 에 바로 넘길 수 있음. 단, 메모리는 O(V+E).
    - Adjacency Matrix: O(1) 간선 조회지만 V² 메모리 낭비 (던전 크기 60×20=1200노드면
      1200² = 144만 원소 → 낭비).
    """
    def __init__(self, floor_id, width, height, max_rooms=8, min_room_size=4, max_room_size=10, max_floors=5):
        self.floor_id = floor_id
        self.width = width
        self.height = height
        self.max_floors = max_floors
        self.ladder = None

        self.max_rooms = max_rooms
        self.min_room_size = min_room_size
        self.max_room_size = max_room_size

        # [자료구조 1: 2D Array] 맵 전체를 벽('#')으로 채워 초기화
        self.grid = [['#' for _ in range(width)] for _ in range(height)]
        self.rooms = []

        # [자료구조 2: Adjacency List (Graph)] 이동 가능 타일들의 연결 관계
        # key: (x, y) 좌표 튜플, value: 인접 이동 가능 좌표 리스트
        # 던전 생성 후 build_graph()로 초기화됨
        self.graph = {}

        # 미로(던전) 생성 알고리즘 실행
        self.generate_dungeon()
        self.build_graph()
        self.place_ladder()

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

    def build_graph(self):
        """
        [자료구조: Adjacency List (Graph)] 던전 생성 후 이동 가능 타일들의 인접 관계를 구성합니다.
        각 walkable 타일을 노드로, 인접한 walkable 타일로의 연결을 간선으로 표현합니다.
        Time Complexity: O(W × H), Space Complexity: O(V + E) where V ≤ W×H, E ≤ 4V
        """
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        self.graph = {}
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] != '#':
                    neighbors = []
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx] != '#':
                            neighbors.append((nx, ny))
                    self.graph[(x, y)] = neighbors

    def get_neighbors(self, x, y):
        """그래프에서 (x, y)의 인접 이동 가능 타일 목록을 O(1)로 반환합니다."""
        return self.graph.get((x, y), [])

    def is_walkable(self, x, y):
        """특정 좌표로 이동 가능한지 O(1)로 검사합니다."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x] != '#'
        return False

    def place_ladder(self):
        """마지막 방에 다음 층으로 내려가는 사다리를 배치합니다."""
        if self.floor_id >= self.max_floors or not self.rooms:
            return

        ladder_x, ladder_y = self.rooms[-1].center()
        self.ladder = Ladder(ladder_x, ladder_y, self.floor_id + 1)

    def get_ladder_at(self, x, y):
        """좌표에 사다리가 있으면 반환합니다."""
        if self.ladder and self.ladder.is_at(x, y):
            return self.ladder
        return None
