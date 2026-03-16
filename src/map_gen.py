class Room:
    def __init__(self, x, y, width, height):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

def create_rooms(leaf):
    if leaf.child_1 or leaf.child_2:
        # 자식 노드가 있으면 계속 내려감 (재귀)
        if leaf.child_1:
            create_rooms(leaf.child_1)
        if leaf.child_2:
            create_rooms(leaf.child_2)
    else:
        # 더 이상 쪼개지지 않는 '잎(Leaf)'에 도달하면 방 생성
        w = random.randint(3, leaf.width - 2)
        h = random.randint(3, leaf.height - 2)
        x = random.randint(1, leaf.width - w - 1)
        y = random.randint(1, leaf.height - h - 1)
        leaf.room = Room(leaf.x + x, leaf.y + y, w, h)