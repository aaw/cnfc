# Solves the Diophantine equation from xkcd.com/287:
#
# 215*x1 + 275*x2 + 335*x3 + 355*x4 + 420*x5+ 580*x6 = 1505

from cnfc import *

import argparse

# None of x1, x2, x3, x4, x5, x6 need to be more than 3 bits, since
# the minimum coefficient is 215 and 215 * 8 > 1505.
BITLENGTH = 3

def encode_equation_as_sat():
    formula = Formula()
    x1 = Integer(*(formula.AddVar('x1_{}'.format(i)) for i in range(BITLENGTH)))
    x2 = Integer(*(formula.AddVar('x2_{}'.format(i)) for i in range(BITLENGTH)))
    x3 = Integer(*(formula.AddVar('x3_{}'.format(i)) for i in range(BITLENGTH)))
    x4 = Integer(*(formula.AddVar('x4_{}'.format(i)) for i in range(BITLENGTH)))
    x5 = Integer(*(formula.AddVar('x5_{}'.format(i)) for i in range(BITLENGTH)))
    x6 = Integer(*(formula.AddVar('x6_{}'.format(i)) for i in range(BITLENGTH)))
    formula.Add(215*x1 + 275*x2 + 335*x3 + 355*x4 + 420*x5 + 580*x6 == 1505)
    return formula

def bin_to_int(blist):
    result = 0
    for b in blist:
        result *= 2
        result += 1 if b else 0
    return result

def print_solution(sol, *extra_args):
    bitlength = extra_args[0]
    x1 = bin_to_int([sol['x1_{}'.format(i)] for i in range(bitlength)])
    x2 = bin_to_int([sol['x2_{}'.format(i)] for i in range(bitlength)])
    x3 = bin_to_int([sol['x3_{}'.format(i)] for i in range(bitlength)])
    x4 = bin_to_int([sol['x4_{}'.format(i)] for i in range(bitlength)])
    x5 = bin_to_int([sol['x5_{}'.format(i)] for i in range(bitlength)])
    x6 = bin_to_int([sol['x6_{}'.format(i)] for i in range(bitlength)])
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
        formula.WriteExtractor(f, print_solution, extra_fns=[bin_to_int], extra_args=[BITLENGTH])
