from cnfc import *
from cnfc.funcs import *
from .util import SatTestCase, write_cnf_to_string

import itertools
import unittest

class TestFuncs(unittest.TestCase, SatTestCase):
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

    def test_max(self):
        f = Formula()

        x1 = Integer(1)
        x2 = Integer(2)
        x3 = Integer(3)
        x4 = Integer(4)
        x5 = Integer(5)
        x6 = Integer(6)

        f.PushCheckpoint()
        f.Add(Max(x6, x5) == x6)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Max(x5, x6) == x6)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Max(x4, x1, x2, x6, x5, x3) == x6)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Max(x4, x1, x2, x6, x5, x3) == x3)
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_min(self):
        f = Formula()

        x = Integer(15)
        y = Integer(27)
        z = Integer(17)

        f.PushCheckpoint()
        f.Add(Min([x,y]) == x)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Min([y,x]) == x)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Min([x,y,z]) == x)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Min([x,y,z]) == y)
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_simple_min_unsat(self):
        f = Formula()
        y = Integer(2)
        z = Integer(1)
        f.Add(Min(y,z) == y)
        self.assertUnsat(f)

    def test_simple_max_unsat(self):
        f = Formula()
        y = Integer(2)
        z = Integer(1)
        f.Add(Max(y,z) == z)
        self.assertUnsat(f)

    def test_min_max_exhaustive(self):
        f = Formula()
        nums = [0,1,1,7,9000]
        for k in range(2, len(nums)+1):
            for subset in itertools.combinations(nums, k):
                cnfc_nums = [Integer(x) for x in subset]

                f.PushCheckpoint()
                f.Add(Min(cnfc_nums) == min(subset))
                self.assertSat(f)
                f.PopCheckpoint()

                f.PushCheckpoint()
                f.Add(Max(cnfc_nums) == max(subset))
                self.assertSat(f)
                f.PopCheckpoint()

if __name__ == '__main__':
    unittest.main()
