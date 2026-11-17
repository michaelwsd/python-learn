"""Example 1-1: a card deck that behaves like a Python sequence.

It implements only two special methods, __len__ and __getitem__, and gets
len(), indexing, slicing, iteration, reversed(), `in`, sorted() and
random.choice() for free.

Run:  uv run python ch01/frenchdeck.py
"""

import collections
from random import choice

# namedtuple builds a small class with named fields and a readable repr
Card = collections.namedtuple("Card", ["rank", "suit"])


class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list("JQKA")
    suits = "spades diamonds clubs hearts".split()

    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks]

    def __len__(self):  # called by len(deck)
        return len(self._cards)

    def __getitem__(self, position):  # called by deck[i], deck[a:b], for, in...
        return self._cards[position]  # delegate to the list: slicing works too


suit_values = dict(spades=3, hearts=2, diamonds=1, clubs=0)


def spades_high(card):
    """Rank by card value, then suit: 2 of clubs = 0, ace of spades = 51."""
    rank_value = FrenchDeck.ranks.index(card.rank)
    return rank_value * len(suit_values) + suit_values[card.suit]


if __name__ == "__main__":
    deck = FrenchDeck()
    print("len(deck)         ", len(deck))  # __len__
    print("deck[0]           ", deck[0])  # __getitem__(0)
    print("deck[-1]          ", deck[-1])  # negative index: list handles it
    print("deck[:3]          ", deck[:3])  # slicing: list handles it
    print("deck[12::13]      ", deck[12::13])  # every ace
    print("choice(deck)      ", choice(deck))  # stdlib works on any sequence
    print("Q hearts in deck  ", Card("Q", "hearts") in deck)  # no __contains__: scans via __getitem__
    print("first 3 reversed  ", list(reversed(deck))[:3])  # reversed needs __len__ + __getitem__
    print("lowest 3 sorted   ", sorted(deck, key=spades_high)[:3])
