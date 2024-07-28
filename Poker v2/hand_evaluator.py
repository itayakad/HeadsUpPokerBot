from collections import Counter

def evaluate_hand(hand):
    """Evaluates the strength of a poker hand."""
    ranks = [card[0] for card in hand]
    suits = [card[1] for card in hand]
    
    flush = len(set(suits)) == 1
    rank_values = sorted([ranks.index(rank) for rank in ranks])
    straight = all(rank_values[i] + 1 == rank_values[i + 1] for i in range(len(rank_values) - 1))
    
    rank_counts = Counter(ranks)
    most_common = rank_counts.most_common()
    
    if flush and straight:
        return 'Straight Flush', rank_values
    elif most_common[0][1] == 4:
        return 'Four of a Kind', most_common
    elif most_common[0][1] == 3 and most_common[1][1] == 2:
        return 'Full House', most_common
    elif flush:
        return 'Flush', rank_values
    elif straight:
        return 'Straight', rank_values
    elif most_common[0][1] == 3:
        return 'Three of a Kind', most_common
    elif most_common[0][1] == 2 and most_common[1][1] == 2:
        return 'Two Pair', most_common
    elif most_common[0][1] == 2:
        return 'One Pair', most_common
    else:
        return 'High Card', rank_values
