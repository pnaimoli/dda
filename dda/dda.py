import array

HONOR_MAP = {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10}
NUM_PLAYERS = 4

class Board(object):
    """ The current state of a bridge game, which includes the number of
        tricks taken so far by each side, the trump suit, the cards played
        to this trick so far, and (of course) the remaining cards in each
        players' hands.
    """

    def __init__(self, hand_string=None, trump=None):
        self.cards = [array.array('B'),
                      array.array('B'),
                      array.array('B'),
                      array.array('B'),
                      array.array('B'), # The Sumit suit
                     ]
        self.this_trick = [None, None, None, None]
        self.current_suit = None
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
                        if card in HONOR_MAP:
                            rank = HONOR_MAP.get(card.upper())
                        else:
                            rank = int(card)
                        self.add_card(suit, rank, player)

            for suit in range(len(self.cards)):
                self.compress(suit)

            # Sanity checks to make sure every player starts with the same
            # number of cards
            cards_per_player = [0]*NUM_PLAYERS
            for card_array in self.cards:
                for owner in card_array:
                    cards_per_player[owner] += 1
            if len(set(cards_per_player)) != 1:
                raise Exception("Board string must contain the same "
                                "number of cards per hand")
            self.max_tricks = cards_per_player[0]

    def copy(self, board):
        for i in range(len(self.cards)):
            self.cards[i] = array.array('B', board.cards[i])
        self.this_trick = board.this_trick[:]
        self.current_suit = board.current_suit
        self.next_to_play = board.next_to_play
        self.tricks = board.tricks[:]
        self.trump = board.trump
        self.max_tricks = board.max_tricks

    def add_card(self, suit, rank, player):
        while len(self.cards[suit]) <= rank:
            self.cards[suit].append(NUM_PLAYERS)
        if self.cards[suit][rank] < NUM_PLAYERS:
            raise Exception("Somebody already owns the {} ({})".format(
                            rank, self.cards[suit]))
        self.cards[suit][rank] = player

    def compress(self, suit):
        i = 0
        while i < len(self.cards[suit]):
            if self.cards[suit][i] >= NUM_PLAYERS:
                self.cards[suit].pop(i)
            else:
                i += 1

    def utility(self, player):
        return self.tricks[player % 2]

    def who_won(self):
        suit_lead = self.this_trick[self.next_to_play][1]
        suit_priority = [0, 0, 0, 0, -1] # The Sumit suit can never win
        suit_priority[suit_lead] = 1
        if self.trump:
            suit_priority[self.trump] = 2
        new_list = [(suit_priority[suit], card) for (card, suit) in self.this_trick]
        return new_list.index(max(new_list))

    def sweep_round(self):
        # All 4 players have played.  Evaluate the round.
        winner = self.who_won()
        self.next_to_play = winner
        self.tricks[winner % 2] += 1

        # Compress the board downward
        for (card, suit) in sorted(self.this_trick, reverse=True):
            self.cards[suit].pop(card)

        self.this_trick = [None, None, None, None]
        self.current_suit = None

    def successors(self):
        # My next card can be anything if we're on lead or if we can't follow
        # suit
        suits = None
        if self.current_suit == None:
            # Lead anything but the Sumit suit!
            suits = range(4)
        else:
            for player in self.cards[self.current_suit]:
                if player == self.next_to_play:
                    suits = [self.current_suit]
                    break
            else:
                suits = range(5)

        for suit_index in suits:
            last_card_tried = None
            for (card, player) in enumerate(self.cards[suit_index]):
                if player != self.next_to_play:
                    continue
                # Make sure we haven't already played a card of equal rank
                if card - 1 == last_card_tried:
                    last_card_tried = card
                    continue
                else:
                    last_card_tried = card

                # Copy the board, remove this card, and advance our state
                b = Board()
                b.copy(self)
                b.cards[suit_index][card] = NUM_PLAYERS
                b.this_trick[b.next_to_play] = (card, suit_index)
                if b.current_suit == None:
                    b.current_suit = suit_index
                b.next_to_play = (b.next_to_play + 1) % 4

                if b.this_trick[b.next_to_play]:
                    b.sweep_round()

                yield ((card, suit_index), b)

def analyze_single_suit(card_array):
    """
    """
    moves = []
    while True:
        if not card_array:
            return moves

        top_card = card_array[-1]
        for (card, player) in reversed(list(enumerate(card_array))):
            if player % 2 == 1:
                opponents_top_card = card
                break
        else:
            opponents_top_card = -1

        if opponents_top_card >= top_card:
            return moves

        cards_per_player = [0]*NUM_PLAYERS
        for (card, player) in enumerate(card_array):
            cards_per_player[player] += 1
        smaller_hand = [0, 2][cards_per_player[0] > cards_per_player[2]]

#        # Check to see if there's a top card in the smaller hand,
#        # and if so play it!
#        if all_hands[smaller_hand]:
#            if all_hands[smaller_hand][-1] > opponents_top_card:
#                # TODO: should we overtake??
#                move = (all_hands[smaller_hand][-1],
#                        all_hands[2-smaller_hand][0])
#                if smaller_hand == 2:
#                    move = list(reversed(move))
#                moves.append(move)
#                for i in range(2):
#                    if all_hands[2*i+1]:
#                        all_hands[2*i+1].pop(0)
#                all_hands[smaller_hand].pop()
#                all_hands[2-smaller_hand].pop(0)
#                continue
#            elif all_hands[2-smaller_hand][-1] > opponents_top_card:
#                move = (all_hands[smaller_hand][0],
#                        all_hands[2-smaller_hand][-1])
#                if smaller_hand == 2:
#                    move = list(reversed(move))
#                moves.append(move)
#                for i in range(2):
#                    if all_hands[2*i+1]:
#                        all_hands[2*i+1].pop(0)
#                all_hands[smaller_hand].pop(0)
#                all_hands[2-smaller_hand].pop()
#                continue
#            else:
#                # else we have no top winners!
#                break
#        else:
#            # One hand is void! Any winners in the long hand?
#            if all_hands[2-smaller_hand][-1] > opponents_top_card:
#                move = (None, all_hands[2-smaller_hand][0])
#                if smaller_hand == 2:
#                    move = list(reversed(move))
#                moves.append(move)
#                for i in range(2):
#                    if all_hands[2*i+1]:
#                        all_hands[2*i+1].pop(0)
#                all_hands[2-smaller_hand].pop(0)
#                continue
#            # else we have no top winners!
#            break

    return moves

def quick_tricks_on_lead(board):
    # TODO: deal with trumps!
    if board.trump:
        return 0
    else:
        return 0

    # Make a copy of each card array because analyze_single_suit will
    # muck with the contents
    rotated_cards = []
    for card_array in board.cards[:4]:
        rotated_cards.append(array.array('B', card_array))
        for card in rotated_cards[-1]:
            card = card - board.next_to_play % 4

    quick_trick_moves = map(analyze_single_suit, rotated_cards)

    # For now, don't worry about entries
    quick_tricks = 0
    for moves in quick_trick_moves:
        for move in moves:
            if move[0] and move[1]:
                quick_tricks += 1
#    print("QT: " + str(quick_tricks) + ", " + str(board.__dict__))
    return quick_tricks


def alpha_beta(state, total_tricks=None, depth=0, alpha=0, beta=None):
#    print(" "*depth + "A:" + str(alpha) + ",B:" + str(beta) + " " + str(state.__dict__))

    # If total_tricks was no specified, play out the whole hand
    if not total_tricks:
        total_tricks = state.max_tricks

    if not beta:
        beta = total_tricks

    # If we've reached our terminal state, return the number of tricks
    # taken by the opening leader
    if depth == total_tricks*4:
        v = state.utility(0)
        return v

    tricks_remaining = state.utility(0) + state.utility(1)
    tricks_remaining = total_tricks - tricks_remaining

    # If we're on lead, compute the number of quick tricks our side can
    # take
    number_played_this_trick = sum([not not e for e in state.this_trick])
    quick_tricks = 0
    if number_played_this_trick == 0:
        quick_tricks = quick_tricks_on_lead(state)
        quick_tricks = min(tricks_remaining, quick_tricks)

    # If the leading team is playing, we're trying to maximize the
    # number of tricks
    if state.next_to_play % 2 == 0:
        # If the remaining tricks are all quick, we're done!
        if quick_tricks == tricks_remaining:
            return state.utility(0) + quick_tricks

        # Update alpha according to the number of quick tricks we are
        # known to possess.
        alpha = max(alpha, state.utility(0) + quick_tricks)

        # Update beta according to the number of tricks the other side
        # has already taken
        # TODO: does this line do anything?
        beta = min(beta, total_tricks - state.utility(1))

        if alpha == beta:
            return alpha
        if alpha > beta:
            # I don't remember why this could happen, but it shouldn't
            # matter if we return alpha or beta, right?
            return beta

        v = alpha
        for (a, s) in state.successors():
            v = max(v, alpha_beta(s, total_tricks, depth+1, alpha, beta))
            alpha = max(alpha, v)
            if alpha == beta:
                return alpha
            if alpha > beta:
                # I don't remember why this could happen, but it shouldn't
                # matter if we return alpha or beta, right?
                return beta
        return v
    else:
        # If the remaining tricks are all quick, we're done!
        if quick_tricks == tricks_remaining:
            return state.utility(0)

        # Update beta according to the number of quick tricks we are
        # known to possess.
        beta = min(beta, state.utility(0) + tricks_remaining - quick_tricks)

        # Update alpha according to the number of tricks the other side
        # has already taken
        # TODO: does this line do anything?
        alpha = max(alpha, state.utility(0))

        if alpha == beta:
            return alpha
        if alpha > beta:
            # I don't remember why this could happen, but it shouldn't
            # matter if we return alpha or beta, right?
            return beta

        v = beta
        for (a, s) in state.successors():
            v = min(v, alpha_beta(s, total_tricks, depth+1, alpha, beta))
            beta = min(beta, v)
            if alpha == beta:
                return alpha
            if alpha > beta:
                # I don't remember why this could happen, but it shouldn't
                # matter if we return alpha or beta, right?
                return beta
        return v
