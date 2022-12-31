from collections import defaultdict, namedtuple

SUIT_NAMES = ['Spade', 'Coppe', 'Denari', 'Bastoni']
SUIT_SHORTNAMES = [suit_name[0] for suit_name in SUIT_NAMES]
PRIMIERA_POINTS = defaultdict(int, {1: 16, 2: 12, 3: 13, 4: 14, 5: 15, 6: 18, 7: 21, 8: 10, 9: 10, 10: 10})
SETTEBELLO_SUIT = 2
SETTEBELLO_VALUE = 7

Trick = namedtuple('Trick', ['card_played', 'cards_picked_up', 'scopa'])

class Player(namedtuple('Player', 'number')):
    def __repr__(self):
        return f"Player{self.number}"

class Card(namedtuple('Card', ['value', 'suit'])):
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

        sage: Card(Card(10, 2))
        10D
        sage: Card(Card('10D'))
        10D

    """
    def __new__(cls, *data):
        if len(data) == 1:
            if isinstance(data[0], Card):
                return data[0]
            if isinstance(data[0], str):
                value = int(data[0][:-1])
                suit  = SUIT_SHORTNAMES.index(data[0][-1])
        else:
            (value, suit) = data
        return super().__new__(cls, value, suit)

    def __repr__(self):
        return f"{self.value}{SUIT_SHORTNAMES[self.suit]}"

class Deck:
    def __init__(self):
        # Create the deck: each card is represented as (suit, value)
        from random import shuffle
        self._cards = [Card(value, suit) for suit in range(4) for value in range(1, 11)]
        shuffle(self._cards)

    def __iter__(self):
        return iter(self._cards)

    def __len__(self):
        return len(self._cards)

    def card_from_str(self, data):
        value = int(data[:-1])
        suit = SUIT_SHORTNAMES.index(data[-1])
        return (value, suit)

    def card_to_str(self, data):
        return f"{data[0]}{SUIT_SHORTNAMES[data[1]]}"

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
        self._tabletop = []
        self._last_player_to_pickup = None
        self._turn_number = 0

    def initialize_deck(self):
        self._deck = Deck()

    def deal_cards_to_table(self):
        self._tabletop.extend(self._deck.deal_cards(4))

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

            sage: M = TestMatch()
            sage: M.deal_cards_to_table()
            sage: M.deal_cards_to_players()
            sage: M
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

        self._turn_number += 1

        if cards_from_table == []:
            self._hands[player].remove(card_to_play)
            self._tabletop.append(card_to_play)
        elif self.verify_play(player, card_to_play, cards_from_table):
            self._hands[player].remove(card_to_play)
            for card in cards_from_table:
                self._tabletop.remove(card)
            scopa_point = 0 if self._tabletop and self._turn_number != 36 else 1
            self._tricks[player].append(Trick(card_to_play, tuple(cards_from_table), scopa_point))
            self._last_player_to_pickup = player
        else:
            raise ValueError

    def verify_play(self, player, card_to_play, cards_from_table):
        r"""
        TESTS::

            sage: M = TestMatch()
            sage: M.deal_cards_to_table()
            sage: M.deal_cards_to_players()
            sage: M
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
        if cards_from_table and card_to_play.value != sum(card.value for card in cards_from_table):
            return False

        # you can only pick up multiple cards from the table if there isn't an exact match
        if len(cards_from_table) > 1:
            if card_to_play.value in [card.value for card in self._tabletop]:
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

    def tally_tricks(self):
        SETTEBELLO = Card(SETTEBELLO_VALUE, SETTEBELLO_SUIT)

        tally = {}
        for player in self.players:
            num_scopas = 0
            num_cards = 0
            num_denari = 0
            settebello = 0
            primiera_cards = [Card(0, 0), Card(0, 1), Card(0, 2), Card(0, 3)]
            primiera_score = [0, 0, 0, 0]

            for trick in self._tricks[player]:
                num_scopas += trick.scopa
                for card in trick.cards_picked_up + (trick.card_played,):
                    if card:
                        num_cards += 1
                        if card.suit == SETTEBELLO_SUIT:
                            num_denari += 1
                        if card == SETTEBELLO:
                            settebello = 1
                        if PRIMIERA_POINTS[card.value] > primiera_score[card.suit]:
                            primiera_cards[card.suit] = card
                            primiera_score[card.suit] = PRIMIERA_POINTS[card.value]

            tally[player] = (num_scopas,
                             num_cards,
                             num_denari,
                             settebello,
                             sum(primiera_score),
                             primiera_cards)

        return tally


    def score_match(self):
        r"""

        TESTS::

            sage: M = TestMatch()
            sage: M.play_random_match()

        """
        tally = self.tally_tricks()

        points = {player: 0 for player in self.players}
        for player in self.players:
            points[player]  = tally[player][0]              # number of scopas
            points[player] += int(tally[player][1] > 20)    # most cards
            points[player] += int(tally[player][2] >  5)    # most denari
            points[player] += tally[player][3]              # settebello

        # primiera
        if   tally[self.players[0]][4] > tally[self.players[1]][4]:
            points[self.players[0]] += 1
        elif tally[self.players[0]][4] < tally[self.players[1]][4]:
            points[self.players[1]] += 1

        return points

    def play_random_match(self, verbose=True):
        r"""

        TESTS::

            sage: M = TestMatch()
            sage: M.play_random_match()

        """
        self.deal_cards_to_table()

        rows = []
        while self._deck:
            self.deal_cards_to_players()
            for _ in range(3):
                for player in self.players:
                    row = [f"{self._tabletop}"]
                    card_to_play, cards_from_table = self.random_play(player)
                    if cards_from_table:
                        row.append(f"{player} plays {card_to_play} to pick up {str(cards_from_table)[1:-1]}")
                    else:
                        row.append(f"{player} places {card_to_play} on table")
                    rows.append(row)

        row = [f"{self._tabletop}"]
        if self._tabletop:
            last_trick = Trick(None, tuple(self._tabletop), 0)
            self._tricks[self._last_player_to_pickup].append(last_trick)
            self._tabletop = []
            row.append(f"Cards on TableTop go to {self._last_player_to_pickup}")
        rows.append(row)

        print(table(rows))
        print()

        print(f"tally: {self.tally_tricks()}")

        print(f"score: {self.score_match()}")


    def random_play(self, player):
        import random
        card_to_play, cards_from_table = random.choice(self.possible_plays(player))
        self.play_card(player, card_to_play, cards_from_table)
        return card_to_play, cards_from_table

    def possible_plays(self, player):
        r"""

        TESTS::

            sage: M = TestMatch();
            sage: M.deal_cards_to_table()
            sage: M.deal_cards_to_players()
            sage: M
            {'Player1': {'hand': [3D, 6S, 4D], 'tricks': []},
             'Player2': {'hand': [7S, 9B, 8D], 'tricks': []},
             'TableTop': [8B, 1C, 1B, 9S]}
            sage: Player1, Player2 = M.players
            sage: M.possible_plays(Player1)
            [(3D, ()), (6S, ()), (4D, ())]
            sage: M.possible_plays(Player2)
            [(8D, (8B,)), (9B, (9S,)), (7S, ())]

        """
        players_hand = self._hands[player]
        plays = []
        for cards_from_table in powerset(self._tabletop):
            s = sum(card.value for card in cards_from_table)
            for card_to_play in players_hand:
                if card_to_play.value == s:
                    if self.verify_play(player, card_to_play, cards_from_table):
                        plays.append((card_to_play, cards_from_table))
        for card_to_play in players_hand:
            if card_to_play not in [play[0] for play in plays]:
                plays.append((card_to_play, ()))
        return plays


class TestMatch(Match):
    r"""

    TESTS:

    Set up a match::

        sage: M = TestMatch();
        sage: M
        {'Player1': {'hand': [], 'tricks': []},
         'Player2': {'hand': [], 'tricks': []},
         'TableTop': []}
        sage: M.deal_cards_to_table()
        sage: M
        {'Player1': {'hand': [], 'tricks': []},
         'Player2': {'hand': [], 'tricks': []},
         'TableTop': [8B, 1C, 1B, 9S]}
        sage: M.deal_cards_to_players()
        sage: M
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

    def play_test_match(self, verbose=True):
        r"""

        TESTS::

            sage: TestMatch().play_test_match()

        """
        self.deal_cards_to_table()

        rows = []
        while self._deck:
            self.deal_cards_to_players()
            for _ in range(3):
                for player in self.players:
                    row = [f"{self._tabletop}"]
                    card_to_play, cards_from_table = self.possible_plays(player)[0]
                    self.play_card(player, card_to_play, cards_from_table)
                    if cards_from_table:
                        row.append(f"{player} plays {card_to_play} to pick up {str(cards_from_table)[1:-1]}")
                    else:
                        row.append(f"{player} places {card_to_play} on table")
                    rows.append(row)

        row = [f"{self._tabletop}"]
        if self._tabletop:
            last_trick = Trick(None, tuple(self._tabletop), 0)
            self._tricks[self._last_player_to_pickup].append(last_trick)
            self._tabletop = []
            row.append(f"Cards on TableTop go to {self._last_player_to_pickup}")
        rows.append(row)

        print(table(rows))
        print()

        print(f"tally: {self.tally_tricks()}")

        print(f"score: {self.score_match()}")


def powerset(s):
    r"""
    Copied from the itertools page
    https://docs.python.org/3/library/itertools.html#itertools-recipes
    """
    from itertools import chain, combinations
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
