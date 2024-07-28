class Player:
    def __init__(self, name, stack):
        self.name = name
        self.stack = stack
        self.hand = []
        self.current_bet = 0
        self.has_acted = False  # Track if the player has acted in the current round

    def bet(self, amount):
        if amount > self.stack:
            raise ValueError("Not enough chips to bet that amount")
        self.stack -= amount
        self.current_bet += amount

    def call(self, amount):
        call_amount = amount - self.current_bet
        self.bet(call_amount)

    def fold(self):
        self.hand = []

    def act(self):
        action = input(f"{self.name}, enter your action (bet, check, raise, all in, fold): ").strip().lower()
        self.has_acted = True
        return action
