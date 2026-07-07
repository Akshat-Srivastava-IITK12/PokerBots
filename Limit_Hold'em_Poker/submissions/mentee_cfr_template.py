import os
import json
import random

class MenteeCFRTemplate:
    """
    INSTRUCTIONS FOR MENTEES:
    1. Rename this class to your actual team name (e.g., TeamAlphaCFR).
    2. Update self.name and the JSON filename in __init__.
    3. Implement your exact training abstraction logic inside `abstract_state`.
    4. DO NOT change the get_action signature.
    """
    def __init__(self):
        # 1. Update this to your team's name for the leaderboard
        self.name = "Team_Name_CFR"
        self.strategy = {}
        
        # 2. Safely resolve the path to your exported JSON strategy file.
        # MUST match the name of the file you submit in your Pull Request.
        current_dir = os.path.dirname(os.path.abspath(__file__))
        strategy_path = os.path.join(current_dir, "your_team_strategy.json")
        
        # 3. Load the blueprint into memory once during initialization
        try:
            with open(strategy_path, 'r') as f:
                self.strategy = json.load(f)
            print(f"[{self.name}] Successfully loaded {len(self.strategy)} info sets.")
        except Exception as e:
            print(f"[{self.name}] ERROR: Could not load strategy file: {e}")
            # Bot will automatically fall back to random/heuristic play

    def abstract_state(self, state) -> str:
        """
        CRITICAL: This function must perfectly match the Information Set 
        bucketing logic you used during your offline training script.
        """
        # Extract betting history
        history_str = "".join(state.history)
        board_len = len(state.board_cards)
        
        # --- REPLACE THIS WITH YOUR ACTUAL BUCKETING LOGIC ---
        # Example dummy abstraction: 
        # Groups all pre-flop hands together, and all post-flop hands together.
        if board_len == 0:
            info_set_key = f"PreFlop_{history_str}"
        else:
            info_set_key = f"PostFlop_{history_str}"
        # ----------------------------------------------------
        
        return info_set_key

    def get_action(self, state) -> str:
        """
        Queries the loaded JSON dictionary and returns a probabilistically 
        sampled action. Do not alter the statistical math below.
        """
        # Base safety mechanism: if the engine caps the betting, take the forced move
        if len(state.valid_actions) == 1:
            return state.valid_actions[0]

        # 1. Translate the raw engine state into your abstracted string key
        info_set_key = self.abstract_state(state)

        # 2. O(1) Hash Map Lookup for your trained strategy
        if info_set_key in self.strategy:
            # Example strategy format: {'r': 0.7, 'c': 0.3}
            action_probs = self.strategy[info_set_key]
            
            actions = list(action_probs.keys())
            probabilities = list(action_probs.values())
            
            # 3. Filter actions to ensure we don't attempt a mathematically illegal move
            valid_action_probs = {a: p for a, p in zip(actions, probabilities) if a in state.valid_actions}
            
            if valid_action_probs:
                # Normalize probabilities (in case an illegal action was filtered out)
                total_prob = sum(valid_action_probs.values())
                norm_actions = list(valid_action_probs.keys())
                norm_probs = [p / total_prob for p in valid_action_probs.values()]
                
                # Make the probabilistic choice based on CFR output
                chosen_action = random.choices(norm_actions, weights=norm_probs, k=1)[0]
                return chosen_action

        # 4. Fallback Mechanism (Damage Control)
        # If your bot reaches a state it never saw in training (or the JSON failed to load),
        # it falls back to basic, safe heuristics to prevent crashing the tournament.
        if state.amount_to_call > 0:
            return random.choice(['c', 'f'])
        return random.choice(['r', 'c'])