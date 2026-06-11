import random

class CFR:
    actions = ['p', 'b']
 
    def __init__(self):
        self.regret_sum   = {a: 0.0 for a in self.actions}
        self.strategy_sum = {a: 0.0 for a in self.actions}

    def my_strategy (self, reach_probability: float) -> dict:
        total_regret = sum(max(self.regret_sum[a],0.0) for a in self.actions)
        strategy={}

        for a in self.actions:
            if total_regret > 0:
                strategy[a] = max(self.regret_sum[a],0.0)/total_regret
            else:
                strategy[a] = 1.0 / len(self.actions)

            self.strategy_sum[a] += reach_probability * strategy[a]
        return strategy
    
    def my_play_strategy(self) -> dict:
        total = sum(self.strategy_sum.values())
        if total > 0:
            return {a: self.strategy_sum[a] / total for a in self.actions}
        return {a: 1.0 / len(self.actions) for a in self.actions}
    
class NashCFRBot:
    HISTORY = frozenset(['pp', 'bb', 'bp', 'pbp', 'pbb'])
    Rank = {'J':1, 'Q':2, 'K':3}

    def __init__(self):
        self.node_map: dict[str, CFR] = {}
        self.train(100000)

    def payoff(self, history, cards, perspective):
        p0_wins = self.Rank[cards[0]] > self.Rank[cards[1]]

        if   history == 'pp':  p0 =  1 if p0_wins else -1
        elif history == 'bp':  p0 =  1
        elif history == 'bb':  p0 =  2 if p0_wins else -2
        elif history == 'pbp': p0 = -1
        elif history == 'pbb': p0 =  2 if p0_wins else -2
        return p0 if perspective == 0 else -p0
    
    def cfr(self, cards, history, p0, p1):
        player = len(history) % 2
        if history in self.HISTORY:
            return self.payoff(history, cards, player)
        info_set = cards[player] + history
        node = self.node_map.setdefault(info_set, CFR())
        reach = p0 if player == 0 else p1
        strategy = node.my_strategy(reach)
        action_util = {}
        node_util = 0.0
        for a in CFR.actions:
            next = history + a
            if player == 0:
                cu = self.cfr(cards, next, p0 * strategy[a], p1)
            else: 
                cu = self.cfr(cards, next, p0, p1 * strategy[a])

            action_util[a] = -cu
            node_util += strategy[a] * action_util[a]

        cf_reach = p1 if player == 0 else p0

        for a in CFR.actions:
            node.regret_sum[a] += cf_reach * (action_util[a] - node_util)
        return node_util
    
    def train(self, iterations):
        deck = ['J', 'Q', 'K']
        for _ in range(iterations):
            random.shuffle(deck)
            self.cfr(deck[:2], '', 1.0, 1.0)
 
    def get_nash_action(self, state) -> str:
        info_set = state.my_card + state.history
        if info_set not in self.node_map:
            return 'b' if state.my_card == 'K' else 'p'
        s = self.node_map[info_set].my_play_strategy()
        return 'p' if random.random() < s['p'] else 'b'
    

class Baniya_Bot:

    def __init__(self):
        self.name = "Baniya_Bot"

        self.nash = NashCFRBot()

        self.opp_opens_bet = 0
        self.opp_opens = 0
        self.opp_calls_bet = 0
        self.opp_calls = 0 

        self.hands = 0

    def record_opponent_actions(self, hist: str):
        n= len(hist)

        if(n==1):
            self.opp_opens += 1
            if hist[0] == 'b':
                self.opp_opens_bet += 1
        elif n==2:
            self.opp_calls +=1
            if hist[1] == 'b':
                self.opp_calls_bet += 1

    def exploit(self, card: str, hist: str)-> str:

        if self.opp_opens >= 50:
            f_open = (self.opp_opens_bet / self.opp_opens)
        else:
            f_open = None

        if self.opp_calls >= 30:
            f_call = (self.opp_calls_bet / self.opp_calls)
        else:
            f_call = None
 
        confidence = min(self.hands / 200.0, 1.0)
 
        if hist == 'b' and f_open is not None and random.random() < confidence:
            if f_open < 0.38:
                return 'b' if card == 'K' else 'p'
            if f_open > 0.52:
                return 'b' if card in ('K', 'Q') else 'p'
 
        if hist == '' and f_call is not None and random.random() < confidence:
            if f_call < 0.25:
                return 'b'
            if f_call > 0.55:
                return 'b' if card == 'K' else 'p'
 
        return None 
    
    def get_action(self, state) -> str:
        card, hist = state.my_card, state.history
 
        self.record_opponent_actions(hist)
        self.hands += 1
 
        exploit = self.exploit(card, hist)
        if exploit is not None:
            return exploit
 
        return self.nash.get_nash_action(state)