from cnfc import *

import argparse

MINE = -1
VALUES = range(-1, 9)  # A mine, or the number of mines in the surrounding cells.

def neighbors(r, c, d):
    return [(r+dr, c+dc) for dr in (-1,0,1) for dc in (-1,0,1)
            if (dr, dc) != (0, 0) and 0 <= r+dr < d and 0 <= c+dc < d]

def encode(n, d):
    formula = Formula()
    # Variable r:c:i means cell at (r,c) contains i. We use i=-1 to signify a
    # mine and i in 0-8 to signify no mine but i mines in the surrounding spaces.
    vs = {(r,c,i): formula.AddVar(f'{r}:{c}:{i}') for r in range(d) for c in range(d) for i in VALUES}

    # Each cell should be associated with exactly one value.
    for r in range(d):
        for c in range(d):
            formula.Add(NumTrue(*(vs[(r,c,i)] for i in VALUES)) == 1)

    # The board needs to have exactly n 0's, n 1's, n 2's, etc.
    for i in range(9):
        formula.Add(NumTrue(*(vs[(r,c,i)] for r in range(d) for c in range(d))) == n)

    # If a cell has a number >= 0, that number should accurately represent the
    # number of mines in surrounding cells.
    for r in range(d):
        for c in range(d):
            surrounding_mines = [vs[(nr,nc,MINE)] for nr, nc in neighbors(r, c, d)]
            for i in range(9):
                if len(surrounding_mines) < i:
                    # An i in this cell is impossible
                    formula.Add(~vs[(r,c,i)])
                else:
                    formula.Add(If(vs[(r,c,i)], NumTrue(*surrounding_mines) == i))

    return formula

def print_solution(sol, *extra_args):
    n, d = extra_args
    for r in range(d):
        row = ''
        for c in range(d):
            value = next(i for i in range(-1, 9) if sol[f'{r}:{c}:{i}'])
            row += 'x' if value == -1 else str(value)
        print(row)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a Minesweeper board where each number appears exactly n times")
    parser.add_argument('n', type=int, help="Times a number can appear.")
    parser.add_argument('d', type=int, help="Dimension of square board.")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode(args.n, args.d)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_args=[args.n, args.d])
