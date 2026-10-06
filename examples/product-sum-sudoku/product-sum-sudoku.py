from cnfc import *
from cnfc.funcs import AllDifferent
from itertools import product
import math

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
        formula.Add(AllDifferent([v[cell] for cell in group], values=range(1, 7)))

    # The sum of the blue box equals the product of each pink diagonal.
    box_sum = sum(v[row + col] for row in 'abc' for col in '123')
    diagonals = [
        ['a1', 'b2', 'c3', 'd4', 'e5', 'f6'],
        ['d1', 'e2', 'f3'],
        ['b6', 'c5', 'd4', 'e3', 'f2'],
        ['a3', 'b2', 'c1'],
    ]
    for diagonal in diagonals:
        formula.Add(box_sum == math.prod(v[cell] for cell in diagonal))

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
