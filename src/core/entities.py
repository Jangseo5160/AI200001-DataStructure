# src/core/entities.py

class Entity:
    """
    모든 생명체(플레이어, 몬스터, NPC 등)의 기본이 되는 부모 클래스입니다.
    """
    def __init__(self, x, y, name, hp, speed, attack_power, symbol):
        self.x = x                      # 현재 X 좌표
        self.y = y                      # 현재 Y 좌표
        self.name = name                # 이름
        self.max_hp = hp                # 최대 체력
        self.hp = hp                    # 현재 체력
        
        # [기능 3: Turn Management 연계] 
        # 이 speed 값이 나중에 Priority Queue(우선순위 큐)에서 턴을 계산할 때 사용됩니다.
        self.speed = speed              
        
        self.attack_power = attack_power # 공격력
        self.symbol = symbol            # 화면에 표시될 기호 (예: '@', 'G')

    def move(self, dx, dy):
        """좌표를 이동시킵니다. (충돌 검사는 외부 엔진에서 처리함)"""
        self.x += dx
        self.y += dy

    def take_damage(self, amount):
        """피해를 입고 체력을 감소시킵니다."""
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        """체력을 회복합니다."""
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def is_alive(self):
        """생존 여부를 반환합니다."""
        return self.hp > 0


class Player(Entity):
    """
    Entity를 상속받은 플레이어 클래스입니다.
    경험치, 레벨, 인벤토리 시스템이 추가됩니다.
    """
    def __init__(self, x, y):
        # 플레이어의 초기 스탯 세팅
        super().__init__(x=x, y=y, name="Hero", hp=100, speed=10, attack_power=15, symbol='@')
        
        self.level = 1
        self.exp = 0
        self.max_exp = 50
        
        # [기능 4: Item Inventories 연계]
        # 향후 inventory.py에서 만들 InventoryTree나 QuickSlots 객체를 여기에 할당합니다.
        self.inventory = [] 

    def gain_exp(self, amount):
        """경험치를 획득하고 필요시 레벨업을 처리합니다."""
        self.exp += amount
        while self.exp >= self.max_exp:
            self.level_up()

    def level_up(self):
        """레벨업 시 스탯을 상승시킵니다."""
        self.level += 1
        self.exp -= self.max_exp
        self.max_exp = int(self.max_exp * 1.5) # 다음 레벨업 요구 경험치 증가
        
        self.max_hp += 20
        self.hp = self.max_hp
        self.attack_power += 5
        self.speed += 1


class Enemy(Entity):
    """
    Entity를 상속받은 몬스터 클래스입니다.
    AI 타입과 처치 시 주는 경험치 정보가 추가됩니다.
    """
    def __init__(self, x, y, name, hp, speed, attack_power, symbol, ai_type, exp_reward):
        super().__init__(x, y, name, hp, speed, attack_power, symbol)
        
        # [기능 5: Enemy AI 연계]
        # 'aggressive'면 A* 알고리즘으로 추적, 'random'이면 무작위 이동 등
        self.ai_type = ai_type 
        
        self.exp_reward = exp_reward # 처치 시 플레이어가 얻는 경험치