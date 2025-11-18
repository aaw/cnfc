from collections import defaultdict
from cnfc import *

import argparse

def encode(n):
    formula = Formula()

    # The two factors p and q should be non-trivial factors, so their
    # bit length should be strictly less than the bit length of n.
    n_bitlength = len(bin(n)[2:])
    p = Integer(formula.AddVars('p', n_bitlength-1))
    q = Integer(formula.AddVars('q', n_bitlength-1))

    formula.Add(p > 1)
    formula.Add(q > 1)
    formula.Add(p * q == n)

    return formula

def print_solution(sol, *extra_args):
    n = extra_args[0]
    n_bitlength = len(bin(n)[2:])
    p = sol.integer('p', n_bitlength-1)
    q = sol.integer('q', n_bitlength-1)
    print('{} can be factored into {} * {}'.format(n, p, q))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Determine if a number is prime by attempting to factor it")
    parser.add_argument('n', type=int, help="Number to factor.")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode(args.n)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, [], extra_args=[args.n])
