class Renderer:
    @staticmethod
    def render(dungeon_map, player, enemy_ai, inventory, turn_manager, messages):
        screen = [row[:] for row in dungeon_map.grid]

        for enemy in enemy_ai.enemies:
            screen[enemy.position.y][enemy.position.x] = "X"

        screen[player.position.y][player.position.x] = "@"

        print("\033[H\033[J", end="")
        for row in screen:
            print("".join(row))

        print()
        print(f"HP: {player.hp}/{player.max_hp} | Turn: {turn_manager.turn_count} | {inventory.display()}")
        print("Controls: w/a/s/d move | space attack | p potion | u undo | l leaderboard | q quit")
        print("Goal: reach G. P=Potion, S=Sword, X=Enemy")

        if messages:
            print()
            for message in messages[-5:]:
                print(f"- {message}")
