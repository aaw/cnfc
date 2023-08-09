from itertools import combinations

# Generates clauses satisfiable iff at most one of the variables in vs is true.
def at_most_one_true(vs):
    vvs = tuple(v for v in vs)
    yield from combinations(vvs, 2)

# Generates clauses satisfiable iff at most one of the variables in vs is false.
def at_most_one_false(vs):
    vvs = tuple(v for v in vs)
    yield from combinations(vvs, 2)

# Given variables a, b, minout, and maxout, generates clauses that are
# satisfiable iff minout = min(a,b) and maxout = max(a,b).
def comparator(a, b, minout, maxout):
    yield (~maxout, a, b)
    yield (~a, maxout)
    yield (~b, maxout)
    yield (minout, ~a, ~b)
    yield (a, ~minout)
    yield (b, ~minout)

def apply_comparator(formula, vin, i, j):
    newmin, newmax = formula.AddVar(), formula.AddVar()
    yield from comparator(vin[i], vin[j], newmin, newmax)
    vin[i], vin[j] = newmax, newmin

def pairwise_sorting_network(formula, vin, begin, end):
    n, a = end - begin, 1
    while a < n:
        b, c = a, 0
        while b < n:
            yield from apply_comparator(formula, vin, begin+b-a, begin+b)
            b, c = b+1, (c+1) % a
            if c == 0: b += a
        a *= 2

    a //= 4
    e = 1
    while a > 0:
        d = e
        while d > 0:
            b = (d+1) * a
            c = 0
            while b < n:
                yield from apply_comparator(formula, vin, begin+b-d*a, begin+b)
                b, c = b+1, (c+1) % a
                if c == 0: b += a
            d //= 2
        a //= 2
        e = e*2 + 1

# Filter [vin[i], vin[i+n]) with [vin[j], vin[j+n)
def filter_network(formula, vin, i, j, n):
    for x in range(n):
        yield from apply_comparator(formula, vin, i+x, j+n-1-x)

# Assert that exactly n of the vars in vin are true.
def exactly_n_true(formula, vin, n):
    yield from n_true(formula, vin, n, True, True)

def at_most_n_true(formula, vin, n):
    yield from n_true(formula, vin, n, True, False)

def at_least_n_true(formula, vin, n):
    yield from n_true(formula, vin, n, False, True)

def n_true(formula, vin, n, at_most_n_true, at_least_n_true):
    if n == 0:
        if at_least_n_true: return
        for v in vin:
            yield (~v,)
        return
    n = n+1  # We'll select the top n+1, verify exactly one true.
    batches = len(vin) // n
    for b in range(1, batches):
        yield from pairwise_sorting_network(formula, vin, 0, n)
        yield from pairwise_sorting_network(formula, vin, b*n, (b+1)*n)
        yield from filter_network(formula, vin, 0, b*n, n)
    # Now take care of the remainder, if there is one.
    rem = len(vin) - batches * n
    if rem > 0:
        yield from pairwise_sorting_network(formula, vin, 0, n)
        yield from pairwise_sorting_network(formula, vin, batches*n, len(vin))
        yield from filter_network(formula, vin, n-rem, batches*n, rem)
    if at_least_n_true:
        # Assert that at most 1 of the first n are false
        for clause in at_most_one_false(vin[:n]):
            yield clause
    if at_most_n_true:
        # Assert that at least 1 of the first n are false
        yield [~v for v in vin[:n]]
