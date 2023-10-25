from cnfc import *
from cnfc.simplify import *
from cnfc.formula import raw_lit
from .util import write_cnf_to_string

import unittest

class TestSimplify(unittest.TestCase):
    def assertClausesEquivalent(self, formula, clauses):
        expected_clauses = sorted([tuple(sorted(raw_lit(v) for v in vs)) for vs in clauses])
        given_clauses = sorted([tuple(sorted(c)) for c in formula.buffer.AllClauses()])
        self.assertEqual(expected_clauses, given_clauses)

    def test_unit_propagation_basic(self):
        f = Formula()
        x1, x2, x3, x4 = f.AddVars('x1 x2 x3 x4')

        f.AddClause(x1, x2, x3)
        f.AddClause(x1)
        f.AddClause(x2, x3, x4)
        f.AddClause(~x4)

        f.buffer = propagate_units(f.buffer)

        self.assertClausesEquivalent(f, [(x1,), (x2, x3), (~x4,)])

    def test_unit_propagation_repeated(self):
        f = Formula()
        x1, x2, x3, x4, x5 = f.AddVars('x1 x2 x3 x4 x5')

        # Deriving ~x3 takes a few rounds of unit propagation.
        f.AddClause(~x2, ~x3)
        f.AddClause(~x1, x2)
        f.AddClause(x1)
        f.AddClause(x3, x4, x5)

        f.buffer = propagate_units(f.buffer)

        self.assertClausesEquivalent(f, [(x1,), (x2,), (~x3,), (x4, x5)])

    def test_self_subsumption(self):
        f = Formula()
        x1, x2, x3 = f.AddVars('x1 x2 x3')

        f.AddClause(x1, x2, ~x3)
        f.AddClause(x1, x3)

        f.buffer = strengthen_self_subsumed(f.buffer)

        self.assertClausesEquivalent(f, [(x1, x2), (x1, x3)])

    def test_self_subsumption_repeated(self):
        f = Formula()
        x1, x2, x3, x4 = f.AddVars('x1 x2 x3 x4')

        f.AddClause(x1, x2, ~x3)
        f.AddClause(x1, x3)
        f.AddClause(~x1, x2, x4)

        f.buffer = strengthen_self_subsumed(f.buffer)

        self.assertClausesEquivalent(f, [(x1, x2), (x1, x3), (x2, x4)])

    # simplify currently does a few simplifications, so we have to be a little
    # careful in the tests below to create minimal examples that exercise only
    # the simplification we're interested in. For example, the following test
    # adds an extra tautology so that literals from the first tautology won't
    # get removed by the pure literal rule.

    def test_tautology_suppression(self):
        f = Formula()
        x1, x2, x3, x4 = f.AddVars('x1 x2 x3 x4')

        f.AddClause(x1, x2, ~x3)  # Not a tautology
        f.AddClause(~x1, ~x2, x3)  # Not a tautology
        f.AddClause(x1, x2, ~x2)  # Tautology
        f.AddClause(~x1, x3, x4, x1)  # Tautology

        f.buffer = simplify(f.buffer)

        self.assertClausesEquivalent(f, [(x1, x2, ~x3), (~x1, ~x2, x3)])

    def test_duplicate_literal_elimination(self):
        f = Formula()
        x1, x2, x3 = f.AddVars('x1 x2 x3')

        f.AddClause(x1, x2, x1, ~x3)  # x1 repeated
        f.AddClause(~x1, ~x2, x3, ~x2, ~x2)  # ~x2 repeated

        f.buffer = simplify(f.buffer)

        self.assertClausesEquivalent(f, [(x1, x2, ~x3), (~x1, ~x2, x3)])

    def test_duplicate_clause_elimination(self):
        f = Formula()
        x1, x2, x3 = f.AddVars('x1 x2 x3')

        f.AddClause(x1, x2, ~x3)
        f.AddClause(~x1, ~x2, x3)
        f.AddClause(x1, x2)
        f.AddClause(x1, x2, ~x3)  # Repeat of first clause
        f.AddClause(x1, x2, ~x3)  # Repeat of first clause
        f.AddClause(~x1, ~x2, x3)  # Repeat of second clause

        f.buffer = simplify(f.buffer)

        self.assertClausesEquivalent(f, [(x1, x2, ~x3), (~x1, ~x2, x3), (x1, x2)])

    def test_pure_literal_removal(self):
        f = Formula()
        x1, x2, x3 = f.AddVars('x1 x2 x3')

        # x3 never appears in the formula, so ~x3 is pure. After ~x3 is set to
        # true, all clauses where ~x3 appears can be removed.
        f.AddClause(x1, x2, ~x3)
        f.AddClause(~x2, ~x3)
        f.AddClause(~x1, ~x2)

        f.buffer = simplify(f.buffer)

        self.assertClausesEquivalent(f, [(~x3,), (~x1, ~x2)])
