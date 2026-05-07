# src/core/map.py

class Floor:
    """
    [자료구조: 2D Array]
    단일 층(또는 방)의 격자 데이터를 관리합니다.
    """
    def __init__(self, floor_id, width, height):
        self.floor_id = floor_id
        self.width = width
        self.height = height
        
        # 2D Array 초기화 ('.'은 길, '#'은 벽으로 가정)
        self.grid = [['.' for _ in range(width)] for _ in range(height)]
        
        # 테두리를 벽으로 막는 간단한 예시
        for x in range(width):
            self.grid[0][x] = '#'
            self.grid[height-1][x] = '#'
        for y in range(height):
            self.grid[y][0] = '#'
            self.grid[y][width-1] = '#'

    def is_walkable(self, x, y):
        """특정 좌표로 이동 가능한지 O(1)로 검사합니다."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x] != '#' # 벽이 아니면 True
        return False


class DungeonGraph:
    """
    [자료구조: Graph (Adjacency List)]
    여러 Floor 객체들을 연결하여 거대한 던전 네트워크를 관리합니다.
    """
    def __init__(self):
        self.nodes = {}       # {floor_id: Floor 객체}
        self.connections = {} # {floor_id: [연결된_floor_id_1, 연결된_floor_id_2, ...]}

    def add_floor(self, floor_id, floor_obj):
        """그래프에 새로운 노드(층)를 추가합니다."""
        self.nodes[floor_id] = floor_obj
        if floor_id not in self.connections:
            self.connections[floor_id] = []

    def connect_floors(self, floor_id_A, floor_id_B):
        """두 층을 연결합니다 (양방향 연결 가정)."""
        if floor_id_A in self.connections and floor_id_B in self.connections:
            self.connections[floor_id_A].append(floor_id_B)
            self.connections[floor_id_B].append(floor_id_A)

    def get_connected_floors(self, floor_id):
        """특정 층에서 이동할 수 있는 다음 층의 목록을 반환합니다."""
        return self.connections.get(floor_id, [])

    def get_floor(self, floor_id):
        return self.nodes.get(floor_id)