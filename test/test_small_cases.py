#!/usr/local/bin/python3
import unittest
import dda

class OneCardEndings(unittest.TestCase):
    def test_duh(self):
        b = dda.Board("2... 3... 4... 5...")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=1)
        self.assertEqual(tricks, 0)
        b = dda.Board("2... 3... 5... 4...")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=1)
        self.assertEqual(tricks, 1)
        b = dda.Board("2... .3.. .5.. .4..")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=1)
        self.assertEqual(tricks, 1)
        b = dda.Board("2... .3.. .5.. .4..", trump=0)
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=1)
        self.assertEqual(tricks, 1)
        b = dda.Board("2... .3.. .4.. .5..", trump=1)
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=1)
        self.assertEqual(tricks, 0)
        b = dda.Board("2... .3.. .5.. .4..", trump=1)
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=1)
        self.assertEqual(tricks, 1)

    def test_two_cards_one_suit(self):
        b = dda.Board("26... 37... 48... 59...")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=2)
        self.assertEqual(tricks, 0)
        b = dda.Board("23... 45... 68... 79...")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=2)
        self.assertEqual(tricks, 0)
        b = dda.Board("23... 68... 79... 45...")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=2)
        self.assertEqual(tricks, 2)
        b = dda.Board("23... 49... 68... 57...")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=2)
        self.assertEqual(tricks, 1)
        b = dda.Board("23... 47... 68... 59...")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=2)
        self.assertEqual(tricks, 1)

    def test_two_cards_two_suits(self):
        b = dda.Board("2.2.. 3.3.. 4.4.. 5.5..")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=2)
        self.assertEqual(tricks, 0)
        b = dda.Board("2.2.. 3.3.. 5.4.. 4.5..")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=2)
        self.assertEqual(tricks, 1)
        b = dda.Board("23... 4.3.. 6.4.. 5.5..", trump=1)
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=2)
        self.assertEqual(tricks, 1)
        b = dda.Board("24... 33... 45... .23..", trump=1)
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=2)
        self.assertEqual(tricks, 0)

    def test_simple_squeezes(self):
        # Positional simple squeeze
        b = dda.Board("2..2.4 ..6.45 ..5.36 ..234.")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=3)
        self.assertEqual(tricks, 3)

        # Positional simple squeeze shouldn't work when the threats are offside
        b = dda.Board("2..2.4 ..234. ..5.36 ..6.45")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=3)
        self.assertEqual(tricks, 2)

        # Positional simple squeeze shouldn't work when there's an extra loser
        b = dda.Board("2.2.2.4 .3.6.45 .4.5.36 .5.234.")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=4)
        self.assertEqual(tricks, 2)

        # Automatic squeeze
        b = dda.Board("2..5.4 ..6.45 .2..36 ..234.")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=3)
        self.assertEqual(tricks, 3)

        # Automatic squeezes work no matter which side has the guards
        b = dda.Board("2..5.4 ..234. .2..36 ..6.45")
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=3)
        self.assertEqual(tricks, 3)
