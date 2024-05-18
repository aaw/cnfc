from cnfc import *
from cnfc.funcs import *
from .util import SatTestCase, write_cnf_to_string

import unittest

class TestFuncs(unittest.TestCase, SatTestCase):
    @unittest.skip("Takes too long. Re-enable when we use a CDCL solver in testing")
    def test_is_palindrome(self):
        f = Formula()

        f.PushCheckpoint()
        f.Add(IsPalindrome(Integer(121)))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(IsPalindrome(Integer(122)))
        self.assertUnsat(f)
        f.PopCheckpoint()


if __name__ == '__main__':
    unittest.main()
