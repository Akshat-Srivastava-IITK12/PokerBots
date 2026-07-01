import random

class MenteeLeducBot:
    """
    INSTRUCTIONS:
    1. Rename this class to your Team Name (e.g., TeamAlphaLeduc).
    2. Do NOT change the get_action signature.
    3. You must return exactly one of the strings listed in `state.valid_actions`.
    """
    def __init__(self):
        # Change this to your actual team name for the leaderboard
        self.name = "Mentee_Leduc_Template" 

    def get_action(self, state) -> str:
        """
        The state object contains the following variables for Leduc Hold'em:
        
        - state.my_card: Your hole card ('J', 'Q', or 'K')
        - state.board_card: The community card (None in Round 1, 'J', 'Q', or 'K' in Round 2)
        - state.history_r1: String of actions in Round 1 (e.g., '', 'r', 'rc')
        - state.history_r2: String of actions in Round 2 (e.g., '', 'r', 'rc')
        - state.pot_size: Total chips currently in the pot (float)
        - state.amount_to_call: Chips required to match the opponent's bet (float)
        - state.valid_actions: A list of legal moves you can make right now.
                               Contains 'f' (fold), 'c' (call/check), and 'r' (raise/bet).
        """
        
        # Base safeguard: If the engine says you only have one choice, take it.
        if len(state.valid_actions) == 1:
            return state.valid_actions[0]

        # --- Example Heuristic Logic ---
        
        # Round 1 (Pre-Flop) Logic
        if state.board_card is None:
            if state.my_card == 'K':
                # Strongest pre-flop card. Raise if allowed.
                return 'r' if 'r' in state.valid_actions else 'c'
            
        # Round 2 (Post-Flop) Logic
        else:
            if state.my_card == state.board_card:
                # We hit a pair! This is the absolute best possible hand.
                return 'r' if 'r' in state.valid_actions else 'c'

        # Fallback: Play randomly from the allowed actions to avoid crashing
        return random.choice(state.valid_actions)