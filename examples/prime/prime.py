from collections import defaultdict
from cnfc import *

import argparse

def encode(n):
    formula = Formula()

    # The two factors p and q should be non-trivial factors, so their
    # bit length should be strictly less than the bit length of n.
    n_bitlength = len(bin(n)[2:])
    ps = [formula.AddVar('p{}'.format(i)) for i in range(n_bitlength-1)]
    qs = [formula.AddVar('q{}'.format(i)) for i in range(n_bitlength-1)]

    p, q = Integer(*ps), Integer(*qs)
    formula.Add(p > Integer(1))
    formula.Add(q > Integer(1))
    formula.Add(Integer(n) == p * q)

    return formula

def bin_to_int(blist):
    result = 0
    for b in blist:
        result *= 2
        result += 1 if b else 0
    return result

def print_solution(sol, *extra_args):
    n = extra_args[0]
    n_bitlength = len(bin(n)[2:])
    p_bits = [sol['p{}'.format(i)] for i in range(n_bitlength-1)]
    q_bits = [sol['q{}'.format(i)] for i in range(n_bitlength-1)]
    p = bin_to_int(p_bits)
    q = bin_to_int(q_bits)
    print('{} can be factored into {} * {}'.format(n, p, q))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Determine if a number is prime by attempting to factor it")
    parser.add_argument('n', type=str, help="Number to factor.")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    n = int(args.n)
    formula = encode(n)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, [bin_to_int], extra_args=[n])
