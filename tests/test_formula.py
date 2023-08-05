from cnfc import *
from dpll import Satisfiable
import io
import unittest

def write_cnf_to_string(f):
    out = io.StringIO()
    f.WriteCNF(out)
    out.seek(0)
    return out.read()

class TestFormula(unittest.TestCase):
    def assertSat(self, formula):
        self.assertTrue(Satisfiable(write_cnf_to_string(formula)))

    def assertUnsat(self, formula):
        self.assertFalse(Satisfiable(write_cnf_to_string(formula)))

    def test_add_variables(self):
        f = Formula()
        x = f.AddVar('x')
        y,z,w = f.AddVars('y,z,w')
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
        x,y,z,w = f.AddVars('x,y,z,w')
        c = (~x == y) & ((z != w) | x)
        self.assertEqual(repr(c), 'And(Eq(Literal(Var(x,1),-1),Var(y,2)),Or(Not(Eq(Var(z,3),Var(w,4))),Var(x,1)))')

    def test_numeric_expr_parsing(self):
        f = Formula()
        x,y,z,w = f.AddVars('x,y,z,w')
        self.assertEqual(repr(NumFalse(x,y,z) == 2), 'Eq(NumFalse(Var(x,1),Var(y,2),Var(z,3)),2)')
        self.assertEqual(repr(3 > NumTrue(x,y,z,w)), 'Lt(NumTrue(Var(x,1),Var(y,2),Var(z,3),Var(w,4)),3)')
        self.assertEqual(repr(Implies(NumTrue(x,y) == 0, z & w)), 'Implies(Eq(NumTrue(Var(x,1),Var(y,2)),0),And(Var(z,3),Var(w,4)))')

    def test_tuple_parsing(self):
        f = Formula()
        xs = f.AddVars('x1,x2,x3')
        ys = f.AddVars('y1,y2,y3')
        zs = f.AddVars('z1,z2')
        self.assertEqual(repr(Tuple(*xs) < Tuple(*ys)), 'Lt(Tuple(Var(x1,1),Var(x2,2),Var(x3,3)),Tuple(Var(y1,4),Var(y2,5),Var(y3,6)))')

        with self.assertRaises(AssertionError):
            Tuple(*xs) >= Tuple(*zs)

    def test_implicit_disjunction_output(self):
        f = Formula()
        x,y,z,w = f.AddVars('x,y,z,w')
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
        x,y,z,w = f.AddVars('x,y,z,w')
        f.AddClause(x | ~w)
        f.AddClause(~y | z)

        expected = (
            'p cnf 4 2\n' +
            '1 -4 0\n' +
            '-2 3 0\n'
        )
        self.assertEqual(write_cnf_to_string(f), expected)

    def test_basic_conjunction_output(self):
        f = Formula()
        x,y,z,w = f.AddVars('x,y,z,w')
        f.AddClause(x & ~w)
        f.AddClause(~y & z)

        expected = (
            'p cnf 4 4\n' +
            '1 0\n' +
            '-4 0\n' +
            '-2 0\n' +
            '3 0\n'
        )
        self.assertEqual(write_cnf_to_string(f), expected)

    def test_disjunctive_cnf(self):
        f = Formula()
        x,y = f.AddVars('x,y')
        f.AddClause(x | y)
        self.assertSat(f)
        f.AddClause(~x | ~y)
        self.assertSat(f)
        f.AddClause(~x | y)
        self.assertSat(f)
        f.AddClause(x | ~y)
        self.assertUnsat(f)

    def test_conjunctive_cnf(self):
        f = Formula()
        x = f.AddVar('x')
        self.assertSat(f)
        f.AddClause(~x & x)
        self.assertUnsat(f)

    def test_eq_cnf(self):
        f = Formula()
        x,y = f.AddVars('x,y')
        f.AddClause(x == ~y)
        f.AddClause(x)
        f.AddClause(y)
        self.assertUnsat(f)

        f = Formula()
        x,y = f.AddVars('x,y')
        f.AddClause(x == ~y)
        f.AddClause(x)
        f.AddClause(~y)
        self.assertSat(f)

        f = Formula()
        x,y,z = f.AddVars('x,y,z')
        f.AddClause(Eq(x,y,z))
        f.AddClause(x)
        f.AddClause(~y)
        self.assertUnsat(f)

        f = Formula()
        x,y,z = f.AddVars('x,y,z')
        f.AddClause(Eq(x,y,~z))
        f.AddClause(x)
        f.AddClause(y)
        f.AddClause(~z)
        self.assertSat(f)

    def test_implies_cnf(self):
        f = Formula()
        x,y = f.AddVars('x,y')
        f.AddClause(Implies(x,y))
        f.AddClause(x)
        self.assertSat(f)
        f.AddClause(~y)
        self.assertUnsat(f)

    def test_not_cnf(self):
        f = Formula()
        x,y = f.AddVars('x,y')
        f.AddClause(~x | ~y)
        self.assertSat(f)
        f.AddClause(x)
        self.assertSat(f)
        f.AddClause(y)
        self.assertUnsat(f)

    def test_embedded_disjunction_in_conjunction(self):
        f = Formula()
        x,y,z,w = f.AddVars('x,y,z,w')
        f.AddClause((x | y) & (z | w))
        self.assertSat(f)
        f.AddClause(~x)
        f.AddClause(~z)
        self.assertSat(f)
        f.AddClause(~y)
        self.assertUnsat(f)

    def test_embedded_conjunction_in_disjunction(self):
        f = Formula()
        x,y,z,w = f.AddVars('x,y,z,w')
        f.AddClause((x & y) | (z & w))
        self.assertSat(f)
        f.AddClause(x)
        f.AddClause(~z)
        f.AddClause(~w)
        self.assertSat(f)
        f.AddClause(~y)
        self.assertUnsat(f)

if __name__ == '__main__':
    unittest.main()
