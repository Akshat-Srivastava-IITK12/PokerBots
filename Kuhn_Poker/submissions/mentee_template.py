import random

class Cryptid_Bot:
    """
    INSTRUCTIONS:
    1. Rename this class to your Team Name (e.g., TeamAlphaBot).
    2. Do NOT change the get_action signature.
    3. Return exactly 'p' (Pass/Fold) or 'b' (Bet/Call).
    """
    def __init__(self):
        self.name = "Cryptid_Bot" # Change this to your team name

    def get_action(self, state) -> str:
        # Access state variables:
        # state.my_card ('J', 'Q', or 'K')
        # state.history (e.g., '', 'p', 'b', 'pb')
        
        card = state.my_card
        history = state.history
        # --- PLAYING A KING
        if card == 'K':
            # Always bet
            return 'b'

        # --- PLAYING A JACK
        elif card == 'J':
            # If the opponent bet, fold cuz they likely have K and wont fold.
            if history == 'b' or history == 'pb':
                return 'p'
            if history == 'p' or history == '':
                chance = random.random()
                # 50% chance to bluff if opponent checked/passed, otherwise check/pass.
                # If the opponent checked/passed, bluff to try and make them fold
                if chance < 0.5:
                    return 'b'
                else:
                    return 'p'

            return 'p'

        # --- PLAYING A QUEEN 
        elif card == 'Q':
            # If the opponent bet ('b' or 'pb'), they might have a King.
            if history == 'b' or history == 'pb':
                chance = random.random()
                # opponent might bluff with a Jack, so 30% chance to call, otherwise fold.
                if chance < 0.3:
                    return 'b'
                else:                   
                    return 'p'
            
            # If no one has bet yet ('', or 'p'), check/pass.
            if history == '' or history == 'p':
                return 'p'

        # Fallback (Should never be reached)
        return 'p'