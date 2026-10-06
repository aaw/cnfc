# Solves Hitori puzzles (https://en.wikipedia.org/wiki/Hitori): shade cells so that
#
#   1. No number appears twice in a row or column among the unshaded cells,
#   2. No two shaded cells are adjacent, and
#   3. The unshaded cells form a single connected region.

from cnfc import *

import argparse

# The example puzzle from the Wikipedia article.
EXAMPLE = '48163257 36721654 23482861 41657735 72318512 35673184 64235478 87142356'

def encode(grid):
    formula = Formula()
    n = len(grid)
    cells = [(r, c) for r in range(n) for c in range(n)]
    shaded = {(r, c): formula.AddVar(f'{r}:{c}') for r, c in cells}

    # 1. No number repeats among the unshaded cells of a row or column.
    lines = [[(r, c) for c in range(n)] for r in range(n)] + [[(r, c) for r in range(n)] for c in range(n)]
    for line in lines:
        for number in set(grid[r][c] for r, c in line):
            unshaded = [~shaded[(r, c)] for r, c in line if grid[r][c] == number]
            formula.Add(NumTrue(*unshaded) <= 1)

    # 2. Shaded cells aren't adjacent. Build a graph of the unshaded cells along the way.
    unshaded = Graph()
    for r, c in cells:
        unshaded.AddVertex(~shaded[(r, c)])
        for neighbor in [(r+1, c), (r, c+1)]:
            if neighbor in shaded:
                formula.Add(Or(~shaded[(r, c)], ~shaded[neighbor]))
                unshaded.AddEdge(~shaded[(r, c)], ~shaded[neighbor])

    # 3. The unshaded cells are connected.
    formula.Add(Connected(unshaded))

    return formula

def print_solution(sol, *extra_args):
    grid = extra_args[0]
    for r, row in enumerate(grid):
        print(' '.join('#' if sol[f'{r}:{c}'] else number for c, number in enumerate(row)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve a Hitori puzzle")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    parser.add_argument('--puzzle', type=str, default=EXAMPLE,
                        help='Rows of the puzzle separated by spaces (default: the Wikipedia example).')
    args = parser.parse_args()

    grid = args.puzzle.split()
    formula = encode(grid)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_args=[grid])
