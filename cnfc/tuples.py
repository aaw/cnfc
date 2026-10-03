from .bool_lit import rpad, lpad, BooleanLiteral
from .tseytin import *
from .util import Generator

def sign_extend(bits, width):
    return [bits[0]] * (width - len(bits)) + bits


def tuple_negate(formula, bits):
    # Invert each bit above the lowest set bit; keep that bit and its zeros.
    result = [bits[-1]]
    lower_nonzero = bits[-1]
    for bit in reversed(bits[:-1]):
        v = formula.AddVar()
        yield from gen_xor((bit, lower_nonzero), v)
        result.append(v)
        v = formula.AddVar()
        yield from gen_or((bit, lower_nonzero), v)
        lower_nonzero = v
    return list(reversed(result))


def tuple_sub(formula, x, y):
    width = max(len(x), len(y)) + 1
    negate = Generator(tuple_negate(formula, sign_extend(y, width)))
    yield from negate
    add = Generator(tuple_add(formula, sign_extend(x, width), negate.result))
    yield from add
    return add.result[-width:]


def tuple_less_than(formula, x, y, strict=False):
    x = lpad(x, len(y) - len(x))
    y = lpad(y, len(x) - len(y))
    n = len(x)

    # Harvey's encoding for lexicographic comparison of tuples. See:
    # https://www.curtisbright.com/bln/2024/12/24/harveys-sat-encoding-for-lexicographic-ordering
    a = [formula.AddVar() for i in range(n)] + [BooleanLiteral(not strict)]
    for i in range(n):
        yield (a[i+1], y[i], ~a[i])
        yield (a[i+1], ~x[i], ~a[i])
        yield (y[i], ~x[i], ~a[i])
        yield (~a[i+1], ~y[i], a[i])
        yield (~a[i+1], x[i], a[i])
        yield (~y[i], x[i], a[i])
    return a[0]


def __tuple_min_or_max(formula, x, y, is_min=True):
    width = max(len(x), len(y))
    x, y = sign_extend(x, width), sign_extend(y, width)
    # Compare in unsigned order, then restore the sign bit.
    x[0], y[0] = ~x[0], ~y[0]
    n = len(x)
    result = [formula.AddVar() for i in range(n)]

    if is_min:
        # Assert that result <= x
        g = Generator(tuple_less_than(formula, result, x, strict=False))
        yield from g
        yield (g.result,)
        # Assert that result <= y
        g = Generator(tuple_less_than(formula, result, y, strict=False))
        yield from g
        yield (g.result,)
    else: # max
        # Assert that x <= result
        g = Generator(tuple_less_than(formula, x, result, strict=False))
        yield from g
        yield (g.result,)
        # Assert that y <= result
        g = Generator(tuple_less_than(formula, y, result, strict=False))
        yield from g
        yield (g.result,)

    # eq_x == (result == x)
    eq_x = formula.AddVar()
    eq_x_vars = []
    for i in range(n):
        # v == (result[i] == x[i])
        v = formula.AddVar()
        eq_x_vars.append(v)
        for clause in gen_eq((result[i], x[i]), v):
            formula.AddClause(*clause)
    yield from gen_and(eq_x_vars, eq_x)

    # eq_y == (result == y)
    eq_y = formula.AddVar()
    eq_y_vars = []
    for i in range(n):
        v = formula.AddVar()
        eq_y_vars.append(v)
        for clause in gen_eq((result[i], y[i]), v):
            formula.AddClause(*clause)
    yield from gen_and(eq_y_vars, eq_y)

    # Assert that result is either x or y
    yield (eq_x, eq_y)

    result[0] = ~result[0]
    return result


def tuple_min(formula, x, y):
    gen = Generator(__tuple_min_or_max(formula, x, y, is_min=True))
    yield from gen
    return gen.result


def tuple_max(formula, x, y):
    gen = Generator(__tuple_min_or_max(formula, x, y, is_min=False))
    yield from gen
    return gen.result


def __ladner_fischer_network(n):
    zs, reduced = [0]*n, [list(range(n))]
    while len(reduced[-1]) > 1:
        prev, current = reduced[-1], []
        for x,y in zip(prev[::2], prev[1::2]):
            yield (x,y)
            current.append(y)
        if len(prev) % 2 == 1:
            current.append(prev[-1])
        reduced.append(current)

    finished = set(r[0] for r in reduced)
    for result in reversed(reduced):
        for i, item in enumerate(result):
            if item not in finished:
                yield (result[i-1], item)
                finished.add(item)


# Brent-Kung adder from "A Regular Layout for Parallel Adders",
# IEEE Trans. on Comp. C-31 (3): 260-264.
def tuple_add(formula, x_a, x_b):
    def operator_o(formula, a, b, g_r, p_r):
        # (g_a, p_a) o (g_b, p_b) = (g_a OR (p_a AND g_b), p_a AND p_b)
        g_a, p_a = a
        g_b, p_b = b
        v = formula.AddVar()
        # v == (p_a AND g_b)
        yield from gen_and((p_a, g_b), v)
        # g_r == (g_a OR v)
        yield from gen_or((g_a, v), g_r)
        # p_r == (p_a AND p_b)
        yield from gen_and((p_a, p_b), p_r)

    nonnegative = all(isinstance(bits[0], BooleanLiteral) and not bits[0].val for bits in (x_a, x_b))
    width = max(len(x_a), len(x_b)) + 1
    if nonnegative:
        # A fixed zero sign lets us add just the magnitude bits.
        x_a, x_b = x_a[1:], x_b[1:]
        x_a = lpad(x_a, len(x_b) - len(x_a))
        x_b = lpad(x_b, len(x_a) - len(x_b))
        if not x_a:
            return [BooleanLiteral(False)]
    else:
        x_a, x_b = sign_extend(x_a, width), sign_extend(x_b, width)

    # Tuples are listed most significant bit in lowest index, we want the reverse for
    # adding so that x[0] is the least significant bit.
    x_a.reverse()
    x_b.reverse()

    gps = []
    for a,b in zip(x_a, x_b):
        g, p = formula.AddVar(), formula.AddVar()
        yield from gen_and((a, b), g)
        yield from gen_xor((a, b), p)
        gps.append((g,p))

    # Naive accumulation of (g_i, p_i) for now, can use tree structure later.
    for i in range(1,len(gps)):
        g, p = formula.AddVar(), formula.AddVar()
        yield from operator_o(formula, gps[i], gps[i-1], g, p)
        gps[i] = (g,p)

    # Work-efficient prefix sums. This does not currently beat the naive
    # linear accumulation above, but leaving it here for testing.
    # https://blog.aaw.io/2023/11/05/work-efficient-prefix-sums.html
    # for x,y in __ladner_fischer_network(len(gps)):
    #     g, p = formula.AddVar(), formula.AddVar()
    #     yield from operator_o(formula, gps[y], gps[x], g, p)
    #     gps[y] = (g,p)

    # Need room for all bits plus a carry.
    n = len(x_a)
    result = [formula.AddVar() for i in range(n+1)]

    # No carry for least significant bit.
    yield from gen_xor((x_a[0], x_b[0]), result[0])
    for i in range(1, len(x_a)):
        # Bit i is a_i XOR b_i XOR c_{i-1}
        a_xor_b = formula.AddVar()
        yield from gen_xor((x_a[i], x_b[i]), a_xor_b)
        # result[i] = a_xor_b XOR c_{i-1}
        yield from gen_xor((a_xor_b, gps[i-1][0]), result[i])
    result[n] = gps[n-1][0]

    result.reverse()
    if nonnegative:
        return [BooleanLiteral(False)] + result
    return result[-width:]


# Very naive multiplier implemented with repeated addition
#
#                      x1 x2 x3
#                    * y1 y2 y3
#                --------------
#                y3x1 y3x2 y3x3
#           y2x1 y2x2 y2x3    0
#    + y3x1 y3x2 y3x3    0    0
#    --------------------------
#
def tuple_mul(formula, x_a, x_b):
    # Keep the shorter operand as the multiplier.
    if len(x_a) < len(x_b): x_a, x_b = x_b, x_a
    width = len(x_a) + len(x_b)
    nonnegative = all(isinstance(bits[0], BooleanLiteral) and not bits[0].val for bits in (x_a, x_b))
    if nonnegative:
        x_a, x_b = x_a[1:], x_b[1:]
    if not x_b:
        return [BooleanLiteral(False)]
    partials = []
    for i, bit in enumerate(reversed(x_b)):
        bits = x_a if nonnegative else sign_extend(x_a, width - i)
        partial = []
        for a in bits:
            v = formula.AddVar()
            yield from gen_and((a, bit), v)
            partial.append(v)
        partial = rpad(partial, i)
        if nonnegative:
            partial = [BooleanLiteral(False)] + partial
        elif i == len(x_b) - 1:
            # The multiplier's sign bit has negative weight.
            negate = Generator(tuple_negate(formula, partial))
            yield from negate
            partial = negate.result
        partials.append(partial)

    while len(partials) > 1:
        reduced = []
        for a, b in zip(partials[:-1:2], partials[1::2]):
            gen = Generator(tuple_add(formula, a, b))
            yield from gen
            reduced.append(gen.result[-width:])
        if len(partials) % 2 == 1:
            reduced.append(partials[-1])
        partials = reduced

    return partials[0]
