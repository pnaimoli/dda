from redeal.redeal import *
import subprocess
import src.libdda as libdda

OUTPUT_TYPE = "lin"

NUM_FOUND = 0
NUM_FAILED = 0

predeal = {"S": SmartStack(balanced + semibalanced, hcp, range(12,18)),
          }

def convert_to_dd_card(hand, original_card):
    """ Given a holding and a card, return the highest adjacent card.
        This is needed because the double dummy results are all
        given in terms of highest equivalent cards.
    """
    # Double dummy solver likes to only compute the results for the largest of adjacent moves
    card = original_card
    holding = hand[card.suit]
    while True:
        if card.rank == Rank["A"]:
            return card
        new_rank = Rank(card.rank.value+1)
        if new_rank in holding:
            card = redeal.Card(suit=card.suit, rank=new_rank)
        else:
            return card

def slam_lead(hand):
    """ Tries to lead using the following priorities:
        1) Top of the strongest 3-card sequence
        2) 4th best from the longest 0 point holding
        2) 3th/5th best from the longest 1 point holding
        3) 4th best from longest and strongest (lazy)
        Returns a pair of Cards.  The first is the systemic lead, the
        second is the adjacent card double dummy solver will recognize.
    """
    def has_top_sequence(holding):
        sorted_h = sorted(holding, reverse=True)
        if len(sorted_h) < 3:
            return False
        return sorted_h[0].value == sorted_h[1].value + 1 and \
               sorted_h[1].value == sorted_h[2].value + 1

    # Do I have a sequence?
    sequence_suits = list(filter(lambda x: has_top_sequence(x[0]), zip(hand, redeal.Suit)))
    if sequence_suits:
        most_hcp_suit = max(sequence_suits, key=lambda x: x[0].hcp)
        if most_hcp_suit[0].hcp > 0:
            return redeal.Card(suit=most_hcp_suit[1], rank=sorted(most_hcp_suit[0], reverse=True)[0])
        longest_suit = max(sequence_suits, key=lambda x: len(x[0]))
        return redeal.Card(suit=longest_suit[1], rank=sorted(longest_suit[0], reverse=True)[0])

    # Do I have a 0 point suit?
    zero_hcp_suits = [(sorted(h, reverse=True), s) for (h, s) in zip(hand, redeal.Suit) if h.hcp == 0 and len(h) > 2]
    if zero_hcp_suits:
        longest_suit = max(zero_hcp_suits, key=lambda x: len(x[0]))
        nth_best = min(3, len(longest_suit[0]) - 1)
        if nth_best == 1:
            nth_best = 0
        return redeal.Card(suit=longest_suit[1], rank=list(longest_suit[0])[nth_best])

    # Do I have a 1 point suit?
    one_hcp_suits = [(sorted(h, reverse=True), s) for (h, s) in zip(hand, redeal.Suit) if h.hcp == 1]
    if one_hcp_suits:
        five_card_suits = [s for s in one_hcp_suits if len(s) >= 5]
        if five_card_suits:
            return redeal.Card(suit=five_card_suits[0][1], rank=list(five_card_suits[0][0])[3])
        three_card_suits = [s for s in one_hcp_suits if len(s) == 3]
        if three_card_suits:
            return redeal.Card(suit=three_card_suits[0][1], rank=list(three_card_suits[0][0])[3])
        four_card_suits = [s for s in one_hcp_suits if len(s) == 3]
        if four_card_suits:
            return redeal.Card(suit=four_card_suits[0][1], rank=list(four_card_suits[0][0])[3])

    return fourth_best_ls(hand)

def fourth_best_ls(hand):
    """ Selects the 4th best card from our longest and strongest suit.
        Returns a pair of Cards.  The first is the systemic lead, the
        second is the adjacent card double dummy solver will recognize.
    """
    # Compute longest/strongest
    longest_length = len(max(hand, key=len))
    longest_suits = [(h, s) for (h, s) in zip(hand, redeal.Suit) if len(h) == longest_length]
    most_hcp_suit = max(longest_suits, key=lambda x: x[0].hcp)
    return redeal.Card(suit=most_hcp_suit[1], rank=sorted(most_hcp_suit[0], reverse=True)[3])

def initial(deal):
    if OUTPUT_TYPE == "pbn":
        print("[Event \"EHAS!\"]")

def accept(deal):
    # Filter out zany distributions
    if deal.south.hcp + deal.north.hcp < 30:
        return False
    if len(deal.south.spades) + len(deal.north.spades) >= 8:
        return False
    if len(deal.south.hearts) + len(deal.north.hearts) >= 8:
        return False
    if not (balanced + semibalanced)(deal.north):
        return False

    TARGET_TRICKS = 12

    # Take only results where N/S make exactly 3NT with the given
    # opening lead
    lead = slam_lead(deal.west)
    dd_lead = convert_to_dd_card(deal.west, lead)
    dd_results = deal.dd_all_tricks("N", "W")
    if dd_results[dd_lead] != 13 - TARGET_TRICKS:
        return False

    # Convert to the hand string format dda accepts
    def suit_string(holding):
        return "".join([card.name for card in holding])
    def hand_string(hand):
        return ".".join([suit_string(holding) for holding in hand])
    hands = [deal.west, deal.north, deal.east, deal.south]
    board_string = " ".join([hand_string(hand) for hand in hands])

    # Run dda!
    # Can we defeat the contract with some extra cards?
    dda = libdda.DDAnalyzer(board_string)
    dda.play_card(lead.suit.value, lead.rank.value)
    dda.give_pitch(0)
    dda.give_pitch(2)

    if dda.can_make(13 - TARGET_TRICKS + 1):
        global NUM_FOUND
        NUM_FOUND += 1
        return True
    else:
        global NUM_FAILED
        NUM_FAILED += 1
        return False

def do(deal):
    lead = slam_lead(deal.west)
    if OUTPUT_TYPE == "pbn":
        redeal.Hand.set_str_style("pbn")
        redeal.Deal.set_str_style("pbn")
        print("[Board \"{}\"]".format(NUM_FOUND))
        print("[Dealer \"S\"]")
        print("[Vulnerable \"None\"]")
        print(format(deal, ""))
        print("[Declarer \"S\"]")
        print("[Contract \"3NT\"]")
        print("[Auction \"S\"]")
        print("1NT	Pass	3NT	AP")
        print("[Play \"W\"]")
        print(lead.suit.name + str(lead.rank) + "	+	-	-")
        print()
    elif OUTPUT_TYPE == "lin":
        redeal.Hand.set_str_style("short")
        redeal.Deal.set_str_style("short")
        redeal.Suit.__str__ = lambda self: self.name
        Deal.set_print_only((redeal.Seat.S, redeal.Seat.W, redeal.Seat.N))
        hand_string = format(deal, "").replace(" ", ",")
        print("qx|o1|md|1{}|rh||ah|Board {}|sv|0|"
              "mb|6N|mb|p|mb|p|mb|p|pg||pc|{}|".format(
              hand_string, NUM_FOUND, lead.suit.name + str(lead.rank)))

def final(n_tries):
    print("% Found: {} Failed: {}".format(NUM_FOUND, NUM_FAILED))
    print()
