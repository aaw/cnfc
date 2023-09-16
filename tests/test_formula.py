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
        self.assertEqual(repr(Implies(NumTrue(x,y) == 0, z & w)), 'Implies(NumEq(NumTrue(Var(x,1),Var(y,2)),0),And(Var(z,3),Var(w,4)))')

    def test_tuple_parsing(self):
        f = Formula()
        xs = f.AddVars('x1 x2 x3')
        ys = f.AddVars('y1 y2 y3')
        zs = f.AddVars('z1 z2')
        self.assertEqual(repr(Tuple(*xs) < Tuple(*ys)), 'TupleLt(Tuple(Var(x1,1),Var(x2,2),Var(x3,3)),Tuple(Var(y1,4),Var(y2,5),Var(y3,6)))')

        with self.assertRaises(AssertionError):
            Tuple(*xs) >= Tuple(*zs)

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

    def test_implies_cnf(self):
        f = Formula()
        x,y = f.AddVars('x y')
        f.Add(Implies(x,y))
        f.Add(x)
        self.assertSat(f)
        f.Add(~y)
        self.assertUnsat(f)

    def test_implies_subformula(self):
        f = Formula()
        x,y,z,w = f.AddVars('x y z w')
        f.Add(Implies(x,y) | ~(z & w))
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
        f.Add(Tuple(*x) == Integer(10, 8))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) != Integer(11, 8))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) > Integer(9, 8))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) < Integer(12, 8))
        self.assertSat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Integer(15,8) == Tuple(*x))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) != Integer(10, 8))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) > Integer(99, 8))
        self.assertUnsat(f)
        f.PopCheckpoint()

        f.PushCheckpoint()
        f.Add(Tuple(*x) < Integer(1, 8))
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

if __name__ == '__main__':
    unittest.main()
