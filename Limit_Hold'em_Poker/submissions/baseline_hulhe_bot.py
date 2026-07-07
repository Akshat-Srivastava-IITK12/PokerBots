import random

class BaselineHULHEBot:
    """
    A heavily abstracted, heuristic-driven agent for Heads-Up Limit Hold'em.
    This bot demonstrates how to parse the state object across all four betting rounds
    and implements basic strategy buckets to decide actions.
    """
    def __init__(self, name="Baseline_Limit_Crusher"):
        self.name = name

    def get_action(self, state) -> str:
        # 1. Base Safety Mechanism
        # If the engine enforces a strict cap (e.g., 4-bets reached), 
        # 'r' is removed from valid_actions. We must not crash the engine.
        if len(state.valid_actions) == 1:
            return state.valid_actions[0]

        # 2. State Parsing & Data Extraction
        # Cards are passed as strings like 'Ah' (Ace of hearts), 'Td' (Ten of diamonds)
        # We extract just the first character (the rank) to evaluate hand strength.
        my_ranks = [card[0] for card in state.my_cards]
        board_ranks = [card[0] for card in state.board_cards]
        
        current_round = len(state.board_cards) # 0, 3, 4, or 5

        # 3. Pre-Flop Strategy (0 Board Cards)
        # Stakes: Small Bet ($2)
        if current_round == 0:
            # Abstraction Bucket 1: Premium Hands (Pocket pairs or high cards)
            if my_ranks[0] == my_ranks[1] or 'A' in my_ranks or 'K' in my_ranks:
                return 'r' if 'r' in state.valid_actions else 'c'
            
            # Abstraction Bucket 2: Playable Hands (Medium cards)
            if 'Q' in my_ranks or 'J' in my_ranks or 'T' in my_ranks:
                return 'c'
            
            # Abstraction Bucket 3: Trash (Fold to aggression, check if free)
            if state.amount_to_call > 0:
                return 'f'
            return 'c'

        # 4. Post-Flop Strategy Initialization
        # Determine if our hole cards connected with the community cards.
        has_pocket_pair = my_ranks[0] == my_ranks[1]
        hit_board_pair = my_ranks[0] in board_ranks or my_ranks[1] in board_ranks
        made_pair = has_pocket_pair or hit_board_pair

        # 5. Flop Strategy (3 Board Cards)
        # Stakes: Small Bet ($2)
        if current_round == 3:
            if made_pair:
                # We have a pair. Play aggressively while bets are cheap.
                return 'r' if 'r' in state.valid_actions else 'c'
            
            # If we missed the flop, do not invest more chips.
            if state.amount_to_call > 0:
                return 'f'
            return 'c'

        # 6. Turn Strategy (4 Board Cards)
        # Stakes: Big Bet ($4) - The price of poker just doubled.
        elif current_round == 4:
            if made_pair:
                # We have a pair, but bets are now expensive. 
                # We switch to a passive "Call Down" strategy to realize equity without over-committing.
                return 'c'
            
            # Missed completely. Surrender to any bet.
            if state.amount_to_call > 0:
                return 'f'
            return 'c'

        # 7. River Strategy (5 Board Cards)
        # Stakes: Big Bet ($4) - Terminal node before showdown.
        elif current_round == 5:
            # On the river, there are no more cards to come. 
            # A simple pair might no longer be good against a 4-bet, but we call to keep them honest.
            if made_pair:
                # If they are raising heavily on the river, they usually have better than one pair.
                # Just call to see the showdown.
                return 'c'
            
            if state.amount_to_call > 0:
                return 'f'
            return 'c'

        # Fallback to prevent engine stalling
        return 'c'