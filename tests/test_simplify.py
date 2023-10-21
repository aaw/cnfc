from cnfc import *
from cnfc.buffer import Buffer, UnitClauses
from cnfc.simplify import propagate_units
from cnfc.formula import raw_lit
from .util import write_cnf_to_string

import unittest

# TODO: make this take a list of clauses, map them all
def ints(*clauses):
    return sorted([tuple(raw_lit(v) for v in vs) for vs in clauses])

class TestSimplify(unittest.TestCase):
    def test_unit_propagation_basic(self):
        units = UnitClauses()
        b = Buffer(visitors=[units])
        f = Formula(buffer=b)
        x1, x2, x3, x4, x5, x6s = f.AddVars('x1 x2 x3 x4 x5 x6')

        f.AddClause(x1, x2, x3)
        f.AddClause(x1)
        f.AddClause(x2, x3, x4)
        f.AddClause(~x4)

        b = propagate_units(b, units.units)

        self.assertEqual(sorted(list(b.AllClauses())), ints((x1,), (x2, x3), (~x4,)))

    def test_unit_propagation_repeated(self):
        units = UnitClauses()
        b = Buffer(visitors=[units])
        f = Formula(buffer=b)
        x1, x2, x3, x4, x5, x6s = f.AddVars('x1 x2 x3 x4 x5 x6')

        # Deriving ~x3 takes a few rounds of unit propagation.
        f.AddClause(~x2, ~x3)
        f.AddClause(~x1, x2)
        f.AddClause(x1)
        f.AddClause(x3, x4, x5)

        b = propagate_units(b, units.units)

        self.assertEqual(sorted(list(b.AllClauses())), ints((x1,), (x2,), (~x3,), (x4, x5)))
