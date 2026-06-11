import random

class TanviBot:

    def __init__(self):
        self.name = "TanviBot"

    def get_action(self, state) -> str:
        card = state.my_card
        history = state.history

        # it's K
        if card == 'K':
            if history == "":
                return 'b' if random.random() < 0.85 else 'p'

            if history == "p":
                return 'b'

            if history in ["b", "pb"]:
                return 'b'

        # card is Q
        elif card == 'Q':
            if history == "":
                return 'p'

            if history == "p":
                return 'b' if random.random() < 0.70 else 'p'

            if history in ["b", "pb"]:
                return 'b' if random.random() < 0.20 else 'p'

        # card is J
        else:
            if history == "":
                return 'b' if random.random() < 0.10 else 'p'

            if history == "p":
                return 'p'

            if history in ["b", "pb"]:
                return 'p'

        return 'p'