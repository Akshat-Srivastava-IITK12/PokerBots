import random

class MenteeKuhnBot:
    """
    INSTRUCTIONS:
    1. Rename this class to your Team Name (e.g., TeamAlphaBot).
    2. Do NOT change the get_action signature.
    3. Return exactly 'p' (Pass/Fold) or 'b' (Bet/Call).
    """
    def __init__(self):
        self.name = "Mentee_Template" # Change this to your team name

    def get_action(self, state) -> str:
        # Access state variables:
        # state.my_card ('J', 'Q', or 'K')
        # state.history (e.g., '', 'p', 'b', 'pb')
        
        # Example heuristic logic:
        if state.my_card == 'K': return 'b'
        if state.my_card == 'J': return 'p'
        return random.choice(['p', 'b'])