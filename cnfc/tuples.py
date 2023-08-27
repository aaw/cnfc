
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
