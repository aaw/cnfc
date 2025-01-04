from cnfc import *
from .util import SatTestCase, write_cnf_to_string
import unittest

class TestFormula(unittest.TestCase, SatTestCase):
    def test_add_variables(self):
        f = Formula()
        x = f.AddVar('x')
        y,z,w = f.AddVars('y z w')
        self.assertEqual([x.vid, y.vid, z.vid, w.vid], [1,2,3,4])
        self.assertEqual([x.name, y.name, z.name, w.name], ['x','y','z','w'])
        self.assertEqual(len(f.vars), 4)
        self.assertEqual(f.vars['x'], 1)
        self.assertEqual(f.vars['y'], 2)
        self.assertEqual(f.vars['z'], 3)
        self.assertEqual(f.vars['w'], 4)

    def test_add_unnamed_var(self):
        f = Formula()
        x = f.AddVar()
        y = f.AddVar()
        self.assertEqual(x.vid, 1)
        self.assertEqual(y.vid, 2)

    def test_boolean_expr_parsing(self):
        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        c = (~x == y) & ((z != w) | x)
        self.assertEqual(repr(c), 'And(Eq(Literal(Var(x,1),-1),Var(y,2)),Or(Neq(Var(z,3),Var(w,4)),Var(x,1)))')

    def test_numeric_expr_parsing(self):
        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        self.assertEqual(repr(NumFalse(x,y,z) == 2), 'NumEq(NumFalse(Var(x,1),Var(y,2),Var(z,3)),2)')
        self.assertEqual(repr(2 == NumFalse(x,y,z)), 'NumEq(NumFalse(Var(x,1),Var(y,2),Var(z,3)),2)')
        self.assertEqual(repr(3 > NumTrue(x,y,z,w)), 'NumLt(NumTrue(Var(x,1),Var(y,2),Var(z,3),Var(w,4)),3)')
        self.assertEqual(repr(If(NumTrue(x,y) == 0, z & w)), 'Implies(NumEq(NumTrue(Var(x,1),Var(y,2)),0),And(Var(z,3),Var(w,4)))')

    def test_tuple_parsing(self):
        f = Formula()
        xs = f.AddVars('x1 x2 x3')
        ys = f.AddVars('y1 y2 y3')
        self.assertEqual(repr(Tuple(*xs) < Tuple(*ys)), 'TupleLt(Tuple(Var(x1,1),Var(x2,2),Var(x3,3)),Tuple(Var(y1,4),Var(y2,5),Var(y3,6)))')

    def test_implicit_disjunction_output(self):
        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        f.AddClause(x,~w)
        f.AddClause(~y,z)

        expected = (
            'p cnf 4 2\n' +
            '1 -4 0\n' +
            '-2 3 0\n'
        )
        self.assertEqual(write_cnf_to_string(f), expected)

    def test_basic_disjunction_output(self):
        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        f.Add(x | ~w)
        f.Add(~y | z)

        expected = (
            'p cnf 4 2\n' +
            '1 -4 0\n' +
            '-2 3 0\n'
        )
        self.assertEqual(write_cnf_to_string(f), expected)

    def test_basic_conjunction_output(self):
        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        f.Add(x & ~w)
        f.Add(~y & z)

        expected = (
            'p cnf 4 4\n' +
            '1 0\n' +
            '-4 0\n' +
            '-2 0\n' +
            '3 0\n'
        )
        self.assertEqual(write_cnf_to_string(f), expected)

    def test_trivial_sat(self):
        f = Formula()
        self.assertSat(f)

    def test_trivial_unsat(self):
        f = Formula()
        # All "False"s get suppressed, so this is acutally the empty clause.
        f.AddClause(False)
        self.assertUnsat(f)

    def test_empty_and(self):
        f = Formula()
        f.Add(And(*[]))
        self.assertSat(f)

    def test_empty_or(self):
        f = Formula()
        f.Add(Or(*[]))
        self.assertUnsat(f)

    def test_add_literals_sat(self):
        f = Formula()
        f.AddClause(True, False, False)
        f.AddClause(False, True)
        self.assertSat(f)

    def test_add_literals_unsat(self):
        f = Formula()
        f.AddClause(False, False)
        f.AddClause(True)
        self.assertUnsat(f)

    def test_disjunctive_cnf(self):
        f = Formula()
        x,y = f.AddVars('x y')
        f.Add(x | y)
        self.assertSat(f)
        f.Add(~x | ~y)
        self.assertSat(f)
        f.Add(~x | y)
        self.assertSat(f)
        f.Add(x | ~y)
        self.assertUnsat(f)

    def test_conjunctive_cnf(self):
        f = Formula()
        x = f.AddVar('x')
        self.assertSat(f)
        f.Add(~x & x)
        self.assertUnsat(f)

    def test_eq_cnf(self):
        f = Formula()
        x,y = f.AddVars('x y')
        f.Add(x == ~y)
        f.Add(x)
        f.Add(y)
        self.assertUnsat(f)

        f = Formula()
        x,y = f.AddVars('x y')
        f.Add(x == ~y)
        f.Add(x)
        f.Add(~y)
        self.assertSat(f)

        f = Formula()
        x,y,z = f.AddVars('x y z')
        f.Add(Eq(x,y))
        f.Add(x)
        f.Add(~y)
        self.assertUnsat(f)

        f = Formula()
        x,y,z = f.AddVars('x y z')
        f.Add(Eq(x,~z))
        f.Add(x)
        f.Add(~z)
        self.assertSat(f)

    def test_if_cnf(self):
        f = Formula()
        x,y = f.AddVars('x y')
        f.Add(If(x,y))
        f.Add(x)
        self.assertSat(f)
        f.Add(~y)
        self.assertUnsat(f)

    def test_if_subformula(self):
        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        f.Add(If(x,y) | ~(z & w))
        self.assertSat(f)

    def test_not_cnf(self):
        f = Formula()
        x,y = f.AddVars('x y')
        f.Add(~x | ~y)
        self.assertSat(f)
        f.Add(x)
        self.assertSat(f)
        f.Add(y)
        self.assertUnsat(f)

    def test_embedded_disjunction_in_conjunction(self):
        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        f.Add((x | y) & (z | w))
        self.assertSat(f)
        f.Add(~x)
        f.Add(~z)
        self.assertSat(f)
        f.Add(~y)
        self.assertUnsat(f)

    def test_embedded_conjunction_in_disjunction(self):
        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        f.Add((x & y) | (z & w))
        self.assertSat(f)
        f.Add(x)
        f.Add(~z)
        f.Add(~w)
        self.assertSat(f)
        f.Add(~y)
        self.assertUnsat(f)

    def test_cardinality_equality(self):
        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        f.Add(x)
        f.Add(~y)
        f.Add(z)
        f.Add(~w)
        self.assertSat(f)

        f.PushCheckpoint()
        f.Add(NumTrue(x,y,z,w) == 2)
        self.assertSat(f)
        f.PopCheckpoint()

        f.Add(2 == NumFalse(x,y,z,w))
        self.assertSat(f)

        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        f.Add(x)
        f.Add(~y)
        f.Add(~z)
        f.Add(~w)
        self.assertSat(f)

        f.PushCheckpoint()
        f.Add(2 == NumTrue(x,y,z,w))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.Add(NumFalse(x,y,z,w) == 2)
        self.assertUnsat(f)

        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        f.Add(x)
        f.Add(y)
        f.Add(~z)
        f.Add(w)
        self.assertSat(f)

        f.PushCheckpoint()
        f.Add(NumTrue(x,y,z,w) == 2)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.Add(NumFalse(x,y,z,w) == 2)
        self.assertUnsat(f)

    def test_cardinality_eq_zero(self):
        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        f.Add(~x)
        f.Add(~y)
        f.Add(z)
        f.Add(w)
        self.assertSat(f)

        f.PushCheckpoint()
        f.Add(NumTrue(x,y) == 0)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(NumTrue(x,y,z) == 0)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(NumFalse(z,w) == 0)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(NumFalse(x,y,z,w) == 0)
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_cardinality_inequality(self):
        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        f.Add(x)
        f.Add(~y)
        f.Add(z)
        f.Add(~w)
        self.assertSat(f)

        f.PushCheckpoint()
        f.Add(NumTrue(x,y,z,w) != 2)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.Add(NumFalse(x,y,z,w) != 2)
        self.assertUnsat(f)

        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        f.Add(x)
        f.Add(~y)
        f.Add(~z)
        f.Add(~w)
        self.assertSat(f)

        f.PushCheckpoint()
        f.Add(NumTrue(x,y,z,w) != 2)
        self.assertSat(f)
        f.PopCheckpoint()

        f.Add(NumFalse(x,y,z,w) != 2)
        self.assertSat(f)

        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        f.Add(x)
        f.Add(y)
        f.Add(~z)
        f.Add(w)
        self.assertSat(f)

        f.PushCheckpoint()
        f.Add(2 != NumTrue(x,y,z,w))
        self.assertSat(f)
        f.PopCheckpoint()

        f.Add(2 != NumFalse(x,y,z,w))
        self.assertSat(f)

    def test_cardinality_gt_gte(self):
        f = Formula()
        x,y,z,w,v = f.AddVars('x y z w v')
        f.Add(x)
        f.Add(~y)
        f.Add(z)
        f.Add(~w)
        f.Add(~v)
        self.assertSat(f)

        f.PushCheckpoint()
        f.Add(0 <= NumTrue(x,y,z,w,v))
        self.assertSat(f)
        f.Add(NumTrue(x,y,z,w,v) > 0)
        self.assertSat(f)
        f.Add(NumTrue(x,y,z,w,v) >= 1)
        self.assertSat(f)
        f.Add(NumTrue(x,y,z,w,v) > 1)
        self.assertSat(f)
        f.Add(NumTrue(x,y,z,w,v) >= 2)
        self.assertSat(f)
        f.Add(NumTrue(x,y,z,w,v) > 2)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(NumTrue(x,y,z,w,v) >= 3)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(0 <= NumFalse(x,y,z,w,v))
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) > 0)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) >= 1)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) > 1)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) >= 2)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) > 2)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) >= 3)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) > 3)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(NumFalse(x,y,z,w,v) >= 4)
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_cardinality_lt_lte(self):
        f = Formula()
        x,y,z,w,v = f.AddVars('x y z w v')
        f.Add(x)
        f.Add(y)
        f.Add(z)
        f.Add(~w)
        f.Add(v)
        self.assertSat(f)

        f.PushCheckpoint()
        f.Add(5 >= NumTrue(x,y,z,w,v))
        self.assertSat(f)
        f.Add(NumTrue(x,y,z,w,v) < 5)
        self.assertSat(f)
        f.Add(NumTrue(x,y,z,w,v) <= 4)
        self.assertSat(f)
        f.Add(NumTrue(x,y,z,w,v) < 4)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(NumTrue(x,y,z,w,v) <= 3)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(5 >= NumFalse(x,y,z,w,v))
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) < 5)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) <= 4)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) < 4)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) <= 3)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) < 3)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) <= 2)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) < 2)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) <= 1)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z,w,v) < 1)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(NumFalse(x,y,z,w,v) <= 0)
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_inequality_trivial(self):
        f = Formula()
        x,y,z = f.AddVars('x y z')
        f.Add(x)
        f.Add(~y)
        f.Add(z)

        f.Add(NumTrue(x,y,z) > -5)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z) >= -10)
        self.assertSat(f)
        f.Add(NumTrue(x,y,z) <= 100)
        self.assertSat(f)
        f.Add(NumFalse(x,y,z) <= 1024)
        self.assertSat(f)

    def test_tuple_equal_not_equal(self):
        f = Formula()
        dimension = 4
        x = [f.AddVar('x{}'.format(i)) for i in range(dimension)]
        y = [f.AddVar('y{}'.format(i)) for i in range(dimension)]

        f.PushCheckpoint()  # x[1] != y[1]
        f.Add(x[1])
        f.Add(~y[1])

        f.PushCheckpoint()
        f.Add(Tuple(*x) == Tuple(*y))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) != Tuple(*y))
        self.assertSat(f)
        f.PopCheckpoint()
        f.PopCheckpoint()  # x[1] != y[1]

        f.PushCheckpoint()  # all coords equal
        f.Add(~x[0])
        f.Add(~y[0])
        f.Add(x[1])
        f.Add(y[1])
        f.Add(~x[2])
        f.Add(~y[2])
        f.Add(x[3])
        f.Add(y[3])

        f.PushCheckpoint()
        f.Add(Tuple(*x) == Tuple(*y))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) != Tuple(*y))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PopCheckpoint()  # all coords equal

    def test_tuple_inequality(self):
        f = Formula()
        dimension = 5
        x = [f.AddVar('x{}'.format(i)) for i in range(dimension)]
        y = [f.AddVar('y{}'.format(i)) for i in range(dimension)]
        z = [f.AddVar('z{}'.format(i)) for i in range(dimension)]

        # x = 01011 (= 11)
        f.Add(~x[0]); f.Add(x[1]); f.Add(~x[2]); f.Add(x[3]); f.Add(x[4])
        # y = 01100 (= 12)
        f.Add(~y[0]); f.Add(y[1]); f.Add(y[2]); f.Add(~y[3]); f.Add(~y[4])
        # z = 01100 (= 12)
        f.Add(~z[0]); f.Add(z[1]); f.Add(z[2]); f.Add(~z[3]); f.Add(~z[4])

        f.PushCheckpoint()
        f.Add(Tuple(*x) < Tuple(*y))
        self.assertSat(f)
        f.Add(Tuple(*x) < Tuple(*z))
        self.assertSat(f)
        f.Add(Tuple(*y) > Tuple(*x))
        self.assertSat(f)
        f.Add(Tuple(*z) > Tuple(*x))
        self.assertSat(f)
        f.Add(Tuple(*x) <= Tuple(*y))
        self.assertSat(f)
        f.Add(Tuple(*x) <= Tuple(*z))
        self.assertSat(f)
        f.Add(Tuple(*y) >= Tuple(*x))
        self.assertSat(f)
        f.Add(Tuple(*z) >= Tuple(*x))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) > Tuple(*y))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) > Tuple(*z))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*y) < Tuple(*x))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*z) < Tuple(*x))
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_degenerate_tuple_inequality(self):
        f = Formula()
        true = f.AddVar()
        f.Add(true)

        f.PushCheckpoint()
        f.Add(Tuple() <= Tuple())
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple() < Tuple())
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple() < Tuple(true))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(true) < Tuple())
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(true) <= Tuple(true))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(true) <= Tuple())
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_composite_tuple_inequality(self):
        f = Formula()
        dimension = 3
        x = [f.AddVar('x{}'.format(i)) for i in range(dimension)]
        y = [f.AddVar('y{}'.format(i)) for i in range(dimension)]
        z = [f.AddVar('z{}'.format(i)) for i in range(dimension)]

        x_greater_than_y = Tuple(*x) > Tuple(*y)
        x_equal_to_z = Tuple(*x) == Tuple(*z)
        f.Add(x_greater_than_y | x_equal_to_z)
        self.assertSat(f)

        f.PushCheckpoint()  # x <= y and x != z
        # x = 010 (= 2)
        f.Add(~x[0]); f.Add(x[1]); f.Add(~x[2])
        # y = 011 (= 3)
        f.Add(~y[0]); f.Add(y[1]); f.Add(y[2])
        # z = 101 (= 5)
        f.Add(z[0]); f.Add(~z[1]); f.Add(z[2])
        self.assertUnsat(f)
        f.PopCheckpoint()  # x <= y and x != z

        f.PushCheckpoint() # x > y and x != z
        # x = 010 (= 2)
        f.Add(~x[0]); f.Add(x[1]); f.Add(~x[2])
        # y = 001 (= 1)
        f.Add(~y[0]); f.Add(~y[1]); f.Add(y[2])
        # z = 111 (= 7)
        f.Add(z[0]); f.Add(z[1]); f.Add(z[2])
        self.assertSat(f)
        f.PopCheckpoint() # x > y and x != z

        f.PushCheckpoint() # x <= y and x == z
        # x = 100 (= 4)
        f.Add(x[0]); f.Add(~x[1]); f.Add(~x[2])
        # y = 110 (= 6)
        f.Add(y[0]); f.Add(y[1]); f.Add(~y[2])
        # z = 100 (= 4)
        f.Add(z[0]); f.Add(~z[1]); f.Add(~z[2])
        self.assertSat(f)
        f.PopCheckpoint() # x <= y and x == z

    def test_integer_comparision(self):
        f = Formula()
        bits = 8
        x = [f.AddVar('x{}'.format(i)) for i in range(bits)]
        # x = 00001010 (= 10)
        f.Add(~x[0]); f.Add(~x[1]); f.Add(~x[2]); f.Add(~x[3])
        f.Add(x[4]);  f.Add(~x[5]); f.Add(x[6]);  f.Add(~x[7])

        f.PushCheckpoint()
        f.Add(Tuple(*x) == 10)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) != 11)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) > 9)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) < 12)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(15 == Tuple(*x))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) != 10)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) > 99)
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) < 1)
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_integer_addition_basic(self):
        f = Formula()
        x1, x0 = f.AddVars('x1 x0')
        f.Add(x1); f.Add(~x0)

        # (x1,x0) == 10b == 2. Does this equal 1 + 1?

        f.PushCheckpoint()
        f.Add(Tuple(x1, x0) == Integer(1) + Integer(1))
        self.assertSat(f)
        f.PopCheckpoint()

    def test_degenerate_integer_addition(self):
        f = Formula()
        true = f.AddVar()
        false = f.AddVar()
        f.Add(true)
        f.Add(~false)

        f.PushCheckpoint()
        f.Add(Tuple() + Tuple() == 0)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(true) + Tuple() == 1)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(false) + Tuple() == 0)
        self.assertSat(f)
        f.PopCheckpoint()

    def test_integer_arithmetic(self):
        f = Formula()
        bits = 8
        x = [f.AddVar('x{}'.format(i)) for i in range(bits)]

        # x = 00001010 (== 10). Does this equal 5 + 5?

        f.Add(~x[0]); f.Add(~x[1]); f.Add(~x[2]); f.Add(~x[3])
        f.Add(x[4]);  f.Add(~x[5]); f.Add(x[6]);  f.Add(~x[7])

        f.PushCheckpoint()
        f.Add(Integer(*x) == Integer(5) + Integer(5))
        self.assertSat(f)
        f.PopCheckpoint()

    def test_addition_exhaustive(self):
        f = Formula()
        # Test addition of all numbers x + y where x,y < 8
        limit = 8
        for x in range(limit):
            for y in range(limit):
                f.PushCheckpoint()
                f.Add(Integer(x+y) == Integer(x) + Integer(y))
                self.assertSat(f)
                f.PopCheckpoint()

                f.PushCheckpoint()
                f.Add(Integer(x+y+1) == Integer(x) + Integer(y))
                self.assertUnsat(f)
                f.PopCheckpoint()

                if x > 0 and y > 0:
                    f.PushCheckpoint()
                    f.Add(Integer(x+y-1) == Integer(x) + Integer(y))
                    self.assertUnsat(f)
                    f.PopCheckpoint()

    def test_integer_multiplication_basic(self):
        f = Formula()
        x2, x1, x0 = f.AddVars('x2 x1 x0')
        f.Add(x2); f.Add(~x1); f.Add(~x0)

        # (x2,x1,x0) == 100b == 4. Does this equal 2 * 2?

        f.PushCheckpoint()
        f.Add(Integer(x2, x1, x0) == Integer(2) * Integer(2))
        self.assertSat(f)
        f.PopCheckpoint()

    def test_degenerate_integer_multiplication(self):
        f = Formula()
        true = f.AddVar()
        false = f.AddVar()
        f.Add(true)
        f.Add(~false)

        f.PushCheckpoint()
        f.Add(Tuple() * Tuple() == 0)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(true) * Tuple() == 0)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(false) * Tuple() == 0)
        self.assertSat(f)
        f.PopCheckpoint()

    def test_multiplication_exhaustive(self):
        f = Formula()
        # Test multiplication of all numbers x * y where x,y < 8
        limit = 8
        for x in range(limit):
            for y in range(limit):
                f.PushCheckpoint()
                f.Add(Integer(x*y) == Integer(x) * Integer(y))
                self.assertSat(f)
                f.PopCheckpoint()

                f.PushCheckpoint()
                f.Add(Integer(x*y+1) == Integer(x) * Integer(y))
                self.assertUnsat(f)
                f.PopCheckpoint()

                if x > 0 and y > 0:
                    f.PushCheckpoint()
                    f.Add(Integer(x*y-1) == Integer(x) * Integer(y))
                    self.assertUnsat(f)
                    f.PopCheckpoint()

    def test_integer_division_basic(self):
        f = Formula()
        x1, x0 = f.AddVars('x1 x0')
        f.Add(x1); f.Add(x0)
        three = Integer(x1, x0)  # (x1, x0) == 11b == 3

        f.PushCheckpoint()
        f.Add(three == Integer(21) // Integer(7))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(three == Integer(22) // Integer(7))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(three == Integer(28) // Integer(7))
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_integer_mod_basic(self):
        f = Formula()
        a,b,c,d,e,g = f.AddVars('a b c d e g')
        f.Add(~a); f.Add(~b)
        zero = Integer(a, b)  # (a, b) == 00b == 0

        f.Add(~c); f.Add(d)
        one = Integer(c, d)  # (c, d) == 01b == 1

        f.Add(e); f.Add(~g)
        two = Integer(e, g)  # (e, g) == 10b == 2

        f.PushCheckpoint()
        f.Add(zero == Integer(21) % Integer(3))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(one == Integer(22) % Integer(3))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(two == Integer(23) % Integer(3))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(one == Integer(23) % Integer(3))
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_integer_rmod(self):
        f = Formula()
        num_bits = 1
        divisor = Integer(*(f.AddVar(f'divisor:{i}') for i in range(num_bits)))
        num2 = Integer(*(f.AddVar(f'cell:{i}') for i in range(num_bits)))
        f.Add(2 % divisor == 0)
        f.Add(num2 % divisor == 0)
        self.assertSat(f)

    def test_integer_mod_multi_infer(self):
        formula = Formula()
        num_bits = 2
        num1 = Integer(*(formula.AddVar(f'num1:{i}') for i in range(num_bits)))
        divisor = Integer(*(formula.AddVar(f'divisor:{i}') for i in range(num_bits)))
        formula.Add(num1 == 2)
        formula.Add((num1 * 4) % divisor == 0)

        #print(write_cnf_to_string(formula))

        # Note: looking at CNF output, there's some contradiction in variable 2, possibly chained to var 60?

        self.assertSat(formula)

    def test_integer_mult_infer(self):
        formula = Formula()
        num_bits = 2
        num1 = Integer(*(formula.AddVar(f'num1:{i}') for i in range(num_bits)))
        divisor = Integer(*(formula.AddVar(f'divisor:{i}') for i in range(num_bits)))
        formula.Add(num1 == 2)
        x = Integer(*[formula.AddVar(f'x:{i}') for i in range(num_bits)])
        formula.Add(divisor * x == (num1 * 4))
        #print(write_cnf_to_string(formula))
        self.assertSat(formula)


    def test_integer_division_by_zero(self):
        f = Formula()
        f.Add(Integer(1) // Integer(0) == Integer(0))
        self.assertUnsat(f)

    def test_integer_mod_by_zero(self):
        f = Formula()
        f.Add(Integer(1) % Integer(0) == Integer(0))
        self.assertUnsat(f)

    def test_integer_division_exhaustive(self):
        f = Formula()

        dividend_limit = 12
        divisor_limit = 5
        for x in range(dividend_limit):
            for y in range(1, divisor_limit):
                f.PushCheckpoint()
                f.Add(Integer(x // y) == Integer(x) // Integer(y))
                self.assertSat(f)
                f.PopCheckpoint()

                f.PushCheckpoint()
                f.Add(Integer(x // y + 1) == Integer(x) // Integer(y))
                self.assertUnsat(f)
                f.PopCheckpoint()

                if x // y > 0:
                    f.PushCheckpoint()
                    f.Add(Integer(x // y - 1) == Integer(x) // Integer(y))
                    self.assertUnsat(f)
                    f.PopCheckpoint()

    def test_integer_division_exhaustive(self):
        f = Formula()

        dividend_limit = 12
        mod_limit = 5
        for x in range(dividend_limit):
            for y in range(1, mod_limit):
                f.PushCheckpoint()
                f.Add(Integer(x % y) == Integer(x) % Integer(y))
                self.assertSat(f)
                f.PopCheckpoint()

                f.PushCheckpoint()
                f.Add(Integer(x % y + 1) == Integer(x) % Integer(y))
                self.assertUnsat(f)
                f.PopCheckpoint()

                if x % y > 0:
                    f.PushCheckpoint()
                    f.Add(Integer(x % y - 1) == Integer(x) % Integer(y))
                    self.assertUnsat(f)
                    f.PopCheckpoint()

    def test_pow_basic(self):
        f = Formula()
        f.PushCheckpoint()
        f.Add(Integer(2) ** 5 == 32)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Integer(2) ** 5 == 33)
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_pow_mod(self):
        f = Formula()
        f.PushCheckpoint()
        f.Add(Integer(2) ** 10 % 3 == 1)
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Integer(2) ** 10 % 3 == 2)
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_tuple_ternary(self):
        f = Formula()
        w = f.AddVar()

        f.PushCheckpoint()
        f.Add(w)
        f.Add(Integer(3) == If(w, Integer(3), Integer(4)))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(w)
        f.Add(Integer(4) == If(~w, Integer(3), Integer(4)))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(~w)
        f.Add(Integer(100) == If(~w, Integer(1), Integer(100)))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(~w)
        f.Add(Integer(100) == If(w, Integer(1), Integer(100)))
        self.assertSat(f)
        f.PopCheckpoint()

    def test_boolean_ternary(self):
        f = Formula()
        a,b,c,d,e = f.AddVars('a b c d e')
        f.Add(a); f.Add(b); f.Add(c); f.Add(d); f.Add(e)

        f.PushCheckpoint()
        f.Add(If(a, b & c, ~d & e))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(If(~a, b & c, ~d & e))
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_composite_cardinality_test(self):
        f = Formula()
        a,b,c,d,e = f.AddVars('a b c d e')
        f.Add(a)
        f.Add(~b)
        f.Add(c)
        f.Add(~d)
        f.Add(e)

        f.PushCheckpoint()
        f.Add((NumTrue(a,b,c) == 2) & (NumFalse(b,d,c,e) == 2))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add((NumTrue(a,b,c) == 2) & (NumFalse(b,d,c,e) == 3))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add((NumTrue(a,b,c) == 3) & (NumFalse(b,d,c,e) == 2))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add((NumTrue(a,c,e) > 2) | (NumFalse(a,b,c,d,e) < 3))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add((NumTrue(a,c,e,b) > 3) | (NumFalse(a,b,c,d,e) < 3))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add((NumTrue(a,c,e) > 2) | (NumFalse(a,b,c,d,e) < 1))
        self.assertSat(f)
        f.PopCheckpoint()

    def test_regex_match_simple(self):
        f = Formula()
        bits = 8
        x = [f.AddVar('x{}'.format(i)) for i in range(bits)]
        # x = 00111010
        f.Add(~x[0]); f.Add(~x[1]); f.Add(x[2]); f.Add(x[3])
        f.Add(x[4]);  f.Add(~x[5]); f.Add(x[6]);  f.Add(~x[7])

        f.PushCheckpoint()
        f.Add(RegexMatch(Tuple(*x), "0+1+010"))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(RegexMatch(Tuple(*x), "0+1+0+"))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(RegexMatch(Tuple(*x), "0*1110*10*"))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(RegexMatch(Tuple(*x), "(0|1)+"))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(RegexMatch(Tuple(*x), "1(0|1)+"))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(RegexMatch(Tuple(*x), "00111010"))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(RegexMatch(Tuple(*x), "001110100"))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(RegexMatch(Tuple(*x), "0011101"))
        self.assertUnsat(f)
        f.PopCheckpoint()

    def test_regex_match_composite_tuples(self):
        f = Formula()

        # Assert that 3 + 13 is a power of 2.
        f.PushCheckpoint()
        f.Add(RegexMatch(Integer(3) + Integer(13), "0*10*"))
        self.assertSat(f)
        f.PopCheckpoint()

        # 8 is also a power of 2
        f.PushCheckpoint()
        f.Add(RegexMatch(Integer(2) * Integer(2) * Integer(2), "0*10*"))
        self.assertSat(f)
        f.PopCheckpoint()

        # 127 is not a power of 2
        f.PushCheckpoint()
        f.Add(RegexMatch(Integer(125) + Integer(1) + Integer(1), "0*10*"))
        self.assertUnsat(f)
        f.PopCheckpoint()

if __name__ == '__main__':
    unittest.main()
