# Finds a date DD/MM/YYYY such that all digits in the date are unique and DD * MM * YYYY is a square.
# Problem posed in https://puzzling.stackexchange.com/questions/126447

from cnfc import *
from cnfc.funcs import AllDifferent

import argparse
import math

DIGIT_BITS = Integer.bits_needed_for_range(0, 9)
DIGIT_NAMES = ['d1', 'd2', 'm1', 'm2', 'y1', 'y2', 'y3', 'y4']

def encode_equation_as_sat(min_year, max_year):
    formula = Formula(FileBuffer)
    # Date is d1d2/m1m2/y1y2y3y4
    d1, d2, m1, m2, y1, y2, y3, y4 = digits = [Integer(formula.AddVars(name, DIGIT_BITS)) for name in DIGIT_NAMES]

    day = 10*d1 + d2
    month = 10*m1 + m2
    year = 1000*y1 + 100*y2 + 10*y3 + y4

    # Constraint: Every digit is actually a digit
    for digit in digits:
        formula.Add(0 <= digit < 10)

    # Constraint: All digits are different.
    formula.Add(AllDifferent(digits, values=range(10)))

    # Constraint: month is valid.
    formula.Add(0 < month <= 12)

    # Constraint: day is valid, given the month
    formula.Add(0 < day <= 31)
    formula.Add(If(day == 31, Or(*(month == m for m in (1, 3, 5, 7, 8, 10, 12)))))
    formula.Add(If(day == 30, month != 2))
    # A year is a leap year if it's divisible by 4, except for centuries, which must be divisible
    # by 400. A number is divisible by 4 iff its last two digits are, so we can work with digits:
    is_leap_year = If(And(y3 == 0, y4 == 0), (10*y1 + y2) % 4 == 0, (10*y3 + y4) % 4 == 0)
    formula.Add(If(And(day == 29, month == 2), is_leap_year))

    # Constraint: year is in the range we're searching.
    formula.Add(min_year <= year <= max_year)

    # Constraint: product of day, month, year is a square.
    root_bits = Integer.bits_needed_for_range(0, math.isqrt(12 * 31 * 9999))
    s = Integer(formula.AddVars('s', root_bits))
    formula.Add(s >= 0)
    formula.Add(month * day * year == s * s)

    return formula

def print_solution(sol, *extra_args):
    d1, d2, m1, m2, y1, y2, y3, y4 = [sol.integer(name) for name in extra_args[0]]
    print(f'{d1}{d2}/{m1}{m2}/{y1}{y2}{y3}{y4}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find pandigital solutions to DD/MM/YYYY with DD * MM * YYYY a square")
    parser.add_argument('--max_year', type=int, help='Maximum year to search (inclusive)', default=9999)
    parser.add_argument('--min_year', type=int, help='Minimum year to search (inclusive)', default=2024)
    parser.add_argument('out', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode_equation_as_sat(args.min_year, args.max_year)
    with open(args.out, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_args=[DIGIT_NAMES])
