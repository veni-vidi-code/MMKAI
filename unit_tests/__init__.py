import os
import unittest
import warnings

alltests = unittest.TestLoader().discover(start_dir=os.path.dirname(os.path.realpath(__file__)), pattern="*.py")

if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        unittest.TextTestRunner(verbosity=2).run(alltests)
