import random

class BaselineLeducBot:
    """
    A heuristic bot that calculates basic hand equity.
    It demonstrates how to parse the expanded LeducGameState object.
    """
    def __init__(self, name="Leduc_Heuristic"):
        self.name = name

    def get_action(self, state) -> str:
        # 1. Base Logic: If we only have one option, take it (avoids crashes)
        if len(state.valid_actions) == 1:
            return state.valid_actions[0]

        # 2. Pre-Flop Strategy (Round 1)
        if state.board_card is None:
            if state.my_card == 'K':
                # Highest equity, raise if legally allowed
                return 'r' if 'r' in state.valid_actions else 'c'
            elif state.my_card == 'Q':
                # Medium equity, call
                return 'c'
            else:
                # Lowest equity, fold if facing a bet, otherwise check
                return 'f' if state.amount_to_call > 0 else 'c'

        # 3. Post-Flop Strategy (Round 2)
        else:
            # Did we hit a pair?
            if state.my_card == state.board_card:
                # Raise infinitely.
                return 'r' if 'r' in state.valid_actions else 'c'
            
            # If we didn't pair, evaluate high card strength
            if state.my_card == 'K':
                # Still a strong high card, but vulnerable to a pair
                return 'c'
            else:
                # Weak high card, no pair. Fold to aggression.
                return 'f' if state.amount_to_call > 0 else 'c'