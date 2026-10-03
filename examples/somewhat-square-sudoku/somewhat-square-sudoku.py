from collections import defaultdict
from cnfc import *
from itertools import product, zip_longest

import argparse

COORDS = [1,2,3,4,5,6,7,8,9]
VALS = [0,1,2,3,4,5,6,7,8,9]
BOXES = [[1,2,3],[4,5,6],[7,8,9]]
NUM_BITS = Integer.bits_needed_for_range(0, 9)
GCD_BITS = Integer.bits_needed_for_range(1, 999999999)

def encode(min_gcd):
    #formula = Formula(FileBuffer)
    formula = Formula()

    exclude = Integer(*(formula.AddVar(f'exclude:{i}') for i in range(NUM_BITS)))
    formula.Add(0 <= exclude < 10)

    varz = {}
    for r in COORDS:
        for c in COORDS:
            i = Integer(*(formula.AddVar(f'cell:{r}:{c}:{i}') for i in range(NUM_BITS)))
            formula.Add(0 <= i < 10)
            formula.Add(i != exclude)
            varz[(r,c)] = i

    # Predefined cells
    formula.Add(varz[(1,8)] == Integer(2))
    formula.Add(varz[(2,9)] == Integer(5))
    formula.Add(varz[(3,2)] == Integer(2))
    formula.Add(varz[(4,3)] == Integer(0))
    formula.Add(varz[(6,4)] == Integer(2))
    formula.Add(varz[(7,5)] == Integer(0))
    formula.Add(varz[(8,6)] == Integer(2))
    formula.Add(varz[(9,7)] == Integer(5))

    # Rows
    for r in COORDS:
        row_vals = [varz[(r,c)] for c in COORDS]
        for v in VALS:
            equal_v = (x == v for x in row_vals)
            formula.Add(If(v != exclude, NumTrue(*equal_v) == 1))

    # Columns
    for c in COORDS:
        col_vals = [varz[(r,c)] for r in COORDS]
        for v in VALS:
            equal_v = (x == v for x in col_vals)
            formula.Add(If(v != exclude, NumTrue(*equal_v) == 1))

    # Boxes
    for box_def in product(BOXES, BOXES):
        box = [varz[vpair] for vpair in product(box_def[0], box_def[1])]
        for v in VALS:
            equal_v = (x == v for x in box)
            formula.Add(If(v != exclude, NumTrue(*equal_v) == 1))

    # Rows interpreted as numbers
    row1 = sum(varz[(1,c)] * 10**(9-c) for c in COORDS)
    row2 = sum(varz[(2,c)] * 10**(9-c) for c in COORDS)
    row3 = sum(varz[(3,c)] * 10**(9-c) for c in COORDS)
    row4 = sum(varz[(4,c)] * 10**(9-c) for c in COORDS)
    row5 = sum(varz[(5,c)] * 10**(9-c) for c in COORDS)
    row6 = sum(varz[(6,c)] * 10**(9-c) for c in COORDS)
    row7 = sum(varz[(7,c)] * 10**(9-c) for c in COORDS)
    row8 = sum(varz[(8,c)] * 10**(9-c) for c in COORDS)
    row9 = sum(varz[(9,c)] * 10**(9-c) for c in COORDS)

    divisor = Integer(*(formula.AddVar(f'divisor:{i}') for i in range(GCD_BITS)))

    formula.Add(row1 % divisor == 0)
    formula.Add(row2 % divisor == 0)
    formula.Add(row3 % divisor == 0)
    formula.Add(row4 % divisor == 0)
    formula.Add(row5 % divisor == 0)
    formula.Add(row6 % divisor == 0)
    formula.Add(row7 % divisor == 0)
    formula.Add(row8 % divisor == 0)
    formula.Add(row9 % divisor == 0)

    formula.Add(1 <= divisor <= 999999999)
    formula.Add(divisor >= min_gcd)

    return formula

def gcd(a,b):
    while b:
        a, b = b, a % b
    return a

def print_solution(sol, *extra_args):
    coords = extra_args[0]
    for r in coords:
        for c in coords:
            print(' {} '.format(sol.integer(f'cell:{r}:{c}')), end='')
        print('')
    print('')
    divisor = sol.integer('divisor')
    print(f'Verified common divisor: {divisor}')

    row1 = sum(sol.integer(f'cell:1:{c}') * 10**(9-c) for c in coords)
    row2 = sum(sol.integer(f'cell:2:{c}') * 10**(9-c) for c in coords)
    row3 = sum(sol.integer(f'cell:3:{c}') * 10**(9-c) for c in coords)
    row4 = sum(sol.integer(f'cell:4:{c}') * 10**(9-c) for c in coords)
    row5 = sum(sol.integer(f'cell:5:{c}') * 10**(9-c) for c in coords)
    row6 = sum(sol.integer(f'cell:6:{c}') * 10**(9-c) for c in coords)
    row7 = sum(sol.integer(f'cell:7:{c}') * 10**(9-c) for c in coords)
    row8 = sum(sol.integer(f'cell:8:{c}') * 10**(9-c) for c in coords)
    row9 = sum(sol.integer(f'cell:9:{c}') * 10**(9-c) for c in coords)

    gcd12 = gcd(row1, row2)
    gcd34 = gcd(row3, row4)
    gcd56 = gcd(row5, row6)
    gcd78 = gcd(row7, row8)
    gcd1234 = gcd(gcd12, gcd34)
    gcd5678 = gcd(gcd56, gcd78)
    gcd12345678 = gcd(gcd1234, gcd5678)
    final_gcd = gcd(gcd12345678, row9)

    print(f'Actual GCD: {final_gcd}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve the somewhat square Sudoku with a GCD target")
    parser.add_argument('min_gcd', type=int, help='Minimum GCD of resulting rows.')
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode(args.min_gcd)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, [gcd], extra_args=[COORDS])
