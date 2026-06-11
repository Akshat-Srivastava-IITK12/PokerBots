import random

class YuniqBot:
    """
    INSTRUCTIONS:
    1. Rename this class to your Team Name (e.g., TeamAlphaBot).
    2. Do NOT change the get_action signature.
    3. Return exactly 'p' (Pass/Fold) or 'b' (Bet/Call).
    """
    def __init__(self):
        self.name = "Yuniq" 
        self.hand_count = 0

    def get_action(self, state) -> str:
        self.hand_count += 1

        card = state.my_card
        history = state.history
        r = random.random()

        # Slightly changing to avoid being predictable
        d = ((self.hand_count // 1000) % 5) * 0.03

        # KING
        if card == 'K':

            if history == '':
                return 'b'

            return 'b'

        # QUEEN
        if card == 'Q':

            if history == '':
                return 'b' if r < (0.25 + d) else 'p'

            if history == 'p':
                return 'b'

            if history == 'b':
                return 'b' if r < (0.65 + d/2) else 'p'

            if history == 'pb':
                return 'b' if r < (0.65 + d/2) else 'p'

        # JACK
        if card == 'J':

            if history in ['b', 'pb']:
                return 'p'

            bluff_rate = 0.40 + d

            return 'b' if r < bluff_rate else 'p'

        return 'p'