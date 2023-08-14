from cnfc.tuple import tuple_less_than
from cnfc import *
from .dpll import Satisfiable

import io
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

    def test_less_than_small_exhaustive(self):
        f = Formula()
        x1,x2,y1,y2 = f.AddVars('x1,x2,y1,y2')

        for x1v in (True,False):
            for x2v in (True,False):
                for y1v in (True,False):
                    for y2v in (True,False):
                        f.PushCheckpoint()  # setting (x1,x2,y1,y2)

                        f.AddClause(x1) if x1v else f.AddClause(~x1)
                        f.AddClause(x2) if x2v else f.AddClause(~x2)
                        f.AddClause(y1) if y1v else f.AddClause(~y1)
                        f.AddClause(y2) if y2v else f.AddClause(~y2)

                        f.PushCheckpoint()  # <= comparison
                        for clause in tuple_less_than(f, (x1,x2), (y1,y2), strict=False):
                            f.AddClause(*clause)
                        if (x1v,x2v) <= (y1v,y2v):
                            self.assertSat(f)
                        else:
                            self.assertUnsat(f)
                        f.PopCheckpoint()  # <= comparison

                        f.PushCheckpoint()  # < comparison
                        for clause in tuple_less_than(f, (x1,x2), (y1,y2), strict=True):
                            f.AddClause(*clause)
                        if (x1v,x2v) < (y1v,y2v):
                            self.assertSat(f)
                        else:
                            self.assertUnsat(f)
                        f.PopCheckpoint()  # < comparison

                        f.PopCheckpoint()  # setting (x1,x2,y1,y2)
