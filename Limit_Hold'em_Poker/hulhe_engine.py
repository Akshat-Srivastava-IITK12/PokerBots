from treys import Deck, Evaluator, Card

class HULHEGameState:
    """The strictly filtered state payload for Heads-Up Limit Hold'em."""
    def __init__(self, my_cards: list, board_cards: list, history: list, valid_actions: list, pot_size: float, amount_to_call: float):
        self.my_cards = my_cards            # e.g., ['Ah', 'Kd']
        self.board_cards = board_cards      # length 0, 3, 4, or 5
        self.history = history              # list of 4 strings: [Pre-flop, Flop, Turn, River]
        self.valid_actions = valid_actions  # e.g., ['f', 'c', 'r']
        self.pot_size = pot_size
        self.amount_to_call = amount_to_call

class HULHEEngine:
    def __init__(self, p1_button, p2_bb):
        # p1 is Button (Small Blind). p2 is Big Blind.
        self.agents = [p1_button, p2_bb]
        self.evaluator = Evaluator()

    def play_hand(self) -> tuple[float, float]:
        deck = Deck()
        cards = [deck.draw(2), deck.draw(2)]
        board = []

        total_commits = [0.0, 0.0]
        history = ["", "", "", ""]
        
        # Round 0: Pre-Flop (Limit: 2)
        # Round 1: Flop (Limit: 2)
        # Round 2: Turn (Limit: 4)
        # Round 3: River (Limit: 4)
        limits = [2.0, 2.0, 4.0, 4.0]
        
        # --- Pre-Flop Setup ---
        # SB (P1) posts 1. BB (P2) posts 2.
        commits_this_round = [1.0, 2.0]
        total_commits = [1.0, 2.0]
        bets_this_round = 1 # The BB counts as the 1st bet pre-flop
        has_acted = [False, False]
        
        current_round = 0
        active_idx = 0 # SB (P1) acts first pre-flop

        while current_round < 4:
            opp_idx = 1 - active_idx
            amount_to_call = commits_this_round[opp_idx] - commits_this_round[active_idx]
            pot_size = total_commits[0] + total_commits[1]
            
            # 1. Enforce the 4-Bet Cap
            valid_actions = ['f', 'c']
            if bets_this_round < 4: 
                valid_actions.append('r')

            # 2. Format cards to string for the API payload
            # Corrected Code
            my_cards_str = [Card.int_to_str(c) for c in cards[active_idx]]
            board_str = [Card.int_to_str(c) for c in board]

            state = HULHEGameState(
                my_cards=my_cards_str,
                board_cards=board_str,
                history=history.copy(), # Pass a copy to prevent agents from mutating engine state
                valid_actions=valid_actions,
                pot_size=pot_size,
                amount_to_call=amount_to_call
            )
            
            # 3. Secure Agent Execution
            try:
                action = self.agents[active_idx].get_action(state)
                if action not in valid_actions: 
                    raise ValueError(f"Illegal action: {action}")
            except Exception as e:
                print(f"[ENGINE WARN] Agent crashed: {e}. Auto-folding.")
                action = 'f' 

            # 4. Apply Action Physics
            history[current_round] += action
            has_acted[active_idx] = True
            
            if action == 'f':
                profit = total_commits[opp_idx]
                return (profit, -profit) if active_idx == 1 else (-profit, profit)
                
            elif action == 'c':
                total_commits[active_idx] += amount_to_call
                commits_this_round[active_idx] += amount_to_call
                        
            elif action == 'r':
                raise_amount = amount_to_call + limits[current_round]
                total_commits[active_idx] += raise_amount
                commits_this_round[active_idx] += raise_amount
                bets_this_round += 1

            # Action passes to the opponent. If the round has ended, this gets
            # overridden below (post-flop streets always start with the BB).
            active_idx = opp_idx

            # 5. Check if the current round is over
            # A round ends ONLY when commits match AND both players have had a chance to act
            if (commits_this_round[0] == commits_this_round[1]) and has_acted[0] and has_acted[1]:
                current_round += 1
                
                if current_round == 4:
                    break # All rounds complete, proceed to Showdown
                
                # --- Setup Next Round ---
                commits_this_round = [0.0, 0.0]
                has_acted = [False, False]
                bets_this_round = 0
                active_idx = 1 # Post-flop, the Big Blind (P2) ALWAYS acts first
                
                # --- BULLETPROOF CARD DEALING ---
                cards_to_draw = 3 if current_round == 1 else 1
                drawn_cards = deck.draw(cards_to_draw)
                
                # Dynamically flatten the output regardless of the treys version
                if isinstance(drawn_cards, list):
                    board.extend(drawn_cards)
                else:
                    board.append(drawn_cards)
                # --------------------------------

        # 6. Terminal Showdown Execution
        p1_score = self.evaluator.evaluate(board, cards[0])
        p2_score = self.evaluator.evaluate(board, cards[1])
        
        # treys evaluator returns LOWER integers for BETTER hands (1 = Royal Flush)
        if p1_score < p2_score:
            return (total_commits[1], -total_commits[1])
        elif p2_score < p1_score:
            return (-total_commits[0], total_commits[0])
        else:
            return (0.0, 0.0) # Split pot