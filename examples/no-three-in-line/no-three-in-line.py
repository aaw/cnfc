from cnfc import *

import argparse

# Return all integer points on the line defined by point1 and point2 within
# the n x n zero-indexed grid.
def intpoints(point1, point2, n):
    r1, c1 = point1
    r2, c2 = point2
    return [
        (r, c)
        for r in range(n)
        for c in range(n)
        if (r - r1) * (c2 - c1) == (c - c1) * (r2 - r1)
    ]

# Just to make sure...
assert (3, 0) in intpoints((1, 0), (5, 0), 10)
assert (0, 0) in intpoints((1, 0), (5, 0), 10)
assert (8, 0) in intpoints((1, 0), (5, 0), 10)
assert (2, 3) in intpoints((2, 1), (2, 5), 10)
assert (2, 0) in intpoints((2, 1), (2, 5), 10)
assert (2, 9) in intpoints((2, 1), (2, 5), 10)
assert (2, 2) in intpoints((0, 0), (4, 4), 5)
assert (4, 0) in intpoints((4, 0), (3, 1), 5)
assert (3, 1) in intpoints((4, 0), (3, 1), 5)
assert (1, 3) in intpoints((4, 0), (3, 1), 5)
assert (3, 2) in intpoints((1, 1), (5, 3), 6)
assert (1, 3) in intpoints((0, 4), (2, 2), 5)
assert (3, 1) in intpoints((1, 7), (2, 4), 10)

def encode(n):
    formula = Formula()

    pos = {}
    for r in range(n):
        for c in range(n):
            # pos[(r,c)] is true exactly when there's a point at row r, column c.
            pos[(r,c)] = formula.AddVar(f'pos:{r}:{c}')

    # Constraint: exactly 2n points are placed.
    all_points = [pos[(r,c)] for r in range(n) for c in range(n)]
    formula.Add(NumTrue(*all_points) == 2*n)

    # Constraint: for every pair of points, no other points on their line exist.
    for r1 in range(n):
        for c1 in range(n):
            for r2 in range(n):
                for c2 in range(n):
                    point1, point2 = (r1,c1), (r2,c2)
                    if point1 == point2: continue
                    for point in intpoints(point1, point2, n):
                        if point in (point1, point2): continue
                        formula.Add(Or(~pos[point1],~pos[point2],~pos[point]))

    return formula

def print_solution(sol, *extra_args):
    n = extra_args[0]
    for r in range(n):
        row = []
        for c in range(n):
            row.append("●" if sol[f"pos:{r}:{c}"] else "┼")
        print("───".join(row))
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
        formula.WriteExtractor(f, print_solution, [], extra_args=[args.n])
