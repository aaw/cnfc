from cnfc import *

import argparse

def encode(n, d):
    formula = Formula()
    vs = {}
    for r in range(d):
        for c in range(d):
            for i in range(-1,9):
                # Variable r:c:i means cell at (r,c) contains i. We use i=-1 to
                # signify a mine and i in 0-8 to signify no mine but i mines in
                # the surrounding spaces.
                vs[(r,c,i)] = formula.AddVar("{}:{}:{}".format(r,c,i))

    # Each cell should be associated with exactly one value.
    for r in range(d):
        for c in range(d):
            cell_vars = (vs[(r,c,i)] for i in range(-1,9))
            formula.Add(NumTrue(*cell_vars) == 1)

    # The board needs to have exactly n 0's, n 1's, n 2's, etc.
    for i in range(9):
        cells_marked_i = (vs[(r,c,i)] for r in range(d) for c in range(d))
        formula.Add(NumTrue(*cells_marked_i) == n)

    # If a cell has a number >= 0, that number should accurately represent the
    # number of mines in surrounding cells.
    for r in range(d):
        for c in range(d):
            for i in range(9):
                surrounding = []
                # Cells above
                surrounding += [vs[(r-1,c-1,-1)]] if r > 0 and c > 0 else []
                surrounding += [vs[(r-1,c,-1)]] if r > 0 else []
                surrounding += [vs[(r-1,c+1,-1)]] if r > 0 and c < d-1 else []
                # Cells to left and right
                surrounding += [vs[(r,c-1,-1)]] if c > 0 else []
                surrounding += [vs[(r,c+1,-1)]] if c < d-1 else []
                # Cells below
                surrounding += [vs[(r+1,c-1,-1)]] if r < d-1 and c > 0 else []
                surrounding += [vs[(r+1,c,-1)]] if r < d-1 else []
                surrounding += [vs[(r+1,c+1,-1)]] if r < d-1 and c < d-1 else []
                if len(surrounding) < i:
                    # An i in this cell is impossible
                    formula.Add(~vs[(r,c,i)])
                else:
                    formula.Add(Implies(vs[(r,c,i)], NumTrue(*surrounding) == i))

    return formula

def print_solution(sol, *extra_args):
    n, d = extra_args
    for r in range(d):
        for c in range(d):
            if sol['{}:{}:-1'.format(r,c)]:
                print('x', end='')
            else:
                for i in range(9):
                    if sol['{}:{}:{}'.format(r,c,i)]:
                        print(i, end='')
                        break
        print()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a Minesweeper board where each number appears exactly n times")
    parser.add_argument('n', type=str, help="Times a number can appear.")
    parser.add_argument('d', type=str, help="Dimension of square board.")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    n = int(args.n)
    d = int(args.d)
    formula = encode(n, d)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_args=[n,d])
