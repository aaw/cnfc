from collections import defaultdict
from cnfc import *
from itertools import product

import argparse

LETTERS = ['a','b','c','d','e','f']
NUMBERS = [1,2,3,4,5,6]
NUM_BITS = 3

def encode():
    formula = Formula()

    varz = {}
    for letter in LETTERS:
        for number in NUMBERS:
            i = Integer(*(formula.AddVar('v{}{}{}'.format(letter, number, i)) for i in range(NUM_BITS)))
            formula.Add(i > 0)
            formula.Add(i < 7)
            varz[(letter,number)] = i

    # Rows
    for letter in LETTERS:
        row = [varz[(letter,number)] for number in NUMBERS]
        for number in NUMBERS:
            equal_n = (x == number for x in row)
            formula.Add(NumTrue(*equal_n) == 1)

    # Columns
    for number in NUMBERS:
        col = [varz[(letter,number)] for letter in LETTERS]
        for number in NUMBERS:
            equal_n = (x == number for x in col)
            formula.Add(NumTrue(*equal_n) == 1)

    # Boxes
    for box_def in product([['a','b'],['c','d'],['e','f']], [[1,2,3],[4,5,6]]):
        box = [varz[vpair] for vpair in product(box_def[0], box_def[1])]
        for number in NUMBERS:
            equal_n = (x == number for x in box)
            formula.Add(NumTrue(*equal_n) == 1)

    # Sum of blue box
    box_sum = (varz[('a',1)] + varz[('a',2)] + varz[('a',3)] +
               varz[('b',1)] + varz[('b',2)] + varz[('b',3)] +
               varz[('c',1)] + varz[('c',2)] + varz[('c',3)])

    # Diagonal products
    d1_prod = varz[('a',1)] * varz[('b',2)] * varz[('c',3)] * varz[('d',4)] * varz[('e',5)] * varz[('f',6)]
    d2_prod = varz[('d',1)] * varz[('e',2)] * varz[('f',3)]
    d3_prod = varz[('b',6)] * varz[('c',5)] * varz[('d',4)] * varz[('e',3)] * varz[('f',2)]
    d4_prod = varz[('a',3)] * varz[('b',2)] * varz[('c',1)]

    formula.Add(box_sum == d1_prod)
    formula.Add(box_sum == d2_prod)
    formula.Add(box_sum == d3_prod)
    formula.Add(box_sum == d4_prod)

    return formula

def bin_to_int(blist):
    result = 0
    for b in blist:
        result *= 2
        result += 1 if b else 0
    return result

def print_solution(sol):
    for letter in ['a','b','c','d','e','f']:
        for number in [1,2,3,4,5,6]:
            print(' {} '.format(bin_to_int([sol['v{}{}{}'.format(letter, number, i)] for i in range(3)])), end='')
        print('')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Determine if a number is prime by attempting to factor it")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode()
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, [bin_to_int])
