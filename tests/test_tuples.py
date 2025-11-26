from cnfc.tuples import tuple_less_than
from cnfc.util import Generator
from cnfc import *
from .util import SatTestCase

import itertools
import unittest

class TestCardinality(unittest.TestCase, SatTestCase):
    # Test all dimension 1, 2 and 3 tuples with < and <=.
    def test_less_than_small_exhaustive(self):
        f = Formula()
        x1,x2,y1,y2 = f.AddVars('x1 x2 y1 y2')

        for dimension in (1, 2,3):
            f = Formula()
            x = list(f.AddVars(' '.join('x{}'.format(i) for i in range(dimension))))
            y = list(f.AddVars(' '.join('y{}'.format(i) for i in range(dimension))))

            for xv in itertools.product([True,False], repeat=dimension):
                for yv in itertools.product([True,False], repeat=dimension):
                    f.PushCheckpoint()  # setting x1,x2,... and y1,y2,...
                    for i in range(dimension):
                        f.AddClause(x[i]) if xv[i] else f.AddClause(~x[i])
                        f.AddClause(y[i]) if yv[i] else f.AddClause(~y[i])

                    f.PushCheckpoint()  # <= comparison

                    gen = Generator(tuple_less_than(f, x, y, strict=False))
                    for clause in gen:
                        f.AddClause(*clause)
                    f.AddClause(gen.result)
                    if xv <= yv:
                        self.assertSat(f)
                    else:
                        self.assertUnsat(f)
                    f.PopCheckpoint()  # <= comparison

                    f.PushCheckpoint()  # < comparison
                    gen = Generator(tuple_less_than(f, x, y, strict=True))
                    for clause in gen:
                        f.AddClause(*clause)
                    f.AddClause(gen.result)
                    if xv < yv:
                        self.assertSat(f)
                    else:
                        self.assertUnsat(f)
                    f.PopCheckpoint()  # < comparison

                    f.PopCheckpoint()  # setting (x1,x2,y1,y2)
