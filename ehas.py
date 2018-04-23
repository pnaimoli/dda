from redeal.redeal import *
import subprocess
import src.libdda as libdda

predeal = {"S": SmartStack(balanced + semibalanced, hcp, range(12,18)),
          }

FOUND_SQUEEZE = 0
FAILED_SQUEEZE = 0

def initial(deal):
    # Output in pbn format
    redeal.Hand.set_str_style("pbn")
    redeal.Deal.set_str_style("pbn")
    print("[Event \"EHAS!\"]")

def accept(deal):
    if deal.dd_tricks("3NS") != 9:
        return False
    def suit_string(holding):
        return "".join([card.name for card in holding])
    def hand_string(hand):
        return ".".join([suit_string(holding) for holding in hand])
    hands = [deal.west, deal.north, deal.east, deal.south]
    board_string = " ".join([hand_string(hand) for hand in hands])

    dda = libdda.DDAnalyzer(board_string)
    dda.give_pitch(0)
    dda.give_pitch(2)

    if dda.analyze(4) != 4:
        global FOUND_SQUEEZE
        print()
        print("[Board \"{}\"]".format(FOUND_SQUEEZE + 1))
        print("[Dealer \"S\"]")
        print("[Vulnerable \"None\"]")
        FOUND_SQUEEZE += 1
        return True
    else:
        global FAILED_SQUEEZE
        FAILED_SQUEEZE += 1
        return False

def final(n_tries):
    print("% Found {} Tried {}".format(FOUND_SQUEEZE, FAILED_SQUEEZE))
