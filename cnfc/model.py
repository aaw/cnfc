# Data model
from abc import ABC, abstractmethod
import math

from .cardinality import exactly_n_true, not_exactly_n_true, at_least_n_true, at_most_n_true
from .bool_lit import BooleanLiteral, lpad
from .tuples import tuple_less_than, tuple_add, tuple_mul, tuple_min, tuple_max
from .regex import regex_match
from .util import Generator, gather_common_operands, reduce_evaluated
from .cache import cached_generate_var

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

    @cached_generate_var
    def generate_var(self, formula):
        return ~self.expr.generate_var(formula)

    def generate_cnf(self, formula):
        yield (~self.expr.generate_var(formula),)

class BooleanTernaryExpr(BoolExpr):
    def __init__(self, cond, if_true, if_false):
        self.cond, self.if_true, self.if_false = cond, if_true, if_false

    def __repr__(self):
        return 'BooleanTernaryExpr({}, {}, {})'.format(self.cond, self.if_true, self.if_false)

    @cached_generate_var
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        yield from Or(And(self.cond, self.if_true), And(~self.cond, self.if_false)).generate_cnf(formula)

class OrderedBinaryBoolExpr(BoolExpr):
    def __init__(self, first, second):
        self.first, self.second = first, second

    def __repr__(self):
        return '{}({},{})'.format(self.__class__.__name__, self.first, self.second)

class Implies(OrderedBinaryBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        return Or(Not(self.first), self.second).generate_var(formula)

    def generate_cnf(self, formula):
        fv = self.first.generate_var(formula)
        sv = self.second.generate_var(formula)
        yield (~fv, sv)

class And(MultiBoolExpr):
    @cached_generate_var
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
    @cached_generate_var
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
    @cached_generate_var
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
    @cached_generate_var
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
    @cached_generate_var
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        t1 = self.first.evaluate(formula)
        t2 = self.second.evaluate(formula)
        t1 = lpad(t1, len(t2) - len(t1))
        t2 = lpad(t2, len(t1) - len(t2))
        yield from And(*(Eq(c1, c2) for c1, c2 in zip(t1, t2))).generate_cnf(formula)

class TupleNeq(OrderedBinaryTupleBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        t1 = self.first.evaluate(formula)
        t2 = self.second.evaluate(formula)
        t1 = lpad(t1, len(t2) - len(t1))
        t2 = lpad(t2, len(t1) - len(t2))
        yield from Or(*(Neq(c1, c2) for c1, c2 in zip(t1, t2))).generate_cnf(formula)

class TupleInequality(OrderedBinaryTupleBoolExpr):
    def _make_generator(self, formula):
        raise NotImplementedError  # Subclasses implement this

    @cached_generate_var
    def generate_var(self, formula):
        gen = self._make_generator(formula)
        for clause in gen:
            formula.AddClause(*clause)
        return gen.result

    def generate_cnf(self, formula):
        gen = self._make_generator(formula)
        yield from gen
        yield (gen.result,)

class TupleLt(TupleInequality):
    def _make_generator(self, formula):
        t1 = self.first.evaluate(formula)
        t2 = self.second.evaluate(formula)
        return Generator(tuple_less_than(formula, t1, t2, strict=True))

class TupleLe(TupleInequality):
    def _make_generator(self, formula):
        t1 = self.first.evaluate(formula)
        t2 = self.second.evaluate(formula)
        return Generator(tuple_less_than(formula, t1, t2, strict=False))

class TupleGt(TupleInequality):
    def _make_generator(self, formula):
        t1 = self.first.evaluate(formula)
        t2 = self.second.evaluate(formula)
        return Generator(tuple_less_than(formula, t2, t1, strict=True))

class TupleGe(TupleInequality):
    def _make_generator(self, formula):
        t1 = self.first.evaluate(formula)
        t2 = self.second.evaluate(formula)
        return Generator(tuple_less_than(formula, t2, t1, strict=False))

# Any expression that results in a Tuple.
class TupleExpr:
    def __len__(self):
        return len(self.exprs)

    def __eq__(self, other):
        return TupleEq(self, other)

    def __ne__(self, other):
        return TupleNeq(self, other)

    def __lt__(self, other):
        return TupleLt(self, other)

    def __le__(self, other):
        return TupleLe(self, other)

    def __gt__(self, other):
        return TupleGt(self, other)

    def __ge__(self, other):
        return TupleGe(self, other)

    def __add__(self, other):
        return TupleAdd(self, other)

    def __radd__(self, other):
        return TupleAdd(other, self)

    def __sub__(self, other):
        return TupleSub(self, other)

    def __rsub__(self, other):
        return TupleSub(other, self)

    def __mul__(self, other):
        return TupleMul(self, other)

    def __rmul__(self, other):
        return TupleMul(other, self)

    def __floordiv__(self, other):
        return TupleDiv(self, other)

    def __rfloordiv__(self, other):
        return TupleDiv(other, self)

    def __mod__(self, other):
        return TupleMod(self, other)

    def __rmod__(self, other):
        return TupleMod(other, self)

    def __pow__(self, other, modulo=None):
        return TuplePow(self, other, modulo)

    def __rpow__(self, other, modulo=None):
        return TuplePow(other, self, modulo)

# An expression combining two Tuples (addition, multiplication) that results in a Tuple
class TupleCompositeExpr(TupleExpr, ABC):
    def __init__(self, *args):
        self.args = [Integer(arg) if isinstance(arg, int) else arg for arg in args]
        # TODO: dummy exprs to make asserts work, fix later when we don't do these asserts any more
        self.exprs = [None]*(len(self.args[0]))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ','.join(map(str, self.args)))

    @abstractmethod
    def __len__(self):
        # len should always return an upper bound on the size of the resulting tuple. This needs to be defined per subclass.
        # See the implementation of TupleMod: we sometimes need an estimate of the bitwidth of a result before it's
        # actually computed, which is why defining len like this is useful.
        pass

class TupleAdd(TupleCompositeExpr):
    def __init__(self, *args):
        super().__init__(*args)
        self.args = gather_common_operands(self.__class__, self.args)

    def evaluate(self, formula):
        return reduce_evaluated(tuple_add, [arg.evaluate(formula) for arg in self.args], formula)

    def __len__(self):
        return max(len(arg) for arg in self.args) + int(math.ceil(math.log2(len(self.args)))) + 1

class TupleMul(TupleCompositeExpr):
    def __init__(self, *args):
        super().__init__(*args)
        self.args = gather_common_operands(self.__class__, self.args)

    def evaluate(self, formula):
        return reduce_evaluated(tuple_mul, [arg.evaluate(formula) for arg in self.args], formula)

    def __len__(self):
        return sum(len(arg) for arg in self.args)

class TupleMax(TupleCompositeExpr):
    def __init__(self, *args):
        super().__init__(*args)
        self.args = gather_common_operands(self.__class__, self.args)

    def evaluate(self, formula):
        return reduce_evaluated(tuple_max, [arg.evaluate(formula) for arg in self.args], formula)

    def __len__(self):
        return max(len(arg) for arg in self.args)

class TupleMin(TupleCompositeExpr):
    def __init__(self, *args):
        super().__init__(*args)
        self.args = gather_common_operands(self.__class__, self.args)

    def evaluate(self, formula):
        return reduce_evaluated(tuple_min, [arg.evaluate(formula) for arg in self.args], formula)

    def __len__(self):
        # "max" is not a typo here. We don't know if the leading bits are set
        # in the longest tuple so we have to assume the worst.
        return max(len(arg) for arg in self.args)

class TupleSub(TupleCompositeExpr):
    def evaluate(self, formula):
        t1, t2 = self.args
        # if t1 - t2 == y, then t2 + y == t1
        ys = [formula.AddVar() for i in range(len(self))]
        y = Tuple(*ys)
        formula.Add(t2 + y == t1)
        return ys

    def __len__(self):
        return max(len(self.args[0]), len(self.args[1]))

class TupleDiv(TupleCompositeExpr):
    def evaluate(self, formula):
        t1, t2 = self.args
        # if t1 // t2 == x, then t2 * x + y == t1, where 0 <= y < t2
        xs = [formula.AddVar() for i in range(len(t1))]
        x = Tuple(*xs)
        y = Tuple(*[formula.AddVar() for i in range(len(t2))])
        formula.Add(t2 * x + y == t1)
        formula.Add(y < t2)
        formula.Add(t2 > 0)  # Disallow division by zero
        return xs

    def __len__(self):
        return len(self.args[0])

class TupleMod(TupleCompositeExpr):
    def evaluate(self, formula):
        t1, t2 = self.args
        # Optimization: Turn '(x ** y) % n' into pow(x,y,n)
        if isinstance(t1, TuplePow) and t1.args[2] is None:
            return TuplePow(t1.args[0], t1.args[1], t2).evaluate(formula)
        # if t1 % t2 == y, then t2 * x + y == t1, where 0 <= y < t2
        x = Tuple(*[formula.AddVar() for i in range(len(t1))])
        ys = [formula.AddVar() for i in range(len(t2))]
        y = Tuple(*ys)
        formula.Add(t2 * x + y == t1)
        formula.Add(y < t2)
        formula.Add(t2 > 0)  # Disallow mod by zero
        return ys

    def __len__(self):
        return len(self.args[1])

class TuplePow(TupleCompositeExpr):
    def evaluate(self, formula):
        base, power, mod = self.args
        base = base.evaluate(formula)
        power = power.evaluate(formula)
        if mod is not None:
            mod = Integer(*mod.evaluate(formula))

        result = Integer(1)
        accum = Integer(*base)
        for bit in reversed(power):
            result = result * If(bit, accum, Integer(1))
            accum = accum * accum
            if mod is not None:
                result = result % mod
                accum = accum % mod
        return result.evaluate(formula)

    def __len__(self):
        base, power, mod = self.args
        if mod is None:
            return int(math.floor(len(power) * math.log2(len(base))) + 1)
        return len(mod)

class Tuple(TupleExpr):
    def __init__(self, *exprs):
        self.exprs = exprs
        for expr in self.exprs:
            assert issubclass(type(expr), (BoolExpr, BooleanLiteral)), "{} needs boolean expressions, got {}".format(self.__class__.__name__, expr)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ','.join(repr(e) for e in self.exprs))

    def evaluate(self, formula):
        return [expr.generate_var(formula) for expr in self.exprs]

    def as_tuple(self):
        return tuple(self.exprs)

class Integer(Tuple):
    def __init__(self, *values):
        if len(values) == 1 and type(values[0]) == int:
            value = values[0]
            assert value >= 0, 'Only positive integers are supported. Got {}'.format(value)
            bitstring = bin(value)[2:]
            m = {'0': False, '1': True}
            self.exprs = [BooleanLiteral(m[ch]) for ch in bitstring]
        elif len(values) == 1 and type(values[0]) == tuple:
            self.exprs = values[0]
        else:
            self.exprs = values

class RegexMatch(BoolExpr):
    def __init__(self, tup: 'TupleExpr', regex):
        self.tuple = tup
        self.regex = regex

    @cached_generate_var
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        yield from regex_match(formula, self.tuple.evaluate(formula), self.regex)

class TupleTernaryExpr(Tuple):
    def __init__(self, cond, if_true, if_false):
        self.cond, self.if_true, self.if_false = cond, if_true, if_false

    def __repr__(self):
        return '{}({},{},{})'.format(self.__class__.__name__, self.cond, self.if_true, self.if_false)

    def __len__(self):
        return max(len(self.if_true), len(self.if_false))

    def evaluate(self, formula):
        t1 = self.if_true.evaluate(formula)
        t2 = self.if_false.evaluate(formula)
        t1 = lpad(t1, len(t2) - len(t1))
        t2 = lpad(t2, len(t1) - len(t2))
        return [Or(And(self.cond, t1[i]), And(~self.cond, t2[i])).generate_var(formula) for i in range(len(t1))]

class CardinalityConstraint(NumExpr):
    def __init__(self, *exprs):
        self.exprs = exprs

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ','.join(repr(e) for e in self.exprs))

class NumTrue(CardinalityConstraint, TupleExpr):
    def evaluate(self, formula):
        if len(self.exprs) == 0:
            return Integer(0)
        indicators = [If(v, Integer(1), Integer(0)).evaluate(formula) for v in self.exprs]
        return reduce_evaluated(tuple_add, indicators, formula)

class NumFalse(CardinalityConstraint, TupleExpr):
    def evaluate(self, formula):
        if len(self.exprs) == 0:
            return Integer(0)
        indicators = [If(v, Integer(0), Integer(1)).evaluate(formula) for v in self.exprs]
        return reduce_evaluated(tuple_add, indicators, formula)

class NumEq(OrderedBinaryBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        if not type(self.second) is int:
            yield from TupleEq(self.first, self.second).generate_cnf(formula)
            return
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            n = self.second
        elif isinstance(self.first, NumFalse):
            n = len(vars) - self.second
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")
        yield from exactly_n_true(formula, vars, n)

class NumNeq(OrderedBinaryBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        if not type(self.second) is int:
            yield from TupleNeq(self.first, self.second).generate_cnf(formula)
            return
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            n = self.second
        elif isinstance(self.first, NumFalse):
            n = len(vars) - self.second
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")
        yield from not_exactly_n_true(formula, vars, n)

class NumLt(OrderedBinaryBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        if not type(self.second) is int:
            yield from TupleLt(self.first, self.second).generate_cnf(formula)
            return
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            yield from at_most_n_true(formula, vars, self.second-1)
        elif isinstance(self.first, NumFalse):
            yield from at_least_n_true(formula, vars, len(vars) - self.second + 1)
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")

class NumLe(OrderedBinaryBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        if not type(self.second) is int:
            yield from TupleLe(self.first, self.second).generate_cnf(formula)
            return
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            yield from at_most_n_true(formula, vars, self.second)
        elif isinstance(self.first, NumFalse):
            yield from at_least_n_true(formula, vars, len(vars) - self.second)
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")

class NumGt(OrderedBinaryBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        if not type(self.second) is int:
            yield from TupleGt(self.first, self.second).generate_cnf(formula)
            return
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            yield from at_least_n_true(formula, vars, self.second+1)
        elif isinstance(self.first, NumFalse):
            yield from at_most_n_true(formula, vars, len(vars) - self.second - 1)
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")

class NumGe(OrderedBinaryBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        return generate_var_from_cnf(self, formula)

    def generate_cnf(self, formula):
        if not type(self.second) is int:
            yield from TupleGe(self.first, self.second).generate_cnf(formula)
            return
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            yield from at_least_n_true(formula, vars, self.second)
        elif isinstance(self.first, NumFalse):
            yield from at_most_n_true(formula, vars, len(vars) - self.second)
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")

# Polymorphic If:
#   - With two params, this is boolean implication.
#   - With three params, this is a ternary operator that evaluates the condition and returns one of the last two args.
def If(arg1, arg2, arg3=None):
    if arg3 is None:
        return Implies(arg1, arg2)
    else:
        if isinstance(arg2, TupleExpr) and isinstance(arg3, TupleExpr):
            return TupleTernaryExpr(arg1, arg2, arg3)
        elif (isinstance(arg2, BoolExpr) or isinstance(arg2, BooleanLiteral)) and (isinstance(arg3, BoolExpr) or isinstance(arg3, BooleanLiteral)):
            return BooleanTernaryExpr(arg1, arg2, arg3)
    raise ValueError("Unsupported form of If.")

# TODO: implement canonical_form method for all Exprs so we can cache them correctly.
#       for now, we just cache based on repr
