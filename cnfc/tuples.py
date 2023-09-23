
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
        yield (~p_a, ~g_b, v)
        yield (~v, p_a)
        yield (~v, g_b)
        # g_r == (g_a OR v)
        yield (g_a, v, ~g_r)
        yield (~g_a, g_r)
        yield (~v, g_r)
        # p_r == (pa AND p_b)
        yield (~p_a, ~p_b, p_r)
        yield (~p_r, p_a)
        yield (~p_r, p_b)

    def G(formula, a, b, v):
        # g = a AND b
        yield (~a, ~b, v)
        yield (~v, a)
        yield (~v, b)

    def P(formula, a, b, v):
        # p = a XOR b
        yield (~a, ~b, ~v)
        yield (a, b, ~v)
        yield (a, ~b, v)
        yield (~a, b, v)

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
        yield from G(formula, a, b, g)
        yield from P(formula, a, b, p)
        gps.append((g,p))

    # Naive accumulation of (g_i, p_i) for now, can use tree structure later.
    for i in range(1,len(gps)):
        g, p = formula.AddVar(), formula.AddVar()
        yield from operator_o(formula, gps[i], gps[i-1], g, p)
        gps[i] = (g,p)

    # TODO: actually wasting a var here because we discard the result[0] passed in.
    for i in range(len(x_a)):
        # Bit i is a_i XOR b_i XOR c_{i-1}
        axorb = formula.AddVar()
        yield (~x_a[i], ~x_b[i], ~axorb)
        yield (x_a[i], x_b[i], ~axorb)
        yield (x_a[i], ~x_b[i], axorb)
        yield (~x_a[i], x_b[i], axorb)
        if i == 0:
            # No carry for least significant bit.
            result[0] = axorb
            continue
        # result[i] = axorb XOR c_{i-1}
        yield (~axorb, ~gps[i-1][0], ~result[i])
        yield (axorb, gps[i-1][0], ~result[i])
        yield (axorb, ~gps[i-1][0], result[i])
        yield (~axorb, gps[i-1][0], result[i])
    result[n] = gps[n-1][0]

    result.reverse()
