import os
import unittest
import warnings

from unit_tests.item_model import TestItemClassModel
from unit_tests.knapsack_model import TestKnapsackModel
from unit_tests.TMKPA.solving import TestTMKPAsolve
from unit_tests.MTM_EXTENDED.solving import TestMTM_Extende_solve

alltests = unittest.TestLoader().discover(start_dir=os.path.dirname(os.path.realpath(__file__)), pattern="*.py")

if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        unittest.TextTestRunner(verbosity=2).run(alltests)
