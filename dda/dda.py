import copy

import signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

class Game(object):
    @classmethod
    def to_move(cls, board):
        return board.next_to_play

    @classmethod
    def terminal_test(cls, board):
        return board.tricks[0] + board.tricks[1] == 13

    @classmethod
    def utility(cls, board, player):
        return board.tricks[player % 2]

    @classmethod
    def current_suit(cls, board):
        for i in range(3):
            next_card = board.this_trick[(board.next_to_play + i + 1) % 4]
            if next_card:
                return next_card[1]
        return None

    @classmethod
    def who_won(cls, board):
        suit_lead = board.this_trick[board.next_to_play][1]
        suit_priority = [0, 0, 0, 0, -1] # The Sumit suit can never win
        suit_priority[suit_lead] = 1
        if board.trump:
            suit_priority[board.trump] = 2
        new_list = [(suit_priority[suit], card) for (card, suit) in board.this_trick]
        return new_list.index(max(new_list))

    @classmethod
    def successors(cls, board):
        # My next card can be anything if we're on lead or if we can't follow
        # suit
        suits = None
        current_suit = cls.current_suit(board)
        if current_suit == None:
            suits = range(4)
        elif board.cards[board.next_to_play][current_suit]:
            suits = [current_suit]
        else:
            suits = range(4)
            # suits = range(5) Uncomment this when we're ready to introduce the Sumit suit

        for suit_index in suits:
            last_card_played = None
            for (i, card) in enumerate(board.cards[board.next_to_play][suit_index]):
                # Make sure we haven't already played a card of equal rank
                if card - 1 == last_card_played:
                    last_card_played = card
                    continue
                else:
                    last_card_played = card

                # Copy the board, remove this card, and advance our state
                b = copy.deepcopy(board)
                del b.cards[b.next_to_play][suit_index][i]
                b.this_trick[b.next_to_play] = (card, suit_index)
                b.next_to_play = (b.next_to_play + 1) % 4

                if b.this_trick[b.next_to_play]:
                    # All 4 players have played.  Evaluate the round.
                    winner = cls.who_won(b)
                    b.next_to_play = winner
                    b.tricks[winner % 2] += 1

                    # Compress the board downward
                    cards_played = sorted(b.this_trick, reverse=True)
                    for (card_played, suit_played) in cards_played:
                        for player_holdings in b.cards:
                            suit_holding = player_holdings[suit_played]
                            for (i, remaining_card) in enumerate(suit_holding):
                                if remaining_card > card_played:
                                    suit_holding[i] -= 1
                    b.this_trick = [None, None, None, None]

                yield ((card, suit_index), b)
            

class Board(object):
    """ The current state of a bridge game, which includes the number of
        tricks taken so far by each side, the trump suit, the cards played
        to this trick so far, and (of course) the remaining cards in each
        players' hands.
    """

    def __init__(self, hand_string=None, trump=None):
        self.cards = [[[], [], [], [], []],
                      [[], [], [], [], []],
                      [[], [], [], [], []],
                      [[], [], [], [], []]]
        self.this_trick = [None, None, None, None]
        self.next_to_play = 0
        self.tricks = [0, 0]
        self.trump = trump
        self.max_tricks = 0
        if hand_string:
            hand_string = hand_string.replace("10", "T")
            hands = hand_string.strip().split()
            if len(hands) != 4:
                raise Exception("Board string must contain 4 hands separated "
                                "by whitespace")
            for (player, hand) in enumerate(hands):
                holdings = hand.split(".")
                if len(holdings) != 4:
                    raise Exception("Each hand must contain 4 suits separated "
                                    "by .'s")
                for (suit, holding) in enumerate(holdings):
                    for card in holding:
                        if card == "A":
                            self.cards[player][suit].append(14)
                        elif card == "K":
                            self.cards[player][suit].append(13)
                        elif card == "Q":
                            self.cards[player][suit].append(12)
                        elif card == "J":
                            self.cards[player][suit].append(11)
                        elif card == "T":
                            self.cards[player][suit].append(10)
                        else:
                            self.cards[player][suit].append(int(card))
                for l in self.cards[player]:
                    l.sort()

            # Sanity checks to make sure everything's well formed
            number_of_cards = []
            for hand in self.cards:
                number_of_cards.append(sum([len(h) for h in hand]))
            if len(set(number_of_cards)) != 1:
                raise Exception("Board string must contain the same "
                                "number of cards per hand")
            self.max_tricks = number_of_cards[0]

            # No duplicates
            for suit_holdings in zip(*[p for p in self.cards]):
                flattened = sum(suit_holdings, [])
                if len(flattened) != len(set(flattened)):
                    raise Exception("Board string must not contain duplicate "
                                    "cards", flattened)

def alpha_beta(state, game, total_tricks=None, depth=0, alpha=-1, beta=14):
    print(" "*depth + str(state.__dict__))

    if not total_tricks:
        total_tricks = state.max_tricks

    if depth == total_tricks*4 or game.terminal_test(state):
        v = game.utility(state, 0)
        return v


    # If N/S is playing, we're trying to maximize the number of tricks
    first_move_tested = False
    if state.next_to_play % 2 == 0:
        v = 0
        for (a, s) in game.successors(state):
            # If the defense has already taken too many tricks,
            # this line of play is already inferior
            upper_bound = total_tricks - game.utility(state, 1)
            if upper_bound < alpha:
                continue
            
            v = max(v, alpha_beta(s, game, total_tricks, depth+1, alpha, beta))
            alpha = max(alpha, v)
            if beta <= alpha:
                break
        return v
    else:
        v = 13
        for (a, s) in game.successors(state):
            # If the offense has already taken too many tricks,
            # this line of play is already inferior
            lower_bound = game.utility(state, 0)
            if lower_bound > beta:
                continue

            v = min(v, alpha_beta(s, game, total_tricks, depth+1, alpha, beta))
            beta = min(beta, v)
            if beta <= alpha:
                break
        return v
