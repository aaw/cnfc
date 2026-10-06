from itertools import permutations
from cnfc import *

import argparse

def encode(n, m):
    formula = Formula()
    positions = range(m)
    symbols = range(1, n+1)

    # variable i:j is true iff position i in the superpermutation is set to j
    varz = {(i,j): formula.AddVar(f'{i}:{j}') for i in positions for j in symbols}

    # Constraint: each position in the superpermutation is set to exactly one value.
    for i in positions:
        formula.Add(NumTrue(*(varz[(i,j)] for j in symbols)) == 1)

    # Constraint: each permutation of order n occurs at least once in the string.
    for perm in permutations(symbols):
        perm_at = [And(*(varz[(start+offset,j)] for offset, j in enumerate(perm))) for start in range(m-n+1)]
        formula.Add(Or(*perm_at))

    # Symmetry-breaking: first n chars of superpermutation are 1,2,...,n
    for i, j in enumerate(symbols):
        formula.Add(varz[(i,j)])

    return formula


def print_solution(sol, *extra_args):
    n, m = extra_args
    print(''.join(str(j) for i in range(m) for j in range(1, n+1) if sol[f'{i}:{j}']))

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
        formula.WriteExtractor(f, print_solution, extra_args=[args.n, args.m])
