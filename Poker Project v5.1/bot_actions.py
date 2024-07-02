import random
from itertools import combinations
from deck import Deck
from hand_evaluation import evaluate_hand

def simulate_hand(player_hand, community_cards, num_simulations=1000):
    wins = 0
    for _ in range(num_simulations):
        deck = Deck()
        deck.cards = [card for card in deck.cards if card not in player_hand + community_cards]
        opponent_hand = deck.deal(2)
        remaining_community_cards = deck.deal(5 - len(community_cards))
        full_community_cards = community_cards + remaining_community_cards

        player_best_hand = max(combinations(player_hand + full_community_cards, 5), key=evaluate_hand)
        opponent_best_hand = max(combinations(opponent_hand + full_community_cards, 5), key=evaluate_hand)

        if evaluate_hand(player_best_hand) > evaluate_hand(opponent_best_hand):
            wins += 1

    win_percentage = wins / num_simulations
    print(f"Simulation complete: Bot win percentage = {win_percentage * 100:.2f}%")
    return win_percentage

def bot_action(game, last_player_amount):
    # Convert last_player_amount to integer if it's not 'all in'
    if last_player_amount != 'all in':
        last_player_amount = int(last_player_amount)
    
    bot_hand = game.bot.show_hand()
    community_cards = game.community_cards[:len(game.community_cards)]
    win_percentage = simulate_hand(bot_hand, community_cards)

    print(f"Bot decision based on win percentage: {win_percentage * 100:.2f}%")

    if win_percentage < 0.3:
        # Check if the bot is the big blind and the player has not raised
        if game.big_blind == game.bot and last_player_amount == game.big_blind.stack:
            action = 'check'
            amount = 0
        else:
            action = 'fold'
            amount = 0
    elif 0.3 <= win_percentage < 0.5:
        if last_player_amount <= 0.05 * game.bot.stack:
            action = 'call'
            amount = last_player_amount
        else:
            action = 'check'
            amount = 0
    elif 0.5 <= win_percentage < 0.85:
        action = 'raise'
        amount = int(((win_percentage - 0.5) * game.bot.stack)/10 * 10 + (random.randint(-5, 5)*10))
        if amount > game.bot.stack:
            amount = game.bot.stack
        # Ensure the bot calls the raise amount if the player raised
        if last_player_amount > 0 and amount < last_player_amount:
            amount = last_player_amount
            action = 'call'
    else:
        action = 'raise'
        amount = 'all in'

    return action, amount

def handle_bot_action(game, action, amount):
    player = game.bot
    opponent = game.player

    if action == 'check':
        game.log.append({'type': 'log-bot', 'message': "Bot: Checks"})
    elif action == 'raise':
        if amount == 'all in':
            amount = player.stack
            game.log.append({'type': 'log-bot', 'message': f"Bot: Raises All In ({amount})"})
        else:
            amount = int(amount)
            game.log.append({'type': 'log-bot', 'message': f"Bot: Raises {amount}"})
        if amount > player.stack:
            raise ValueError(f"Cannot raise more than the bot's stack")
        player.stack -= amount
        game.pot += amount
        game.last_raise_amount = amount
    elif action == 'call':
        if amount == 0:
            game.log.append({'type': 'log-bot', 'message': "Bot: Checks"})
        else:
            if amount == 'all in':
                amount = player.stack
            else:
                amount = int(amount)
            game.log.append({'type': 'log-bot', 'message': f"Bot: Calls {amount}"})
            player.stack -= amount
            game.pot += amount
    elif action == 'fold':
        game.stage = 4
        game.log.append({'type': 'log-bot', 'message': "Bot: Folds"})
        game.determine_winner('bot')
