import copy

NUM_SUITS = 5
HONOR_MAP = {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10}
HONOR_MAP.update(dict([reversed(i) for i in HONOR_MAP.items()]))
NUM_PLAYERS = 4

class Holding(object):
    BITS_PER_SUIT = 15
    def __init__(self):
        self.cards = 0 # "AKQJT98765432?? x 5"

    def __repr__(self):
        def per_suit(suit):
            s = ""
            for rank in range(self.BITS_PER_SUIT):
                if self.contains(suit, rank):
                    if rank >= 10:
                        s += HONOR_MAP[rank]
                    else:
                        s += str(rank)
            return s
        return ".".join(map(per_suit, range(NUM_SUITS)))

    def smallest(self, suit):
        tmp = (self.cards >> (suit * self.BITS_PER_SUIT))
        if not tmp:
            return None
        elif tmp & 4:
            return 2
        elif tmp & 8:
            return 3
        elif tmp & 16:
            return 4
        elif tmp & 32:
            return 5
        elif tmp & 64:
            return 6
        elif tmp & 128:
            return 7
        elif tmp & 256:
            return 8
        elif tmp & 512:
            return 9
        elif tmp & 1024:
            return 10
        elif tmp & 2048:
            return 11
        elif tmp & 4096:
            return 12
        elif tmp & 8192:
            return 13
        elif tmp & 16384:
            return 14


    def highest(self, suit):
        card_mask = (1 << 14) << (suit * self.BITS_PER_SUIT)
        for i in range(14, 1, -1):
            if self.cards & card_mask:
                return i
            card_mask >> 1
        return None

    def empty(self, suit):
        suit_bits = ((1 << self.BITS_PER_SUIT) - 1) << self.BITS_PER_SUIT * suit
        return self.cards & suit_bits == 0

    def length(self, suit=None):
        if suit:
            tmp = self.cards >> (suit * self.BITS_PER_SUIT)
            tmp &= (1 << self.BITS_PER_SUIT) - 1
        else:
            tmp = self.cards

        num = 0
        while tmp:
            if tmp & 1:
                num += 1
            tmp = tmp >> 1

        return num

    def contains(self, suit, rank):
        card_mask = (1 << rank) << (suit * self.BITS_PER_SUIT)
        return self.cards & card_mask

    def add_card(self, suit, rank):
        card_mask = (1 << rank) << (suit * self.BITS_PER_SUIT)
        if self.cards & card_mask:
            raise Exception("Suit #{} already contains the {}".format(
                            suit, rank))
        self.cards += card_mask

    def remove_card(self, suit, rank):
        card_mask = (1 << rank) << (suit * self.BITS_PER_SUIT)
        if not self.cards & card_mask:
            raise Exception("Suit #{} does not contain the {}".format(
                            suit, rank))
        self.cards -= card_mask
        pass

    def remove_suit(self, suit):
        all_bits = (1 << self.BITS_PER_SUIT * 5) - 1
        suit_bits = ((1 << self.BITS_PER_SUIT) - 1) << self.BITS_PER_SUIT * suit
        self.cards &= all_bits - suit_bits

    def keep_only_suit(self, suit):
        suit_bits = ((1 << self.BITS_PER_SUIT) - 1) << self.BITS_PER_SUIT * suit
        self.cards &= suit_bits

class TrickState(object):
    def __init__(self):
        self.holdings = [Holding() for _ in range(NUM_PLAYERS)]
        self.legal_moves = [Holding() for _ in range(NUM_PLAYERS)]
        self.played = [None] * NUM_PLAYERS
        self.current_suit = None
        self.next_to_play = 0
        self.tricks_won = 0
        self.opp_tricks_won = 0

    def compute_legal_moves(self):
        lm = self.legal_moves[self.next_to_play]
        lm.cards = self.holdings[self.next_to_play].cards
        if self.current_suit == None:
            # Cannot lead the Sumit suit!
            lm.remove_suit(4)
        elif not lm.empty(self.current_suit):
            lm.keep_only_suit(self.current_suit)

class AlphaBeta(object):
    def __init__(self, hand_string, trump=None):
        self.initial_state = TrickState()
        self.trump = trump

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
                    if card.upper() == 'X':
                        all_holdings = Holding()
                        for p in range(NUM_PLAYERS):
                            all_holdings.cards |= self.initial_state.holdings[p].cards
                        for rank in range(2, 15):
                            if not all_holdings.contains(suit, rank):
                                self.initial_state.holdings[player].add_card(suit, rank)
                                break
                        else:
                            raise Exception("WTF")
                        continue
                    if card in HONOR_MAP:
                        rank = HONOR_MAP.get(card.upper())
                    else:
                        rank = int(card)
                    self.initial_state.holdings[player].add_card(suit, rank)

        # Sanity checks to make sure every player starts with the same
        # number of cards
        cards_per_player = [h.length() for h in self.initial_state.holdings]
        if len(set(cards_per_player)) != 1:
            raise Exception("Board string must contain the same "
                            "number of cards per hand")

    def search(self, total_tricks=None):
        if total_tricks == None:
            total_tricks = min([h.length() for h in self.initial_state.holdings])
        self.trick_states = [copy.deepcopy(self.initial_state)
                             for _ in range(total_tricks + 1)]
        return self.alpha_beta(0, total_tricks, 0, total_tricks*4)

    def alpha_beta(self, alpha, beta, depth, max_depth):
        tsx = int(depth / 4) # Trick State Index
        ts = self.trick_states[tsx]
#        print(" "*depth + "A:" + str(alpha) + ",B:" + str(beta) + " ", ts.__dict__)

        # Terminal state!
        if depth == max_depth:
            return ts.tricks_won

        # If the leading team is playing, we're trying to maximize the
        # number of tricks
        if ts.next_to_play % 2 == 0:
            ts.compute_legal_moves()
            v = alpha
            for suit in range(NUM_SUITS):
                rank = ts.legal_moves[ts.next_to_play].smallest(suit)
                while rank:
                    self.play_card(depth, suit, rank)
                    v = self.alpha_beta(alpha, beta, depth+1, max_depth)
                    self.undo_play(depth, suit, rank)
                    alpha = max(alpha, v)
                    if alpha == beta:
                        return alpha
                    if alpha > beta:
                        return beta
                    rank = ts.legal_moves[ts.next_to_play].smallest(suit)
            return alpha
        else:
            ts.compute_legal_moves()
            v = beta
            for suit in range(NUM_SUITS):
                rank = ts.legal_moves[ts.next_to_play].smallest(suit)
                while rank:
                    self.play_card(depth, suit, rank)
                    v = self.alpha_beta(alpha, beta, depth+1, max_depth)
                    self.undo_play(depth, suit, rank)
                    beta = min(beta, v)
                    if alpha == beta:
                        return alpha
                    if alpha > beta:
                        return beta
                    rank = ts.legal_moves[ts.next_to_play].smallest(suit)
            return beta

    def play_card(self, depth, suit, rank):
        tsx = int(depth / 4) # Trick State Index
        ts = self.trick_states[tsx]

        ts.legal_moves[ts.next_to_play].remove_card(suit, rank)
        ts.holdings[ts.next_to_play].remove_card(suit, rank)
        ts.played[ts.next_to_play] = (rank, suit)
        if ts.current_suit == None:
            ts.current_suit = suit
        ts.next_to_play = (ts.next_to_play + 1) % 4

        if depth % 4 == 3:
            # Last trick of the round, see who won!
            suit_priority = [0, 0, 0, 0, -1] # The Sumit suit can never win
            suit_priority[ts.current_suit] = 1
            if self.trump:
                suit_priority[self.trump] = 2
            new_list = [(suit_priority[suit], card) for
                        (card, suit) in ts.played]
            winner = new_list.index(max(new_list))

            next_ts = self.trick_states[tsx+1]
            for i in range(NUM_PLAYERS):
                next_ts.holdings[i].cards = ts.holdings[i].cards
                next_ts.legal_moves[i].cards = ts.legal_moves[i].cards
                next_ts.played[i] = None
            next_ts.current_suit = None

            next_ts.next_to_play = winner
            if winner % 2 == 0:
                next_ts.tricks_won = ts.tricks_won + 1
                next_ts.opp_tricks_won = ts.opp_tricks_won
            else:
                next_ts.tricks_won = ts.tricks_won
                next_ts.opp_tricks_won = ts.opp_tricks_won + 1

    def undo_play(self, depth, suit, rank):
        tsx = int(depth / 4) # Trick State Index
        ts = self.trick_states[tsx]

        ts.next_to_play = (ts.next_to_play - 1) % 4
        ts.holdings[ts.next_to_play].add_card(suit, rank)
        ts.played[ts.next_to_play] = None
        if depth % 4 == 0:
            ts.current_suit = None
