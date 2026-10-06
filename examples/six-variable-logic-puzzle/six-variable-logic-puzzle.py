from itertools import combinations
from cnfc import *
from cnfc.funcs import AllDifferent

import argparse

NUM_BITS = Integer.bits_needed_for_range(1, 10)

def encode():
    formula = Formula()

    a, b, c, d, e, f = varz = [Integer(formula.AddVars(name, NUM_BITS)) for name in 'abcdef']

    # Constraint: a,b,c,d,e,f between 1 and 10, inclusive.
    for v in varz:
        formula.Add(1 <= v <= 10)

    # Constraint: a,b,c,d,e,f all distinct.
    formula.Add(AllDifferent(varz))

    # Constraint: 1. B - D = 2
    formula.Add(b - d == 2)

    # Constraint: 2. F + A = 11
    formula.Add(f + a == 11)

    # Constraint: 3. A is between D and C
    formula.Add(d < a < c)

    # Constraint: 4. No two variables sum to 14
    for x,y in combinations(varz, 2):
        formula.Add(x + y != 14)

    # Constraint: 5. No two variables sum to 5
    for x,y in combinations(varz, 2):
        formula.Add(x + y != 5)

    # Constraint: 6. C - A = 1
    formula.Add(c - a == 1)

    return formula

def print_solution(sol, *extra_args):
    for name in 'abcdef':
        print(f'{name.upper()} = {sol.integer(name)}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve a six variable logic puzzle")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode()
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution)
