# src/core/entities.py

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

        self.inventory = []
        self.weapon = None
        self.armor = None

    def add_item(self, item):
        """인벤토리 리스트 끝에 아이템을 추가합니다."""
        self.inventory.append(item)

    def remove_item(self, item):
        """사용하거나 버린 아이템을 인벤토리에서 제거합니다."""
        if item in self.inventory:
            self.inventory.remove(item)

    def find_first_item(self, item_type):
        """인벤토리에서 특정 클래스의 첫 번째 아이템을 찾습니다."""
        for item in self.inventory:
            if isinstance(item, item_type):
                return item
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
