from cnfc import *
from itertools import combinations

import argparse

# Returns true exactly when the three points lie on a common line.
def collinear(point1, point2, point3):
    (r1, c1), (r2, c2), (r3, c3) = point1, point2, point3
    return (r2 - r1) * (c3 - c1) == (r3 - r1) * (c2 - c1)

assert collinear((1, 0), (5, 0), (3, 0))
assert collinear((0, 0), (4, 4), (2, 2))
assert collinear((4, 0), (3, 1), (1, 3))
assert collinear((1, 7), (2, 4), (3, 1))
assert not collinear((0, 0), (1, 2), (2, 3))

def encode(n):
    formula = Formula()

    # pos[(r,c)] is true exactly when there's a point at row r, column c.
    pos = {(r,c): formula.AddVar(f'pos:{r}:{c}') for r in range(n) for c in range(n)}

    # Constraint: exactly 2n points are placed.
    formula.Add(NumTrue(*pos.values()) == 2*n)

    # Constraint: no three points are placed on a common line.
    for point1, point2, point3 in combinations(pos, 3):
        if collinear(point1, point2, point3):
            formula.Add(Or(~pos[point1], ~pos[point2], ~pos[point3]))

    return formula

def print_solution(sol, *extra_args):
    n = extra_args[0]
    for r in range(n):
        print("───".join("●" if sol[f"pos:{r}:{c}"] else "┼" for c in range(n)))
        if r < n - 1:
            print("│   " * (n - 1) + "│")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate an n-by-n grid with 2n points, no three in a line.")
    parser.add_argument('n', type=int, help="Dimension of grid, n-by-n.")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode(args.n)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_args=[args.n])
