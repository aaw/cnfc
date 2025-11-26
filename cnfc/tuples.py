from .bool_lit import rpad, lpad, BooleanLiteral
from .tseytin import *
from .util import Generator

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
    x = lpad(x, len(y) - len(x))
    y = lpad(y, len(x) - len(y))
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
# TODO: here and below, use gen_* helpers from tseytin module
        formula.AddClause(~result[i], ~x[i], v)
        formula.AddClause(result[i], x[i], v)
        formula.AddClause(result[i], ~x[i], ~v)
        formula.AddClause(~result[i], x[i], ~v)
    # Set eq_x to the AND of all of the intermediate v's
    yield (eq_x, *(~cv for cv in eq_x_vars))
    for cv in eq_x_vars: yield (~eq_x, cv)

    # eq_y == (result == y)
    eq_y = formula.AddVar()
    eq_y_vars = []
    for i in range(n):
        v = formula.AddVar()
        eq_y_vars.append(v)
        formula.AddClause(~result[i], ~y[i], v)
        formula.AddClause(result[i], y[i], v)
        formula.AddClause(result[i], ~y[i], ~v)
        formula.AddClause(~result[i], y[i], ~v)
    # Set eq_y to the AND of all of the intermediate v's
    yield (eq_y, *(~cv for cv in eq_y_vars))
    for cv in eq_y_vars: yield (~eq_y, cv)

    # Assert that result is either x or y
    yield (eq_x, eq_y)

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

    x_a = lpad(x_a, len(x_b) - len(x_a))
    x_b = lpad(x_b, len(x_a) - len(x_b))
    if len(x_a) == 0:
        x_a, x_b = [BooleanLiteral(False)], [BooleanLiteral(False)]

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
    return result


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
    # Make len(x_a) >= len(x_b) so that we minimize additions.
    if len(x_a) < len(x_b): x_a, x_b = x_b, x_a
    if len(x_b) == 0:
        return [BooleanLiteral(False)]
    partials = []
    for i in range(len(x_b)):
        # AND each bit of x_a with x_b[i]
        partial = x_a[:]
        bit = x_b[len(x_b)-i-1]
        for ia in range(len(partial)):
            v = formula.AddVar()
            yield from gen_and((partial[ia], bit), v)
            partial[ia] = v
        # Pad result on right with i zeros
        partial = rpad(partial, i)
        partials.append(partial)

    # Now reduce all of the partials pair-by-pair using addition
    while len(partials) > 1:
        reduced = []
        for a, b in zip(partials[:-1:2], partials[1::2]):
            gen = Generator(tuple_add(formula, a, b))
            yield from gen
            reduced.append(gen.result)

        # If there was an odd number of elements, we didn't reduce the last one.
        if len(partials) % 2 == 1:
            reduced.append(partials[-1])
        partials = reduced

    return partials[0]
