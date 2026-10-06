from cnfc import *
from itertools import product

import argparse

# Cells are named like a chessboard: 'a1' is the top-left cell, 'f6' is the bottom-right.
ROWS = 'abcdef'
COLS = '123456'
NUM_BITS = Integer.bits_needed_for_range(1, 6)

def encode():
    formula = Formula()

    v = {}
    for row in ROWS:
        for col in COLS:
            cell = Integer(formula.AddVars(f'v:{row}:{col}', NUM_BITS))
            formula.Add(0 < cell < 7)
            v[row + col] = cell

    # Normal Sudoku rules: each row, column, and 2x3 box contains each number exactly once.
    rows = [[row + col for col in COLS] for row in ROWS]
    cols = [[row + col for row in ROWS] for col in COLS]
    boxes = [[row + col for row in box_rows for col in box_cols]
             for box_rows, box_cols in product(['ab', 'cd', 'ef'], ['123', '456'])]
    for group in rows + cols + boxes:
        for number in range(1, 7):
            formula.Add(NumTrue(*(v[cell] == number for cell in group)) == 1)

    # The sum of the blue box equals the product of each pink diagonal.
    box_sum = (v['a1'] + v['a2'] + v['a3'] +
               v['b1'] + v['b2'] + v['b3'] +
               v['c1'] + v['c2'] + v['c3'])
    formula.Add(box_sum == v['a1'] * v['b2'] * v['c3'] * v['d4'] * v['e5'] * v['f6'])
    formula.Add(box_sum == v['d1'] * v['e2'] * v['f3'])
    formula.Add(box_sum == v['b6'] * v['c5'] * v['d4'] * v['e3'] * v['f2'])
    formula.Add(box_sum == v['a3'] * v['b2'] * v['c1'])

    return formula

def print_solution(sol, *extra_args):
    for row in 'abcdef':
        print(''.join(f" {sol.integer(f'v:{row}:{col}')} " for col in '123456'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve the Product-Sum Sudoku from the RSS Christmas Quiz 2023")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode()
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution)
