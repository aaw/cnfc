# Solves the Diophantine equation from xkcd.com/287:
#
# 215*x1 + 275*x2 + 335*x3 + 355*x4 + 420*x5+ 580*x6 = 1505

from cnfc import *

import argparse

# The cheapest item bounds the number of items we can buy.
BITLENGTH = Integer.bits_needed_for_range(0, 1505 // 215)

def encode_equation_as_sat():
    formula = Formula()
    x1 = Integer(formula.AddVars('x1', BITLENGTH))
    x2 = Integer(formula.AddVars('x2', BITLENGTH))
    x3 = Integer(formula.AddVars('x3', BITLENGTH))
    x4 = Integer(formula.AddVars('x4', BITLENGTH))
    x5 = Integer(formula.AddVars('x5', BITLENGTH))
    x6 = Integer(formula.AddVars('x6', BITLENGTH))
    for x in (x1, x2, x3, x4, x5, x6):
        formula.Add(x >= 0)
    formula.Add(215*x1 + 275*x2 + 335*x3 + 355*x4 + 420*x5 + 580*x6 == 1505)
    return formula

def print_solution(sol, *extra_args):
    x1 = sol.integer('x1')
    x2 = sol.integer('x2')
    x3 = sol.integer('x3')
    x4 = sol.integer('x4')
    x5 = sol.integer('x5')
    x6 = sol.integer('x6')
    print('(2.15 * {}) + (2.75 * {}) + (3.35 * {}) + (3.55 * {}) + (4.20 * {}) + (5.80 * {}) = 15.05'.format(x1,x2,x3,x4,x5,x6))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve xkcd #287")
    parser.add_argument('out', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode_equation_as_sat()
    with open(args.out, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_fns=[], extra_args=[])
