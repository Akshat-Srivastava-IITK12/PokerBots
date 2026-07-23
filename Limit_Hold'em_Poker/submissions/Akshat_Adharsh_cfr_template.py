import os
import json
import random
import bisect
from treys import Card, Evaluator

# ============================================================================
# Embedded card-abstraction data (precomputed offline, see training notes
# at the bottom of this file). No external files or imports beyond the
# standard library and treys -- this keeps the submission to exactly the
# two required files: this agent and AkBotCFR_strategy.json.
# ============================================================================

RANKS = "23456789TJQKA"
N_BUCKETS = 6

# 169 canonical preflop hands -> win-equity vs. a random hand,
# precomputed via Monte Carlo (4000 rollouts/hand) during offline training.
_PREFLOP_EQUITY = {'22': 0.5006, '32o': 0.329, '32s': 0.3444, '33': 0.5414, '42o': 0.3394, '42s': 0.3646, '43o': 0.3564, '43s': 0.3785, '44': 0.572, '52o': 0.3401, '52s': 0.3641, '53o': 0.3596, '53s': 0.4007, '54o': 0.3796, '54s': 0.4099, '55': 0.594, '62o': 0.3345, '62s': 0.3745, '63o': 0.3691, '63s': 0.3859, '64o': 0.3929, '64s': 0.4118, '65o': 0.399, '65s': 0.4335, '66': 0.6399, '72o': 0.3434, '72s': 0.3841, '73o': 0.3564, '73s': 0.4026, '74o': 0.3861, '74s': 0.4115, '75o': 0.4196, '75s': 0.4385, '76o': 0.4105, '76s': 0.4524, '77': 0.6595, '82o': 0.3703, '82s': 0.4017, '83o': 0.381, '83s': 0.4156, '84o': 0.3882, '84s': 0.4424, '85o': 0.4134, '85s': 0.4449, '86o': 0.4245, '86s': 0.4677, '87o': 0.446, '87s': 0.4729, '88': 0.6833, '92o': 0.3877, '92s': 0.4249, '93o': 0.3997, '93s': 0.4441, '94o': 0.4145, '94s': 0.4331, '95o': 0.4294, '95s': 0.4522, '96o': 0.4368, '96s': 0.4693, '97o': 0.4784, '97s': 0.4904, '98o': 0.4885, '98s': 0.4995, '99': 0.7194, 'A2o': 0.5564, 'A2s': 0.5697, 'A3o': 0.5576, 'A3s': 0.5789, 'A4o': 0.5695, 'A4s': 0.5843, 'A5o': 0.5796, 'A5s': 0.591, 'A6o': 0.5773, 'A6s': 0.5846, 'A7o': 0.5965, 'A7s': 0.6099, 'A8o': 0.5982, 'A8s': 0.6284, 'A9o': 0.6115, 'A9s': 0.6341, 'AA': 0.8542, 'AJo': 0.6509, 'AJs': 0.6567, 'AKo': 0.6597, 'AKs': 0.6673, 'AQo': 0.6436, 'AQs': 0.6515, 'ATo': 0.6245, 'ATs': 0.6448, 'J2o': 0.4412, 'J2s': 0.4836, 'J3o': 0.4721, 'J3s': 0.4826, 'J4o': 0.4592, 'J4s': 0.493, 'J5o': 0.4649, 'J5s': 0.4964, 'J6o': 0.4913, 'J6s': 0.5088, 'J7o': 0.4839, 'J7s': 0.5317, 'J8o': 0.5269, 'J8s': 0.5376, 'J9o': 0.5265, 'J9s': 0.5523, 'JJ': 0.7689, 'JTo': 0.5673, 'JTs': 0.5824, 'K2o': 0.5156, 'K2s': 0.5238, 'K3o': 0.5248, 'K3s': 0.5329, 'K4o': 0.5219, 'K4s': 0.5298, 'K5o': 0.535, 'K5s': 0.5456, 'K6o': 0.5409, 'K6s': 0.5643, 'K7o': 0.5446, 'K7s': 0.5719, 'K8o': 0.5593, 'K8s': 0.5815, 'K9o': 0.5797, 'K9s': 0.6042, 'KJo': 0.6026, 'KJs': 0.6255, 'KK': 0.8185, 'KQo': 0.6182, 'KQs': 0.6365, 'KTo': 0.6124, 'KTs': 0.6209, 'Q2o': 0.4786, 'Q2s': 0.502, 'Q3o': 0.4959, 'Q3s': 0.5206, 'Q4o': 0.4956, 'Q4s': 0.5255, 'Q5o': 0.5136, 'Q5s': 0.5469, 'Q6o': 0.5115, 'Q6s': 0.535, 'Q7o': 0.5294, 'Q7s': 0.5487, 'Q8o': 0.5269, 'Q8s': 0.56, 'Q9o': 0.5496, 'Q9s': 0.5731, 'QJo': 0.5807, 'QJs': 0.598, 'QQ': 0.796, 'QTo': 0.5874, 'QTs': 0.5903, 'T2o': 0.4158, 'T2s': 0.4605, 'T3o': 0.443, 'T3s': 0.4572, 'T4o': 0.4341, 'T4s': 0.4656, 'T5o': 0.4411, 'T5s': 0.4728, 'T6o': 0.4567, 'T6s': 0.4786, 'T7o': 0.4666, 'T7s': 0.5129, 'T8o': 0.4916, 'T8s': 0.539, 'T9o': 0.5258, 'T9s': 0.5284, 'TT': 0.7502}

# Percentile boundaries of the raw treys evaluator score at flop(5)/turn(6)/river(7)
# cards seen, computed once over 60,000 random hands per street during training.
_POSTFLOP_THRESHOLDS = {5: [3951, 5073, 6188, 6616, 7042], 6: [3112, 4123, 5114, 6106, 6687], 7: [2516, 3131, 4015, 5106, 6194]}

_sorted_preflop_equities = sorted(_PREFLOP_EQUITY.values())
_PREFLOP_BOUNDARIES = [
    _sorted_preflop_equities[int(len(_sorted_preflop_equities) * b / N_BUCKETS)]
    for b in range(1, N_BUCKETS)
]

_evaluator = Evaluator()


def _canonical_hand_str(card1_str, card2_str):
    r1, s1 = card1_str[0], card1_str[1]
    r2, s2 = card2_str[0], card2_str[1]
    if r1 == r2:
        return f"{r1}{r2}"
    hi, lo = (r1, r2) if RANKS.index(r1) >= RANKS.index(r2) else (r2, r1)
    suited = s1 == s2
    return f"{hi}{lo}{'s' if suited else 'o'}"


def _preflop_bucket(my_cards):
    hand_str = _canonical_hand_str(my_cards[0], my_cards[1])
    equity = _PREFLOP_EQUITY.get(hand_str, 0.5)
    return bisect.bisect_left(_PREFLOP_BOUNDARIES, equity)


def _postflop_bucket(my_cards, board_cards):
    n_seen = len(my_cards) + len(board_cards)  # 5, 6, or 7
    hole_ints = [Card.new(c) for c in my_cards]
    board_ints = [Card.new(c) for c in board_cards]
    score = _evaluator.evaluate(board_ints, hole_ints)
    boundaries = _POSTFLOP_THRESHOLDS[n_seen]
    idx_from_strong = bisect.bisect_left(boundaries, score)
    return (N_BUCKETS - 1) - idx_from_strong


def _round_label(board_len):
    return {0: "Preflop", 3: "Flop", 4: "Turn", 5: "River"}[board_len]


def _info_set_key(my_cards, board_cards, history):
    """
    Canonical info-set key builder. MUST exactly match the bucketing logic
    used offline in the training script (train_cfr.py, not submitted --
    see the note at the bottom of this file). Any drift between the two
    makes the loaded strategy meaningless, since the bot would be looking
    up the wrong bucket at the table.
    """
    if len(board_cards) == 0:
        b = _preflop_bucket(my_cards)
    else:
        b = _postflop_bucket(my_cards, board_cards)
    rlabel = _round_label(len(board_cards))
    history_str = "".join(history)
    return f"{rlabel}_B{b}_{history_str}"


# ============================================================================
# Tournament agent
# ============================================================================

class AkBotCFR:
    """
    HULHE bot backed by an offline-trained (external-sampling MCCFR) strategy.
    All "thinking" happened before the tournament -- this class only loads
    a precomputed strategy table and does O(1) dictionary lookups at play
    time, per the tournament's offline-training requirement.
    """
    def __init__(self):
        self.name = "AkBotCFR"
        self.strategy = {}

        current_dir = os.path.dirname(os.path.abspath(__file__))
        strategy_path = os.path.join(current_dir, "AkBotCFR_strategy.json")

        try:
            with open(strategy_path, 'r') as f:
                self.strategy = json.load(f)
            print(f"[{self.name}] Successfully loaded {len(self.strategy)} info sets.")
        except Exception as e:
            print(f"[{self.name}] ERROR: Could not load strategy file: {e}")
            # Bot will automatically fall back to random/heuristic play

    def abstract_state(self, state) -> str:
        """
        Must perfectly match the bucketing logic used during offline training.
        """
        return _info_set_key(state.my_cards, state.board_cards, state.history)

    def get_action(self, state) -> str:
        """
        Queries the loaded JSON dictionary and returns a probabilistically
        sampled action.
        """
        # Base safety mechanism: if the engine caps the betting, take the forced move
        if len(state.valid_actions) == 1:
            return state.valid_actions[0]

        info_set_key_str = self.abstract_state(state)

        if info_set_key_str in self.strategy:
            action_probs = self.strategy[info_set_key_str]

            actions = list(action_probs.keys())
            probabilities = list(action_probs.values())

            # Filter actions to ensure we don't attempt a mathematically illegal move
            valid_action_probs = {a: p for a, p in zip(actions, probabilities) if a in state.valid_actions}

            if valid_action_probs:
                # Normalize probabilities (in case an illegal action was filtered out)
                total_prob = sum(valid_action_probs.values())
                norm_actions = list(valid_action_probs.keys())
                norm_probs = [p / total_prob for p in valid_action_probs.values()]

                chosen_action = random.choices(norm_actions, weights=norm_probs, k=1)[0]
                return chosen_action

        # Fallback Mechanism: if the bot reaches a state it never saw in
        # training (or the JSON failed to load), fall back to a safe
        # heuristic so it never crashes the tournament.
        if state.amount_to_call > 0:
            return random.choice(['c', 'f'])
        return random.choice(['r', 'c'])


# ============================================================================
# Training notes (not submitted -- see tournament rules: training scripts
# are excluded from the PR). Strategy was produced by an external-sampling
# MCCFR trainer run offline against a mirror of HULHEEngine's exact rules
# (blinds 1/2, limits [2,2,4,4], 4-bet cap, BB acts first postflop),
# 570,000 iterations, 38,235 info sets discovered. Card abstraction: 6
# preflop equity buckets (Monte Carlo vs. random hand) + 6 postflop
# percentile buckets (raw treys evaluator score, no rollout). Betting
# history kept exact, not bucketed further.
# ============================================================================