# Find a solution to the diophantine equation a/(b+c) + b/(a+c) + c/(a+b) = 4.
# From https://mathoverflow.net/questions/227713/estimating-the-size-of-solutions-of-a-diophantine-equation,
# the smallest known solution is:
#
# a=4373612677928697257861252602371390152816537558161613618621437993378423467772036
# b=36875131794129999827197811565225474825492979968971970996283137471637224634055579
# c=154476802108746166441951315019919837485664325669565431700026634898253202035277999

from cnfc import *

import argparse

# Enough capacity for the known solution, with room to search.
MAX_VALUE = 10**81 - 1
BITLENGTH = Integer.bits_needed_for_range(1, MAX_VALUE)

def encode_equation_as_sat():
    formula = Formula(FileBuffer)
    a, b, c = (Integer(formula.AddVars(name, BITLENGTH)) for name in 'abc')
    # Clearing denominators turns a/(b+c) + b/(a+c) + c/(a+b) = 4 into this polynomial:
    a2, b2, c2 = a*a, b*b, c*c
    formula.Add(a2*a + b2*b + c2*c == 3*(a2*b + a*b2 + a2*c + a*c2 + b2*c + b*c2) + 5*a*b*c)
    for x in (a, b, c):
        formula.Add(x > 0)
    return formula

def print_solution(sol, *extra_args):
    for name in 'abc':
        print(f'{name} = {sol.integer(name)}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve a tough diophantine equation.")
    parser.add_argument('out', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode_equation_as_sat()
    with open(args.out, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution)
