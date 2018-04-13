#!/usr/local/bin/python3
import unittest
import dda

class OneCardEndings(unittest.TestCase):
    def test_3nt_strip_squeeze(self):
        #https://www.larryco.com/bridge-learning-center/detail/524
        b = dda.Board("3478Q.8JK.8T.7JK "
                      "69A.27TA.QK.489T "
                      "25K.346.23467.25 "
                      "TJ.59Q.58JQ.36QA"
                      )
        tricks = dda.alpha_beta(b, dda.Game, total_tricks=2)
        self.assertEqual(tricks, 4)
