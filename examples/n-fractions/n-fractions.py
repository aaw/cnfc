from cnfc import *
from cnfc.funcs import Max, Min

import argparse
import math

DIGIT_BITS = Integer.bits_needed_for_range(1, 9)

def encode(n, max_lcm):
    formula = Formula()

    max_d = math.ceil(max_lcm / 11)
    d_bits = Integer.bits_needed_for_range(0, max_d)
    lcm_bits = Integer.bits_needed_for_range(1, max_lcm)

    lcm = Integer(formula.AddVars('lcm', lcm_bits))
    formula.Add(0 < lcm <= max_lcm)

    # The ith fraction is x_i / (10*y_i + z_i), and d_i is LCM / (10*y_i + z_i).
    xs, ys, zs, ds = [], [], [], []
    for i in range(1, n+1):
        x = Integer(formula.AddVars(f'x{i}', DIGIT_BITS))
        y = Integer(formula.AddVars(f'y{i}', DIGIT_BITS))
        z = Integer(formula.AddVars(f'z{i}', DIGIT_BITS))
        d = Integer(formula.AddVars(f'd{i}', d_bits))
        formula.Add(0 < x < 10)
        formula.Add(0 < y < 10)
        formula.Add(0 < z < 10)
        xs.append(x)
        ys.append(y)
        zs.append(z)
        ds.append(d)
    denominators = [y*10 + z for y, z in zip(ys, zs)]

    # Constraint: Each digit in {1,2,...,9} must occur at least once and at
    # most ceil(n/3) times among x, y, and z values.
    max_occurrences = math.ceil(n / 3)
    for digit in range(1, 10):
        occurrences = NumTrue(*(v == digit for v in xs + ys + zs))
        formula.Add(1 <= occurrences <= max_occurrences)

    # Constraint: Relationship between d's and LCM in terms of y's and z's.
    for denominator, d in zip(denominators, ds):
        formula.Add(denominator * d == lcm)

    # Constraint: Main puzzle constraint: sum of x_i * (LCM / (y_i*10 + z_i)) is LCM.
    # Since the d's are just LCM / (y*10 + z), this simplifies to x_i * d_i.
    formula.Add(sum(x * d for x, d in zip(xs, ds)) == lcm)

    # Symmetry breaking: (y_i, z_i, x_i) tuples are lexicographically ordered.
    # The x, y, and z bits are concatenated into a single tuple for comparison.
    yzx = [Tuple(*y.as_tuple(), *z.as_tuple(), *x.as_tuple()) for x, y, z in zip(xs, ys, zs)]
    for prev, curr in zip(yzx, yzx[1:]):
        formula.Add(prev <= curr)

    # Symmetry breaking: Bound on sum of x's
    formula.Add(Min(denominators) <= sum(xs) <= Max(denominators))

    return formula

def print_solution(sol, *extra_args):
    n, max_lcm = extra_args
    fractions = [f"{sol.integer(f'x{i}')}/{sol.integer(f'y{i}')}{sol.integer(f'z{i}')}" for i in range(1, n+1)]
    print(' + '.join(fractions))
    print(f"LCM of ys and zs: {sol.integer('lcm')}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve the n-fractions puzzle.")
    parser.add_argument('n', type=int, help="Number of fractions.")
    parser.add_argument('max_lcm', type=int, help="Max LCM.")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode(args.n, args.max_lcm)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_args=[args.n, args.max_lcm])
