# src/core/entities.py

from src.core.inventory import InventoryTree

class Entity:
    """
    모든 생명체(플레이어, 몬스터, NPC 등)의 기본 부모 클래스입니다.
    """

    def __init__(self, x, y, name, hp, speed, attack_power, symbol):
        self.x = x
        self.y = y
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.speed = speed
        self.attack_power = attack_power
        self.symbol = symbol

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def is_alive(self):
        return self.hp > 0

    def is_at(self, x, y):
        return self.x == x and self.y == y


class Player(Entity):
    """
    플레이어 클래스입니다.
    Entity를 상속받고 경험치, 레벨, 인벤토리, 장비 정보를 추가합니다.

    [자료구조: List + Dict + Tree — 세 가지를 역할에 따라 병행 사용]

    1. List (self.inventory): 순서 있는 전체 아이템 목록. 순차 순회, 인덱스 접근에 사용.
       - add/remove: O(1) amortized / O(N)
    2. Dict (self._inventory_dict): 타입별 아이템 빠른 조회.
       - key = 클래스 이름, value = 해당 타입 아이템 리스트
       - find_first_item: O(1) dict lookup 후 리스트 첫 원소 → 사실상 O(1)
       - 대안(List 선형 탐색)은 O(N): 아이템이 많을수록 느려짐
    3. Tree (self.inventory_tree, InventoryTree): 카테고리 계층 구조로 아이템 관리.
       - 무기/소모품/기타 분류를 트리 노드로 표현 → 카테고리별 탐색 O(k)
       - 대안(플랫 리스트)은 카테고리 필터링에 O(N) 필요
    """

    def __init__(self, x, y):
        super().__init__(
            x=x,
            y=y,
            name="Hero",
            hp=100,
            speed=10,
            attack_power=15,
            symbol="@"
        )

        self.level = 1
        self.exp = 0
        self.max_exp = 50

        # [List] 전체 아이템 순서 목록
        self.inventory = []
        # [Dict] 타입명 → 아이템 리스트 (O(1) 타입별 조회)
        self._inventory_dict = {}
        # [Tree] 카테고리 계층 구조 (Weapon / Consumable / Etc)
        self.inventory_tree = InventoryTree()

        self.weapon = None
        self.armor = None

    def _item_category(self, item):
        """아이템 클래스를 InventoryTree 카테고리 키로 변환합니다."""
        from src.core.entities import Weapon, Armor, Potion
        if isinstance(item, Weapon):
            return "Weapon"
        if isinstance(item, (Potion,)):
            return "Consumable"
        return "Etc"

    def add_item(self, item):
        """
        인벤토리의 세 자료구조에 아이템을 동시에 추가합니다.
        - List: append O(1)
        - Dict: 타입별 버킷에 append O(1)
        - Tree: 카테고리 노드에 자식 추가 O(1)
        """
        self.inventory.append(item)

        type_key = type(item).__name__
        if type_key not in self._inventory_dict:
            self._inventory_dict[type_key] = []
        self._inventory_dict[type_key].append(item)

        from src.core.inventory import Item as InvItem
        cat = self._item_category(item)
        inv_item = InvItem(id(item), item.name, cat, getattr(item, 'heal_amount', getattr(item, 'attack_bonus', getattr(item, 'defense_bonus', 0))))
        self.inventory_tree.add_item(inv_item)

    def remove_item(self, item):
        """
        세 자료구조에서 아이템을 동시에 제거합니다.
        - List: remove O(N)
        - Dict: 버킷에서 remove O(k) where k = 해당 타입 아이템 수
        """
        if item in self.inventory:
            self.inventory.remove(item)

        type_key = type(item).__name__
        bucket = self._inventory_dict.get(type_key)
        if bucket and item in bucket:
            bucket.remove(item)
            if not bucket:
                del self._inventory_dict[type_key]

    def find_first_item(self, item_type):
        """
        Dict를 사용해 특정 타입의 첫 아이템을 O(1)로 조회합니다.
        (List 선형 탐색 O(N) 대비 타입별 버킷 직접 접근)
        """
        bucket = self._inventory_dict.get(item_type.__name__)
        if bucket:
            return bucket[0]
        return None

    def gain_exp(self, amount):
        self.exp += amount

        while self.exp >= self.max_exp:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp -= self.max_exp
        self.max_exp = int(self.max_exp * 1.5)

        self.max_hp += 20
        self.hp = self.max_hp
        self.attack_power += 5
        self.speed += 1

    def get_total_attack_power(self):
        total = self.attack_power

        if self.weapon is not None:
            total += self.weapon.attack_bonus

        return total

    def get_total_defense(self):
        total = 0

        if self.armor is not None:
            total += self.armor.defense_bonus

        return total


class Enemy(Entity):
    """
    몬스터 클래스입니다.
    Entity를 상속받고 AI 타입과 경험치 보상을 추가합니다.
    """

    def __init__(self, x, y, name, hp, speed, attack_power, symbol, ai_type, exp_reward):
        super().__init__(
            x=x,
            y=y,
            name=name,
            hp=hp,
            speed=speed,
            attack_power=attack_power,
            symbol=symbol
        )

        self.ai_type = ai_type
        self.exp_reward = exp_reward


class ObjectEntity:
    """
    생명체가 아닌 맵 오브젝트의 부모 클래스입니다.
    예: 사다리, 포션, 무기, 방어구
    """

    def __init__(self, x, y, name, symbol):
        self.x = x
        self.y = y
        self.name = name
        self.symbol = symbol

    def is_at(self, x, y):
        return self.x == x and self.y == y


class Ladder(ObjectEntity):
    """
    다음 층으로 이동하는 사다리입니다.
    """

    def __init__(self, x, y, target_floor_id):
        super().__init__(
            x=x,
            y=y,
            name="Ladder",
            symbol=">"
        )

        self.target_floor_id = target_floor_id

    def use(self):
        return self.target_floor_id


class Goal(ObjectEntity):
    """
    마지막 층의 클리어 지점입니다.
    """

    def __init__(self, x, y):
        super().__init__(
            x=x,
            y=y,
            name="GOAL",
            symbol="X"
        )


class Item(ObjectEntity):
    """
    줍거나 사용할 수 있는 아이템의 부모 클래스입니다.
    """

    def __init__(self, x, y, name, symbol):
        super().__init__(x, y, name, symbol)

    def pickup(self, player):
        player.inventory.append(self)


class Potion(Item):
    """
    체력 회복 포션입니다.
    """

    def __init__(self, x, y, heal_amount=30):
        super().__init__(
            x=x,
            y=y,
            name="Potion",
            symbol="!"
        )

        self.heal_amount = heal_amount

    def use(self, player):
        player.heal(self.heal_amount)


class Weapon(Item):
    """
    공격력을 올려주는 무기입니다.
    """

    def __init__(self, x, y, name="Sword", attack_bonus=5):
        super().__init__(
            x=x,
            y=y,
            name=name,
            symbol=")"
        )

        self.attack_bonus = attack_bonus

    def equip(self, player):
        player.weapon = self


class Armor(Item):
    """
    방어력을 올려주는 방어구입니다.
    """

    def __init__(self, x, y, name="Armor", defense_bonus=3):
        super().__init__(
            x=x,
            y=y,
            name=name,
            symbol="["
        )

        self.defense_bonus = defense_bonus

    def equip(self, player):
        player.armor = self
