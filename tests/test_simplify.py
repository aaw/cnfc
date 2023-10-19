from cnfc import *
from cnfc.buffer import Buffer, UnitClauses
from cnfc.simplify import propagate_units
from .util import write_cnf_to_string

import unittest

class TestSimplify(unittest.TestCase):
    def test_unit_propagation_basic(self):
        units = UnitClauses()
        b = Buffer(visitors=[units])
        f = Formula(buffer=b)
        xs = [f.AddVar() for i in range(6)]

        f.AddClause(xs[0], xs[1], xs[2])
        f.AddClause(xs[0])
        f.AddClause(xs[3], xs[4], xs[5])
        f.AddClause(~xs[5])

        b = propagate_units(b, units.units)

        self.assertEqual(list(b.AllClauses()), [(xs[3].vid, xs[4].vid), (xs[0],), (~xs[5])])

    def test_unit_propagation_repeated(self):
        units = UnitClauses()
        b = Buffer(visitors=[units])
        f = Formula(buffer=b)
        xs = [f.AddVar() for i in range(6)]

        # Deriving ~xs[2] takes a few rounds of unit propagation.
        f.AddClause(~xs[1], ~xs[2])
        f.AddClause(~xs[0], xs[1])
        f.AddClause(xs[0])
        f.AddClause(xs[2], xs[3], xs[4])

        b = propagate_units(b, units.units)

        self.assertEqual(list(b.AllClauses()), [(xs[3].vid, xs[4].vid), (xs[0],), (xs[1],), (~xs[2],)])
