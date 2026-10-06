from cnfc import *
from itertools import product

import argparse

COORDS = [1,2,3,4,5,6,7,8,9]
VALS = [0,1,2,3,4,5,6,7,8,9]
BOXES = [[1,2,3],[4,5,6],[7,8,9]]
NUM_BITS = Integer.bits_needed_for_range(0, 9)
GCD_BITS = Integer.bits_needed_for_range(1, 999999999)

def encode(min_gcd):
    formula = Formula()

    # The one digit 0-9 that doesn't appear anywhere in the grid.
    exclude = Integer(formula.AddVars('exclude', NUM_BITS))
    formula.Add(0 <= exclude < 10)

    varz = {}
    for r in COORDS:
        for c in COORDS:
            cell = Integer(formula.AddVars(f'cell:{r}:{c}', NUM_BITS))
            formula.Add(0 <= cell < 10)
            formula.Add(cell != exclude)
            varz[(r,c)] = cell

    # Predefined cells
    formula.Add(varz[(1,8)] == 2)
    formula.Add(varz[(2,9)] == 5)
    formula.Add(varz[(3,2)] == 2)
    formula.Add(varz[(4,3)] == 0)
    formula.Add(varz[(6,4)] == 2)
    formula.Add(varz[(7,5)] == 0)
    formula.Add(varz[(8,6)] == 2)
    formula.Add(varz[(9,7)] == 5)

    # Each row, column, and box contains every digit except the excluded one exactly once.
    rows = [[(r,c) for c in COORDS] for r in COORDS]
    cols = [[(r,c) for r in COORDS] for c in COORDS]
    boxes = [list(product(box_rows, box_cols)) for box_rows, box_cols in product(BOXES, BOXES)]
    for group in rows + cols + boxes:
        for v in VALS:
            formula.Add(If(v != exclude, NumTrue(*(varz[cell] == v for cell in group)) == 1))

    # Every row, interpreted as a 9-digit number, is divisible by a common divisor.
    divisor = Integer(formula.AddVars('divisor', GCD_BITS))
    formula.Add(1 <= divisor <= 999999999)
    formula.Add(divisor >= min_gcd)
    for r in COORDS:
        row = sum(varz[(r,c)] * 10**(9-c) for c in COORDS)
        formula.Add(row % divisor == 0)

    return formula

def print_solution(sol, *extra_args):
    from functools import reduce
    from math import gcd
    coords = extra_args[0]
    for r in coords:
        print(''.join(f" {sol.integer(f'cell:{r}:{c}')} " for c in coords))
    print('')
    print(f"Verified common divisor: {sol.integer('divisor')}")
    rows = [sum(sol.integer(f'cell:{r}:{c}') * 10**(9-c) for c in coords) for r in coords]
    print(f'Actual GCD: {reduce(gcd, rows)}')

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
        formula.WriteExtractor(f, print_solution, extra_args=[COORDS])
