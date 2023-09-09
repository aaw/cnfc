from collections import defaultdict
from cnfc import *

import argparse

def encode(n):
    formula = Formula()
    # Variable i:j is true if there's a queen in position (i,j) on the board.
    vs = dict(((i,j), formula.AddVar('{}:{}'.format(i,j)))
              for i in range(n)
              for j in range(n))

    # Each row has exactly one queen.
    for r in range(n):
        row_vars = (vs[(r,c)] for c in range(n))
        formula.Add(NumTrue(*row_vars) == 1)

    # Each column has exactly one queen.
    for c in range(n):
        col_vars = (vs[(r,c)] for r in range(n))
        formula.Add(NumTrue(*col_vars) == 1)

    # Each diagonal has at most one queen.
    forward, backward = defaultdict(list), defaultdict(list)
    for r in range(n):
        for c in range(n):
            forward[r-c].append(vs[(r,c)])
            backward[r+c].append(vs[(r,c)])
    for diagonal in forward.values():
        formula.Add(NumTrue(*diagonal) <= 1)
    for diagonal in backward.values():
        formula.Add(NumTrue(*diagonal) <= 1)
    return formula

def print_solution(sol, *extra_args):
    n = extra_args[0]
    for r in range(n):
        print('+---'*n + '+')
        for c in range(n):
            print('| {} '.format('Q' if sol['{}:{}'.format(r,c)] else ' '), end='')
        print('|')
    print('+---'*n + '+')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate an n-Queens solver")
    parser.add_argument('n', type=str, help="Number of queens (also width and height of chessboard).")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    n = int(args.n)
    formula = encode(n)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_args=[n])
