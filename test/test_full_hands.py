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
        tricks = dda.analyze()
        self.assertEqual(tricks, 3) # Can actually make 4NT

    def test_fabpedigree(self):
        #https://fabpedigree.com/james/dbldum.htm
        dda = libdda.DDAnalyzer("QJT98.4.QJT9.KT2 "
                                "AK76543.32.AK2.3 "
                                "2.QT87.876.87654 "
                                ".AKJ965.543.AQJ9",
                                1
                                )
        dda.play_card(0,12) # Q lead allows declarer to make
        tricks = dda.analyze()
        self.assertEqual(tricks, 0)

        dda = libdda.DDAnalyzer("QJT98.4.QJT9.KT2 "
                                "AK76543.32.AK2.3 "
                                "2.QT87.876.87654 "
                                ".AKJ965.543.AQJ9",
                                1
                                )
        dda.play_card(1,4) # Leading trumps can set the contract
        tricks = dda.analyze()
        self.assertEqual(tricks, 1)
