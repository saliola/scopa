_suit_names = ['Spade', 'Coppe', 'Denari', 'Bastoni']
_suit_shortnames = [suit_name[0] for suit_name in _suit_names]

class Card:
    def __init__(self, value, suit):
        self._value = value
        self._suit = suit

    def suit(self):
        return self._suit

    def value(self):
        return self._value

    def to_str(self):
        return f"{self._value}{_suit_shortnames[self._suit]}"

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        return type(self) == type(other) and self.value() == other.value() and self.suit() == other.suit()


class Deck:
    def __init__(self):
        # Create the deck: each card is represented as (suit, value)
        from random import shuffle
        self._cards = [Card(value, suit) for suit in range(4) for value in range(1, 11)]
        shuffle(self._cards)

    def __iter__(self):
        return iter(self._cards)

    def card_from_str(self, data):
        value = int(data[:-1])
        suit = _suit_shortnames.index(data[-1])
        return (value, suit)

    def card_to_str(self, data):
        return f"{data[0]}{_suit_shortnames[data[1]]}"

    def cards_to_str(self, cards):
        return [card.to_str() for card in cards]

    def display_state(self):
        print(' '.join(self.card_to_str(card) for card in self._cards))

    def deal_cards(self, num_cards):
        return [self._cards.pop() for _ in range(num_cards)]


class Match:
    def __init__(self):
        self.initialize_deck()
        self.deal_cards()

    def initialize_deck(self):
        self._deck = Deck()

    def deal_cards(self):
        self._tabletop = self._deck.deal_cards(4)
        self._players = [{'hand': self._deck.deal_cards(3), 'tricks': []},
                         {'hand': self._deck.deal_cards(3), 'tricks': []}]

    def __repr__(self):
        r"""
        Show current state of the game.
        """
        s  = f"tabletop: {self._tabletop}\n"
        s += f"player0 : {self._players[0]}\n"
        s += f"player1 : {self._players[1]}\n"
        s += f"deck    : {list(self._deck)}"
        return s

    def display_state(self):
        print(self)

    def tabletop(self):
        return self._tabletop

    def play_card(self, player, card_to_play, cards_from_table):
        r"""

        TESTS::

            sage: M = Match()
            sage: M._tabletop = [Card(1, 1), Card(7, 2), Card(5, 3), Card(2, 0)]
            sage: M.tabletop()
            [1C, 7D, 5B, 2S]
            sage: M.play_card(Card(1, 0), [Card(1, 1)])
            [1S, 1C]
            sage: M.tabletop()
            [7D, 5B, 2S]
            sage: M.play_card(Card(7, 1), [Card(7, 2)])
            [7C, 7D]
            sage: M.tabletop()
            [5B, 2S]
            sage: M.play_card(Card(8, 1), [Card(5, 3), Card(2, 0)])

        """
        if cards_from_table == []:
            player['hand'].remove(card_to_play)
            self._tabletop.append(card_to_play)
        elif self.verify_play(player, card_to_play, cards_from_table):
            player['hand'].remove(card_to_play)
            for card in cards_from_table:
                self._tabletop.remove(card)
            player['tricks'].append([card_to_play] + cards_from_table)
        else:
            raise ValueError

    def verify_play(self, player, card_to_play, cards_from_table):
        r"""
        TESTS::

            sage: M = Match()
            sage: M._tabletop = [Card(1, 1), Card(7, 2), Card(5, 3), Card(2, 0)]
            sage: M.tabletop()
            [1C, 7D, 5B, 2S]

        All cards in ``cards_from_table`` must be on the table::

            sage: M.verify_play(Card(6, 1), [Card(5, 3), Card(1, 0)])
            False

        Sum of values of ``cards_from_table`` is the value of ``card_to_play``::

            sage: M.verify_play(Card(8, 1), [Card(5, 3), Card(2, 0)])
            False
            sage: M.verify_play(Card(6, 1), [Card(5, 3), Card(1, 1)])
            True
            sage: M.verify_play(Card(1, 0), [Card(1, 1)])
            True
            sage: M.verify_play(Card(7, 1), [Card(7, 2)])
            True

        If the value of ``card_to_play`` matches the value of a single card on
        the table, then multiple cards cannot be taken::

            sage: M.verify_play(Card(7, 1), [Card(5, 3), Card(2, 0)])
            False

        """

        # card to play is in player's hand
        if card_to_play not in player['hand']:
            return False

        # all cards in cards_from_table are on the table
        if any(card not in self._tabletop for card in cards_from_table):
            return False

        # sum of cards from table equals value of card played
        if card_to_play.value() != sum(card.value() for card in cards_from_table):
            return False

        # you can only pick up multiple cards from the table if there isn't an exact match
        if len(cards_from_table) > 1:
            if card_to_play.value() in [card.value() for card in self._tabletop]:
                return False

        return True

    def play_turn(self, player):
        while True:
            card_to_play = input('card to play: ')
            card_to_play = self._deck.card_from_str(card_to_play)
            print(f"{card_to_play = }")

            cards_from_table = input('cards from table: ').replace(',', ' ').split(' ')
            cards_from_table = [self._deck.card_from_str(card) for card in cards_from_table]
            print(f"{cards_from_table = }")

class TestMatch(Match):
    r"""

    TESTS::

        sage: M = TestMatch()
        sage: players = M._players
        sage: M
        tabletop: [8B, 1C, 1B, 9S]
        player0 : {'hand': [3D, 6S, 4D], 'tricks': []}
        player1 : {'hand': [7S, 9B, 8D], 'tricks': []}
        deck    : [4C, 5D, 5C, 8C, 4B, 1D, 3S, 6C, 9C, 7D, 7C, 6D, 10C, 10B, 9D, 2C, 2D, 10D, 10S, 1S, 3C, 4S, 5S, 2S, 2B, 7B, 8S, 5B, 6B, 3B]

        sage: M.play_card(players[0], Card(4, 1), [Card(4, 0)]); M
        sage: M.play_card(players[1], Card(5, 0), []); M
        sage: M.play_card(players[0], Card(1, 1), []); M

    """
    def initialize_deck(self):
        test_deck = [(4,1),(5,2),(5,1),(8,1),(4,3),(1,2),(3,0),(6,1),(9,1),(7,2),(7,1),(6,2),(10,1),(10,3),(9,2),(2,1),(2,2),(10,2),(10,0),(1,0),(3,1),(4,0),(5,0),(2,0),(2,3),(7,3),(8,0),(5,3),(6,3),(3,3),(8,2),(9,3),(7,0),(4,2),(6,0),(3,2),(9,0),(1,3),(1,1),(8,3)]
        deck = Deck()
        deck._cards = [Card(value, suit) for (value, suit) in test_deck]
        self._deck = deck
