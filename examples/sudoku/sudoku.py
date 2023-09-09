from cnfc import *

import argparse

def parse_board(board_string):
    assert len(board_string) == 81, " Sudoku board encoding must be exactly 81 characters, one per square."
    board = []
    while len(board_string) > 0:
        board.append([int(ch) if ch.isnumeric() else None for ch in board_string[:9]])
        board_string = board_string[9:]
    return board

def print_board(board):
    for i, row in enumerate(board):
        if i % 3 == 0: print('+---------+---------+---------+')
        for j, cell in enumerate(row):
            if j % 3 == 0: print('|', end='')
            if cell is None:
                print('   ', end='')
            else:
                print(' {} '.format(cell), end='')
        print('|')
    print('+---------+---------+---------+')

def encode_board_as_sat(board, formula):
    # Variable i:j:k is true if position (i,j) on the board is set to k.
    vs = dict(((i,j,k), formula.AddVar('{}:{}:{}'.format(i,j,k)))
              for i in range(1,10)
              for j in range(1,10)
              for k in range(1,10))

    # Add constraints from given clues.
    for r in range(9):
        for c in range(9):
            if board[r][c] is not None: formula.AddClause(vs[(r+1,c+1,board[r][c])])

    # Each cell contains exactly one number 1-9.
    for r in range(1,10):
        for c in range(1,10):
            cell_vars = (vs[(r,c,n)] for n in range(1,10))
            formula.Add(NumTrue(*cell_vars) == 1)

    # Each row contains each number 1-9 exactly once.
    for r in range(1,10):
        for n in range(1,10):
            row_vars = (vs[(r,c,n)] for c in range(1,10))
            formula.Add(NumTrue(*row_vars) == 1)

    # Each column contains each number 1-9 exactly once.
    for c in range(1,10):
        for n in range(1,10):
            col_vars = (vs[(r,c,n)] for r in range(1,10))
            formula.Add(NumTrue(*col_vars) == 1)

    # Each box contains each number 1-9 exactly once.
    for b in range(9):
        br, bc = 3 * (b // 3) + 1, 3 * (b % 3) + 1
        for n in range(1,10):
            box_vars = (vs[(r,c,n)] for r in range(br,br+3) for c in range(bc,bc+3))
            formula.Add(NumTrue(*box_vars) == 1)

def extract_board_from_solution(sol, *extra_args):
    board = [[None for c in range(9)] for r in range(9)]
    for r in range(1,10):
        for c in range(1,10):
            for n in range(1,10):
                if sol['{}:{}:{}'.format(r,c,n)]:
                    board[r-1][c-1] = n
                    break
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
