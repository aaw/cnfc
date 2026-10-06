# Solves the Diophantine equation from xkcd.com/287:
#
# 215*x1 + 275*x2 + 335*x3 + 355*x4 + 420*x5 + 580*x6 = 1505

from cnfc import *

import argparse

# The cheapest item bounds the number of items we can buy.
BITLENGTH = Integer.bits_needed_for_range(0, 1505 // 215)

def encode_equation_as_sat():
    formula = Formula()
    x1, x2, x3, x4, x5, x6 = xs = [Integer(formula.AddVars(f'x{i}', BITLENGTH)) for i in range(1, 7)]
    for x in xs:
        formula.Add(x >= 0)
    formula.Add(215*x1 + 275*x2 + 335*x3 + 355*x4 + 420*x5 + 580*x6 == 1505)
    return formula

def print_solution(sol, *extra_args):
    xs = [sol.integer(f'x{i}') for i in range(1, 7)]
    print('(2.15 * {}) + (2.75 * {}) + (3.35 * {}) + (3.55 * {}) + (4.20 * {}) + (5.80 * {}) = 15.05'.format(*xs))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve xkcd #287")
    parser.add_argument('out', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode_equation_as_sat()
    with open(args.out, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution)
