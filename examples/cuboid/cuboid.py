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

    a = Integer(formula.AddVars('a', n))
    b = Integer(formula.AddVars('b', n))
    c = Integer(formula.AddVars('c', n))
    d = Integer(formula.AddVars('d', n))
    e = Integer(formula.AddVars('e', n))
    f = Integer(formula.AddVars('f', n))
    g = Integer(formula.AddVars('g', n))

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

def print_solution(sol, *extra_args):
    n = extra_args[0]
    print('a = {}'.format(sol.integer('a', n)))
    print('b = {}'.format(sol.integer('b', n)))
    print('c = {}'.format(sol.integer('c', n)))
    print('d = {}'.format(sol.integer('d', n)))
    print('e = {}'.format(sol.integer('e', n)))
    print('f = {}'.format(sol.integer('f', n)))
    print('g = {}'.format(sol.integer('g', n)))

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
        formula.WriteExtractor(f, print_solution, [], extra_args=[n])
