import random

class GameState:
    def __init__(self, my_card: str, history: str):
        self.my_card = my_card
        self.history = history
        self.pot_size = 2 + history.count('b') 

class KuhnEngine:
    def __init__(self, p1, p2):
        self.agents = [p1, p2] 
        self.deck = ['J', 'Q', 'K']

    def is_terminal(self, history: str) -> bool:
        return history in ['pp', 'bb', 'bp', 'pbp', 'pbb']

    def get_payoff(self, history: str, cards: list) -> float:
        rank = {'J': 1, 'Q': 2, 'K': 3}
        p1_wins = rank[cards[0]] > rank[cards[1]]

        if history == 'pp': return 1 if p1_wins else -1
        elif history == 'bp': return 1  
        elif history == 'bb': return 2 if p1_wins else -2
        elif history == 'pbp': return -1 
        elif history == 'pbb': return 2 if p1_wins else -2
        raise ValueError("Invalid terminal history.")

    def play_hand(self) -> tuple[float, float]:
        random.shuffle(self.deck)
        cards = [self.deck[0], self.deck[1]]
        history = ""
        active_idx = 0

        while not self.is_terminal(history):
            state = GameState(cards[active_idx], history)
            agent = self.agents[active_idx]
            
            try:
                action = agent.get_action(state)
                if action not in ['p', 'b']: raise ValueError()
            except:
                action = 'p' # Auto-fold on crash or invalid move

            history += action
            active_idx = 1 - active_idx 

        p1_profit = self.get_payoff(history, cards)
        return (p1_profit, -p1_profit)