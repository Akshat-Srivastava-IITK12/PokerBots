import random

class perkeo:
    """
    INSTRUCTIONS:
    1. Rename this class to your Team Name (e.g., TeamAlphaBot).
    2. Do NOT change the get_action signature.
    3. Return exactly 'p' (Pass/Fold) or 'b' (Bet/Call).
    """
    def __init__(self):
        self.name = "perkeo" # Change this to your team name

    def get_action(self, state) -> str:
        # Access state variables:
        # state.my_card ('J', 'Q', or 'K')
        # state.history (e.g., '', 'p', 'b', 'pb')
        bluff_king = 0.2
        bluff_jack = 0.4
        bluff_queen = 0.4

        rand = random.random()
        
        # Example heuristic logic:
        if state.my_card == 'K':
            if rand < bluff_king and state.history == '':
                return 'p'
            else:
                return 'b'
            
        elif state.my_card == 'J': 
            if state.history == 'b' or state.history == 'pb':
                return 'p'
            else:
                if rand< bluff_jack:
                    return 'b'    #bluffing when the opponent did not bet
                else:
                    return 'p'

        elif state.my_card == 'Q':
            if state.history == 'p' and rand < 2*bluff_queen:
                return 'b'
            elif state.history == '' and rand < bluff_queen:
                return 'b'
            elif (state.history == 'pb' or state.history == 'b') and rand < bluff_queen/2:
                return 'b'
            else:
                return 'p'
                
        return random.choice(['p', 'b'])
