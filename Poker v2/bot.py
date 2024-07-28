class Bot:
    def __init__(self, name, stack):
        self.name = name
        self.stack = stack
        self.hand = []
        self.current_bet = 0
        self.has_acted = False  # Track if the bot has acted in the current round

    def bet(self, amount):
        if amount > self.stack:
            raise ValueError("Not enough chips to bet that amount")
        self.stack -= amount
        self.current_bet += amount

    def call(self, amount):
        call_amount = amount
        print(f"DEBUG: {self.name} calling with {call_amount}")
        self.bet(call_amount)

    def fold(self):
        self.hand = []

    def act(self, player_current_bet):
        print(f"DEBUG: {self.name} act called with player_current_bet: {player_current_bet}, bot's current_bet: {self.current_bet}")
        if player_current_bet == 0:
            action = 'check'
        else:
            action = 'call'
        
        self.has_acted = True
        print(f"DEBUG: {self.name} action chosen: {action}")
        return action
