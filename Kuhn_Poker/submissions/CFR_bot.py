import random

class neBot:
    
    CARDS = ['J', 'Q', 'K']
    ACTIONS = ['p', 'b']
    
    def __init__(self):
        self.name = "CFR_Bot"
        self.regret_sum = {}
        self.strategy_sum = {}
        #1 million iteration for more accurate probs
        self._train(iterations=1000000)
    
    def _get_info_key(self, card, history):
        return (card, history)
    
    def _init_tables(self, key):
        if key not in self.regret_sum:
            self.regret_sum[key]   = [0.0, 0.0]
            self.strategy_sum[key] = [0.0, 0.0]
    
    def _get_strategy(self, key, realization_weight, accumulate):
        self._init_tables(key)
        regrets = self.regret_sum[key]
        positive = [max(0.0, r) for r in regrets]
        total = sum(positive)
        
        if total > 0:
            strategy = [p / total for p in positive]
        else:
            strategy = [0.5, 0.5]
            
        if accumulate:
            for i in range(2):
                self.strategy_sum[key][i] += realization_weight * strategy[i]
                
        return strategy
    
    def _is_terminal(self, history):
        return history in ['pp', 'bb', 'bp', 'pbp', 'pbb']
    
    def _get_payoff(self, history, cards):
        rank = {'J': 1, 'Q': 2, 'K': 3}
        p1_wins = rank[cards[0]] > rank[cards[1]]
        if history == 'pp':  return  1 if p1_wins else -1
        if history == 'bp':  return  1
        if history == 'bb':  return  2 if p1_wins else -2
        if history == 'pbp': return -1
        if history == 'pbb': return  2 if p1_wins else -2
        return 0

    def _cfr(self, cards, history, p0, p1, accumulate):
        if self._is_terminal(history):
            return self._get_payoff(history, cards)
        
        #even for p2 and odd for p1
        player = len(history) % 2
        my_card = cards[player]
        key = self._get_info_key(my_card, history)
        
        # Strategy sum IS weighted by the player's own reach probability
        player_reach = p0 if player == 0 else p1
        strategy = self._get_strategy(key, player_reach, accumulate)
        
        action_values = [0.0, 0.0]
        for i, action in enumerate(self.ACTIONS):
            new_history = history + action
            if player == 0:
                action_values[i] = self._cfr(cards, new_history, p0 * strategy[i], p1, accumulate)
            else:
                action_values[i] = self._cfr(cards, new_history, p0, p1 * strategy[i], accumulate)
        
        node_value = sum(strategy[i] * action_values[i] for i in range(2))
        
        # Regret update is weighted by the opponent's reach probability
        opponent_reach = p1 if player == 0 else p0
        for i in range(2):
            regret = action_values[i] - node_value if player == 0 else -(action_values[i] - node_value)
            self.regret_sum[key][i] += opponent_reach * regret
        
        return node_value

    def _train(self, iterations):
        # discard the first 50% of iterations to prevent 50/50 pollution
        burn_in = iterations // 2
        
        for i in range(iterations):
            cards = random.sample(self.CARDS, 2)
            accumulate = i > burn_in
            self._cfr(cards, "", 1.0, 1.0, accumulate)
            
        print("\n CFR ")
        for key in sorted(self.strategy_sum.keys()):
            total = sum(self.strategy_sum[key])
            if total > 0:
                avg = [round(s/total, 3) for s in self.strategy_sum[key]]
                print(f"  {key}: p={avg[0]}, b={avg[1]}")

    def get_action(self, state) -> str:
        key = self._get_info_key(state.my_card, state.history)
        if key not in self.strategy_sum:
            return 'b' if state.my_card == 'K' else 'p'
        
        total = sum(self.strategy_sum[key])
        if total <= 0:
            return 'b' if state.my_card == 'K' else 'p'
        
        avg = [s / total for s in self.strategy_sum[key]]
        return 'p' if random.random() < avg[0] else 'b'
    
    
    #the final return is not that high despite of 1million iteration like ig the cfr bot played defensive against the default bot like it do not have that great strategy
    # if  instead of nash eql we choose to completely exploit the default bot can give good returns . but here not going with nash eql if the other player is smarter our bot will also become exploitable 