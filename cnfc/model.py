# Data model
from .cardinality import exactly_n_true, not_exactly_n_true, at_least_n_true, at_most_n_true
from .bool_lit import BooleanLiteral, lpad
from .tuples import tuple_less_than, tuple_add, tuple_mul
from .regex import regex_match
from .util import Generator

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

class CardinalityConstraint(NumExpr):
    def __init__(self, *exprs):
        self.exprs = exprs
        for expr in self.exprs:
            assert issubclass(type(expr), BoolExpr), "{} needs boolean expressions, got {}".format(self.__class__.__name__, expr)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ','.join(repr(e) for e in self.exprs))

class NumTrue(CardinalityConstraint): pass
class NumFalse(CardinalityConstraint): pass

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
        yield (~self.expr.generate_var(formula),)

class OrderedBinaryBoolExpr(BoolExpr):
    def __init__(self, first, second):
        self.first, self.second = first, second

    def __repr__(self):
        return '{}({},{})'.format(self.__class__.__name__, self.first, self.second)

class If(OrderedBinaryBoolExpr):
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

class OrderedBinaryTupleBoolExpr(BoolExpr):
    def __init__(self, first, second):
        self.first, self.second = first, second
        if isinstance(self.first, int):
            self.first = Integer(self.first)
        if isinstance(self.second, int):
            self.second = Integer(self.second)

    def __repr__(self):
        return '{}({},{})'.format(self.__class__.__name__, self.first, self.second)

class TupleEq(OrderedBinaryTupleBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        t1 = self.first.evaluate(formula)
        t2 = self.second.evaluate(formula)
        t1 = lpad(t1, len(t2) - len(t1))
        t2 = lpad(t2, len(t1) - len(t2))
        yield from And(*(Eq(c1, c2) for c1, c2 in zip(t1, t2))).generate_cnf(formula)

class TupleNeq(OrderedBinaryTupleBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        t1 = self.first.evaluate(formula)
        t2 = self.second.evaluate(formula)
        t1 = lpad(t1, len(t2) - len(t1))
        t2 = lpad(t2, len(t1) - len(t2))
        yield from Or(*(Neq(c1, c2) for c1, c2 in zip(t1, t2))).generate_cnf(formula)

class TupleLt(OrderedBinaryTupleBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        t1 = self.first.evaluate(formula)
        t2 = self.second.evaluate(formula)
        yield from tuple_less_than(formula, t1, t2, strict=True)

class TupleLe(OrderedBinaryTupleBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        t1 = self.first.evaluate(formula)
        t2 = self.second.evaluate(formula)
        yield from tuple_less_than(formula, t1, t2, strict=False)

class TupleGt(OrderedBinaryTupleBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        t1 = self.first.evaluate(formula)
        t2 = self.second.evaluate(formula)
        yield from tuple_less_than(formula, t2, t1, strict=True)

class TupleGe(OrderedBinaryTupleBoolExpr):
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        t1 = self.first.evaluate(formula)
        t2 = self.second.evaluate(formula)
        yield from tuple_less_than(formula, t2, t1, strict=False)

# Any expression that results in a Tuple.
class TupleExpr:
    def __len__(self):
        return len(self.exprs)

    def __eq__(self, other: 'TupleExpr'):
        return TupleEq(self, other)

    def __ne__(self, other: 'TupleExpr'):
        return TupleNeq(self, other)

    def __lt__(self, other: 'TupleExpr'):
        return TupleLt(self, other)

    def __le__(self, other: 'TupleExpr'):
        return TupleLe(self, other)

    def __gt__(self, other: 'TupleExpr'):
        return TupleGt(self, other)

    def __ge__(self, other: 'TupleExpr'):
        return TupleGe(self, other)

    def __add__(self, other):
        return TupleAdd(self, other)

    def __radd__(self, other):
        return TupleAdd(self, other)

    def __mul__(self, other):
        return TupleMul(self, other)

    def __rmul__(self, other):
        return TupleMul(self, other)

# An expression combining two Tuples (addition, multiplication) that results in a Tuple
class TupleCompositeExpr(TupleExpr):
    def __init__(self, first, second):
        self.first, self.second = first, second
        if isinstance(self.first, int):
            self.first = Integer(self.first)
        if isinstance(self.second, int):
            self.second = Integer(self.second)
        # TODO: dummy exprs to make asserts work, fix later when we don't do these asserts any more
        self.exprs = [None]*(len(self.first))

    def __repr__(self):
        return '{}({},{})'.format(self.__class__.__name__, self.first, self.second)

class TupleAdd(TupleCompositeExpr):
    def evaluate(self, formula):
        t1 = self.first.evaluate(formula)
        t2 = self.second.evaluate(formula)
        gen = Generator(tuple_add(formula, t1, t2))
        for clause in gen:
            formula.AddClause(*clause)
        return gen.result

class TupleMul(TupleCompositeExpr):
    def evaluate(self, formula):
        t1 = self.first.evaluate(formula)
        t2 = self.second.evaluate(formula)
        gen = Generator(tuple_mul(formula, t1, t2))
        for clause in gen:
            formula.AddClause(*clause)
        return gen.result

class Tuple(TupleExpr):
    def __init__(self, *exprs):
        self.exprs = exprs
        for expr in self.exprs:
            assert issubclass(type(expr), BoolExpr), "{} needs boolean expressions, got {}".format(self.__class__.__name__, expr)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ','.join(repr(e) for e in self.exprs))

    def evaluate(self, formula):
        return [expr.generate_var(formula) for expr in self.exprs]

class Integer(Tuple):
    def __init__(self, *values):
        if len(values) == 1 and type(values[0]) == int:
            value = values[0]
            assert value >= 0
            bitstring = bin(value)[2:]
            m = {'0': False, '1': True}
            self.exprs = [BooleanLiteral(m[ch]) for ch in bitstring]
        else:
            self.exprs = values

class RegexMatch(BoolExpr):
    def __init__(self, tup: 'TupleExpr', regex):
        self.tuple = tup
        self.regex = regex

    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        yield from regex_match(formula, self.tuple.evaluate(formula), self.regex)

# TODO: implement canonical_form method for all Exprs so we can cache them correctly.
#       for now, we just cache based on repr
