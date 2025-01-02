from collections import defaultdict
from cnfc import *
from itertools import product, zip_longest

import argparse

COORDS = [1,2,3,4,5,6,7,8,9]
VALS = [0,1,2,3,4,5,6,7,8,9]
BOXES = [[1,2,3],[4,5,6],[7,8,9]]
NUM_BITS = 4
GCD_BITS = 30

def encode(min_gcd):
    #formula = Formula(FileBuffer)
    formula = Formula()

    exclude = Integer(*(formula.AddVar('exclude{}'.format(i)) for i in range(NUM_BITS)))
    formula.Add(exclude < 10)

    varz = {}
    for r in COORDS:
        for c in COORDS:
            # i holds the 3-bit value of cell (r,c).
            i = Integer(*(formula.AddVar(f'cell:{r}:{c}:{i}') for i in range(NUM_BITS)))
            formula.Add(i >= 0)
            formula.Add(i < 10)
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

    gcd = Integer(*(formula.AddVar('gcd{}'.format(i)) for i in range(GCD_BITS)))

    x1 = Integer(*(formula.AddVar('x1:{}'.format(i)) for i in range(GCD_BITS)))
    formula.Add(row1 == x1 * gcd)
    x2 = Integer(*(formula.AddVar('x2:{}'.format(i)) for i in range(GCD_BITS)))
    formula.Add(row2 == x2 * gcd)
    x3 = Integer(*(formula.AddVar('x3:{}'.format(i)) for i in range(GCD_BITS)))
    formula.Add(row3 == x3 * gcd)
    x4 = Integer(*(formula.AddVar('x4:{}'.format(i)) for i in range(GCD_BITS)))
    formula.Add(row4 == x4 * gcd)
    x5 = Integer(*(formula.AddVar('x5:{}'.format(i)) for i in range(GCD_BITS)))
    formula.Add(row5 == x5 * gcd)
    x6 = Integer(*(formula.AddVar('x6:{}'.format(i)) for i in range(GCD_BITS)))
    formula.Add(row6 == x6 * gcd)
    x7 = Integer(*(formula.AddVar('x7:{}'.format(i)) for i in range(GCD_BITS)))
    formula.Add(row7 == x7 * gcd)
    x8 = Integer(*(formula.AddVar('x8:{}'.format(i)) for i in range(GCD_BITS)))
    formula.Add(row8 == x8 * gcd)
    x9 = Integer(*(formula.AddVar('x9:{}'.format(i)) for i in range(GCD_BITS)))
    formula.Add(row9 == x9 * gcd)

    formula.Add(gcd >= min_gcd)

    return formula

def bin_to_int(blist):
    result = 0
    for b in blist:
        result *= 2
        result += 1 if b else 0
    return result

def gcd(a,b):
    while b:
        a, b = b, a % b
    return a

def print_solution(sol, *extra_args):
    coords, num_bits, gcd_bits = extra_args
    for r in coords:
        for c in coords:
            print(' {} '.format(bin_to_int([sol[f'cell:{r}:{c}:{i}'] for i in range(num_bits)])), end='')
        print('')
    print('')
    divisor = bin_to_int([sol[f'gcd{i}'] for i in range(gcd_bits)])
    print(f'Verified common divisor: {divisor}')

    row1 = sum(bin_to_int([sol[f'cell:1:{c}:{i}'] for i in range(num_bits)]) * 10**(9-c) for c in coords)
    row2 = sum(bin_to_int([sol[f'cell:2:{c}:{i}'] for i in range(num_bits)]) * 10**(9-c) for c in coords)
    row3 = sum(bin_to_int([sol[f'cell:3:{c}:{i}'] for i in range(num_bits)]) * 10**(9-c) for c in coords)
    row4 = sum(bin_to_int([sol[f'cell:4:{c}:{i}'] for i in range(num_bits)]) * 10**(9-c) for c in coords)
    row5 = sum(bin_to_int([sol[f'cell:5:{c}:{i}'] for i in range(num_bits)]) * 10**(9-c) for c in coords)
    row6 = sum(bin_to_int([sol[f'cell:6:{c}:{i}'] for i in range(num_bits)]) * 10**(9-c) for c in coords)
    row7 = sum(bin_to_int([sol[f'cell:7:{c}:{i}'] for i in range(num_bits)]) * 10**(9-c) for c in coords)
    row8 = sum(bin_to_int([sol[f'cell:8:{c}:{i}'] for i in range(num_bits)]) * 10**(9-c) for c in coords)
    row9 = sum(bin_to_int([sol[f'cell:9:{c}:{i}'] for i in range(num_bits)]) * 10**(9-c) for c in coords)

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
        formula.WriteExtractor(f, print_solution, [bin_to_int, gcd], extra_args=[COORDS, NUM_BITS, GCD_BITS])
