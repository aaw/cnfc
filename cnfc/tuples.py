from .tseytin import *

def tuple_less_than(formula, x, y, strict=False):
    n = len(x)
    assert n == len(y), "Comparisons between tuples of different dimensions not supported."
    assert n >= 2, "Only tuples of dimension 2 or greater are supported."

    a = [formula.AddVar() for i in range(n-1)]

    yield (~x[0], y[0])
    yield (~x[0], a[0])
    yield (y[0], a[0])
    for i in range(1, n-1):
        yield (~x[i], y[i], ~a[i-1])
        yield (~x[i], a[i], ~a[i-1])
        yield (y[i], a[i], ~a[i-1])
    if strict:
        yield (~x[n-1], ~a[n-2])
        yield (y[n-1], ~a[n-2])
    else:
        yield (~x[n-1], y[n-1], ~a[n-2])

# Brent-Kung adder from "A Regular Layout for Parallel Adders",
# IEEE Trans. on Comp. C-31 (3): 260-264.
def tuple_add(formula, x_a, x_b, result):
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

    n = len(x_a)
    assert n == len(x_b), "Comparisons between tuples of different dimensions not supported."
    assert n >= 2, "Only tuples of dimension 2 or greater are supported."

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

    # TODO: actually wasting a var here because we discard the result[0] passed in.
    for i in range(len(x_a)):
        # Bit i is a_i XOR b_i XOR c_{i-1}
        a_xor_b = formula.AddVar()
        yield from gen_xor((x_a[i], x_b[i]), a_xor_b)
        if i == 0:
            # No carry for least significant bit.
            result[0] = a_xor_b
            continue
        # result[i] = a_xor_b XOR c_{i-1}
        yield from gen_xor((a_xor_b, gps[i-1][0]), result[i])
    result[n] = gps[n-1][0]

    result.reverse()

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
def tuple_mul(formula, x_a, x_b, pad_fn, rpad_fn, result):
    # Make len(x_a) >= len(x_b) so that we minimize additions.
    if len(x_a) < len(x_b): x_a, x_b = x_b, x_a
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
        partial = rpad_fn(partial, i)
        partials.append(partial)

    # Now reduce all of the partials pair-by-pair using addition
    while len(partials) > 1:
        reduced = []
        for a, b in zip(partials[:-1:2], partials[1::2]):
            a, b = pad_fn(a,b)
            partial_result = [formula.AddVar() for i in range(len(a) + 1)]
            yield from tuple_add(formula, a, b, partial_result)
            reduced.append(partial_result)

        # If there was an odd number of elements, we didn't reduce the last one.
        if len(partials) % 2 == 1:
            reduced.append(partials[-1])
        partials = reduced

    # Copy partials into result
    assert(len(partials) == 1)
    partial = partials[0]
    # Don't want an rpad here, but need to redo how result is passed anyway...
    for i in range(len(partial)-len(result)): result.append(None)
    for i in range(len(result)):
        result[i] = partial[i]
