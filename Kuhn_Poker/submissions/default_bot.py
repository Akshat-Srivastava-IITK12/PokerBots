import random

class DefaultBot:
    """
    A logical but non-optimal heuristic bot for Kuhn Poker.
    It plays purely based on card strength and does not bluff.
    """
    def __init__(self, name="Default"):
        # The engine uses this name for the leaderboard
        self.name = name

    def get_action(self, state) -> str:
        """
        Takes in a GameState object and returns exactly 'p' (Pass/Fold) or 'b' (Bet/Call).
        
        Available State Variables:
        - state.my_card: Your current card ('J', 'Q', or 'K')
        - state.history: The betting history so far (e.g., '', 'p', 'b', 'pb')
        - state.pot_size: Current total chips in the pot
        """
        card = state.my_card
        history = state.history

        # --- PLAYING A KING (Strongest Card) ---
        if card == 'K':
            # Always bet or call with the best card.
            return 'b'

        # --- PLAYING A JACK (Weakest Card) ---
        elif card == 'J':
            # Never bluff. Always pass or fold the worst card.
            return 'p'

        # --- PLAYING A QUEEN (Medium Card) ---
        elif card == 'Q':
            # If the opponent bet ('b' or 'pb'), they might have a King.
            # This bot plays it safe and folds.
            if history == 'b' or history == 'pb':
                return 'p'
            
            # If no one has bet yet ('', or 'p'), check/pass.
            return 'p'

        # Fallback (Should never be reached)
        return 'p'