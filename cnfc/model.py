# Data model
from .cardinality import exactly_n_true, not_exactly_n_true, at_least_n_true, at_most_n_true
from .tuples import tuple_less_than

# A generic way to implement generate_var from a generate_cnf implementation.
# Not always the most efficient, but a good fallback.
def generate_var_from_cnf(instance, formula):
    vars_to_and = []
    for clause in instance.generate_cnf(formula):
        v = formula.AddVar()
        vars_to_and.append(v)
        formula.AddClause(~v, *clause)
        for cv in clause:
            formula.AddClause(v, ~cv)

    return And(*vars_to_and).generate_var(formula)

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

class CardinalityConstraint(NumExpr):
    def __init__(self, *exprs):
        self.exprs = exprs
        for expr in self.exprs:
            assert issubclass(type(expr), BoolExpr), "{} needs boolean expressions, got {}".format(self.__class__.__name__, expr)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ','.join(repr(e) for e in self.exprs))

class NumTrue(CardinalityConstraint): pass
class NumFalse(CardinalityConstraint): pass

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
        return ~self.expr.generate_var(formula)

    def generate_cnf(self, formula):
        yield ~self.expr.generate_var(formula)

class OrderedBinaryBoolExpr(BoolExpr):
    def __init__(self, first, second):
        self.first, self.second = first, second

    def __repr__(self):
        return '{}({},{})'.format(self.__class__.__name__, self.first, self.second)

class Implies(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        return Or(Not(self.first), self.second).generate_var(formula)

    def generate_cnf(self, formula):
        fv = self.first.generate_var(formula)
        sv = self.second.generate_var(formula)
        yield (~fv, sv)

class And(MultiBoolExpr):
    def generate_var(self, formula):
        v = formula.AddVar()
        subvars = [expr.generate_var(formula) for expr in self.exprs]
        formula.AddClause(*([~sv for sv in subvars] + [v]))
        for subvar in subvars:
            formula.AddClause(~v, subvar)
        return v

    def generate_cnf(self, formula):
        for expr in self.exprs:
            yield (expr.generate_var(formula),)

class Or(MultiBoolExpr):
    def generate_var(self, formula):
        v = formula.AddVar()
        subvars = [expr.generate_var(formula) for expr in self.exprs]
        formula.AddClause(*(subvars + [~v]))
        for subvar in subvars:
            formula.AddClause(v, ~subvar)
        return v

    def generate_cnf(self, formula):
        yield tuple(expr.generate_var(formula) for expr in self.exprs)

class Eq(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        v = formula.AddVar()
        fv = self.first.generate_var(formula)
        sv = self.second.generate_var(formula)
        formula.AddClause(~fv, ~sv, v)
        formula.AddClause(fv, sv, v)
        formula.AddClause(fv, ~sv, ~v)
        formula.AddClause(~fv, sv, ~v)
        return v

    def generate_cnf(self, formula):
        fv = self.first.generate_var(formula)
        sv = self.second.generate_var(formula)
        yield (~fv, sv)
        yield (~sv, fv)

class Neq(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        v = formula.AddVar()
        fv = self.first.generate_var(formula)
        sv = self.second.generate_var(formula)
        formula.AddClause(~fv, ~sv, ~v)
        formula.AddClause(fv, sv, ~v)
        formula.AddClause(fv, ~sv, v)
        formula.AddClause(~fv, sv, v)
        return v

    def generate_cnf(self, formula):
        fv = self.first.generate_var(formula)
        sv = self.second.generate_var(formula)
        yield (fv, sv)
        yield (~fv, ~sv)

class NumEq(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        assert type(self.second) is int, "Cardinality comparisons require integers"
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            n = self.second
        elif isinstance(self.first, NumFalse):
            n = len(vars) - self.second
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")
        yield from exactly_n_true(formula, vars, n)

class NumNeq(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        assert type(self.second) is int, "Cardinality comparisons require integers"
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            n = self.second
        elif isinstance(self.first, NumFalse):
            n = len(vars) - self.second
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")
        yield from not_exactly_n_true(formula, vars, n)

class NumLt(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        assert type(self.second) is int, "Cardinality comparisons require integers"
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            yield from at_most_n_true(formula, vars, self.second-1)
        elif isinstance(self.first, NumFalse):
            yield from at_least_n_true(formula, vars, len(vars) - self.second + 1)
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")

class NumLe(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        assert type(self.second) is int, "Cardinality comparisons require integers"
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            yield from at_most_n_true(formula, vars, self.second)
        elif isinstance(self.first, NumFalse):
            yield from at_least_n_true(formula, vars, len(vars) - self.second)
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")

class NumGt(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        assert type(self.second) is int, "Cardinality comparisons require integers"
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            yield from at_least_n_true(formula, vars, self.second+1)
        elif isinstance(self.first, NumFalse):
            yield from at_most_n_true(formula, vars, len(vars) - self.second - 1)
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")

class NumGe(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        assert type(self.second) is int, "Cardinality comparisons require integers"
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            yield from at_least_n_true(formula, vars, self.second)
        elif isinstance(self.first, NumFalse):
            yield from at_most_n_true(formula, vars, len(vars) - self.second)
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")

class TupleEq(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        t1 = [expr.generate_var(formula) for expr in self.first.exprs]
        t2 = [expr.generate_var(formula) for expr in self.second.exprs]
        yield from And(*(Eq(c1, c2) for c1, c2 in zip(t1, t2))).generate_cnf(formula)

class TupleNeq(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        t1 = [expr.generate_var(formula) for expr in self.first.exprs]
        t2 = [expr.generate_var(formula) for expr in self.second.exprs]
        yield from Or(*(Neq(c1, c2) for c1, c2 in zip(t1, t2))).generate_cnf(formula)

class TupleLt(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        t1 = [expr.generate_var(formula) for expr in self.first.exprs]
        t2 = [expr.generate_var(formula) for expr in self.second.exprs]
        yield from tuple_less_than(formula, t1, t2, strict=True)

class TupleLe(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        t1 = [expr.generate_var(formula) for expr in self.first.exprs]
        t2 = [expr.generate_var(formula) for expr in self.second.exprs]
        yield from tuple_less_than(formula, t1, t2, strict=False)

class TupleGt(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        t1 = [expr.generate_var(formula) for expr in self.first.exprs]
        t2 = [expr.generate_var(formula) for expr in self.second.exprs]
        yield from tuple_less_than(formula, t2, t1, strict=True)

class TupleGe(OrderedBinaryBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        t1 = [expr.generate_var(formula) for expr in self.first.exprs]
        t2 = [expr.generate_var(formula) for expr in self.second.exprs]
        yield from tuple_less_than(formula, t2, t1, strict=False)

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
        return TupleEq(self, other)

    def __ne__(self, other: 'Tuple'):
        self.__check_length(other)
        return TupleNeq(self, other)

    def __lt__(self, other: 'Tuple'):
        self.__check_length(other)
        return TupleLt(self, other)

    def __le__(self, other: 'Tuple'):
        self.__check_length(other)
        return TupleLe(self, other)

    def __gt__(self, other: 'Tuple'):
        self.__check_length(other)
        return TupleGt(self, other)

    def __ge__(self, other: 'Tuple'):
        self.__check_length(other)
        return TupleGe(self, other)

# TODO: implement canonical_form method for all Exprs so we can cache them correctly.
#       for now, we just cache based on repr
