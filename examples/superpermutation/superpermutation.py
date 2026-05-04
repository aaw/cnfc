from itertools import permutations
from cnfc import *

import argparse

def encode(n, m):
    formula = Formula()
    POSITIONS = range(m)
    VALS = range(1,n+1)
    varz = {}

    # variable i:j is true iff position i in the superpermutation is set to j
    for i in POSITIONS:
        for j in VALS:
            varz[(i,j)] = formula.AddVar(f'{i}:{j}')

    # Constraint: each position in the superpermutation is set to exactly one value.
    for i in POSITIONS:
        vals = [varz[(i,j)] for j in VALS]
        formula.Add(NumTrue(*vals) == 1)

    # Constraint: each permutation of order n occurs at least once in the string.
    for perm in permutations(VALS):
        perm_in_string = []
        for i in range(m-n+1):
            perm_in_string.append(And(*[varz[(i+pi,pv)] for pi, pv in enumerate(perm)]))
        formula.Add(Or(*perm_in_string))

    # Symmetry-breaking: first n chars of superpermutation are 1,2,...,n
    for pi,pv in enumerate(VALS):
        formula.Add(varz[(pi,pv)])

    return formula


def print_solution(sol, *extra_args):
    n, m = extra_args
    for i in range(m):
        for j in range(1,n+1):
            if sol[f'{i}:{j}']: print(j, end='')
    print('')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a superpermutation of order n.")
    parser.add_argument('n', type=int, help="Order of the superpermutation.")
    parser.add_argument('m', type=int, help="Length of the superpermutation.")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode(args.n, args.m)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, [], extra_args=[args.n, args.m])
