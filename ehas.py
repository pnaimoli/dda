from redeal import *
import subprocess
import src.libdda as libdda

predeal = {"S": SmartStack(balanced + semibalanced, hcp, range(12,18)),
          }

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
        return True
    else:
        print("Failed")
        return False
