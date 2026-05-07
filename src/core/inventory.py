# src/core/inventory.py

class Item:
    """아이템의 기본 정보를 담는 클래스입니다."""
    def __init__(self, item_id, name, item_type, value):
        self.item_id = item_id      # 고유 ID (Hash Map Key)
        self.name = name            # 이름
        self.item_type = item_type  # 분류 (무기, 소모품 등)
        self.value = value          # 위력 또는 회복량

class InventoryNode:
    """
    [자료구조: Tree Node]
    인벤토리의 카테고리 또는 개별 아이템을 나타내는 노드입니다.
    """
    def __init__(self, name, is_category=True):
        self.name = name
        self.is_category = is_category
        self.children = []  # 하위 카테고리 또는 아이템 노드들

    def add_child(self, node):
        self.children.append(node)

class InventoryTree:
    """
    [자료구조: General Tree]
    카테고리별로 아이템을 계층 구조로 관리합니다.
    """
    def __init__(self):
        # 루트 노드 생성
        self.root = InventoryNode("가방")
        # 기본 카테고리 생성
        self.categories = {
            "Weapon": InventoryNode("무기"),
            "Consumable": InventoryNode("소모품"),
            "Etc": InventoryNode("기타")
        }
        for cat_node in self.categories.values():
            self.root.add_child(cat_node)

    def add_item(self, item):
        """아이템의 타입에 맞는 카테고리에 아이템 노드를 추가합니다."""
        target_cat = self.categories.get(item.item_type, self.categories["Etc"])
        item_node = InventoryNode(item.name, is_category=False)
        target_cat.add_child(item_node)

    def get_all_items_in_category(self, category_name):
        """특정 카테고리의 모든 아이템 이름을 반환합니다 (Tree Traversal)."""
        if category_name in self.categories:
            return [child.name for child in self.categories[category_name].children]
        return []

class ItemDatabase:
    """
    [자료구조: Hash Map (Dictionary)]
    게임 내 모든 아이템 정보를 O(1)로 조회하기 위한 데이터베이스입니다.
    """
    def __init__(self):
        # 실제 개발 시에는 JSON 파일에서 로드하는 것이 좋습니다.
        self.db = {
            "sword_01": Item("sword_01", "녹슨 칼", "Weapon", 5),
            "sword_02": Item("sword_02", "강철 검", "Weapon", 15),
            "potion_01": Item("potion_01", "빨간 포션", "Consumable", 20),
            "scroll_01": Item("scroll_01", "귀환 주문서", "Etc", 0)
        }

    def get_item(self, item_id):
        """아이템 ID로 정보를 조회합니다. O(1)"""
        return self.db.get(item_id)

class QuickSlots:
    """
    [자료구조: Array (List)]
    숫자키(1~4)에 대응하는 빠른 아이템 접근 슬롯입니다.
    """
    def __init__(self, size=4):
        # 고정된 크기의 배열 사용
        self.slots = [None] * size

    def assign(self, index, item):
        """특정 슬롯에 아이템을 등록합니다."""
        if 0 <= index < len(self.slots):
            self.slots[index] = item

    def use(self, index):
        """슬롯의 아이템을 사용하고 반환합니다."""
        if 0 <= index < len(self.slots):
            return self.slots[index]
        return None