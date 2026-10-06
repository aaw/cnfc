from collections import defaultdict
from cnfc import *

import argparse

def encode(n):
    formula = Formula()
    # Variable i:j is true if there's a queen in position (i,j) on the board.
    vs = {(i,j): formula.AddVar(f'{i}:{j}') for i in range(n) for j in range(n)}

    # Each row has exactly one queen.
    for r in range(n):
        formula.Add(NumTrue(*(vs[(r,c)] for c in range(n))) == 1)

    # Each column has exactly one queen.
    for c in range(n):
        formula.Add(NumTrue(*(vs[(r,c)] for r in range(n))) == 1)

    # Each diagonal has at most one queen.
    forward, backward = defaultdict(list), defaultdict(list)
    for (r,c), v in vs.items():
        forward[r-c].append(v)
        backward[r+c].append(v)
    for diagonal in [*forward.values(), *backward.values()]:
        formula.Add(NumTrue(*diagonal) <= 1)

    return formula, list(vs.values())

def print_solution(sol, *extra_args):
    n = extra_args[0]
    for r in range(n):
        print('+---'*n + '+')
        print(''.join('| Q ' if sol[f'{r}:{c}'] else '|   ' for c in range(n)) + '|')
    print('+---'*n + '+')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate an n-Queens solver")
    parser.add_argument('n', type=int, help="Number of queens (also width and height of chessboard).")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    parser.add_argument('--blocker', help='Path to output solution blocker script.')
    args = parser.parse_args()

    formula, board_vars = encode(args.n)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_args=[args.n])
    if args.blocker:
        with open(args.blocker, 'w') as f:
            formula.WriteBlocker(f, board_vars)
