import random

def create_deck():
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    suit_symbols = {
        'Hearts': '♥',
        'Diamonds': '♦',
        'Clubs': '♣',
        'Spades': '♠'
    }
    deck = [(rank, suit_symbols[suit]) for suit in suits for rank in ranks]
    return deck

def shuffle_deck(deck):
    random.shuffle(deck)
    return deck
