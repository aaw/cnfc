# class SimpleEq:
#     def __eq__(self, other):
#         return type(other) is type(self) and self._members() == other._members()

#     def __hash__(self):
#         return hash(self._members())

class BoolExpr:
    def __eq__(self, other):
        return Eq(self, other)

    def __ne__(self, other):
        return Not(Eq(self, other))

    def __invert__(self):
        return Not(self)

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

class NumExpr:
    def __eq__(self, other):
        return Eq(self, other)

    def __ne__(self, other):
        return Not(Eq(self, other))

    def __lt__(self, other):
        return Lt(self, other)

    def __le__(self, other):
        return Le(self, other)

    def __gt__(self, other):
        return Gt(self, other)

    def __ge__(self, other):
        return Ge(self, other)

class NumTrue(NumExpr):
    def __init__(self, *exprs):
        if len(exprs) == 1 and type(exprs) == list:
            self.exprs = exprs[0]
        else:
            self.exprs = exprs
        for expr in self.exprs:
            assert issubclass(type(expr), BoolExpr), "NumTrue needs a boolean argument, got {}".format(expr)

    def __repr__(self):
        return 'NumTrue({})'.format(','.join(repr(e) for e in self.exprs))

class NumFalse(NumExpr):
    def __init__(self, *exprs):
        if len(exprs) == 1 and type(exprs) == list:
            self.exprs = exprs[0]
        else:
            self.exprs = exprs
        for expr in self.exprs:
            assert issubclass(type(expr), BoolExpr), "NumFalse needs a boolean argument, got {}".format(expr)

    def __repr__(self):
        return 'NumFalse({})'.format(','.join(repr(e) for e in self.exprs))

class Var(BoolExpr):
    def __init__(self, name, vid):
        self.name = name
        self.vid = vid

    def __repr__(self):
        return 'Var({},{})'.format(self.name, self.vid)

class Eq(BoolExpr):
    def __init__(self, *exprs):
        self.exprs = exprs

    def __repr__(self):
        return 'Eq({})'.format(','.join(repr(expr) for expr in self.exprs))

class Not(BoolExpr):
    def __init__(self, var):
        self.var = var

    def __repr__(self):
        return 'Not({})'.format(self.var)

class And(BoolExpr):
    def __init__(self, *exprs):
        self.exprs = exprs

    def __repr__(self):
        return 'And({})'.format(','.join(repr(expr) for expr in self.exprs))

class Or(BoolExpr):
    def __init__(self, *exprs):
        self.exprs = exprs

    def __repr__(self):
        return 'Or({})'.format(','.join(repr(expr) for expr in self.exprs))

class Lt(BoolExpr):
    def __init__(self, *exprs):
        self.exprs = exprs

    def __repr__(self):
        return 'Lt({})'.format(','.join(repr(expr) for expr in self.exprs))

class Le(BoolExpr):
    def __init__(self, *exprs):
        self.exprs = exprs

    def __repr__(self):
        return 'Le({})'.format(','.join(repr(expr) for expr in self.exprs))

class Gt(BoolExpr):
    def __init__(self, *exprs):
        self.exprs = exprs

    def __repr__(self):
        return 'Gt({})'.format(','.join(repr(expr) for expr in self.exprs))

class Ge(BoolExpr):
    def __init__(self, *exprs):
        self.exprs = exprs

    def __repr__(self):
        return 'Ge({})'.format(','.join(repr(expr) for expr in self.exprs))

class Formula:
    def __init__(self):
        self.vars = {}
        self.clauses = []
        self.nextvar = 1

    def AddVar(self, name=None):
        if name is None:
            name = '_' + str(self.nextvar)
        if self.vars.get(name) is not None:
            raise ValueError('Variable already exists in formula')
        vid = self.nextvar
        self.vars[name] = vid
        self.nextvar += 1
        return Var(name, vid)

    def AddVars(self, names):
        return (self.AddVar(name.strip()) for name in names.split(','))

    def AddClause(self, clause):
        pass

    def AddClauses(self, clauses):
        for clause in clauses:
            self.AddClause(clause)
