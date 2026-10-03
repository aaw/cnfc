from cnfc.cardinality import exactly_n_true, at_least_n_true, at_most_n_true
from cnfc import *
from .util import SatTestCase, write_cnf_to_string

import io
import itertools
import unittest

class TestCardinality(unittest.TestCase, SatTestCase):
    def test_constant_integer_minimum_true_count(self):
        f = Formula()
        a,b,c = f.AddVars('a b c')
        f.Add(NumTrue(a,b,c) >= Integer(1))
        f.Add(~b)
        f.Add(~c)
        self.assertSat(f)
        f.Add(~a)
        self.assertUnsat(f)

    def test_constant_integer_maximum_false_count(self):
        f = Formula()
        a,b,c = f.AddVars('a b c')
        f.Add(NumFalse(a,b,c) <= Integer(1))
        f.Add(~a)
        f.Add(b)
        self.assertSat(f)
        f.Add(~c)
        self.assertUnsat(f)

    def test_constant_integer_strict_minimum(self):
        f = Formula()
        a,b,c = f.AddVars('a b c')
        f.Add(NumTrue(a,b,c) > Integer(1))
        f.Add(a)
        f.Add(~b)
        self.assertSat(f)
        f.Add(~c)
        self.assertUnsat(f)

    def test_constant_integer_strict_maximum(self):
        f = Formula()
        a,b,c = f.AddVars('a b c')
        f.Add(NumFalse(a,b,c) < Integer(2))
        f.Add(~a)
        f.Add(b)
        self.assertSat(f)
        f.Add(~c)
        self.assertUnsat(f)

    def test_constant_integer_exact_count(self):
        f = Formula()
        a,b,c = f.AddVars('a b c')
        f.Add(NumTrue(a,b,c) == Integer(1))
        f.Add(a)
        f.Add(~b)
        self.assertSat(f)
        f.Add(c)
        self.assertUnsat(f)

    def test_constant_integer_not_equal_count(self):
        f = Formula()
        a,b,c = f.AddVars('a b c')
        f.Add(a)
        f.Add(~b)
        f.Add(~c)

        f.PushCheckpoint()
        f.Add(NumFalse(a,b,c) != Integer(1))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(NumFalse(a,b,c) != Integer(2))
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_negated_constant_integer_comparison(self):
        f = Formula()
        a,b,c = f.AddVars('a b c')
        f.Add(a)
        f.Add(~b)
        f.Add(~c)

        f.PushCheckpoint()
        f.Add(Not(NumTrue(a,b,c) >= Integer(1)))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Not(NumTrue(a,b,c) >= Integer(2)))
        self.assertSat(f)
        f.PopCheckpoint()

    def test_symbolic_integer_count_bound(self):
        f = Formula()
        a,b,bound_bit = f.AddVars('a b bound')
        f.Add(a)
        f.Add(~b)
        f.Add(NumTrue(a,b) == Integer(bound_bit))

        f.PushCheckpoint()
        f.Add(bound_bit)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(~bound_bit)
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_constant_integer_count_above_number_of_inputs(self):
        f = Formula()
        a,b,c = f.AddVars('a b c')
        f.Add(NumTrue(a,b,c) == Integer(4))
        self.assertUnsat(f)

    def test_constant_integer_strict_bound_at_zero(self):
        f = Formula()
        a,b,c = f.AddVars('a b c')
        f.Add(NumTrue(a,b,c) < Integer(0))
        self.assertUnsat(f)

    def test_constant_integer_strict_bound_at_number_of_inputs(self):
        f = Formula()
        a,b,c = f.AddVars('a b c')
        f.Add(NumFalse(a,b,c) > Integer(3))
        self.assertUnsat(f)

    def test_large_true_count(self):
        f = Formula()
        xs = f.AddVars('x', 64)
        for x in xs[:16]:
            f.Add(x)
        for x in xs[16:]:
            f.Add(~x)

        f.PushCheckpoint()
        f.Add(NumTrue(*xs) == 16)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(NumTrue(*xs) == 15)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(NumTrue(*xs) == 17)
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_large_false_count(self):
        f = Formula()
        xs = f.AddVars('x', 64)
        for x in xs[:16]:
            f.Add(x)
        for x in xs[16:]:
            f.Add(~x)

        f.PushCheckpoint()
        f.Add(NumFalse(*xs) == 48)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(NumFalse(*xs) == 47)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(NumFalse(*xs) == 49)
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_large_count_not_equal(self):
        f = Formula()
        xs = f.AddVars('x', 64)
        for x in xs[:16]:
            f.Add(x)
        for x in xs[16:]:
            f.Add(~x)

        f.PushCheckpoint()
        f.Add(NumFalse(*xs) != 48)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(NumFalse(*xs) != 47)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(NumFalse(*xs) != 49)
        self.assertSat(f)
        f.PopCheckpoint()

    def test_negated_large_count_equality(self):
        f = Formula()
        xs = f.AddVars('x', 64)
        for x in xs[:16]:
            f.Add(x)
        for x in xs[16:]:
            f.Add(~x)

        f.PushCheckpoint()
        f.Add(Not(NumTrue(*xs) == 16))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Not(NumTrue(*xs) == 17))
        self.assertSat(f)
        f.PopCheckpoint()

    def test_negated_large_count_inequality(self):
        f = Formula()
        xs = f.AddVars('x', 64)
        for x in xs[:16]:
            f.Add(x)
        for x in xs[16:]:
            f.Add(~x)

        f.PushCheckpoint()
        f.Add(Not(NumFalse(*xs) != 48))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Not(NumFalse(*xs) != 47))
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_exactly_two_false_among_six(self):
        f = Formula()
        a,b,c,d,e,g = f.AddVars('a b c d e g')
        f.Add(NumFalse(a,b,c,d,e,g) == 2)
        f.Add(a)
        f.Add(b)
        f.Add(c)
        f.Add(~g)

        f.PushCheckpoint()
        f.Add(d)
        f.Add(~e)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(~d)
        f.Add(~e)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(d)
        f.Add(e)
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_not_exactly_four_true_among_six(self):
        f = Formula()
        a,b,c,d,e,g = f.AddVars('a b c d e g')
        f.Add(NumTrue(a,b,c,d,e,g) != 4)
        f.Add(a)
        f.Add(b)
        f.Add(c)
        f.Add(~g)

        f.PushCheckpoint()
        f.Add(d)
        f.Add(~e)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(~d)
        f.Add(~e)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(d)
        f.Add(e)
        self.assertSat(f)
        f.PopCheckpoint()

    def test_at_most_four_true_among_six(self):
        f = Formula()
        a,b,c,d,e,g = f.AddVars('a b c d e g')
        f.Add(NumTrue(a,b,c,d,e,g) < 5)
        f.Add(a)
        f.Add(b)
        f.Add(c)
        f.Add(~g)

        f.PushCheckpoint()
        f.Add(d)
        f.Add(~e)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(~d)
        f.Add(~e)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(d)
        f.Add(e)
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_at_least_four_true_among_six(self):
        f = Formula()
        a,b,c,d,e,g = f.AddVars('a b c d e g')
        f.Add(NumTrue(a,b,c,d,e,g) >= 4)
        f.Add(a)
        f.Add(b)
        f.Add(c)
        f.Add(~g)

        f.PushCheckpoint()
        f.Add(d)
        f.Add(~e)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(~d)
        f.Add(~e)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(d)
        f.Add(e)
        self.assertSat(f)
        f.PopCheckpoint()

    def test_at_least_one_exhaustive(self):
        for size in range(1, 9):
            f = Formula()
            vs = f.AddVars('x', size)
            f.Add(NumTrue(*vs) >= 1)

            for values in itertools.product((False, True), repeat=size):
                f.PushCheckpoint()
                for v, value in zip(vs, values):
                    f.Add(v if value else ~v)
                if any(values):
                    self.assertSat(f)
                else:
                    self.assertUnsat(f)
                f.PopCheckpoint()

    def test_at_most_one_exhaustive(self):
        for size in range(1, 9):
            f = Formula()
            vs = f.AddVars('x', size)
            f.Add(NumTrue(*vs) <= 1)

            for values in itertools.product((False, True), repeat=size):
                f.PushCheckpoint()
                for v, value in zip(vs, values):
                    f.Add(v if value else ~v)
                if sum(values) <= 1:
                    self.assertSat(f)
                else:
                    self.assertUnsat(f)
                f.PopCheckpoint()

    def test_exactly_one_exhaustive(self):
        for size in range(1, 9):
            f = Formula()
            vs = f.AddVars('x', size)
            f.Add(NumTrue(*vs) == 1)

            for values in itertools.product((False, True), repeat=size):
                f.PushCheckpoint()
                for v, value in zip(vs, values):
                    f.Add(v if value else ~v)
                if sum(values) == 1:
                    self.assertSat(f)
                else:
                    self.assertUnsat(f)
                f.PopCheckpoint()

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

    def test_exactly_one(self):
        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        for clause in exactly_n_true(f, [x,y,z,w], 1):
            f.AddClause(*clause)

        f.PushCheckpoint()
        self.assertSat(f)
        f.AddClause(~x)
        f.AddClause(~z)
        f.AddClause(~y)
        f.AddClause(~w)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        self.assertSat(f)
        f.AddClause(~x)
        f.AddClause(z)
        f.AddClause(~y)
        f.AddClause(~w)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        self.assertSat(f)
        f.AddClause(~x)
        f.AddClause(z)
        f.AddClause(~y)
        f.AddClause(w)
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_larger_set_exactly_one(self):
        fm = Formula()
        a,b,c,d,e,f,g,h,i = fm.AddVars('a b c d e f g h i')
        for clause in exactly_n_true(fm, [a,b,c,d,e,f,g,h,i], 1):
            fm.AddClause(*clause)

        fm.AddClause(~a)
        fm.AddClause(~c)
        fm.AddClause(d)
        fm.AddClause(~e)
        fm.AddClause(~f)
        fm.AddClause(~g)
        fm.AddClause(~h)
        fm.AddClause(~i)
        self.assertSat(fm)

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

    # at_most_one_{true,false} used to be implemented recursively, which meant that
    # you'd need to adjust the recursion limit with sys.setrecursionlimit() to make
    # larger cardinality constraints work. This test used to generate a RecursionError.
    def test_many_vars(self):
        f = Formula()
        import sys
        limit = sys.getrecursionlimit() * 2
        varz = [f.AddVar() for i in range(2 * limit)]
        f.Add(NumTrue(*varz) >= limit)
