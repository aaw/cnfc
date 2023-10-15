class BoolExpr:
    def __eq__(self, other):
        return Eq(self, other)

    def __ne__(self, other):
        return Neq(self, other)

    def __invert__(self):
        return Not(self)

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

class NumExpr:
    def __eq__(self, other):
        return NumEq(self, other)

    def __ne__(self, other):
        return NumNeq(self, other)

    def __lt__(self, other):
        return NumLt(self, other)

    def __le__(self, other):
        return NumLe(self, other)

    def __gt__(self, other):
        return NumGt(self, other)

    def __ge__(self, other):
        return NumGe(self, other)

class Literal(BoolExpr):
    def __init__(self, var, sign):
        self.var, self.sign = var, sign

    def __repr__(self):
        return 'Literal({},{})'.format(self.var, self.sign)

    def __invert__(self):
        return Literal(self.var, sign=-self.sign)

    def generate_var(self, formula):
        return self

    def generate_cnf(self, formula):
        yield (self,)

class Var(BoolExpr):
    def __init__(self, name, vid):
        self.name = name
        self.vid = vid

    def __repr__(self):
        return 'Var({},{})'.format(self.name, self.vid)

    def __invert__(self):
        return Literal(self, sign=-1)

    def generate_var(self, formula):
        return Literal(self, sign=1)

    def generate_cnf(self, formula):
        yield (self,)

class BooleanLiteral:
    def __init__(self, val):
        assert type(val) == bool
        self.val = val

    def __repr__(self):
        return 'BooleanLiteral({})'.format(self.val)

    def __invert__(self):
        return BooleanLiteral(not self.val)

    def generate_var(self, formula):
        return self

    def generate_cnf(self, formula):
        yield (self,)
