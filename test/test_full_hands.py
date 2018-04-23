import unittest
import src.libdda as libdda

class FullDeals(unittest.TestCase):
    def test_3nt_strip_squeeze(self):
        #https://www.larryco.com/bridge-learning-center/detail/524
        dda = libdda.DDAnalyzer("3478Q.8JK.8T.7JK "
                                "69A.27TA.AK.489T "
                                "25K.346.23467.25 "
                                "TJ.59Q.59JQ.36QA"
                                )
        dda.play_card(0,4)
        self.assertEqual(dda.analyze(3), 3) # Can actually make 4NT

    def test_fabpedigree(self):
        #https://fabpedigree.com/james/dbldum.htm
        # The original problem
        dda = libdda.DDAnalyzer("QJT98.4.QJT9.KT2 "
                                "AK76543.32.AK2.3 "
                                "2.QT87.876.87654 "
                                ".AKJ965.543.AQJ9",
                                1
                                )
        dda.play_card(0,12) # Q lead allows declarer to make
        self.assertEqual(dda.analyze(0), 0)

        # A different lead can set
        dda = libdda.DDAnalyzer("QJT98.4.QJT9.KT2 "
                                "AK76543.32.AK2.3 "
                                "2.QT87.876.87654 "
                                ".AKJ965.543.AQJ9",
                                1
                                )
        dda.play_card(1,4) # Leading trumps can set the contract
        self.assertEqual(dda.can_make(1), True)
        self.assertEqual(dda.can_make(2), False)
        self.assertEqual(dda.analyze(1), 1)

        # What if we give everybody a pitch?
        dda = libdda.DDAnalyzer("QJT98.4.QJT9.KT2 "
                                "AK76543.32.AK2.3 "
                                "2.QT87.876.87654 "
                                ".AKJ965.543.AQJ9",
                                1
                                )
        dda.play_card(0,12) # Q lead allows declarer to make
        dda.give_pitch(0)
        self.assertEqual(dda.analyze(0), 1)
