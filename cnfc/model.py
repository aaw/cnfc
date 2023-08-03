# Data model

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

    def generate_var(self, formula):
        # TODO
        pass

    def generate_cnf(self, formula):
        yield Not(self.expr.generate_var())

class OrderedBinaryBoolExpr(BoolExpr):
    def __init__(self, first, second):
        self.first, self.second = first, second

    def __repr__(self):
        return '{}({},{})'.format(self.__class__.__name__, self.first, self.second)

class Implies(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        # TODO
        pass

    def generate_cnf(self, formula):
        fv = self.first.generate_var(formula)
        sv = self.second.generate_var(formula)
        yield (Not(fv), sv)

class Eq(MultiBoolExpr):
    def generate_var(self, formula):
        # TODO
        pass

    def generate_cnf(self, formula):
        # TODO
        pass

class And(MultiBoolExpr):
    def generate_var(self, formula):
        # TODO
        pass

    def generate_cnf(self, formula):
        for expr in self.exprs:
            yield (expr.generate_var(formula),)

class Or(MultiBoolExpr):
    def generate_var(self, formula):
        # TODO
        pass

    def generate_cnf(self, formula):
        yield tuple(expr.generate_var(formula) for expr in self.exprs)

class Lt(OrderedBinaryBoolExpr): pass
class Le(OrderedBinaryBoolExpr): pass
class Gt(OrderedBinaryBoolExpr): pass
class Ge(OrderedBinaryBoolExpr): pass

class Tuple:
    def __init__(self, *exprs):
        self.exprs = exprs
        for expr in self.exprs:
            assert issubclass(type(expr), BoolExpr), "{} needs boolean expressions, got {}".format(self.__class__.__name__, expr)

    def __check_length(self, other: 'Tuple'):
        assert len(self) == len(other), "Can't compare tuples of different dimensions: {} vs. {}".format(self, other)

    def __len__(self):
        return len(self.exprs)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ','.join(repr(e) for e in self.exprs))

    def __eq__(self, other: 'Tuple'):
        self.__check_length(other)
        return Eq(self, other)

    def __ne__(self, other: 'Tuple'):
        self.__check_length(other)
        return Not(Eq(self, other))

    def __lt__(self, other: 'Tuple'):
        self.__check_length(other)
        return Lt(self, other)

    def __le__(self, other: 'Tuple'):
        self.__check_length(other)
        return Le(self, other)

    def __gt__(self, other: 'Tuple'):
        self.__check_length(other)
        return Gt(self, other)

    def __ge__(self, other: 'Tuple'):
        self.__check_length(other)
        return Ge(self, other)

# TODO: implement canonical_form method for all Exprs so we can cache them correctly.
#       for now, we just cache based on repr

# Return the Var that holds the value of this expr, or None if there is none
# TODO: make this a decorator that can wrap generate_var for each class
def get_var(expr):
    if isinstance(expr, Var):
        return expr
    else:
        return getattr(expr, '_var', None)

def register_var(expr, v):
    expr._var = v
