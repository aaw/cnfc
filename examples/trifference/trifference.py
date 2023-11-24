from cnfc import *

import argparse
from itertools import combinations, product

# Generates all ternary strings of lenth n in lexicographic order.
def ternary_strings(n):
    from itertools import product
    yield from (''.join(x) for x in product(map(str, range(3)), repeat=n))

assert(list(ternary_strings(2)) == ['00','01','02','10','11','12','20','21','22'])

# Returns true exactly when x,y, and z have at least one coordinate where
# they all disagree.
def trifferent(x,y,z):
    assert(len(x) == len(y) == len(z))
    for i in range(len(x)):
        if len(set((x[i],y[i],z[i]))) == 3:
            return True
    return False

# Generate all words lexicographically less than the given word, except the
# all-zero word.
def non_zero_lex_less_than(word):
    n = len(word)
    all_zero = '0'*n
    for w in ternary_strings(n):
        if w == all_zero: continue
        if w > word: return
        yield w

def encode_trifference_as_sat(n, k):
    formula = Formula()
    strings = list(ternary_strings(n))

    # Variable x will be true iff the string x is in the trifferent set.
    varz = dict((x, formula.AddVar(x)) for x in strings)

    # Generate a clause for each forbidden triple.
    for x,y,z in combinations(strings, 3):
        if not trifferent(x,y,z):
            formula.AddClause(~varz[x], ~varz[y], ~varz[z])

    # Require that the resulting trifferent set have cardinality k.
    formula.Add(NumTrue(*varz.values()) == k)

    # A trifferent set can be modified by permuting the values in any particular
    # coordinate position and the resulting set will still be trifferent. So we
    # can always assume that the all-zero word is part of the trifferent set.
    formula.AddClause(varz['0'*n])

    return formula

def extract_set_from_solution(sol, *extra_args):
    n = extra_args[0]
    C = []
    for s in ternary_strings(n):
        if sol[s]:
            C.append(s)
    print('{' + ', '.join(C) + '}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a formula satisfiable iff T(n) <= k")
    parser.add_argument('n', type=int, help='Length of ternary strings')
    parser.add_argument('k', type=int, help='Size of trifferent set')
    parser.add_argument('out', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode_trifference_as_sat(args.n, args.k)
    with open(args.out, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, extract_set_from_solution, extra_fns=[ternary_strings], extra_args=[args.n])
