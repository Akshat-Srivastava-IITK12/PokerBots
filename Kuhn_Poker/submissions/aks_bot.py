import random

class AksBot:
    """
    INSTRUCTIONS:
    1. Rename this class to your Team Name (e.g., TeamAlphaBot).
    2. Do NOT change the get_action signature.
    3. Return exactly 'p' (Pass/Fold) or 'b' (Bet/Call).
    """
    def __init__(self):
        self.name = "AksBot"

    def get_action(self, state) -> str:
        card = state.my_card #('J', 'Q', or 'K')
        his = state.history #(e.g., '', 'p', 'b', 'pb')
        # Bot plays first
        if his == '':
            if card == 'K': 
                    if(random.random() < 0.95):
                        return 'b'
                    else :
                        return 'p'
            if card == 'Q':
                if(random.random() <= 0.5):
                    return 'b'
                else :
                    return 'p'
            if card == 'J':
                if(random.random() <= 0.2):
                    return 'b'
                else :
                    return 'p'
        #Bot plays second        
        if his == 'p' or his == 'b':
            if card == 'K': 
                return 'b'
            if card == 'Q' and his == 'p':
                if(random.random() < 0.7):
                    return 'b'
                else :
                    return 'p'
            if card == 'Q' and his == 'b':
                if(random.random() < 0.3):
                    return 'b'
                else :
                    return 'p'
            if card == 'J' and his == 'p': 
                if(random.random() < 0.25):
                    return 'b'
                else :
                    return 'p'
            if card == 'J' and his == 'b': 
                return 'p'
        # Bot plays first and this is the second move
        if his == 'pb':
            if card == 'K': 
                return 'b'
            if card == 'Q':
                if(random.random() < 0.3):
                    return 'b'
                else :
                    return 'p'
            if card == 'J':
                return 'p'
            
        return random.choice(['p', 'b'])