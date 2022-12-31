from collections import namedtuple

_suit_names = ['Spade', 'Coppe', 'Denari', 'Bastoni']
_suit_shortnames = [suit_name[0] for suit_name in _suit_names]
Player = namedtuple('Player', 'number')
Trick = namedtuple('Trick', 'card_played cards_picked_up scopa')

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
        self.players = [Player(1), Player(2)]
        self._tricks = {player: [] for player in self.players}
        self._hands  = {player: [] for player in self.players}
        self.deal_cards_to_table()
        self.deal_cards_to_players()

    def initialize_deck(self):
        self._deck = Deck()

    def deal_cards_to_table(self):
        self._tabletop = self._deck.deal_cards(4)

    def deal_cards_to_players(self):
        for player in self.players:
            self._hands[player] = self._deck.deal_cards(3)

    def state(self, deck=True):
        d = {}
        d["TableTop"] = self._tabletop
        for player in self.players:
            d[f"Player{player.number}"] = dict(hand=self._hands[player], tricks=self._tricks[player])
        if deck:
            d["Deck"] = list(self._deck)
        return d

    def __repr__(self):
        from pprint import pformat
        return pformat(self.state(deck=False))

    def tabletop(self):
        return self._tabletop

    def play_card(self, player, card_to_play, cards_from_table):
        r"""

        TESTS::

            sage: M = TestMatch(); M
            {'Player1': {'hand': [3D, 6S, 4D], 'tricks': []},
             'Player2': {'hand': [7S, 9B, 8D], 'tricks': []},
             'TableTop': [8B, 1C, 1B, 9S]}
            sage: Player1, Player2 = M.players
            sage: M.play_card(Player1, '4D', []); M
            {'Player1': {'hand': [3D, 6S], 'tricks': []},
             'Player2': {'hand': [7S, 9B, 8D], 'tricks': []},
             'TableTop': [8B, 1C, 1B, 9S, 4D]}
            sage: M.play_card(Player2, '9B', ['9S']); M
            {'Player1': {'hand': [3D, 6S], 'tricks': []},
             'Player2': {'hand': [7S, 8D],
                         'tricks': [Trick(card_played=9B, cards_picked_up=(9S,), scopa=0)]},
             'TableTop': [8B, 1C, 1B, 4D]}

        """
        card_to_play = Card(card_to_play)
        cards_from_table = [Card(card) for card in cards_from_table]

        if cards_from_table == []:
            self._hands[player].remove(card_to_play)
            self._tabletop.append(card_to_play)
        elif self.verify_play(player, card_to_play, cards_from_table):
            self._hands[player].remove(card_to_play)
            for card in cards_from_table:
                self._tabletop.remove(card)
            scopa_point = 0 if self._tabletop else 1
            self._tricks[player].append(Trick(card_to_play, tuple(cards_from_table), scopa_point))
        else:
            raise ValueError

    def verify_play(self, player, card_to_play, cards_from_table):
        r"""
        TESTS::

            sage: M = TestMatch(); M
            {'Player1': {'hand': [3D, 6S, 4D], 'tricks': []},
             'Player2': {'hand': [7S, 9B, 8D], 'tricks': []},
             'TableTop': [8B, 1C, 1B, 9S]}
            sage: Player1, Player2 = M.players

        Card to play must be in player's hand::

            sage: M.verify_play(Player1, Card(6, 1), [])
            False
            sage: M.verify_play(Player1, Card(6, 0), [])
            True

            sage: M.verify_play(Player2, Card(9, 0), [Card(9, 0)])
            False
            sage: M.verify_play(Player2, Card(9, 3), [Card(9, 0)])
            True

        All cards in ``cards_from_table`` must be on the table::

            sage: M.verify_play(Player2, Card(8, 2), [Card(8, 1)])
            False
            sage: M.verify_play(Player2, Card(8, 2), [Card(8, 3)])
            True

        Sum of values of ``cards_from_table`` is the value of ``card_to_play``::

            sage: M.play_card(Player1, Card(6, 0), [])
            sage: M
            {'Player1': {'hand': [3D, 4D], 'tricks': []},
             'Player2': {'hand': [7S, 9B, 8D], 'tricks': []},
             'TableTop': [8B, 1C, 1B, 9S, 6S]}
            sage: M.verify_play(Player2, Card(7, 0), [Card(6, 0), Card(1, 3)])
            True
            sage: M.verify_play(Player2, Card(7, 0), [Card(9, 0), Card(1, 3)])
            False
            sage: M.verify_play(Player2, Card(9, 3), [Card(9, 0)])
            True

        If the value of ``card_to_play`` matches the value of a single card on
        the table, then multiple cards cannot be taken::

            sage: M.verify_play(Player2, Card(9, 3), [Card(8, 3), Card(1, 1)])
            False

        """

        # card to play is in player's hand
        if card_to_play not in self._hands[player]:
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

        sage: M = TestMatch(); M
        {'Player1': {'hand': [3D, 6S, 4D], 'tricks': []},
         'Player2': {'hand': [7S, 9B, 8D], 'tricks': []},
         'TableTop': [8B, 1C, 1B, 9S]}
        sage: Player1, Player2 = M.players

    Round begins. Players alternate playing a card, starting with player 0::

        sage: M.play_card(Player1, '4D', []); M
        {'Player1': {'hand': [3D, 6S], 'tricks': []},
         'Player2': {'hand': [7S, 9B, 8D], 'tricks': []},
         'TableTop': [8B, 1C, 1B, 9S, 4D]}
        sage: M.play_card(Player2, '9B', ['9S']); M
        {'Player1': {'hand': [3D, 6S], 'tricks': []},
         'Player2': {'hand': [7S, 8D],
                     'tricks': [Trick(card_played=9B, cards_picked_up=(9S,), scopa=0)]},
         'TableTop': [8B, 1C, 1B, 4D]}
        sage: M.play_card(Player1, '6S', ['1C', '1B', '4D']); M
        {'Player1': {'hand': [3D],
                     'tricks': [Trick(card_played=6S, cards_picked_up=(1C, 1B, 4D), scopa=0)]},
         'Player2': {'hand': [7S, 8D],
                     'tricks': [Trick(card_played=9B, cards_picked_up=(9S,), scopa=0)]},
         'TableTop': [8B]}
        sage: M.play_card(Player2, '8D', ['8B']); M
        {'Player1': {'hand': [3D],
                     'tricks': [Trick(card_played=6S, cards_picked_up=(1C, 1B, 4D), scopa=0)]},
         'Player2': {'hand': [7S],
                     'tricks': [Trick(card_played=9B, cards_picked_up=(9S,), scopa=0),
                                Trick(card_played=8D, cards_picked_up=(8B,), scopa=1)]},
         'TableTop': []}
        sage: M.play_card(Player1, '3D', []); M
        {'Player1': {'hand': [],
                     'tricks': [Trick(card_played=6S, cards_picked_up=(1C, 1B, 4D), scopa=0)]},
         'Player2': {'hand': [7S],
                     'tricks': [Trick(card_played=9B, cards_picked_up=(9S,), scopa=0),
                                Trick(card_played=8D, cards_picked_up=(8B,), scopa=1)]},
         'TableTop': [3D]}
        sage: M.play_card(Player2, '7S', []); M
        {'Player1': {'hand': [],
                     'tricks': [Trick(card_played=6S, cards_picked_up=(1C, 1B, 4D), scopa=0)]},
         'Player2': {'hand': [],
                     'tricks': [Trick(card_played=9B, cards_picked_up=(9S,), scopa=0),
                                Trick(card_played=8D, cards_picked_up=(8B,), scopa=1)]},
         'TableTop': [3D, 7S]}


    Round is over. Deal three more cards to each player::

        sage: M.deal_cards_to_players(); M
        {'Player1': {'hand': [3B, 6B, 5B],
                     'tricks': [Trick(card_played=6S, cards_picked_up=(1C, 1B, 4D), scopa=0)]},
         'Player2': {'hand': [8S, 7B, 2B],
                     'tricks': [Trick(card_played=9B, cards_picked_up=(9S,), scopa=0),
                                Trick(card_played=8D, cards_picked_up=(8B,), scopa=1)]},
         'TableTop': [3D, 7S]}

    Second round begins::

        ...

    """
    def initialize_deck(self):
        test_deck = [(4,1),(5,2),(5,1),(8,1),(4,3),(1,2),(3,0),(6,1),(9,1),(7,2),(7,1),(6,2),(10,1),(10,3),(9,2),(2,1),(2,2),(10,2),(10,0),(1,0),(3,1),(4,0),(5,0),(2,0),(2,3),(7,3),(8,0),(5,3),(6,3),(3,3),(8,2),(9,3),(7,0),(4,2),(6,0),(3,2),(9,0),(1,3),(1,1),(8,3)]
        deck = Deck()
        deck._cards = [Card(value, suit) for (value, suit) in test_deck]
        self._deck = deck
