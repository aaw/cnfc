# Solves Slitherlink puzzles (https://en.wikipedia.org/wiki/Slitherlink): draw a
# single loop along the edges of a grid so that each numbered cell has exactly
# that many of its four edges on the loop.

from cnfc import *
from itertools import combinations

import argparse

# The example puzzle from the Wikipedia article, with '.' for cells without a clue.
EXAMPLE = '....0. 33..1. ..12.. ..20.. .1..11 .2....'

def encode(grid):
    formula = Formula()
    rows, cols = len(grid), len(grid[0])

    # h:r:c is the horizontal edge above cell (r,c); v:r:c is the vertical edge to its left.
    h = {(r, c): formula.AddVar(f'h:{r}:{c}') for r in range(rows+1) for c in range(cols)}
    v = {(r, c): formula.AddVar(f'v:{r}:{c}') for r in range(rows) for c in range(cols+1)}

    # Each clue counts the loop edges around its cell.
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != '.':
                sides = [h[(r, c)], h[(r+1, c)], v[(r, c)], v[(r, c+1)]]
                formula.Add(NumTrue(*sides) == int(grid[r][c]))

    # At each dot, the loop either passes through (2 edges) or doesn't (0 edges).
    # Edges that meet at a dot are neighbors in a graph of loop edges.
    loop = Graph()
    for r in range(rows+1):
        for c in range(cols+1):
            edges = [e for e in (h.get((r, c-1)), h.get((r, c)), v.get((r-1, c)), v.get((r, c))) if e is not None]
            formula.Add(NumTrue(*edges) != 1)
            formula.Add(NumTrue(*edges) <= 2)
            for e1, e2 in combinations(edges, 2):
                loop.AddEdge(e1, e2)

    # Every dot touching the loop has exactly two loop edges, so the loop edges
    # form one or more separate loops. Requiring them to be connected leaves a
    # single loop.
    formula.Add(Connected(loop))

    return formula

def print_solution(sol, *extra_args):
    grid = extra_args[0]
    rows, cols = len(grid), len(grid[0])
    for r in range(rows+1):
        print('+' + '+'.join('---' if sol[f'h:{r}:{c}'] else '   ' for c in range(cols)) + '+')
        if r < rows:
            cells = [('|' if sol[f'v:{r}:{c}'] else ' ') + f' {grid[r][c].replace(".", " ")} ' for c in range(cols)]
            print(''.join(cells) + ('|' if sol[f'v:{r}:{cols}'] else ' '))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve a Slitherlink puzzle")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    parser.add_argument('--puzzle', type=str, default=EXAMPLE,
                        help="Rows of clues separated by spaces, with '.' for no clue (default: the Wikipedia example).")
    args = parser.parse_args()

    grid = args.puzzle.split()
    formula = encode(grid)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_args=[grid])
