import random

class TeamShauryaBot:
    """
    INSTRUCTIONS:
    1. Rename this class to your Team Name (e.g., TeamAlphaBot).
    2. Do NOT change the get_action signature.
    3. Return exactly 'p' (Pass/Fold) or 'b' (Bet/Call).
    """
    def __init__(self):
        self.name = "team_shaurya" # Change this to your team name

    def get_action(self, state) -> str:
        # Access state variables:
        # state.my_card ('J', 'Q', or 'K')
        # state.history (e.g., '', 'p', 'b', 'pb')
        card=state.my_card
        history=state.history
        if card=='K' and history=='': return 'b' if random.random()<0.67 else 'p'
        elif card=='K' and history=='b': return 'b'
        elif card=='K' and history=='p': return 'b'
        elif card=='K' and history=='pb': return 'b'
        elif card=='J' and history=='': return 'b' if random.random()<0.33 else 'p'
        elif card=='J' and history=='b': return 'p'
        elif card=='J' and history=='p': return 'b' if random.random()<0.33 else 'p'
        elif card=='J' and history=='pb': return 'p'
        elif card=='Q' and history=='': return 'b' if random.random()<0.5 else 'p'
        elif card=='Q' and history=='b': return 'b' if random.random()<0.2 else 'p'
        elif card=='Q' and history=='p': return 'b' if random.random()<0.67 else 'p'
        elif card=='Q' and history=='pb': return 'b' if random.random()<0.2 else 'p'
       