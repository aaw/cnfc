from collections import defaultdict
from cnfc import *

import argparse

NUM_BITS=4  # Need enough to encode integers 1-10

def encode():
    formula = Formula()

    a = Integer(formula.AddVars('a', NUM_BITS))
    b = Integer(formula.AddVars('b', NUM_BITS))
    c = Integer(formula.AddVars('c', NUM_BITS))
    d = Integer(formula.AddVars('d', NUM_BITS))
    e = Integer(formula.AddVars('e', NUM_BITS))
    f = Integer(formula.AddVars('f', NUM_BITS))

    varz = [a,b,c,d,e,f]

    # Constraint: a,b,c,d,e,f between 1 and 10, inclusive.
    for v in varz:
        formula.Add(1 <= v <= 10)

    # Constraint: a,b,c,d,e,f all distinct.
    for i in range(len(varz)):
        for j in range(i+1, len(varz)):
            formula.Add(varz[i] != varz[j])

    # Constraint: 1. B - D = 2
    formula.Add(b - d == 2)

    # Constraint: 2. F + A = 11
    formula.Add(f + a == 11)

    # Constraint: 3. A is between D and C
    formula.Add(d < a < c)

    # Constraint: 4. No two variables sum to 14
    for i in range(len(varz)):
        for j in range(i+1, len(varz)):
            formula.Add(varz[i] + varz[j] != 14)

    # Constraint: 5. No two variables sum to 5
    for i in range(len(varz)):
        for j in range(i+1, len(varz)):
            formula.Add(varz[i] + varz[j] != 5)

    # Constraint: 6. C - A = 1
    formula.Add(c - a == 1)

    return formula


def print_solution(sol, *extra_args):
    num_bits = extra_args[0]
    a = sol.integer('a', num_bits)
    b = sol.integer('b', num_bits)
    c = sol.integer('c', num_bits)
    d = sol.integer('d', num_bits)
    e = sol.integer('e', num_bits)
    f = sol.integer('f', num_bits)
    print(f'A = {a}\nB = {b}\nC = {c}\nD = {d}\nE = {e}\nF = {f}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve a six variable logic puzzle")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode()
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, [], extra_args=[NUM_BITS])
