from cardinality import exactly_n_true, at_least_n_true, at_most_n_true
from cnfc import *
from dpll import Satisfiable

import io
import unittest

# TODO: test_formula.py uses this, extract it.
def write_cnf_to_string(f):
    out = io.StringIO()
    f.WriteCNF(out)
    out.seek(0)
    return out.read()

class TestCache(unittest.TestCase):
    # TODO: test_formula.py uses these two helpers too, extract them.
    def assertSat(self, formula):
        self.assertTrue(Satisfiable(write_cnf_to_string(formula)))

    def assertUnsat(self, formula):
        self.assertFalse(Satisfiable(write_cnf_to_string(formula)))

    def test_exact(self):
        f = Formula()
        x,y,z,w = f.AddVars('x,y,z,w')
        exactly_n_true(f, [x,y,z,w], 2)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(z)
        f.AddClause(~y)
        f.AddClause(~w)
        self.assertSat(f)

        f = Formula()
        x,y,z,w = f.AddVars('x,y,z,w')
        exactly_n_true(f, [x,y,z,w], 2)
        f.AddClause(x)
        f.AddClause(~z)
        f.AddClause(~y)
        f.AddClause(~w)
        self.assertUnsat(f)

        f = Formula()
        x,y,z,w = f.AddVars('x,y,z,w')
        exactly_n_true(f, [x,y,z,w], 2)
        f.AddClause(x)
        f.AddClause(z)
        f.AddClause(y)
        f.AddClause(~w)
        self.assertUnsat(f)
