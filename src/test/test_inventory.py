import unittest

from src.core.entities import Player, Potion, Weapon


class InventoryTest(unittest.TestCase):
    def test_player_can_find_and_remove_item_by_type(self):
        player = Player(0, 0)
        potion = Potion(0, 0)
        weapon = Weapon(0, 0)

        player.add_item(weapon)
        player.add_item(potion)

        self.assertIs(player.find_first_item(Potion), potion)

        player.remove_item(potion)

        self.assertIsNone(player.find_first_item(Potion))
        self.assertEqual(player.inventory, [weapon])


if __name__ == "__main__":
    unittest.main()
