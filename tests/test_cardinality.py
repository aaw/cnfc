from cnfc.cardinality import exactly_n_true, at_least_n_true, at_most_n_true
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

    def test_exact_basic(self):
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

    def test_at_least_basic(self):
        f = Formula()
        x,y,z = f.AddVars('x,y,z')
        at_least_n_true(f, [x,y,z], 2)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(~y)
        f.AddClause(z)
        self.assertSat(f)

        f = Formula()
        x,y,z = f.AddVars('x,y,z')
        at_least_n_true(f, [x,y,z], 2)
        f.AddClause(x)
        f.AddClause(~y)
        f.AddClause(~z)
        self.assertUnsat(f)

        f = Formula()
        x,y,z = f.AddVars('x,y,z')
        at_least_n_true(f, [x,y,z], 2)
        f.AddClause(~x)
        f.AddClause(~y)
        f.AddClause(~z)
        self.assertUnsat(f)

    def test_at_most_basic(self):
        f = Formula()
        x,y,z,w,v = f.AddVars('x,y,z,w,v')
        at_most_n_true(f, [x,y,z,w,v], 2)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(~y)
        f.AddClause(z)
        f.AddClause(~w)
        f.AddClause(~v)
        self.assertSat(f)

        f = Formula()
        x,y,z,w,v = f.AddVars('x,y,z,w,v')
        at_most_n_true(f, [x,y,z,w,v], 2)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(~y)
        f.AddClause(z)
        f.AddClause(~w)
        f.AddClause(v)
        self.assertUnsat(f)

        f = Formula()
        x,y,z,w,v = f.AddVars('x,y,z,w,v')
        at_most_n_true(f, [x,y,z,w,v], 2)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(y)
        f.AddClause(z)
        f.AddClause(~w)
        f.AddClause(v)
        self.assertUnsat(f)

        f = Formula()
        x,y,z,w,v = f.AddVars('x,y,z,w,v')
        at_most_n_true(f, [x,y,z,w,v], 2)
        self.assertSat(f)
        f.AddClause(~x)
        f.AddClause(~y)
        f.AddClause(~z)
        f.AddClause(~w)
        f.AddClause(v)
        self.assertSat(f)
