_suit_names = ['Spade', 'Coppe', 'Denari', 'Bastoni']
_suit_shortnames = [suit_name[0] for suit_name in _suit_names]

class Card:
    def __init__(self, *data):
        r"""
        EXAMPLES::

            sage: Card(8, 0)
            8S
            sage: Card('8S')
            8S

            sage: Card(10, 2)
            10D
            sage: Card('10D')
            10D

        """
        if len(data) == 1:
            if isinstance(data[0], str):
                value = int(data[0][:-1])
                suit  = _suit_shortnames.index(data[0][-1])
            if isinstance(data[0], Card):
                value = data[0].value()
                suit  = data[0].suit()
        else:
            (value, suit) = data
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
        self._players = [{'hand': [], 'tricks': []},
                         {'hand': [], 'tricks': []}]
        self.deal_cards_to_table()
        self.deal_cards_to_players()

    def initialize_deck(self):
        self._deck = Deck()

    def deal_cards_to_table(self):
        self._tabletop = self._deck.deal_cards(4)

    def deal_cards_to_players(self):
        for player in self._players:
            player['hand'] = self._deck.deal_cards(3)

    def __repr__(self):
        r"""
        Show current state of the game.
        """
        s  = f"tabletop: {self._tabletop}\n"
        s += f"player0 : {self._players[0]}\n"
        s += f"player1 : {self._players[1]}"
        return s

    def display_state(self):
        print(self)
        s  = f"tabletop: {self._tabletop}\n"
        s += f"player0 : {self._players[0]}\n"
        s += f"player1 : {self._players[1]}\n"
        s += f"deck    : {list(self._deck)}"
        print(s)

    def tabletop(self):
        return self._tabletop

    def play_card(self, player, card_to_play, cards_from_table):
        r"""

        TESTS::

            sage: M = TestMatch()
            sage: players = M._players
            sage: M
            tabletop: [8B, 1C, 1B, 9S]
            player0 : {'hand': [3D, 6S, 4D], 'tricks': []}
            player1 : {'hand': [7S, 9B, 8D], 'tricks': []}
            sage: M.play_card(players[0], '4D', []); M
            tabletop: [8B, 1C, 1B, 9S, 4D]
            player0 : {'hand': [3D, 6S], 'tricks': []}
            player1 : {'hand': [7S, 9B, 8D], 'tricks': []}
            sage: M.play_card(players[1], '9B', ['9S']); M
            tabletop: [8B, 1C, 1B, 4D]
            player0 : {'hand': [3D, 6S], 'tricks': []}
            player1 : {'hand': [7S, 8D], 'tricks': [(9B, 9S, 0)]}

        """
        card_to_play = Card(card_to_play)
        cards_from_table = [Card(card) for card in cards_from_table]

        if cards_from_table == []:
            player['hand'].remove(card_to_play)
            self._tabletop.append(card_to_play)
        elif self.verify_play(player, card_to_play, cards_from_table):
            player['hand'].remove(card_to_play)
            for card in cards_from_table:
                self._tabletop.remove(card)
            scopa_point = 0 if self._tabletop else 1
            player['tricks'].append(tuple([card_to_play] + cards_from_table + [scopa_point]))
        else:
            raise ValueError

    def verify_play(self, player, card_to_play, cards_from_table):
        r"""
        TESTS::

            sage: M = TestMatch()
            sage: players = M._players
            sage: M
            tabletop: [8B, 1C, 1B, 9S]
            player0 : {'hand': [3D, 6S, 4D], 'tricks': []}
            player1 : {'hand': [7S, 9B, 8D], 'tricks': []}

        Card to play must be in player's hand::

            sage: M.verify_play(players[0], Card(6, 1), [])
            False
            sage: M.verify_play(players[0], Card(6, 0), [])
            True

            sage: M.verify_play(players[1], Card(9, 0), [Card(9, 0)])
            False
            sage: M.verify_play(players[1], Card(9, 3), [Card(9, 0)])
            True

        All cards in ``cards_from_table`` must be on the table::

            sage: M.verify_play(players[1], Card(8, 2), [Card(8, 1)])
            False
            sage: M.verify_play(players[1], Card(8, 2), [Card(8, 3)])
            True

        Sum of values of ``cards_from_table`` is the value of ``card_to_play``::

            sage: M.play_card(players[0], Card(6, 0), [])
            sage: M
            tabletop: [8B, 1C, 1B, 9S, 6S]
            player0 : {'hand': [3D, 4D], 'tricks': []}
            player1 : {'hand': [7S, 9B, 8D], 'tricks': []}
            sage: M.verify_play(players[1], Card(7, 0), [Card(6, 0), Card(1, 3)])
            True
            sage: M.verify_play(players[1], Card(7, 0), [Card(9, 0), Card(1, 3)])
            False
            sage: M.verify_play(players[1], Card(9, 3), [Card(9, 0)])
            True

        If the value of ``card_to_play`` matches the value of a single card on
        the table, then multiple cards cannot be taken::

            sage: M.verify_play(players[1], Card(9, 3), [Card(8, 3), Card(1, 1)])
            False

        """

        # card to play is in player's hand
        if card_to_play not in player['hand']:
            return False

        # all cards in cards_from_table are on the table
        if any(card not in self._tabletop for card in cards_from_table):
            return False

        # sum of cards from table equals value of card played
        if cards_from_table and card_to_play.value() != sum(card.value() for card in cards_from_table):
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

    TESTS:

    Initialize a match::

        sage: M = TestMatch()
        sage: players = M._players
        sage: M
        tabletop: [8B, 1C, 1B, 9S]
        player0 : {'hand': [3D, 6S, 4D], 'tricks': []}
        player1 : {'hand': [7S, 9B, 8D], 'tricks': []}

    Round begins. Players alternate playing a card, starting with player 0::

        sage: M.play_card(players[0], '4D', []); M
        tabletop: [8B, 1C, 1B, 9S, 4D]
        player0 : {'hand': [3D, 6S], 'tricks': []}
        player1 : {'hand': [7S, 9B, 8D], 'tricks': []}
        sage: M.play_card(players[1], '9B', ['9S']); M
        tabletop: [8B, 1C, 1B, 4D]
        player0 : {'hand': [3D, 6S], 'tricks': []}
        player1 : {'hand': [7S, 8D], 'tricks': [(9B, 9S, 0)]}
        sage: M.play_card(players[0], '6S', ['1C', '1B', '4D']); M
        tabletop: [8B]
        player0 : {'hand': [3D], 'tricks': [(6S, 1C, 1B, 4D, 0)]}
        player1 : {'hand': [7S, 8D], 'tricks': [(9B, 9S, 0)]}
        sage: M.play_card(players[1], '8D', ['8B']); M
        tabletop: []
        player0 : {'hand': [3D], 'tricks': [(6S, 1C, 1B, 4D, 0)]}
        player1 : {'hand': [7S], 'tricks': [(9B, 9S, 0), (8D, 8B, 1)]}
        sage: M.play_card(players[0], '3D', []); M
        tabletop: [3D]
        player0 : {'hand': [], 'tricks': [(6S, 1C, 1B, 4D, 0)]}
        player1 : {'hand': [7S], 'tricks': [(9B, 9S, 0), (8D, 8B, 1)]}
        sage: M.play_card(players[1], '7S', []); M
        tabletop: [3D, 7S]
        player0 : {'hand': [], 'tricks': [(6S, 1C, 1B, 4D, 0)]}
        player1 : {'hand': [], 'tricks': [(9B, 9S, 0), (8D, 8B, 1)]}

    Round is over. Deal three more cards to each player::

        sage: M.deal_cards_to_players(); M
        tabletop: [3D, 7S]
        player0 : {'hand': [3B, 6B, 5B], 'tricks': [(6S, 1C, 1B, 4D, 0)]}
        player1 : {'hand': [8S, 7B, 2B], 'tricks': [(9B, 9S, 0), (8D, 8B, 1)]}

    Second round begins::

        ...

    """
    def initialize_deck(self):
        test_deck = [(4,1),(5,2),(5,1),(8,1),(4,3),(1,2),(3,0),(6,1),(9,1),(7,2),(7,1),(6,2),(10,1),(10,3),(9,2),(2,1),(2,2),(10,2),(10,0),(1,0),(3,1),(4,0),(5,0),(2,0),(2,3),(7,3),(8,0),(5,3),(6,3),(3,3),(8,2),(9,3),(7,0),(4,2),(6,0),(3,2),(9,0),(1,3),(1,1),(8,3)]
        deck = Deck()
        deck._cards = [Card(value, suit) for (value, suit) in test_deck]
        self._deck = deck
