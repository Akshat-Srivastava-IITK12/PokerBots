import random

class LeducGameState:
    """
    The strictly filtered state payload for Leduc Hold'em.
    """
    def __init__(self, my_card: str, board_card: str, history_r1: str, history_r2: str, valid_actions: list, pot_size: float, amount_to_call: float):
        self.my_card = my_card
        self.board_card = board_card          # Will be None during Round 1
        self.history_r1 = history_r1          # e.g., 'rc' (raise, call)
        self.history_r2 = history_r2
        self.valid_actions = valid_actions    # e.g., ['f', 'c', 'r']
        self.pot_size = pot_size
        self.amount_to_call = amount_to_call

class LeducEngine:
    def __init__(self, p1, p2):
        self.agents = [p1, p2]
        self.deck = ['J', 'J', 'Q', 'Q', 'K', 'K']

    def evaluate_showdown(self, p1_card: str, p2_card: str, board_card: str) -> int:
        """Returns 1 if P1 wins, -1 if P2 wins, 0 for a tie."""
        ranks = {'J': 1, 'Q': 2, 'K': 3}
        
        # Pairing the board grants a massive value boost (+10)
        p1_val = ranks[p1_card] + (10 if p1_card == board_card else 0)
        p2_val = ranks[p2_card] + (10 if p2_card == board_card else 0)
        
        if p1_val > p2_val: return 1
        if p2_val > p1_val: return -1
        return 0

    def play_hand(self) -> tuple[float, float]:
        random.shuffle(self.deck)
        cards = [self.deck.pop(), self.deck.pop()]
        board_card = self.deck.pop()

        commits = [1.0, 1.0] # 1 chip ante each
        histories = ["", ""] # [Round 1 History, Round 2 History]
        
        current_round = 0 # 0 for Pre-flop, 1 for Post-flop
        active_idx = 0
        
        while True:
            # 1. State Parsing
            opp_idx = 1 - active_idx
            amount_to_call = commits[opp_idx] - commits[active_idx]
            pot_size = commits[0] + commits[1]
            
            # 2. Determine Valid Actions
            num_raises = histories[current_round].count('r')
            valid_actions = ['f', 'c']
            if num_raises < 2:
                valid_actions.append('r')

            # 3. Secure Agent Execution
            state = LeducGameState(
                my_card=cards[active_idx],
                board_card=board_card if current_round == 1 else None,
                history_r1=histories[0],
                history_r2=histories[1],
                valid_actions=valid_actions,
                pot_size=pot_size,
                amount_to_call=amount_to_call
            )
            
            try:
                action = self.agents[active_idx].get_action(state)
                if action not in valid_actions: 
                    raise ValueError(f"Illegal action: {action}")
            except Exception as e:
                # Disqualify crashed code on this specific hand by forcing a fold
                action = 'f'

            # 4. State Transition Matrix
            histories[current_round] += action
            
            if action == 'f':
                # Terminal State: Opponent wins the pot they did not commit
                profit = commits[opp_idx]
                return (profit, -profit) if active_idx == 1 else (-profit, profit)
                
            elif action == 'c':
                commits[active_idx] = commits[opp_idx]
                # A call ends the round IF it is not the first action of the round
                if len(histories[current_round]) > 1:
                    if current_round == 0:
                        # Advance to Round 2
                        current_round = 1
                        active_idx = 0 # Player 1 always acts first in a new round
                        continue
                    else:
                        # Terminal State: Showdown
                        break
                        
            elif action == 'r':
                bet_size = 2.0 if current_round == 0 else 4.0
                commits[active_idx] = commits[opp_idx] + bet_size

            # Swap active player
            active_idx = opp_idx

        # 5. Showdown Calculation
        winner = self.evaluate_showdown(cards[0], cards[1], board_card)
        if winner == 1:
            return (commits[1], -commits[1])
        elif winner == -1:
            return (-commits[0], commits[0])
        else:
            return (0.0, 0.0) # Split pot