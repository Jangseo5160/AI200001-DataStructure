class TurnManager:
    PLAYER = "PLAYER"
    ENEMY = "ENEMY"

    def __init__(self):
        self.current_turn = self.PLAYER
        self.turn_count = 1

    def switch_turn(self):
        if self.current_turn == self.PLAYER:
            self.current_turn = self.ENEMY
        else:
            self.current_turn = self.PLAYER
            self.turn_count += 1

    def reset(self):
        self.current_turn = self.PLAYER
        self.turn_count = 1
