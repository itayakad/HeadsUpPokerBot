class Player:
    def __init__(self, name, stack=1000):
        self.name = name
        self.hand = []
        self.stack = stack
        self.best_hand = []

    def receive_cards(self, cards):
        self.hand.extend(cards)

    def show_hand(self):
        return self.hand

    def evaluate_best_hand(self, community_cards):
        from itertools import combinations
        from hand_evaluation import evaluate_hand

        all_cards = self.hand + community_cards
        all_combinations = combinations(all_cards, 5)
        best_combination = max(all_combinations, key=evaluate_hand)
        self.best_hand = best_combination
