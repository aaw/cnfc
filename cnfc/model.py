# Data model
from abc import ABC, abstractmethod
import math

from .cardinality import exactly_n_true, not_exactly_n_true, at_least_n_true, at_most_n_true, select_max_n, pairwise_sorting_network
from .tseytin import gen_and, gen_or, gen_eq, gen_neq, gen_if
from .bool_lit import BooleanLiteral, lpad
from .tuples import tuple_less_than, tuple_add, tuple_mul, tuple_min, tuple_max
from .regex import regex_match, regex_match_states
from .util import Generator, gather_common_operands, reduce_evaluated
from .cache import cached_generate_var, cached_evaluate

# A generic way to implement generate_var from a generate_cnf implementation.
# Not always the most efficient, but a good fallback.
def generate_var_from_cnf(instance, formula):
    vars_to_and = []
    for clause in instance.generate_cnf(formula):
        v = formula.AddVar()
        vars_to_and.append(v)
        # Set v equal to the original clause
        for c in gen_or(clause, v):
            formula.AddClause(*c)

    # AND the clause variables to recreate the CNF as a single variable
    return And(*vars_to_and).generate_var(formula)

def _combine_comparisons(operand, comparison):
    pending = getattr(operand, '_pending_chain', None)
    if pending is None:
        return comparison
    tail = pending.exprs[-1] if isinstance(pending, And) else pending
    for endpoint in (tail.first, tail.second):
        if getattr(endpoint, '_pending_chain', None) is pending:
            endpoint._pending_chain = None
    if isinstance(pending, And):
        return _ChainedComparison(*pending.exprs, comparison)
    return _ChainedComparison(pending, comparison)

class _ChainableComparison:
    def __bool__(self):
        # Python checks the first comparison before evaluating the next one.
        tail = self.exprs[-1] if isinstance(self, And) else self
        for operand in (tail.first, tail.second):
            if isinstance(operand, (NumExpr, TupleExpr)):
                operand._pending_chain = self
        return True

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
        return _combine_comparisons(self, NumLt(self, other))

    def __le__(self, other):
        return _combine_comparisons(self, NumLe(self, other))

    def __gt__(self, other):
        return _combine_comparisons(self, NumGt(self, other))

    def __ge__(self, other):
        return _combine_comparisons(self, NumGe(self, other))

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
        cond = self.cond.generate_var(formula)
        if_true = self.if_true.generate_var(formula)
        if_false = self.if_false.generate_var(formula)
        v = formula.AddVar()
        for clause in gen_if(cond, if_true, if_false, v):
            formula.AddClause(*clause)
        return v

    def generate_cnf(self, formula):
        cond = self.cond.generate_var(formula)
        if_true = self.if_true.generate_var(formula)
        if_false = self.if_false.generate_var(formula)
        yield (~cond, if_true)
        yield (cond, if_false)

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
        for clause in gen_and(subvars, v):
            formula.AddClause(*clause)
        return v

    def generate_cnf(self, formula):
        for expr in self.exprs:
            yield (expr.generate_var(formula),)

class _ChainedComparison(_ChainableComparison, And):
    pass

class Or(MultiBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        v = formula.AddVar()
        subvars = [expr.generate_var(formula) for expr in self.exprs]
        for clause in gen_or(subvars, v):
            formula.AddClause(*clause)
        return v

    def generate_cnf(self, formula):
        yield tuple(expr.generate_var(formula) for expr in self.exprs)

class Eq(OrderedBinaryBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        v = formula.AddVar()
        fv = self.first.generate_var(formula)
        sv = self.second.generate_var(formula)
        for clause in gen_eq((fv, sv), v):
            formula.AddClause(*clause)
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
        for clause in gen_neq((fv, sv), v):
            formula.AddClause(*clause)
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

class TupleInequality(_ChainableComparison, OrderedBinaryTupleBoolExpr):
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
        return _combine_comparisons(self, TupleLt(self, other))

    def __le__(self, other):
        return _combine_comparisons(self, TupleLe(self, other))

    def __gt__(self, other):
        return _combine_comparisons(self, TupleGt(self, other))

    def __ge__(self, other):
        return _combine_comparisons(self, TupleGe(self, other))

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

    @cached_evaluate
    def evaluate(self, formula):
        return reduce_evaluated(tuple_add, [arg.evaluate(formula) for arg in self.args], formula)

    def __len__(self):
        return max(len(arg) for arg in self.args) + int(math.ceil(math.log2(len(self.args)))) + 1

class TupleMul(TupleCompositeExpr):
    def __init__(self, *args):
        super().__init__(*args)
        self.args = gather_common_operands(self.__class__, self.args)

    @cached_evaluate
    def evaluate(self, formula):
        return reduce_evaluated(tuple_mul, [arg.evaluate(formula) for arg in self.args], formula)

    def __len__(self):
        return sum(len(arg) for arg in self.args)

class TupleMax(TupleCompositeExpr):
    def __init__(self, *args):
        super().__init__(*args)
        self.args = gather_common_operands(self.__class__, self.args)

    @cached_evaluate
    def evaluate(self, formula):
        return reduce_evaluated(tuple_max, [arg.evaluate(formula) for arg in self.args], formula)

    def __len__(self):
        return max(len(arg) for arg in self.args)

class TupleMin(TupleCompositeExpr):
    def __init__(self, *args):
        super().__init__(*args)
        self.args = gather_common_operands(self.__class__, self.args)

    @cached_evaluate
    def evaluate(self, formula):
        return reduce_evaluated(tuple_min, [arg.evaluate(formula) for arg in self.args], formula)

    def __len__(self):
        # "max" is not a typo here. We don't know if the leading bits are set
        # in the longest tuple so we have to assume the worst.
        return max(len(arg) for arg in self.args)

class TupleSub(TupleCompositeExpr):
    @cached_evaluate
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
    @cached_evaluate
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
    @cached_evaluate
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
    @cached_evaluate
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

    def __repr__(self):
        return '{}({},{!r})'.format(self.__class__.__name__, self.tuple, self.regex)

    @cached_generate_var
    def generate_var(self, formula):
        gen = Generator(regex_match_states(formula, self.tuple.evaluate(formula), self.regex))
        for clause in gen:
            formula.AddClause(*clause)
        return Or(*gen.result).generate_var(formula)

    def generate_cnf(self, formula):
        yield from regex_match(formula, self.tuple.evaluate(formula), self.regex)

class TupleTernaryExpr(Tuple):
    def __init__(self, cond, if_true, if_false):
        self.cond, self.if_true, self.if_false = cond, if_true, if_false

    def __repr__(self):
        return '{}({},{},{})'.format(self.__class__.__name__, self.cond, self.if_true, self.if_false)

    def __len__(self):
        return max(len(self.if_true), len(self.if_false))

    @cached_evaluate
    def evaluate(self, formula):
        t1 = self.if_true.evaluate(formula)
        t2 = self.if_false.evaluate(formula)
        t1 = lpad(t1, len(t2) - len(t1))
        t2 = lpad(t2, len(t1) - len(t2))
        cond = self.cond.generate_var(formula)
        return [BooleanTernaryExpr(cond, t1[i], t2[i]).generate_var(formula) for i in range(len(t1))]

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

_BINARY_COUNT_MIN_SIZE = 64
_BINARY_COUNT_MIN_TARGET = 16

def _cardinality_bound(count, bound, relation):
    if not isinstance(bound, Integer) or not all(isinstance(bit, BooleanLiteral) for bit in bound.exprs):
        return bound
    value = 0
    for bit in bound.exprs:
        value = 2 * value + bit.val
    size = len(count.exprs)
    # Keep the arithmetic encoding where literal-int bounds would raise.
    if value > size or (relation is TupleLt and value == 0) or (relation is TupleGt and value == size):
        return bound
    return value

def _cardinality_equality_bound(count, bound):
    if type(bound) is not int:
        return bound
    size = len(count.exprs)
    if size >= _BINARY_COUNT_MIN_SIZE and min(bound, size - bound) >= _BINARY_COUNT_MIN_TARGET:
        return Integer(bound)
    return bound

def generate_cardinality_var(instance, formula, relation):
    bound = _cardinality_bound(instance.first, instance.second, relation)
    if relation in (TupleEq, TupleNeq):
        bound = _cardinality_equality_bound(instance.first, bound)
    if type(bound) is not int:
        return relation(instance.first, bound).generate_var(formula)

    vs = [expr.generate_var(formula) for expr in instance.first.exprs]
    if isinstance(instance.first, NumFalse):
        vs = [~v for v in vs]
    elif not isinstance(instance.first, NumTrue):
        raise ValueError("Only NumTrue and NumFalse are supported.")
    n, size = bound, len(vs)

    if relation in (TupleEq, TupleNeq):
        if n < 0 or n > size:
            raise ValueError("n out of range")
        if n > size // 2:
            vs, n = [~v for v in vs], size - n
        if n == 0:
            result = And(*[~v for v in vs]).generate_var(formula)
        else:
            # Always enforce the sorting network.
            # Negation applies only to the comparison result.
            for clause in select_max_n(formula, vs, n+1):
                formula.AddClause(*clause)
            for clause in pairwise_sorting_network(formula, vs, 0, n+1):
                formula.AddClause(*clause)
            result = And(vs[n-1], ~vs[n]).generate_var(formula)
        return ~result if relation is TupleNeq else result

    # Reduce inequalities to a threshold: at least n inputs are true.
    negate = relation in (TupleLt, TupleLe)
    if relation in (TupleGt, TupleLe):
        n += 1
    if (negate and n <= 0) or (not negate and n > size):
        raise ValueError("n out of range")
    if n <= 0:
        result = BooleanLiteral(True)
    elif n > size:
        result = BooleanLiteral(False)
    else:
        # Use the smaller threshold on the complemented inputs.
        if n > (size+1) // 2:
            vs, n, negate = [~v for v in vs], size-n+1, not negate
        if n == 1:
            result = Or(*vs).generate_var(formula)
        else:
            for clause in select_max_n(formula, vs, n):
                formula.AddClause(*clause)
            result = And(*vs[:n]).generate_var(formula)
    return ~result if negate else result

class NumEq(OrderedBinaryBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        return generate_cardinality_var(self, formula, TupleEq)

    def generate_cnf(self, formula):
        bound = _cardinality_bound(self.first, self.second, TupleEq)
        bound = _cardinality_equality_bound(self.first, bound)
        if type(bound) is not int:
            yield from TupleEq(self.first, bound).generate_cnf(formula)
            return
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            n = bound
        elif isinstance(self.first, NumFalse):
            n = len(vars) - bound
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")
        yield from exactly_n_true(formula, vars, n)

class NumNeq(OrderedBinaryBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        return generate_cardinality_var(self, formula, TupleNeq)

    def generate_cnf(self, formula):
        bound = _cardinality_bound(self.first, self.second, TupleNeq)
        bound = _cardinality_equality_bound(self.first, bound)
        if type(bound) is not int:
            yield from TupleNeq(self.first, bound).generate_cnf(formula)
            return
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            n = bound
        elif isinstance(self.first, NumFalse):
            n = len(vars) - bound
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")
        yield from not_exactly_n_true(formula, vars, n)

class NumLt(_ChainableComparison, OrderedBinaryBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        return generate_cardinality_var(self, formula, TupleLt)

    def generate_cnf(self, formula):
        bound = _cardinality_bound(self.first, self.second, TupleLt)
        if type(bound) is not int:
            yield from TupleLt(self.first, bound).generate_cnf(formula)
            return
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            yield from at_most_n_true(formula, vars, bound-1)
        elif isinstance(self.first, NumFalse):
            yield from at_least_n_true(formula, vars, len(vars) - bound + 1)
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")

class NumLe(_ChainableComparison, OrderedBinaryBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        return generate_cardinality_var(self, formula, TupleLe)

    def generate_cnf(self, formula):
        bound = _cardinality_bound(self.first, self.second, TupleLe)
        if type(bound) is not int:
            yield from TupleLe(self.first, bound).generate_cnf(formula)
            return
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            yield from at_most_n_true(formula, vars, bound)
        elif isinstance(self.first, NumFalse):
            yield from at_least_n_true(formula, vars, len(vars) - bound)
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")

class NumGt(_ChainableComparison, OrderedBinaryBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        return generate_cardinality_var(self, formula, TupleGt)

    def generate_cnf(self, formula):
        bound = _cardinality_bound(self.first, self.second, TupleGt)
        if type(bound) is not int:
            yield from TupleGt(self.first, bound).generate_cnf(formula)
            return
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            yield from at_least_n_true(formula, vars, bound+1)
        elif isinstance(self.first, NumFalse):
            yield from at_most_n_true(formula, vars, len(vars) - bound - 1)
        else:
            raise ValueError("Only NumTrue and NumFalse are supported.")

class NumGe(_ChainableComparison, OrderedBinaryBoolExpr):
    @cached_generate_var
    def generate_var(self, formula):
        return generate_cardinality_var(self, formula, TupleGe)

    def generate_cnf(self, formula):
        bound = _cardinality_bound(self.first, self.second, TupleGe)
        if type(bound) is not int:
            yield from TupleGe(self.first, bound).generate_cnf(formula)
            return
        vars = [expr.generate_var(formula) for expr in self.first.exprs]
        if isinstance(self.first, NumTrue):
            yield from at_least_n_true(formula, vars, bound)
        elif isinstance(self.first, NumFalse):
            yield from at_most_n_true(formula, vars, len(vars) - bound)
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
