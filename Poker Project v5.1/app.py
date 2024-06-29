from flask import Flask, request, jsonify, render_template
from deck import Deck
from player import Player
from hand_evaluation import evaluate_hand, HAND_RANKS

app = Flask(__name__)

from player_actions import player_action
from bot_actions import bot_action, handle_bot_action

class PokerGame:
    def __init__(self, player_name):
        self.deck = Deck()
        self.player = Player(player_name)
        self.bot = Player("Bot", stack=1000)
        self.community_cards = []
        self.pot = 0
        self.stage = 0  # 0: pre-flop, 1: post-flop, 2: post-turn, 3: post-river, 4: hand end
        self.log = []
        self.last_winner = None
        self.last_raise_amount = 0  # Track the last raised amount
        self.game_over = False
        self.game_over_message = ""
        self.small_blind = self.player  # Initially, the player is the small blind
        self.big_blind = self.bot  # Initially, the bot is the big blind

        self.pay_blinds()  # Pay the blinds at the start of the game
        self.deal_hands()  # Deal hands after initializing blinds

    def pay_blinds(self):
        self.small_blind.stack -= 10
        self.big_blind.stack -= 20
        self.pot += 30
        self.log.append({'type': 'log-' + ('player' if self.small_blind == self.player else 'bot'), 'message': f"{'Player' if self.small_blind == self.player else 'Bot'}: Posts Small Blind (10)"})
        self.log.append({'type': 'log-' + ('player' if self.big_blind == self.player else 'bot'), 'message': f"{'Player' if self.big_blind == self.player else 'Bot'}: Posts Big Blind (20)"})

    def deal_hands(self):
        self.player.hand = []
        self.bot.hand = []
        self.player.receive_cards(self.deck.deal(2))
        self.bot.receive_cards(self.deck.deal(2))
        self.community_cards = self.deck.deal(5)

    def switch_blinds(self):
        if self.small_blind == self.player:
            self.small_blind = self.bot
            self.big_blind = self.player
        else:
            self.small_blind = self.player
            self.big_blind = self.bot

    def reset_for_next_hand(self):
        if self.last_winner == "player":
            self.player.stack += self.pot
        elif self.last_winner == "bot":
            self.bot.stack += self.pot
        else:
            self.player.stack += self.pot / 2
            self.bot.stack += self.pot / 2
        self.pot = 0
        if self.check_endgame():
            print("Endgame reached. One player has 0 stack.")
            return
        self.deck = Deck()
        self.community_cards = self.deck.deal(5)
        self.stage = 0
        self.switch_blinds()  # Switch the blinds after each hand
        self.deal_hands()
        self.pay_blinds()  # Pay the blinds after dealing hands

    def show_hands(self):
        player_hand = [str(card) for card in self.player.show_hand()]
        bot_hand = ['X', 'X'] if self.stage < 4 else [str(card) for card in self.bot.show_hand()]
        community_cards = [str(card) for card in self.show_community_cards()]

        player_label = "Player" + (" (SB)" if self.small_blind == self.player else " (BB)")
        bot_label = "Bot" + (" (SB)" if self.small_blind == self.bot else " (BB)")

        return {
            'player': player_hand,
            'bot': bot_hand,
            'community': community_cards,
            'pot': self.pot,
            'player_stack': self.player.stack,
            'bot_stack': self.bot.stack,
            'player_label': player_label,
            'bot_label': bot_label
        }

    def show_community_cards(self):
        if self.stage == 0:
            revealed_cards = ['X'] * 5
        elif self.stage == 1:
            revealed_cards = self.community_cards[:3] + ['X'] * 2
        elif self.stage == 2:
            revealed_cards = self.community_cards[:4] + ['X'] * 1
        elif self.stage == 3 or self.stage == 4:
            revealed_cards = self.community_cards[:5]
        return revealed_cards

    def determine_winner(self, folded_player=None):
        if folded_player:
            winner_message = f"{folded_player.capitalize()} folded. "
            if folded_player == "player":
                winner_message += "Bot wins!"
                self.last_winner = "bot"
            else:
                winner_message += "Player wins!"
                self.last_winner = "player"

            log_message = {
                'type': 'log-result',
                'message': winner_message,
                'player_best_hand': [],
                'bot_best_hand': []
            }
            self.log.append(log_message)
            self.check_endgame()  # Check for game over
            print(f"Winner message: {winner_message}")
            return {
                'winner_message': winner_message,
                'player_best_hand': [],
                'bot_best_hand': []
            }

        self.player.evaluate_best_hand(self.community_cards)
        self.bot.evaluate_best_hand(self.community_cards)
        player_hand_value = evaluate_hand(self.player.best_hand)
        bot_hand_value = evaluate_hand(self.bot.best_hand)
        hand_ranking = {v: k for k, v in HAND_RANKS.items()}

        print(f"Player best hand: {self.player.best_hand}, Value: {player_hand_value}")
        print(f"Bot best hand: {self.bot.best_hand}, Value: {bot_hand_value}")

        if player_hand_value == bot_hand_value:
            winner_message = "Split the pot!"
            self.last_winner = None
        elif player_hand_value > bot_hand_value:
            winner_message = f"User's {hand_ranking[player_hand_value[0]]} beats the Bot's {hand_ranking[bot_hand_value[0]]}!"
            self.last_winner = "player"
        else:
            winner_message = f"Bot's {hand_ranking[bot_hand_value[0]]} beats the User's {hand_ranking[player_hand_value[0]]}!"
            self.last_winner = "bot"

        log_message = {
            'type': 'log-result',
            'message': winner_message,
            'player_best_hand': [str(card) for card in self.player.best_hand],
            'bot_best_hand': [str(card) for card in self.bot.best_hand]
        }
        self.log.append(log_message)
        self.check_endgame()  # Check for game over
        print(f"Winner message: {winner_message}")
        return {
            'winner_message': winner_message,
            'player_best_hand': [str(card) for card in self.player.best_hand],
            'bot_best_hand': [str(card) for card in self.bot.best_hand]
        }

    def check_endgame(self):
        if (self.player.stack == 0 and self.bot.stack > 0) or (self.bot.stack == 0 and self.player.stack > 0):
            self.game_over = True
            self.game_over_message = f"Game is over. {'Player' if self.bot.stack == 0 else 'Bot'} won!"
            self.log.append({'type': 'log-result', 'message': self.game_over_message})
            return True
        return False

    def next_stage(self):
        if self.stage == 0:  # Pre-flop
            print("Dealing flop...")
            self.stage = 1
            print(f"Community cards: {self.show_community_cards()[:3]}")
        elif self.stage == 1:  # Post-flop
            print("Dealing turn...")
            self.stage = 2
            print(f"Community cards: {self.show_community_cards()[:4]}")
        elif self.stage == 2:  # Post-turn
            print("Dealing river...")
            self.stage = 3
            print(f"Community cards: {self.show_community_cards()[:5]}")
        elif self.stage == 3:  # Post-river
            print("Determining winner...")
            self.stage = 4
            winner_details = self.determine_winner()
            return winner_details
        return None

    def betting_round(self, player_action_str, amount):
        print(f"Player action: {player_action_str}, Amount: {amount}")

        # Handle player action
        continue_round = player_action(self, player_action_str, amount)
        print(f"Continue round after player action: {continue_round}")
        if not continue_round:
            self.stage = 4
            if player_action_str == 'fold':
                folded_player = 'player'
            else:
                folded_player = 'bot'
            result = self.determine_winner(folded_player)
            print(f"Winner determined: {result['winner_message']}")
            if self.check_endgame():
                result['endgame'] = True
            return {'result': result, 'continue': False}

        # Handle bot action
        if self.stage != 4:
            bot_action_choice, bot_amount = bot_action(self, amount)
            print(f"Bot action: {bot_action_choice}, Amount: {bot_amount}")
            handle_bot_action(self, bot_action_choice, bot_amount)
            if not continue_round:
                self.stage = 4
                result = self.determine_winner(folded_player='bot' if bot_action_choice == 'fold' else 'player')
                print(f"Winner determined: {result['winner_message']}")
                if self.check_endgame():
                    result['endgame'] = True
                return {'result': result, 'continue': False}

            # Special case: Both players are all in
            if self.player.stack == 0 or self.bot.stack == 0:
                print("At least one player is all in. Revealing all cards...")
                while self.stage < 4:
                    self.next_stage()
                result = self.determine_winner()
                print(f"Winner determined: {result['winner_message']}")
                if self.check_endgame():
                    result['endgame'] = True
                return {'result': result, 'continue': False}

        if self.stage == 3:
            self.stage = 4
            result = self.determine_winner()
            print(f"Winner determined: {result['winner_message']}")
            if self.check_endgame():
                result['endgame'] = True
            return {'result': result, 'continue': False}
        return {'result': None, 'continue': True}

game = PokerGame("Player")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['GET'])
def start_game():
    return jsonify(game.show_hands())

# In app.py, ensure the responses are consistent
@app.route('/bet', methods=['POST'])
def bet():
    data = request.json
    action = data['action']
    amount = data.get('amount', 0)
    round_result = game.betting_round(action, amount)
    next_stage_result = None
    if round_result['continue']:
        next_stage_result = game.next_stage()
    else:
        next_stage_result = round_result['result']

    response = {
        'hands': game.show_hands(),
        'result': next_stage_result,
        'continue': round_result['continue'],
        'pot': game.pot,
        'player_stack': game.player.stack,
        'bot_stack': game.bot.stack,
        'stage': game.stage,
        'log': game.log,
        'endgame': game.game_over,
        'game_over_message': game.game_over_message if game.game_over else ''
    }

    if game.stage == 4 and next_stage_result:
        response.update(next_stage_result)
    return jsonify(response)

@app.route('/next_hand', methods=['POST'])
def next_hand():
    game.reset_for_next_hand()
    response = {'hands': game.show_hands(), 'log': game.log}
    return jsonify(response)

@app.route('/reveal/<int:number>', methods=['GET'])
def reveal(number):
    return jsonify(game.show_hands())

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)