# Finds solutions to the pandigital alphametic A x BC x DEF = GHIJ.
# See https://puzzling.stackexchange.com/questions/126266/a-pandigital-alphametic

from cnfc import *

import argparse

BITLENGTH = Integer.bits_needed_for_range(0, 9)

# Returns a constraint that rules out a known solution like '1 x 26 x 345 = 8970'.
def block(solution, varz):
    digits = [int(ch) for ch in solution if ch.isdigit()]
    return Or(*(v != digit for v, digit in zip(varz, digits)))

def encode_equation_as_sat():
    formula = Formula(FileBuffer)
    a, b, c, d, e, f, g, h, i, j = varz = [Integer(formula.AddVars(name, BITLENGTH)) for name in 'abcdefghij']

    # Block known solutions
    solutions = [
        '1 x 26 x 345 = 8970', # No leading zeros
        '2 x 14 x 307 = 8596', # No leading zeros
        '1 x 08 x 459 = 3672',
        '1 x 08 x 469 = 3752',
        '1 x 08 x 537 = 4296',
        '1 x 08 x 579 = 4632',
        '1 x 08 x 592 = 4736',
        '1 x 08 x 674 = 5392',
        '1 x 08 x 679 = 5432',
        '1 x 08 x 742 = 5936',
        '1 x 08 x 794 = 6352',
        '1 x 08 x 932 = 7456',
        '1 x 08 x 942 = 7536',
        '1 x 08 x 953 = 7624',
        '1 x 08 x 954 = 7632',
        '1 x 09 x 638 = 5742',
        '1 x 09 x 647 = 5823',
        '1 x 09 x 836 = 7524',
        '1 x 53 x 092 = 4876',
        '1 x 62 x 087 = 5394',
        '1 x 87 x 062 = 5394',
        '1 x 92 x 053 = 4876',
        '2 x 07 x 594 = 8316',
        '2 x 07 x 681 = 9534',
        '2 x 34 x 087 = 5916',
        '2 x 39 x 061 = 4758',
        '2 x 41 x 073 = 5986',
        '2 x 59 x 073 = 8614',
        '2 x 61 x 039 = 4758',
        '2 x 73 x 041 = 5986',
        '2 x 73 x 059 = 8614',
        '2 x 87 x 034 = 5916',
        '3 x 04 x 581 = 6972',
        '3 x 04 x 716 = 8592',
        '3 x 28 x 071 = 5964',
        '3 x 71 x 028 = 5964',
        '4 x 03 x 581 = 6972',
        '4 x 03 x 716 = 8592',
        '4 x 06 x 158 = 3792',
        '6 x 04 x 158 = 3792',
        '6 x 08 x 154 = 7392',
        '6 x 09 x 138 = 7452',
        '7 x 02 x 594 = 8316',
        '7 x 02 x 681 = 9534',
        '7 x 18 x 029 = 3654',
        '7 x 19 x 026 = 3458',
        '7 x 26 x 019 = 3458',
        '7 x 29 x 018 = 3654',
        '8 x 01 x 459 = 3672',
        '8 x 01 x 469 = 3752',
        '8 x 01 x 537 = 4296',
        '8 x 01 x 579 = 4632',
        '8 x 01 x 592 = 4736',
        '8 x 01 x 674 = 5392',
        '8 x 01 x 679 = 5432',
        '8 x 01 x 742 = 5936',
        '8 x 01 x 794 = 6352',
        '8 x 01 x 932 = 7456',
        '8 x 01 x 942 = 7536',
        '8 x 01 x 953 = 7624',
        '8 x 01 x 954 = 7632',
        '8 x 06 x 154 = 7392',
        '8 x 19 x 036 = 5472',
        '8 x 19 x 037 = 5624',
        '8 x 36 x 019 = 5472',
        '8 x 37 x 019 = 5624',
        '9 x 01 x 638 = 5742',
        '9 x 01 x 647 = 5823',
        '9 x 01 x 836 = 7524',
        '9 x 06 x 138 = 7452',
        '9 x 16 x 038 = 5472',
        '9 x 38 x 016 = 5472',
    ]
    for solution in solutions:
        formula.Add(block(solution, varz))

    # Every number 0-9 is assigned to a variable exactly once.
    for number in range(10):
        formula.Add(NumTrue(*(x == number for x in varz)) == 1)

    # A x BC x DEF = GHIJ
    bc = 10*b + c
    def_ = 100*d + 10*e + f
    ghij = 1000*g + 100*h + 10*i + j
    formula.Add(a * bc * def_ == ghij)

    return formula

def print_solution(sol, *extra_args):
    a, b, c, d, e, f, g, h, i, j = [sol.integer(name) for name in 'abcdefghij']
    print(f'{a} x {b}{c} x {d}{e}{f} = {g}{h}{i}{j}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find solutions to the pandigital alphametic A x BC x DEF = GHIJ")
    parser.add_argument('out', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode_equation_as_sat()
    with open(args.out, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution)
