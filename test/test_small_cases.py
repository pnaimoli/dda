import unittest
import dda

class OneCardEndings(unittest.TestCase):
    def test_duh(self):
        b = dda.Board("2... 3... 4... 5...")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 0)
        b = dda.Board("2... 3... 5... 4...")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 1)
        b = dda.Board("2... .3.. .5.. .4..")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 1)
        b = dda.Board("2... .3.. .5.. .4..", trump=0)
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 1)
        b = dda.Board("2... .3.. .4.. .5..", trump=1)
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 0)
        b = dda.Board("2... .3.. .5.. .4..", trump=1)
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 1)

class TwoCardEndings(unittest.TestCase):
    def test_one_suit(self):
        b = dda.Board("26... 37... 48... 59...")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 0)
        b = dda.Board("23... 45... 68... 79...")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 0)
        b = dda.Board("23... 68... 79... 45...")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 2)
        b = dda.Board("23... 49... 68... 57...")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 1)
        b = dda.Board("23... 47... 68... 59...")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 1)

    def test_two_suits(self):
        b = dda.Board("2.2.. 3.3.. 4.4.. 5.5..")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 0)
        b = dda.Board("2.2.. 3.3.. 5.4.. 4.5..")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 1)
        b = dda.Board("23... 4.3.. 6.4.. 5.5..", trump=1)
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 1)
        b = dda.Board("24... 57... 68... .23..", trump=1)
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 0)

class SqueezeEndings(unittest.TestCase):
    def test_simple_squeezes(self):
        # Positional simple squeeze
        b = dda.Board("2..2.2 ..7.45 ..6.36 ..345.")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 3)

        # Positional simple squeeze shouldn't work when the threats are offside
        b = dda.Board("2..2.2 ..345. ..6.36 ..7.45")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 2)

        # Positional simple squeeze shouldn't work when there's an extra loser
        b = dda.Board("2.2.2.2 .3.7.45 .4.6.36 .5.345.")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 2)

        # Automatic squeeze
        b = dda.Board("2..5.2 ..6.45 .2..36 ..234.")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 3)

        # Automatic squeezes work no matter which side has the guards
        b = dda.Board("2..5.2 ..234. .2..36 ..6.45")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 3)

    def test_fabpedigree(self):
        #https://fabpedigree.com/james/dbldum.htm
        b = dda.Board(".A2.K97.A T32.T.T.T AJ4..Q8.2 KQ.98.A2.")
        tricks = dda.alpha_beta(b)
        self.assertEqual(tricks, 5)
