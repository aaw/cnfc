# Finds a date DD/MM/YYYY such that all digits in the date are unique and DD * MM * YYYY is a square.
# Problem posed in https://puzzling.stackexchange.com/questions/126447

from cnfc import *

import argparse

BITLENGTH = 4

def encode_equation_as_sat(min_year, max_year):
    formula = Formula(FileBuffer)
    # Date is d1d2/m1m2/y1y2y3y4
    d1 = Integer(*(formula.AddVar('d1_{}'.format(i)) for i in range(BITLENGTH)))
    d2 = Integer(*(formula.AddVar('d2_{}'.format(i)) for i in range(BITLENGTH)))
    m1 = Integer(*(formula.AddVar('m1_{}'.format(i)) for i in range(BITLENGTH)))
    m2 = Integer(*(formula.AddVar('m2_{}'.format(i)) for i in range(BITLENGTH)))
    y1 = Integer(*(formula.AddVar('y1_{}'.format(i)) for i in range(BITLENGTH)))
    y2 = Integer(*(formula.AddVar('y2_{}'.format(i)) for i in range(BITLENGTH)))
    y3 = Integer(*(formula.AddVar('y3_{}'.format(i)) for i in range(BITLENGTH)))
    y4 = Integer(*(formula.AddVar('y4_{}'.format(i)) for i in range(BITLENGTH)))
    varz = [d1, d2, m1, m2, y1, y2, y3, y4]

    day = d1 * Integer(10) + d2
    month = m1 * Integer(10) + m2
    year = y1 * Integer(1000) + y2 * Integer(100) + y3 * Integer(10) + y4

    # Constraint: Every digit is actually a digit
    for v in varz:
        formula.Add(v < 10)

    # Constraint: Every number 0-9 is assigned to a digit variable at most once.
    for number in range(10):
        equal_n = (x == number for x in varz)
        formula.Add(NumTrue(*equal_n) <= 1)

    # Constraint: month is valid.
    formula.Add(month > 0)
    formula.Add(month <= 12)

    # Constraint: day is valid, given the month
    formula.Add(day > 0)
    formula.Add(day <= 31)
    formula.Add(Implies(day == 31, Or(month == 1, month == 3, month == 5, month == 7, month == 8, month == 10, month == 12)))
    formula.Add(Implies(day == 30, Or(month != 2)))
    # The correct leap year constraint (divisible by 4, unless divisible by 100, unless divisible by 400) is hard
    # to encode, so we'll just use a simpler check and deal with invalid leap years by blocking them if they
    # arise as solutions to the other constraints.
    x = Integer(*(formula.AddVar('x_{}'.format(i)) for i in range(12)))
    formula.Add(Implies(day == 29, Or(month != 2, And(month == 2, year == x * Integer(4)))))

    # Constraint: year is in the range we're searching.
    # 2024 <= year <= max_year
    formula.Add(year >= 2024)
    formula.Add(year <= Integer(max_year))
    formula.Add(year >= Integer(min_year))

    # Constraint: product of day, month, year is a square.
    # log_2(12) + log_2(31) + log_2(9999) + 2 <= 24 bits should be enough to hold the product, so 12 bits
    # should be enough to hold the square root of the product. We use 13 just in case.
    s = Integer(*(formula.AddVar('s_{}'.format(i)) for i in range(13)))
    formula.Add(month * day * year == s * s)

    return formula

def bin_to_int(blist):
    result = 0
    for b in blist:
        result *= 2
        result += 1 if b else 0
    return result

def print_solution(sol, *extra_args):
    bitlength = extra_args[0]
    d1 = bin_to_int([sol['d1_{}'.format(i)] for i in range(bitlength)])
    d2 = bin_to_int([sol['d2_{}'.format(i)] for i in range(bitlength)])
    m1 = bin_to_int([sol['m1_{}'.format(i)] for i in range(bitlength)])
    m2 = bin_to_int([sol['m2_{}'.format(i)] for i in range(bitlength)])
    y1 = bin_to_int([sol['y1_{}'.format(i)] for i in range(bitlength)])
    y2 = bin_to_int([sol['y2_{}'.format(i)] for i in range(bitlength)])
    y3 = bin_to_int([sol['y3_{}'.format(i)] for i in range(bitlength)])
    y4 = bin_to_int([sol['y4_{}'.format(i)] for i in range(bitlength)])
    print('{}{}/{}{}/{}{}{}{}'.format(d1,d2,m1,m2,y1,y2,y3,y4))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find pandigital solutions to DD/MM/YYYY with DD * MM * YYYY a square")
    parser.add_argument('--max_year', type=int, help='Maximum year to search (inclusive)', default=9999)
    parser.add_argument('--min_year', type=int, help='Minimum year to search (inclusive)', default=0)
    parser.add_argument('out', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode_equation_as_sat(args.min_year, args.max_year)
    with open(args.out, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_fns=[bin_to_int], extra_args=[BITLENGTH])
