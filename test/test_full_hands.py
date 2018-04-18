#!/usr/local/bin/python3
import unittest
import dda

class FullDeals(unittest.TestCase):
    def test_3nt_strip_squeeze(self):
        #https://www.larryco.com/bridge-learning-center/detail/524
        b = dda.Board("3478Q.8JK.8T.7JK "
                      "69A.27TA.AK.489T "
                      "25K.346.23467.25 "
                      "TJ.59Q.59JQ.36QA"
                      )
        tricks = dda.alpha_beta(b, dda.Game)
        self.assertEqual(tricks, 4)

    def test_fabpedigree(self):
        #https://fabpedigree.com/james/dbldum.htm
        b = dda.Board("QJT98.4.QJT9.KT2 "
                      "AK76543.32.AK2.3 "
                      "2.QT87.876.87654 "
                      ".AKJ965.543.AQJ9"
                      )
        # TODO: trump?!?
        tricks = dda.alpha_beta(b, dda.Game, beta=1)
        self.assertEqual(tricks, 0)
