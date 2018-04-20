import unittest
import dda

class OneCardEndings(unittest.TestCase):
    def test_duh(self):
        ab = dda.AlphaBeta("2... 3... 4... 5...")
        tricks = ab.search()
        self.assertEqual(tricks, 0)
        ab = dda.AlphaBeta("2... 3... 5... 4...")
        tricks = ab.search()
        self.assertEqual(tricks, 1)
        ab = dda.AlphaBeta("2... .3.. .5.. .4..")
        tricks = ab.search()
        self.assertEqual(tricks, 1)
        ab = dda.AlphaBeta("2... .3.. .5.. .4..", trump=0)
        tricks = ab.search()
        self.assertEqual(tricks, 1)
        ab = dda.AlphaBeta("2... .3.. .4.. .5..", trump=1)
        tricks = ab.search()
        self.assertEqual(tricks, 0)
        ab = dda.AlphaBeta("2... .3.. .5.. .4..", trump=1)
        tricks = ab.search()
        self.assertEqual(tricks, 1)

class TwoCardEndings(unittest.TestCase):
    def test_one_suit(self):
        ab = dda.AlphaBeta("26... 37... 48... 59...")
        tricks = ab.search()
        self.assertEqual(tricks, 0)
        ab = dda.AlphaBeta("23... 45... 68... 79...")
        tricks = ab.search()
        self.assertEqual(tricks, 0)
        ab = dda.AlphaBeta("23... 68... 79... 45...")
        tricks = ab.search()
        self.assertEqual(tricks, 2)
        ab = dda.AlphaBeta("23... 49... 68... 57...")
        tricks = ab.search()
        self.assertEqual(tricks, 1)
        ab = dda.AlphaBeta("23... 47... 68... 59...")
        tricks = ab.search()
        self.assertEqual(tricks, 1)

    def test_two_suits(self):
        ab = dda.AlphaBeta("2.2.. 3.3.. 4.4.. 5.5..")
        tricks = ab.search()
        self.assertEqual(tricks, 0)
        ab = dda.AlphaBeta("2.2.. 3.3.. 5.4.. 4.5..")
        tricks = ab.search()
        self.assertEqual(tricks, 1)
        ab = dda.AlphaBeta("23... 4.3.. 6.4.. 5.5..", trump=1)
        tricks = ab.search()
        self.assertEqual(tricks, 1)
        ab = dda.AlphaBeta("24... 57... 68... .23..", trump=1)
        tricks = ab.search()
        self.assertEqual(tricks, 0)

class SqueezeEndings(unittest.TestCase):
    def test_simple_squeezes(self):
        # Positional simple squeeze
        ab = dda.AlphaBeta("2..2.2 ..7.45 ..6.36 ..345.")
        tricks = ab.search()
        self.assertEqual(tricks, 3)

        # Positional simple squeeze shouldn't work when the threats are offside
        ab = dda.AlphaBeta("2..2.2 ..345. ..6.36 ..7.45")
        tricks = ab.search()
        self.assertEqual(tricks, 2)

        # Positional simple squeeze shouldn't work when there's an extra loser
        ab = dda.AlphaBeta("2.2.2.2 .3.7.45 .4.6.36 .5.345.")
        tricks = ab.search()
        self.assertEqual(tricks, 2)

        # Automatic squeeze
        ab = dda.AlphaBeta("2..5.2 ..6.45 .2..36 ..234.")
        tricks = ab.search()
        self.assertEqual(tricks, 3)

        # Automatic squeezes work no matter which side has the guards
        ab = dda.AlphaBeta("2..5.2 ..234. .2..36 ..6.45")
        tricks = ab.search()
        self.assertEqual(tricks, 3)

    def test_fabpedigree(self):
        #https://fabpedigree.com/james/dbldum.htm
        ab = dda.AlphaBeta(".A2.K97.A T32.T.T.T AJ4..Q8.2 KQ.98.A2.")
        tricks = ab.search()
        self.assertEqual(tricks, 5)

    def test_guard_squeezes(self):
        #http://www.bridgeguys.com/squeeze/guard_squeeze.html
        ab = dda.AlphaBeta("A...KT3 .A.A.Q6 .K.K.A7 4...J54")
        tricks = ab.search()
        self.assertEqual(tricks, 4)

    def test_strip_and_duck(self):
        #https://www.lajollabridge.com/French/misc/Squeeze-Refresher.pdf
        ab = dda.AlphaBeta("AK.xx.xx. .KQJ.KQ.x x.ATx.AJ. xx.xx..xx")
        tricks = ab.search()
        self.assertEqual(tricks, 5)

    def test_three_suit_strip(self):
        # https://www.lajollabridge.com/French/misc/Squeeze-Refresher.pdf
        # Page 31, they are wrong

        # We should only be able to take our 2 aces
        ab = dda.AlphaBeta(".Tx.xx.Qx .Q.KQx.KJ .x.AJ.Axx ..Txx.Txx")
        tricks = ab.search()
        self.assertEqual(tricks, 2)

        # We can endplay W
        ab = dda.AlphaBeta("A.T.xx.Qx .Q.KQx.KJ x..AJ.Axx ..Txx.Txx")
        tricks = ab.search()
        self.assertEqual(tricks, 4)

        # They say this shouldn't work, but it does if you play a heart first
        ab = dda.AlphaBeta("A.Tx.xx.Qx .QJ.KQx.KJ x.x.AJ.Axx ..Txxx.Txx")
        tricks = ab.search()
        self.assertEqual(tricks, 4)

        # This should work too, as they promise
        ab = dda.AlphaBeta("A.Tx.xx.Ax .QJ.KQx.KJ x.x.AJ.Qxx ..Txxx.Txx")
        tricks = ab.search()
        self.assertEqual(tricks, 4)
