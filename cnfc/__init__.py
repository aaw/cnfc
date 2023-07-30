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

class CountingRelation(NumExpr):
    def __init__(self, *exprs):
        self.exprs = exprs
        for expr in self.exprs:
            assert issubclass(type(expr), BoolExpr), "{} needs boolean expressions, got {}".format(self.__class__.__name__, expr)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ','.join(repr(e) for e in self.exprs))

class NumTrue(CountingRelation): pass
class NumFalse(CountingRelation): pass

class Var(BoolExpr):
    def __init__(self, name, vid):
        self.name = name
        self.vid = vid

    def __repr__(self):
        return 'Var({},{})'.format(self.name, self.vid)

class MultiBoolExpr(BoolExpr):
    def __init__(self, *exprs):
        self.exprs = exprs

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ','.join(repr(expr) for expr in self.exprs))

class Not(BoolExpr):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return 'Not({})'.format(self.expr)

class Implies(BoolExpr):
    def __init__(self, antecedent, consequent) :
        self.antecedent, self.consequent = antecedent, consequent

    def __repr__(self):
        return 'Implies({},{})'.format(self.antecedent, self.consequent)

class Eq(MultiBoolExpr): pass
class And(MultiBoolExpr): pass
class Or(MultiBoolExpr): pass
class Lt(MultiBoolExpr): pass
class Le(MultiBoolExpr): pass
class Gt(MultiBoolExpr): pass
class Ge(MultiBoolExpr): pass

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
