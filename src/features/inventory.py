class Inventory:
    def __init__(self):
        self.items = []

    def add(self, item_name: str):
        self.items.append(item_name)

    def has(self, item_name: str) -> bool:
        return item_name in self.items

    def count(self, item_name: str) -> int:
        return self.items.count(item_name)

    def use_potion(self, player) -> bool:
        if "Potion" not in self.items:
            return False

        self.items.remove("Potion")
        player.hp = min(player.max_hp, player.hp + 5)
        return True

    def copy_items(self):
        return list(self.items)

    def restore_items(self, items):
        self.items = list(items)

    def display(self) -> str:
        return f"Potion x{self.count('Potion')} | Sword: {'Yes' if self.has('Sword') else 'No'}"
