import random

from panel import state

class SacrosanctBot:
    """
    INSTRUCTIONS:
    1. Rename this class to your Team Name (e.g., TeamAlphaBot).
    2. Do NOT change the get_action signature.
    3. Return exactly 'p' (Pass/Fold) or 'b' (Bet/Call).
    """
    def __init__(self):
        self.name = "Sacrosanct" # Change this to your team name

    def get_action(self, state) -> str:
        # Access state variables:
        # state.my_card ('J', 'Q', or 'K')
        # state.history (e.g., '', 'p', 'b', 'pb')
        if state.my_card == 'K':
            return 'b'   
        if state.my_card == 'J':
            if state.history == '':
                return 'b' if random.random() < 0.20 else 'p'
            if state.history == 'p':
                return 'b' if random.random() < 0.60 else 'p'    
            
            return 'p'
            
        # Queen:
        if state.my_card == 'Q':
            if state.history == '':
                return 'b' if random.random() < 0.30 else 'p'
            if state.history == 'p':
                return 'b'
            return 'p'       # if opponent already bet, fold Queen

        return 'p'
