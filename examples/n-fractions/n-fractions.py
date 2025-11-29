from collections import defaultdict
from cnfc import *
from cnfc.funcs import Max, Min

import argparse
import math

SOLUTION_BITS=4  # Need to represent 1-9

def bits_needed(n): return len(bin(n)[2:])

def encode(n, max_lcm):
    formula = Formula()

    max_d = int(math.ceil(max_lcm/11))
    d_bits = bits_needed(max_d)
    lcm_bits = bits_needed(max_lcm)

    lcm = Integer(formula.AddVars('lcm', lcm_bits))
    formula.Add(lcm > 0)
    formula.Add(lcm <= max_lcm)

    varz = {}
    ns = range(1,n+1)
    for i in ns:
        x = Integer(formula.AddVars(f'x{i}', SOLUTION_BITS))
        y = Integer(formula.AddVars(f'y{i}', SOLUTION_BITS))
        z = Integer(formula.AddVars(f'z{i}', SOLUTION_BITS))
        d = Integer(formula.AddVars(f'd{i}', d_bits))
        formula.Add(x > 0)
        formula.Add(x < 10)
        formula.Add(y > 0)
        formula.Add(y < 10)
        formula.Add(z > 0)
        formula.Add(z < 10)
        varz[f'x{i}'] = x
        varz[f'y{i}'] = y
        varz[f'z{i}'] = z
        varz[f'd{i}'] = d

    # Constraint: Each digit in {1,2,...,9} must occur at least once and at
    # most ceil(n/3) times among x, y, and z values.
    max_occurrences = int(math.ceil(n/3))
    for i in range(1,10):
        values = [varz[f'x{j}'] == i for j in ns] + [varz[f'y{j}'] == i for j in ns] + [varz[f'z{j}'] == i for j in ns]
        formula.Add(NumTrue(*values) > 0)
        formula.Add(NumTrue(*values) <= max_occurrences)

    # Constraint: Relationship between d's and LCM in terms of y's an z's.
    for i in ns:
        yi, zi, di = varz[f'y{i}'], varz[f'z{i}'], varz[f'd{i}']
        formula.Add((yi*10 + zi) * di == lcm)

    # Constraint: Main puzzle constraint: sum of x_i * (LCM / (y_i*10 + z_i)) is LCM.
    # Since the d's are just LCM / (y*10 + z), this simplifies to x_i * d_i.
    formula.Add(sum(varz[f'x{i}'] * varz[f'd{i}'] for i in ns) == lcm)

    # Symmetry breaking: (y_i, z_i, x_i) tuples are lexicographically ordered.
    for i in range(2,n+1):
        # These x, y, zs are tuples, so we're just concatenating them together.
        prev = varz[f'y{i-1}'].as_tuple() + varz[f'z{i-1}'].as_tuple() + varz[f'x{i-1}'].as_tuple()
        current = varz[f'y{i}'].as_tuple() + varz[f'z{i}'].as_tuple() + varz[f'x{i}'].as_tuple()
        formula.Add(Tuple(*prev) <= Tuple(*current))

    # Symmetry breakding: Bound on sum of x's
    formula.Add(Min([varz[f'y{i}']*10 + varz[f'z{i}'] for i in ns]) <= sum(varz[f'x{i}'] for i in ns))
    formula.Add(sum(varz[f'x{i}'] for i in ns) <= Max([varz[f'y{i}']*10 + varz[f'z{i}'] for i in ns]))

    return formula

def print_solution(sol, *extra_args):
    solution_bits = 4
    n, max_lcm = extra_args
    lcm_bits = len(bin(max_lcm)[2:])

    for i in range(1,n+1):
        x = sol.integer(f'x{i}', solution_bits)
        y = sol.integer(f'y{i}', solution_bits)
        z = sol.integer(f'z{i}', solution_bits)
        print(f'{x}/{y}{z}', end='')
        if i != n: print(' + ', end='')

    print('')
    print(f"LCM of ys and zs: {sol.integer('lcm', lcm_bits)}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve the n-fractions puzzle.")
    parser.add_argument('n', type=int, help="Number to factor.")
    parser.add_argument('max_lcm', type=int, help="Max LCM.")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode(args.n, args.max_lcm)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, [], extra_args=[args.n, args.max_lcm])
