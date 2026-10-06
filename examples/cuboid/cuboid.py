from cnfc import *

import argparse

def encode(n):
    formula = Formula()

    # The existence of a perfect cuboid is equivalent to a solution of the Diophantine equations:
    #
    # A^2 + B^2 = C^2
    # A^2 + D^2 = E^2
    # B^2 + D^2 = F^2
    # B^2 + E^2 = G^2

    bits = Integer.bits_needed_for_range(0, (1 << n) - 1)
    a, b, c, d, e, f, g = (Integer(formula.AddVars(name, bits)) for name in 'abcdefg')
    for x in (a, b, c, d, e, f, g):
        formula.Add(x > 1)

    formula.Add(a*a + b*b == c*c)
    formula.Add(a*a + d*d == e*e)
    formula.Add(b*b + d*d == f*f)
    formula.Add(b*b + e*e == g*g)

    return formula

def print_solution(sol, *extra_args):
    for name in 'abcdefg':
        print(f'{name} = {sol.integer(name)}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Search for a perfect cuboid with n-bit edges and diagonals")
    parser.add_argument('n', type=int, help="Number of bits.")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode(args.n)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution)
