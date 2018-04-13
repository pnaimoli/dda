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
            for (i, card) in enumerate(board.cards[board.next_to_play][suit_index]):
                b = copy.deepcopy(board)
                del b.cards[b.next_to_play][suit_index][i]
                b.this_trick[b.next_to_play] = (card, suit_index)
                b.next_to_play = (b.next_to_play + 1) % 4
                if b.this_trick[b.next_to_play]:
                    # All 4 players have played.  Evaluate the round.
                    winner = cls.who_won(b)
                    b.tricks[winner % 2] += 1
                    b.this_trick = [None, None, None, None]
                    b.next_to_play = winner

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
        if hand_string:
            hand_string = hand_string.replace("10", "T")
            hands = hand_string.split()
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
            

#    @staticmethod
#    def from_str(hand_str):
#        pass
#
#    def __hash__():
#        return 0
#
#    def __equal__():
#        return False

argmax = lambda iterable, func: max(iterable, key=func)

def alpha_beta(state, game, total_tricks=13, depth=0, alpha=-1, beta=14):
#    print(" "*depth + str(state.__dict__))

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

if __name__ == "__main__":

#    b = Board()
#    b.cards = (([14], [], [2], [4], []), # South
#               ([], [], [14], [12, 13], [0]), # West
#               ([], [], [13], [11, 14], []), # North
#               ([], [], [10, 11, 12], [], [0])) # East
#    tricks = alpha_beta(b, Game, total_tricks=3)
#    print()
#    print("Final: ", tricks)

#    b = Board()
#    b.cards = (([14], [], [2], [4], []), # South
#               ([], [], [10, 11, 12], [], [0]), # West
#               ([], [], [13], [11, 14], []), # North
#               ([], [], [14], [12, 13], [0])) # East
#    tricks = alpha_beta(b, Game, total_tricks=3)
#    print()
#    print("Final: ", tricks)

#    b = Board()
#    b.cards = (([1,5,14], [], [2], [4]),
#               ([2,6], [], [14], [12, 13]),
#               ([3,7], [], [13], [11, 14]),
#               ([4,8], [], [10, 11, 12], []))
#    tricks = alpha_beta(b, Game, total_tricks=5)
#    print()
#    print("Final: ", tricks)

# https://www.larryco.com/bridge-learning-center/detail/524
    b = Board()
    b.cards = (([3,4,7,8,12], [8,11,13], [10,8], [7,11,13]),
               ([6,9,14], [2,7,10,14], [13,14], [4,8,9,10]),
               ([2,5,13], [3,4,6], [2,3,4,6,7], [2,5]),
               ([10,11], [5,9,12], [5,8,11,12], [3,6,12,14]))
    tricks = alpha_beta(b, Game, total_tricks=3)
    print()
    print("Final: ", tricks)
