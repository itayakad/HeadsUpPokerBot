def player_action(game, action, amount, player_type='player'):
    player = game.player if player_type == 'player' else game.bot
    opponent = game.bot if player_type == 'player' else game.player

    if action == 'check':
        game.log.append({'type': 'log-' + player_type, 'message': f"{player_type.capitalize()}: Checks"})
        return True
    elif action == 'raise':
        if amount == 'all in':
            if player.stack > opponent.stack:
                amount = opponent.stack
            else:
                amount = player.stack
            game.log.append({'type': 'log-' + player_type, 'message': f"{player_type.capitalize()}: Raises All In ({amount})"})
        else:
            amount = int(amount)
            game.log.append({'type': 'log-' + player_type, 'message': f"{player_type.capitalize()}: Raises {amount}"})
        if amount > player.stack:
            raise ValueError(f"Cannot raise more than the {player_type}'s stack")
        player.stack -= amount
        game.pot += amount
        game.last_raise_amount = amount  # Update the last raise amount
        print(f"{player_type.capitalize()}'s stack after raise: {player.stack}")
        return True
    elif action == 'call':
        if amount == 'all in':
            amount = min(player.stack, game.last_raise_amount)
        else:
            amount = int(amount)
        game.log.append({'type': 'log-' + player_type, 'message': f"{player_type.capitalize()}: Calls {amount}"})
        player.stack -= amount
        game.pot += amount
        print(f"{player_type.capitalize()}'s stack after call: {player.stack}")
        return True
    elif action == 'fold':
        game.stage = 4
        game.log.append({'type': 'log-' + player_type, 'message': f"{player_type.capitalize()}: Folds"})
        folded_player = player_type
        game.determine_winner(folded_player)
        return False
