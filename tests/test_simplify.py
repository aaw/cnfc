from cnfc import *
from cnfc.simplify import *
from cnfc.formula import raw_lit
from .util import write_cnf_to_string

import unittest

def ints(*clauses):
    return sorted([tuple(raw_lit(v) for v in vs) for vs in clauses])

class TestSimplify(unittest.TestCase):
    def test_unit_propagation_basic(self):
        f = Formula()
        x1, x2, x3, x4, x5, x6s = f.AddVars('x1 x2 x3 x4 x5 x6')

        f.AddClause(x1, x2, x3)
        f.AddClause(x1)
        f.AddClause(x2, x3, x4)
        f.AddClause(~x4)

        f.buffer = propagate_units(f.buffer)

        self.assertEqual(sorted(list(f.buffer.AllClauses())), ints((x1,), (x2, x3), (~x4,)))

    def test_unit_propagation_repeated(self):
        f = Formula()
        x1, x2, x3, x4, x5, x6s = f.AddVars('x1 x2 x3 x4 x5 x6')

        # Deriving ~x3 takes a few rounds of unit propagation.
        f.AddClause(~x2, ~x3)
        f.AddClause(~x1, x2)
        f.AddClause(x1)
        f.AddClause(x3, x4, x5)

        f.buffer = propagate_units(f.buffer)

        self.assertEqual(sorted(list(f.buffer.AllClauses())), ints((x1,), (x2,), (~x3,), (x4, x5)))

    def test_self_subsumption(self):
        f = Formula()
        x1, x2, x3, x4, x5, x6s = f.AddVars('x1 x2 x3 x4 x5 x6')

        f.AddClause(x1, x2, ~x3)
        f.AddClause(x1, x3)

        f.buffer = strengthen_self_subsumed(f.buffer)

        self.assertEqual(sorted(list(f.buffer.AllClauses())), ints((x1, x2), (x1, x3)))

    def test_self_subsumption_repeated(self):
        f = Formula()
        x1, x2, x3, x4, x5, x6s = f.AddVars('x1 x2 x3 x4 x5 x6')

        f.AddClause(x1, x2, ~x3)
        f.AddClause(x1, x3)
        f.AddClause(~x1, x2, x4)

        f.buffer = strengthen_self_subsumed(f.buffer)

        self.assertEqual(sorted(list(f.buffer.AllClauses())), ints((x1, x2), (x1, x3), (x2, x4)))
