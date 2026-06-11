import random

class ProJuariBot:
    """
    An unexploitable Kuhn Poker bot (Nash Equilibrium).
    Fixed the Player 1 Queen check-calling frequency leak.
    """
    def __init__(self):
        self.name = "pro_juari" 

    def get_action(self, state) -> str:
        card = state.my_card
        history = state.history
        chance = random.random()

        if card == 'K':
            return 'b'

        elif card == 'Q':
            if history == '':
                return 'p'
            elif history == 'p':
                return 'p'
            elif history == 'b':
                return 'b' if chance < (1 / 3) else 'p'
            elif history == 'pb':
                return 'b' if chance < (2 / 3) else 'p'

        elif card == 'J':
            if history == 'b' or history == 'pb':
                return 'p'
            elif history == '' or history == 'p':
                return 'b' if chance < (1 / 3) else 'p'

        # Fallback
        return 'p'
