from itertools import combinations
from .tseytin import *

# Generates clauses satisfiable iff at most one of the variables in vs is false.
# Uses Heule's encoding, see TAOCP 7.2.2.2 exercise 12.
def at_most_one_false(formula, vs):
    if len(vs) <= 4:
        yield from at_most_one_false_exhaustive(vs)
    else:
        head, tail = vs[:3], vs[3:]
        v = formula.AddVar()
        yield from at_most_one_false_exhaustive(head + [v])
        yield from at_most_one_false(formula, [~v] + tail)

def at_most_one_false_exhaustive(vs):
    yield from combinations(vs, 2)

def at_most_one_true(formula, vs):
    if len(vs) <= 4:
        yield from at_most_one_true_exhaustive(vs)
    else:
        head, tail = vs[:3], vs[3:]
        v = formula.AddVar()
        yield from at_most_one_true_exhaustive(head + [v])
        yield from at_most_one_true(formula, [~v] + tail)

def at_most_one_true_exhaustive(vs):
    for x,y in combinations(vs, 2):
        yield (~x, ~y)

def at_least_one_false(vs):
    yield [~v for v in vs]

# Given variables a, b, minout, and maxout, generates clauses that are
# satisfiable iff minout = min(a,b) and maxout = max(a,b).
def comparator(a, b, minout, maxout):
    yield from gen_or((a, b), maxout)
    yield from gen_and((a, b), minout)

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

def select_max_n(formula, vin, n):
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

# Assert that exactly n of the vars in vin are true.
def exactly_n_true(formula, vin, n):
    if n < 0 or n > len(vin): raise ValueError("n out of range")
    if n == 0:
        for v in vin: yield (~v,)
        return
    elif n == len(vin):
        for v in vin: yield (v,)
        return
    yield from select_max_n(formula, vin, n+1)
    yield from at_least_one_false(vin[:n+1])
    yield from at_most_one_false(formula, vin[:n+1])

def not_exactly_n_true(formula, vin, n):
    if n < 0 or n > len(vin): raise ValueError("n out of range")
    if n == 0:
        yield [v for v in vin]
        return
    elif n == len(vin):
        yield [~v for v in vin]
        return
    yield from select_max_n(formula, vin, n)
    yield [~v for v in vin[:n]] + [v for v in vin[n:]]

def at_most_n_true(formula, vin, n):
    if n < 0: raise ValueError("n out of range")
    if n == 0:
        for v in vin: yield (~v,)
        return
    elif n >= len(vin):
        return
    yield from select_max_n(formula, vin, n+1)
    yield from at_least_one_false(vin[:n+1])

def at_least_n_true(formula, vin, n):
    if n > len(vin): raise ValueError("n out of range")
    if n <= 0:
        return
    elif n == len(vin):
        for v in vin: yield (v,)
        return
    yield from select_max_n(formula, vin, n+1)
    yield from at_most_one_false(formula, vin[:n+1])
