from collections import defaultdict
from cnfc import *

import argparse

def encode(n):
    formula = Formula()

    # The existence of a perfect cuboid is equivalent to a solution of the Diophantine equations:
    #
    # A^2 + B^2 = C^2
    # A^2 + D^2 = E^2
    # B^2 + D^2 + F^2
    # B^2 + E^2 = G^2

    a = Integer(*(formula.AddVar('a{}'.format(i)) for i in range(n)))
    b = Integer(*(formula.AddVar('b{}'.format(i)) for i in range(n)))
    c = Integer(*(formula.AddVar('c{}'.format(i)) for i in range(n)))
    d = Integer(*(formula.AddVar('d{}'.format(i)) for i in range(n)))
    e = Integer(*(formula.AddVar('e{}'.format(i)) for i in range(n)))
    f = Integer(*(formula.AddVar('f{}'.format(i)) for i in range(n)))
    g = Integer(*(formula.AddVar('g{}'.format(i)) for i in range(n)))

    formula.Add(a > 1)
    formula.Add(b > 1)
    formula.Add(c > 1)
    formula.Add(d > 1)
    formula.Add(e > 1)
    formula.Add(f > 1)
    formula.Add(g > 1)

    formula.Add(a*a + b*b == c*c)
    formula.Add(a*a + d*d == e*e)
    formula.Add(b*b + d*d == f*f)
    formula.Add(b*b + e*e == g*g)

    #formula.Simplify()  # Takes a while and doesn't really simplify the CNF much.
    return formula

def bin_to_int(blist):
    result = 0
    for b in blist:
        result *= 2
        result += 1 if b else 0
    return result

def print_solution(sol, *extra_args):
    n = extra_args[0]

    a_bits = [sol['a{}'.format(i)] for i in range(n)]
    b_bits = [sol['b{}'.format(i)] for i in range(n)]
    c_bits = [sol['c{}'.format(i)] for i in range(n)]
    d_bits = [sol['d{}'.format(i)] for i in range(n)]
    e_bits = [sol['e{}'.format(i)] for i in range(n)]
    f_bits = [sol['f{}'.format(i)] for i in range(n)]
    g_bits = [sol['g{}'.format(i)] for i in range(n)]

    print('a = {}'.format(bin_to_int(a_bits)))
    print('b = {}'.format(bin_to_int(b_bits)))
    print('c = {}'.format(bin_to_int(c_bits)))
    print('d = {}'.format(bin_to_int(d_bits)))
    print('e = {}'.format(bin_to_int(e_bits)))
    print('f = {}'.format(bin_to_int(f_bits)))
    print('g = {}'.format(bin_to_int(g_bits)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Determine if a number is prime by attempting to factor it")
    parser.add_argument('n', type=str, help="Number of bits.")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    n = int(args.n)
    formula = encode(n)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, [bin_to_int], extra_args=[n])
