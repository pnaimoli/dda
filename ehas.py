from redeal.redeal import *
import subprocess
import src.libdda as libdda

predeal = {"S": SmartStack(balanced + semibalanced, hcp, range(12,18)),
          }

FOUND_SQUEEZE = 0
FAILED_SQUEEZE = 0

def opening_lead(hand):
    # Compute longest/strongest
    longest_length = len(max(hand, key=len))
    longest_suits = [(h, s) for (h, s) in zip(hand, redeal.Suit) if len(h) == longest_length]
    most_hcp_suit = max(longest_suits, key=lambda x: x[0].hcp)
    original_card = redeal.Card(suit=most_hcp_suit[1], rank = sorted(most_hcp_suit[0], reverse=True)[3])

    # Double dummy solver likes to only compute the results for the largest of adjacent moves
    card = original_card
    while True:
        if card.rank == Rank["A"]:
            break
        new_rank = Rank(card.rank.value+1)
        if new_rank in most_hcp_suit[0]:
            card = Card(suit=card.suit, rank=new_rank)
        else:
            break

    return (original_card, card)

def initial(deal):
    # Output in pbn format
    redeal.Hand.set_str_style("pbn")
    redeal.Deal.set_str_style("pbn")
    print("[Event \"EHAS!\"]")

def accept(deal):
    # Filter out zany distributions
    if deal.south.hcp + deal.north.hcp < 23:
        return False
    if len(deal.south.spades) + len(deal.north.spades) >= 8:
        return False
    if len(deal.south.hearts) + len(deal.north.hearts) >= 8:
        return False
    if not (balanced + semibalanced)(deal.north):
        return False

    # Take only results where N/S make exactly 3NT with the given
    # opening lead
    lead = opening_lead(deal.west)
    dd_results = deal.dd_all_tricks("N", "W")[lead[1]]
    if dd_results != 4:
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
    dda.play_card(lead[0].suit.value, lead[0].rank.value)
    dda.give_pitch(0)
    dda.give_pitch(2)

    if dda.can_make(5):
        global FOUND_SQUEEZE
        FOUND_SQUEEZE += 1
        return True
    else:
        global FAILED_SQUEEZE
        FAILED_SQUEEZE += 1
        return False

def do(deal):
    lead = opening_lead(deal.west)
    print("[Board \"{}\"]".format(FOUND_SQUEEZE))
    print("[Dealer \"S\"]")
    print("[Vulnerable \"None\"]")
    print(format(deal, ""))
    print("[Declarer \"S\"]")
    print("[Contract \"3NT\"]")
    print("[Auction \"S\"]")
    print("1NT	Pass	3NT	AP")
    print("[Play \"W\"]")
    print(lead[0].suit.name + str(lead[0].rank.value) + "	+	-	-")
    print()

def final(n_tries):
    print("% Found: {} Failed: {}".format(FOUND_SQUEEZE, FAILED_SQUEEZE))
