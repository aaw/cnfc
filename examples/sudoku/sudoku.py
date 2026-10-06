from cnfc import *

import argparse

DIGITS = range(1, 10)

def parse_board(board_string):
    assert len(board_string) == 81, "Sudoku board encoding must be exactly 81 characters, one per square."
    return [[int(ch) if ch.isnumeric() else None for ch in board_string[r:r+9]]
            for r in range(0, 81, 9)]

def print_board(board):
    for i, row in enumerate(board):
        if i % 3 == 0: print('+---------+---------+---------+')
        for j, cell in enumerate(row):
            if j % 3 == 0: print('|', end='')
            print('   ' if cell is None else f' {cell} ', end='')
        print('|')
    print('+---------+---------+---------+')

def encode_board_as_sat(board, formula):
    # Variable r:c:n is true if position (r,c) on the board is set to n.
    vs = {(r,c,n): formula.AddVar(f'{r}:{c}:{n}') for r in range(9) for c in range(9) for n in DIGITS}

    # Add constraints from given clues.
    for r in range(9):
        for c in range(9):
            if board[r][c] is not None:
                formula.Add(vs[(r,c,board[r][c])])

    # Each cell contains exactly one number 1-9.
    for r in range(9):
        for c in range(9):
            formula.Add(NumTrue(*(vs[(r,c,n)] for n in DIGITS)) == 1)

    # Each row, column, and box contains each number 1-9 exactly once.
    rows = [[(r,c) for c in range(9)] for r in range(9)]
    cols = [[(r,c) for r in range(9)] for c in range(9)]
    boxes = [[(br+r,bc+c) for r in range(3) for c in range(3)] for br in (0,3,6) for bc in (0,3,6)]
    for group in rows + cols + boxes:
        for n in DIGITS:
            formula.Add(NumTrue(*(vs[(r,c,n)] for r,c in group)) == 1)

def extract_board_from_solution(sol, *extra_args):
    board = [[next(n for n in range(1, 10) if sol[f'{r}:{c}:{n}']) for c in range(9)] for r in range(9)]
    print("Solution: ")
    print_board(board)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a Sudoku solver")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    parser.add_argument('board', type=str, help='Sudoku board, encoded row-by-row as an 81-character string with non-numbers as empty squares.')
    args = parser.parse_args()

    board = parse_board(args.board)
    print("Board to solve:")
    print_board(board)

    formula = Formula()
    encode_board_as_sat(board, formula)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, extract_board_from_solution, [print_board])
