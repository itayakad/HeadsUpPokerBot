RANK_ORDER = {str(i): i for i in range(2, 11)}
RANK_ORDER.update({'J': 11, 'Q': 12, 'K': 13, 'A': 14})

HAND_RANKS = {
    "High Card": 1,
    "One Pair": 2,
    "Two Pair": 3,
    "Three of a Kind": 4,
    "Straight": 5,
    "Flush": 6,
    "Full House": 7,
    "Four of a Kind": 8,
    "Straight Flush": 9,
    "Royal Flush": 10
}

def evaluate_hand(hand):
    ranks = sorted([RANK_ORDER[card.rank] for card in hand], reverse=True)
    suits = [card.suit for card in hand]
    unique_ranks = set(ranks)
    rank_counts = {rank: ranks.count(rank) for rank in unique_ranks}
    counts = sorted(rank_counts.values(), reverse=True)
    is_flush = len(set(suits)) == 1
    is_straight = len(unique_ranks) == 5 and max(ranks) - min(ranks) == 4
    if ranks == [14, 5, 4, 3, 2]:  # A-5 straight (wheel)
        is_straight = True
        ranks = [5, 4, 3, 2, 1]

    if is_straight and is_flush:
        if ranks[0] == 14:
            return (HAND_RANKS["Royal Flush"], ranks)
        return (HAND_RANKS["Straight Flush"], ranks)
    if counts == [4, 1]:
        return (HAND_RANKS["Four of a Kind"], sorted(rank_counts.items(), key=lambda x: (-x[1], -x[0])))
    if counts == [3, 2]:
        return (HAND_RANKS["Full House"], sorted(rank_counts.items(), key=lambda x: (-x[1], -x[0])))
    if is_flush:
        return (HAND_RANKS["Flush"], ranks)
    if is_straight:
        return (HAND_RANKS["Straight"], ranks)
    if counts == [3, 1, 1]:
        return (HAND_RANKS["Three of a Kind"], sorted(rank_counts.items(), key=lambda x: (-x[1], -x[0])))
    if counts == [2, 2, 1]:
        return (HAND_RANKS["Two Pair"], sorted(rank_counts.items(), key=lambda x: (-x[1], -x[0])))
    if counts == [2, 1, 1, 1]:
        return (HAND_RANKS["One Pair"], sorted(rank_counts.items(), key=lambda x: (-x[1], -x[0])))
    return (HAND_RANKS["High Card"], ranks)
