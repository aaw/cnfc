from cnfc import *
import unittest

class TestFormula(unittest.TestCase):
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
        self.assertEqual(repr(c), 'And(Eq(Not(Var(x,1)),Var(y,2)),Or(Not(Eq(Var(z,3),Var(w,4))),Var(x,1)))')

    def test_numeric_expr_parsing(self):
        f = Formula()
        x,y,z,w = f.AddVars('x,y,z,w')
        self.assertEqual(repr(NumFalse(x,y,z) == 2), 'Eq(NumFalse(Var(x,1),Var(y,2),Var(z,3)),2)')
        self.assertEqual(repr(3 > NumTrue(x,y,z,w)), 'Lt(NumTrue(Var(x,1),Var(y,2),Var(z,3),Var(w,4)),3)')
        self.assertEqual(repr(Implies(NumTrue(x,y) == 0, z & w)), 'Implies(Eq(NumTrue(Var(x,1),Var(y,2)),0),And(Var(z,3),Var(w,4)))')

if __name__ == '__main__':
    unittest.main()
