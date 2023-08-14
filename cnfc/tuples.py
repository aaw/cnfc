
def tuple_less_than(formula, t1, t2, strict=False):
    n = len(t1)
    assert n == len(t2), "Comparisons between tuples of different dimensions not supported."
    assert n >= 2, "Only tuples of dimension 2 or greater are supported."

    a = [formula.AddVar() for i in range(n-1)]

    yield (~t1[0], t2[0])
    yield (~t1[0], a[0])
    yield (t2[0], a[0])
    for i in range(1, n-1):
        yield (~t1[i], t2[i], ~a[i-1])
        yield (~t1[i], a[i], ~a[i-1])
        yield (t2[i], a[i], ~a[i-1])
    if strict:
        yield (~t1[n-1], ~a[n-2])
        yield (t2[n-1], ~a[n-2])
    else:
        yield (~t1[n-1], t2[n-1], ~a[n-2])
