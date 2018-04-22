import unittest
import src.libdda as libdda

class OneCardEndings(unittest.TestCase):
    def test_duh(self):
        dda = libdda.DDAnalyzer("2... 3... 4... 5...")
        tricks = dda.analyze()
        self.assertEqual(tricks, 0)
        dda = libdda.DDAnalyzer("2... 3... 5... 4...")
        tricks = dda.analyze()
        self.assertEqual(tricks, 1)
        dda = libdda.DDAnalyzer("2... .3.. .5.. .4..")
        tricks = dda.analyze()
        self.assertEqual(tricks, 1)
        dda = libdda.DDAnalyzer("2... .3.. .5.. .4..", 0)
        tricks = dda.analyze()
        self.assertEqual(tricks, 1)
        dda = libdda.DDAnalyzer("2... .3.. .4.. .5..", 1)
        tricks = dda.analyze()
        self.assertEqual(tricks, 0)
        dda = libdda.DDAnalyzer("2... .3.. .5.. .4..", 1)
        tricks = dda.analyze()
        self.assertEqual(tricks, 1)

class TwoCardEndings(unittest.TestCase):
    def test_one_suit(self):
        dda = libdda.DDAnalyzer("26... 37... 48... 59...")
        tricks = dda.analyze()
        self.assertEqual(tricks, 0)
        dda = libdda.DDAnalyzer("23... 45... 68... 79...")
        tricks = dda.analyze()
        self.assertEqual(tricks, 0)
        dda = libdda.DDAnalyzer("23... 68... 79... 45...")
        tricks = dda.analyze()
        self.assertEqual(tricks, 2)
        dda = libdda.DDAnalyzer("23... 49... 68... 57...")
        tricks = dda.analyze()
        self.assertEqual(tricks, 1)
        dda = libdda.DDAnalyzer("23... 47... 68... 59...")
        tricks = dda.analyze()
        self.assertEqual(tricks, 1)

    def test_two_suits(self):
        dda = libdda.DDAnalyzer("2.2.. 3.3.. 4.4.. 5.5..")
        tricks = dda.analyze()
        self.assertEqual(tricks, 0)
        dda = libdda.DDAnalyzer("2.2.. 3.3.. 5.4.. 4.5..")
        tricks = dda.analyze()
        self.assertEqual(tricks, 1)
        dda = libdda.DDAnalyzer("23... 4.3.. 6.4.. 5.5..", 1)
        tricks = dda.analyze()
        self.assertEqual(tricks, 1)
        dda = libdda.DDAnalyzer("24... 57... 68... .23..", 1)
        tricks = dda.analyze()
        self.assertEqual(tricks, 0)

class SqueezeEndings(unittest.TestCase):
    def test_simple_squeezes(self):
        # Positional simple squeeze
        dda = libdda.DDAnalyzer("2..2.2 ..7.45 ..6.36 ..345.")
        tricks = dda.analyze()
        self.assertEqual(tricks, 3)

        # Positional simple squeeze shouldn't work when the threats are offside
        dda = libdda.DDAnalyzer("2..2.2 ..345. ..6.36 ..7.45")
        tricks = dda.analyze()
        self.assertEqual(tricks, 2)

        # Positional simple squeeze shouldn't work when there's an extra loser
        dda = libdda.DDAnalyzer("2.2.2.2 .3.A.KQ .4.K.JA .5.345.")
        tricks = dda.analyze()
        self.assertEqual(tricks, 2)

        # Positional simple squeeze also shouldn't work if
        # we have the SUMIT suit!!!
        dda = libdda.DDAnalyzer("2..2.2 ..7.45 ..6.36 ..345.")
        dda.give_pitch(1);
        tricks = dda.analyze()
        self.assertEqual(tricks, 2)

        # Automatic squeeze
        dda = libdda.DDAnalyzer("2..5.2 ..6.45 .2..36 ..234.")
        tricks = dda.analyze()
        self.assertEqual(tricks, 3)

        # Automatic squeezes work no matter which side has the guards
        dda = libdda.DDAnalyzer("2..5.2 ..234. .2..36 ..6.45")
        tricks = dda.analyze()
        self.assertEqual(tricks, 3)

    def test_fabpedigree(self):
        #https://fabpedigree.com/james/dbldum.htm
        dda = libdda.DDAnalyzer(".A2.K97.A T32.T.T.T AJ4..Q8.2 KQ.98.A2.")
        tricks = dda.analyze()
        self.assertEqual(tricks, 5)

        # Shouldn't work with Sumit suit
        dda = libdda.DDAnalyzer(".A2.K97.A T32.T.T.T AJ4..Q8.2 KQ.98.A2.")
        dda.give_pitch(3)
        tricks = dda.analyze()
        self.assertEqual(tricks, 4)

    def test_guard_squeezes(self):
        #http://www.bridgeguys.com/squeeze/guard_squeeze.html
        dda = libdda.DDAnalyzer("A...KT3 .A.A.Q6 .K.K.A7 4...J54")
        tricks = dda.analyze()
        self.assertEqual(tricks, 4)

    def test_strip_and_duck(self):
        #https://www.lajollabridge.com/French/misc/Squeeze-Refresher.pdf
        dda = libdda.DDAnalyzer("AK.xx.xx. .KQJ.KQ.x x.ATx.AJ. xx.xx..xx")
        tricks = dda.analyze()
        self.assertEqual(tricks, 5)

    def test_three_suit_strip(self):
        # https://www.lajollabridge.com/French/misc/Squeeze-Refresher.pdf
        # Page 31, they are wrong

        # We should only be able to take our 2 aces
        dda = libdda.DDAnalyzer(".Tx.xx.Qx .Q.KQx.KJ .x.AJ.Axx ..Txx.Txx")
        tricks = dda.analyze()
        self.assertEqual(tricks, 2)

        # We can endplay W
        dda = libdda.DDAnalyzer("A.T.xx.Qx .Q.KQx.KJ x..AJ.Axx ..Txx.Txx")
        tricks = dda.analyze()
        self.assertEqual(tricks, 4)

        # They say this shouldn't work, but it does if you play a heart first
        dda = libdda.DDAnalyzer("A.Tx.xx.Qx .QJ.KQx.KJ x.x.AJ.Axx ..Txxx.Txx")
        tricks = dda.analyze()
        self.assertEqual(tricks, 4)

        # This should work too, as they promise
        dda = libdda.DDAnalyzer("A.Tx.xx.Ax .QJ.KQx.KJ x.x.AJ.Qxx ..Txxx.Txx")
        tricks = dda.analyze()
        self.assertEqual(tricks, 4)
