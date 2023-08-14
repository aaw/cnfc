from cnfc.tuple import tuple_less_than
from cnfc import *
from .dpll import Satisfiable

import io
import itertools
import unittest

# TODO: test_formula.py uses this, extract it.
def write_cnf_to_string(f):
    out = io.StringIO()
    f.WriteCNF(out)
    out.seek(0)
    return out.read()

class TestCardinality(unittest.TestCase):
    # TODO: test_formula.py uses these two helpers too, extract them.
    def assertSat(self, formula):
        self.assertTrue(Satisfiable(write_cnf_to_string(formula)))

    def assertUnsat(self, formula):
        self.assertFalse(Satisfiable(write_cnf_to_string(formula)))

    # Test all dimension 2 and 3 tuples with < and <=.
    def test_less_than_small_exhaustive(self):
        f = Formula()
        x1,x2,y1,y2 = f.AddVars('x1,x2,y1,y2')

        for dimension in (2,3):
            f = Formula()
            x = list(f.AddVars(','.join('x{}'.format(i) for i in range(dimension))))
            y = list(f.AddVars(','.join('y{}'.format(i) for i in range(dimension))))

            for xv in itertools.product([True,False], repeat=dimension):
                for yv in itertools.product([True,False], repeat=dimension):
                    f.PushCheckpoint()  # setting x1,x2,... and y1,y2,...
                    for i in range(dimension):
                        f.AddClause(x[i]) if xv[i] else f.AddClause(~x[i])
                        f.AddClause(y[i]) if yv[i] else f.AddClause(~y[i])

                    f.PushCheckpoint()  # <= comparison
                    for clause in tuple_less_than(f, x, y, strict=False):
                        f.AddClause(*clause)
                    if xv <= yv:
                        self.assertSat(f)
                    else:
                        self.assertUnsat(f)
                    f.PopCheckpoint()  # <= comparison

                    f.PushCheckpoint()  # < comparison
                    for clause in tuple_less_than(f, x, y, strict=True):
                        f.AddClause(*clause)
                    if xv < yv:
                        self.assertSat(f)
                    else:
                        self.assertUnsat(f)
                    f.PopCheckpoint()  # < comparison

                    f.PopCheckpoint()  # setting (x1,x2,y1,y2)
