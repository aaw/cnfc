from cnfc.cardinality import exactly_n_true, at_least_n_true, at_most_n_true
from cnfc import *
from .util import SatTestCase, write_cnf_to_string

import io
import unittest

class TestCardinality(unittest.TestCase, SatTestCase):
    def test_exact_basic(self):
        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        for clause in exactly_n_true(f, [x,y,z,w], 2):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(z)
        f.AddClause(~y)
        f.AddClause(~w)
        self.assertSat(f)

        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        for clause in exactly_n_true(f, [x,y,z,w], 2):
            f.AddClause(*clause)
        f.AddClause(x)
        f.AddClause(~z)
        f.AddClause(~y)
        f.AddClause(~w)
        self.assertUnsat(f)

        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        for clause in exactly_n_true(f, [x,y,z,w], 2):
            f.AddClause(*clause)
        f.AddClause(x)
        f.AddClause(z)
        f.AddClause(y)
        f.AddClause(~w)
        self.assertUnsat(f)

    def test_at_least_basic(self):
        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in at_least_n_true(f, [x,y,z], 2):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(~y)
        f.AddClause(z)
        self.assertSat(f)

        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in at_least_n_true(f, [x,y,z], 2):
            f.AddClause(*clause)
        f.AddClause(x)
        f.AddClause(~y)
        f.AddClause(~z)
        self.assertUnsat(f)

        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in at_least_n_true(f, [x,y,z], 2):
            f.AddClause(*clause)
        f.AddClause(~x)
        f.AddClause(~y)
        f.AddClause(~z)
        self.assertUnsat(f)

    def test_at_most_basic(self):
        f = Formula()
        x,y,z,w,v = f.AddVars('x y z w v')
        for clause in at_most_n_true(f, [x,y,z,w,v], 2):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(~y)
        f.AddClause(z)
        f.AddClause(~w)
        f.AddClause(~v)
        self.assertSat(f)

        f = Formula()
        x,y,z,w,v = f.AddVars('x y z w v')
        for clause in at_most_n_true(f, [x,y,z,w,v], 2):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(~y)
        f.AddClause(z)
        f.AddClause(~w)
        f.AddClause(v)
        self.assertUnsat(f)

        f = Formula()
        x,y,z,w,v = f.AddVars('x y z w v')
        for clause in at_most_n_true(f, [x,y,z,w,v], 2):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(y)
        f.AddClause(z)
        f.AddClause(~w)
        f.AddClause(v)
        self.assertUnsat(f)

        f = Formula()
        x,y,z,w,v = f.AddVars('x y z w v')
        for clause in at_most_n_true(f, [x,y,z,w,v], 2):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(~x)
        f.AddClause(~y)
        f.AddClause(~z)
        f.AddClause(~w)
        f.AddClause(v)
        self.assertSat(f)

    # Test some boundary conditions for equality
    def test_eq_boundary(self):
        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in exactly_n_true(f, [x,y,z], 0):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(~x)
        f.AddClause(~y)
        f.AddClause(~z)
        self.assertSat(f)

        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in exactly_n_true(f, [x,y,z], 0):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(~x)
        f.AddClause(y)
        f.AddClause(~z)
        self.assertUnsat(f)

        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in exactly_n_true(f, [x,y,z], 3):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(y)
        f.AddClause(z)
        self.assertSat(f)

        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in exactly_n_true(f, [x,y,z], 3):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(~x)
        f.AddClause(y)
        f.AddClause(z)
        self.assertUnsat(f)

    # Test some boundary conditions for inequality
    def test_eq_boundary(self):
        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in not_exactly_n_true(f, [x,y,z], 0):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(~y)
        f.AddClause(~z)
        self.assertSat(f)

        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in not_exactly_n_true(f, [x,y,z], 0):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(~x)
        f.AddClause(~y)
        f.AddClause(~z)
        self.assertUnsat(f)

        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in not_exactly_n_true(f, [x,y,z], 3):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(~x)
        f.AddClause(y)
        f.AddClause(z)
        self.assertSat(f)

        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in not_exactly_n_true(f, [x,y,z], 3):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(y)
        f.AddClause(z)
        self.assertUnsat(f)

    # Test some boundary conditions for 'at least' comparisons
    def test_eq_boundary(self):
        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in at_least_n_true(f, [x,y,z], 0):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(~y)
        f.AddClause(~z)
        self.assertSat(f)

        # At least 0 are true is a tautology, no way to create unsat formula.

        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in at_least_n_true(f, [x,y,z], 3):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(y)
        f.AddClause(z)
        self.assertSat(f)

        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in at_least_n_true(f, [x,y,z], 3):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(~y)
        f.AddClause(z)
        self.assertUnsat(f)

    # Test some boundary conditions for 'at most' comparisons
    def test_eq_boundary(self):
        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in at_most_n_true(f, [x,y,z], 0):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(~x)
        f.AddClause(~y)
        f.AddClause(~z)
        self.assertSat(f)

        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in at_most_n_true(f, [x,y,z], 0):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(~y)
        f.AddClause(~z)
        self.assertUnsat(f)

        f = Formula()
        x,y,z = f.AddVars('x y z')
        for clause in at_most_n_true(f, [x,y,z], 3):
            f.AddClause(*clause)
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(~y)
        f.AddClause(z)
        self.assertSat(f)

        # At most n true is a tautology, no way to create an unsat formula.
