# bot_actions.py
def bot_action(game, last_player_amount):
    if last_player_amount == 'all in':
        return 'call', 'all in'
    last_player_amount = int(last_player_amount)  # Convert to integer
    if last_player_amount == 0:
        return 'check', 0
    elif last_player_amount >= game.bot.stack:
        return 'call', 'all in'
    else:
        return 'call', last_player_amount

def handle_bot_action(game, action, amount):
    player = game.bot
    opponent = game.player

    if action == 'check':
        game.log.append({'type': 'log-bot', 'message': "Bot: Checks"})
    elif action == 'raise':
        if amount == 'all in':
            if player.stack > opponent.stack:
                amount = opponent.stack
            else:
                amount = player.stack
            game.log.append({'type': 'log-bot', 'message': f"Bot: Raises All In ({amount})"})
        else:
            amount = int(amount)
            game.log.append({'type': 'log-bot', 'message': f"Bot: Raises {amount}"})
        if amount > player.stack:
            raise ValueError(f"Cannot raise more than the bot's stack")
        player.stack -= amount
        game.pot += amount
        game.last_raise_amount = amount  # Update the last raise amount
    elif action == 'call':
        if amount == 'all in':
            amount = min(player.stack, game.last_raise_amount)
        else:
            amount = int(amount)
        game.log.append({'type': 'log-bot', 'message': f"Bot: Calls {amount}"})
        player.stack -= amount
        game.pot += amount
    elif action == 'fold':
        game.stage = 4
        game.log.append({'type': 'log-bot', 'message': "Bot: Folds"})
