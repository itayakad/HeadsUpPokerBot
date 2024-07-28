from deck import create_deck, shuffle_deck
from hand_evaluator import evaluate_hand
from player import Player
from bot import Bot

class Game:
    def __init__(self, player_name, bot_name, initial_stack):
        self.deck = shuffle_deck(create_deck())
        self.player = Player(player_name, initial_stack)
        self.bot = Bot(bot_name, initial_stack)
        self.pot = 0
        self.community_cards = []
        self.current_bet = 0
        self.small_blind_player = self.player
        self.big_blind_player = self.bot
        self.small_blind_amount = 10
        self.big_blind_amount = 20

    def reset_game_state(self):
        self.deck = shuffle_deck(create_deck())
        self.community_cards = []
        self.player.hand = []
        self.bot.hand = []
        self.reset_bets_and_actions()
        print(f"DEBUG: {self.player.name}'s stack: {self.player.stack}, {self.bot.name}'s stack: {self.bot.stack}")
        print(f"DEBUG: {self.small_blind_player.name} is the small blind, {self.big_blind_player.name} is the big blind")

    def blinds(self):
        self.small_blind_player.bet(self.small_blind_amount)
        self.big_blind_player.bet(self.big_blind_amount)
        self.small_blind_player.current_bet = self.small_blind_amount
        self.big_blind_player.current_bet = self.big_blind_amount
        self.current_bet = self.big_blind_amount
        print(f"DEBUG: {self.small_blind_player.name} posts small blind of {self.small_blind_amount}")
        print(f"DEBUG: {self.big_blind_player.name} posts big blind of {self.big_blind_amount}")
        print(f"DEBUG: {self.small_blind_player.name}'s current bet: {self.small_blind_player.current_bet}, {self.big_blind_player.name}'s current bet: {self.big_blind_player.current_bet}")

    def deal_cards(self):
        self.player.hand = [self.deck.pop() for _ in range(2)]
        self.bot.hand = [self.deck.pop() for _ in range(2)]
        print(f"DEBUG: {self.player.name} was dealt {self.player.hand}")
        print(f"DEBUG: {self.bot.name} was dealt {self.bot.hand}")

    def deal_flop(self):
        self.community_cards = [self.deck.pop() for _ in range(3)]
        print(f"DEBUG: Flop dealt: {self.community_cards}")

    def deal_turn(self):
        self.community_cards.append(self.deck.pop())
        print(f"DEBUG: Turn dealt: {self.community_cards}")

    def deal_river(self):
        self.community_cards.append(self.deck.pop())
        print(f"DEBUG: River dealt: {self.community_cards}")

    def reset_bets_and_actions(self):
        self.current_bet = 0
        self.player.current_bet = 0
        self.bot.current_bet = 0
        self.player.has_acted = False
        self.bot.has_acted = False
        print("DEBUG: Bets and actions reset")

    def process_action(self, player, action):
        print(f"DEBUG: {player.name} chose to {action}")
        player.has_acted = True
        if action == 'raise':
            amount = input(f"{player.name}, enter the amount to raise (or 'all in'): ")
            if amount.lower() == 'all in':
                amount = player.stack
                print(f"DEBUG: {player.name} is going all in with {amount}")
            else:
                amount = int(amount)
            print(f"DEBUG: Before raise - {player.name}'s current bet: {player.current_bet}, Current bet: {self.current_bet}")
            player.bet(amount)
            print(f"DEBUG: After raise - {player.name}'s current bet: {player.current_bet}")
            self.current_bet = player.current_bet
            print(f"DEBUG: Updated current bet: {self.current_bet}")
        elif action == 'call':
            call_amount = self.current_bet - player.current_bet
            print(f"DEBUG: Call amount: {call_amount}")
            player.call(call_amount)
        elif action == 'fold':
            player.fold()
            self.award_pot_to_remaining_player()
            return True  # Indicate that the round should end
        elif action == 'check':
            player.has_acted = True
        print(f"DEBUG: {player.name}'s stack: {self.player.stack}, {self.bot.name}'s stack: {self.bot.stack}")
        return False  # Indicate that the round should continue

    def betting_round(self, pre_flop=False):
        if pre_flop:
            self.reset_bets_and_actions()
            self.blinds()
        else:
            self.reset_bets_and_actions()

        while True:
            print(f"DEBUG: Starting new betting round. Pot: {self.pot}")
            if self.player.current_bet == self.bot.current_bet:
                actions = ['check', 'raise', 'fold']
            else:
                actions = ['call', 'raise', 'fold']

            print(f"DEBUG: {self.player.name}'s hand: {self.player.hand}")
            player_action = input(f"{self.player.name}, enter your action ({', '.join(actions)}): ")
            while player_action not in actions:
                player_action = input(f"Invalid action. {self.player.name}, enter your action ({', '.join(actions)}): ")
            if self.process_action(self.player, player_action):
                return True

            print(f"DEBUG: Player's current bet: {self.player.current_bet}, Bot's current bet: {self.bot.current_bet}")
            print(f"DEBUG: Pot: {self.pot}")
            print(f"DEBUG: {self.player.name}'s stack: {self.player.stack}, {self.bot.name}'s stack: {self.bot.stack}")

            if self.check_betting_progression():
                print("DEBUG: Betting progression criteria met")
                break
            else:
                print(f"DEBUG: Betting progression not met - Player has acted: {self.player.has_acted}, Bot has acted: {self.bot.has_acted}, Player's current bet: {self.player.current_bet}, Bot's current bet: {self.bot.current_bet}")

            # Bot's turn to act
            if self.player.current_bet != self.bot.current_bet:
                actions = ['call', 'raise', 'fold']
            else:
                actions = ['check', 'raise', 'fold']
            
            bot_action = self.bot.act(self.current_bet)
            if bot_action == 'call' and self.current_bet > self.bot.stack:
                bot_action = 'call all in'

            if self.process_action(self.bot, bot_action):
                return True

            print(f"DEBUG: Player's current bet: {self.player.current_bet}, Bot's current bet: {self.bot.current_bet}")
            print(f"DEBUG: Pot: {self.pot}")
            print(f"DEBUG: {self.player.name}'s stack: {self.player.stack}, {self.bot.name}'s stack: {self.bot.stack}")

            if self.check_betting_progression():
                print("DEBUG: Betting progression criteria met")
                break
            else:
                print(f"DEBUG: Betting progression not met - Player has acted: {self.player.has_acted}, Bot has acted: {self.bot.has_acted}, Player's current bet: {self.player.current_bet}, Bot's current bet: {self.bot.current_bet}")

        self.pot += self.player.current_bet + self.bot.current_bet
        print(f"DEBUG: Pot after betting round: {self.pot}")
        self.reset_bets_and_actions()
        return False

    def play(self):
        while True:
            self.reset_game_state()
            self.deal_cards()
            if self.betting_round(pre_flop=True):
                self.alternate_blinds()
                continue  # End the game if a player folded

            self.deal_flop()
            if self.betting_round():
                self.alternate_blinds()
                continue  # End the game if a player folded

            self.deal_turn()
            if self.betting_round():
                self.alternate_blinds()
                continue  # End the game if a player folded

            self.deal_river()
            if self.betting_round():
                self.alternate_blinds()
                continue  # End the game if a player folded

            self.showdown()
            self.alternate_blinds()
            
    def award_pot_to_remaining_player(self):
        if not self.player.hand:  # Player folded
            self.bot.stack += self.pot
            print(f"DEBUG: {self.bot.name} wins the pot of {self.pot} by default (Player folded)")
        elif not self.bot.hand:  # Bot folded
            self.player.stack += self.pot
            print(f"DEBUG: {self.player.name} wins the pot of {self.pot} by default (Bot folded)")
        self.pot = 0  # Reset the pot for the next round

    def check_betting_progression(self):
        return (
            self.player.has_acted and self.bot.has_acted and
            self.player.current_bet == self.bot.current_bet
        )

    def evaluate_hand_display(self, cards):
        # This function evaluates the hand and returns a string describing the best hand and the best 5-card combination
        # You may want to use a proper poker hand evaluation library for more accurate results
        # This is a simplified example for demonstration purposes
        sorted_cards = sorted(cards, key=lambda x: x[0])  # Sort cards by rank
        hand_type = "High Card"  # Simplified hand evaluation
        best_hand = sorted_cards[-5:]  # Simplified best 5-card hand
        return hand_type, best_hand

    def showdown(self):
        player_hand = self.player.hand + self.community_cards
        bot_hand = self.bot.hand + self.community_cards
        player_hand_type, player_best_hand = self.evaluate_hand_display(player_hand)
        bot_hand_type, bot_best_hand = self.evaluate_hand_display(bot_hand)
        
        print(f"{self.player.name}'s best hand: {player_hand_type}, {player_best_hand}")
        print(f"{self.bot.name}'s best hand: {bot_hand_type}, {bot_best_hand}")
        
        player_hand_strength = evaluate_hand(player_hand)
        bot_hand_strength = evaluate_hand(bot_hand)
        
        if player_hand_strength > bot_hand_strength:
            print(f"{self.player.name} wins the pot!")
            self.player.stack += self.pot
        else:
            print(f"{self.bot.name} wins the pot!")
            self.bot.stack += self.pot
        print(f"DEBUG: Final pot: {self.pot}")
        print(f"DEBUG: {self.player.name}'s stack: {self.player.stack}, {self.bot.name}'s stack: {self.bot.stack}")
        self.pot = 0  # Reset the pot for the next round

    def alternate_blinds(self):
        if self.small_blind_player == self.player:
            self.small_blind_player = self.bot
            self.big_blind_player = self.player
        else:
            self.small_blind_player = self.player
            self.big_blind_player = self.bot
