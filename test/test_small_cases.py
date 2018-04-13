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

    def test_2cards(self):
        pass
