from cnfc import *
from itertools import product

import argparse

COEFFICIENT_BITS = Integer.bits_needed_for_range(-1, 1)

def coefficient_product(a, b, c):
    # For coefficients in {-1, 0, 1}, a product is nonzero iff all factors
    # are nonzero, and negative iff an odd number of factors are negative.
    nonzero = And(a != 0, b != 0, c != 0)
    negative = ((a < 0) != (b < 0)) != (c < 0)
    # Two's-complement bits: 00 = 0, 01 = 1, 11 = -1. This avoids the
    # larger circuit needed to multiply arbitrary signed integers.
    return Integer(And(nonzero, negative), nonzero)

def encode(m):
    dims = range(1, 3)
    formula = Formula()

    # There are m products that each look like:
    #
    # (a_{1,1} - a_{2,1} + b_{1,1}) * (c_{1,1} - d_{1,2} + d{2,2})
    #
    # In other words, sum of some a's and b's, possibly negated, multiplied by the
    # sum of some c's and d's, possibly negated.
    #
    # Each coefficient is -1, 0, or 1: subtract, omit, or add the matrix element.
    varz = {}
    mk_vars = [[] for i in range(m)]
    for k in range(m):
        for i in dims:
            for j in dims:
                for x in ('a','b','c','d'):
                    coefficient = Integer(formula.AddVars(f'{x}:{i}:{j}:{k}', COEFFICIENT_BITS))
                    formula.Add(-1 <= coefficient <= 1)
                    varz[(x,i,j,k)] = coefficient
                    mk_vars[k].extend(coefficient.as_tuple())

    # Symmetry-breaking: order the bit patterns of the subproduct coefficients.
    for i in range(m-1):
        formula.Add(Tuple(*mk_vars[i]) < Tuple(*mk_vars[i+1]))

    # Signed coefficients specify how each subproduct contributes to the real
    # and imaginary components of C_{i,j}.
    rcs, ics = {}, {}
    for i in dims:
        for j in dims:
            for k in range(m):
                real = Integer(formula.AddVars(f'CR:{i}:{j}:{k}', COEFFICIENT_BITS))
                imag = Integer(formula.AddVars(f'CI:{i}:{j}:{k}', COEFFICIENT_BITS))
                formula.Add(-1 <= real <= 1)
                formula.Add(-1 <= imag <= 1)
                rcs[(i,j,k)] = real
                ics[(i,j,k)] = imag

    # Finally, we know what each element of the matrix product should be in
    # terms of a_{i,k}s and b_{k,j}s, so we add constraints that ensure that
    # these are what we expect.

    # Match every monomial's signed coefficient to the expected matrix product.
    # expected maps monomials like ('a',1,2,'c',2,1), meaning a_{1,2}*c_{2,1}, to their coefficients.
    def assert_final_product(i, j, expected, component):
        for v1, v2, i1, i2, j1, j2 in product(('a','b'), ('c','d'), dims, dims, dims, dims):
            coefficient = sum(coefficient_product(component[(i,j,kk)], varz[(v1,i1,j1,kk)], varz[(v2,i2,j2,kk)]) for kk in range(m))
            formula.Add(coefficient == expected.get((v1,i1,j1,v2,i2,j2), 0))

    # (A + Bi)(C + Di) = (AC - BD) + (AD + BC)i, so each entry C_{i,j} of the product is:
    #
    #   C_{i,j} = sum(a_{i,l}*c_{l,j} - b_{i,l}*d_{l,j} for l in dims) + sum(a_{i,l}*d_{l,j} + b_{i,l}*c_{l,j} for l in dims)*I
    for i, j in product(dims, repeat=2):
        reals, imags = {}, {}
        for l in dims:
            reals[('a',i,l,'c',l,j)] = 1
            reals[('b',i,l,'d',l,j)] = -1
            imags[('a',i,l,'d',l,j)] = 1
            imags[('b',i,l,'c',l,j)] = 1
        assert_final_product(i, j, reals, rcs)
        assert_final_product(i, j, imags, ics)

    return formula

def print_solution(sol, *extra_args):
    m = extra_args[0]
    dims = range(1,3)

    # Formats a sum of terms with coefficients in {-1, 0, 1}, given (coefficient, term) pairs.
    def signed_sum(terms):
        return ' + '.join(('-' if coefficient < 0 else '') + term for coefficient, term in terms if coefficient != 0)

    for k in range(m):
        ab_sum = signed_sum((sol.integer(f'{x}:{i}:{j}:{k}'), f'{x}_{{{i},{j}}}') for x in 'ab' for i in dims for j in dims)
        cd_sum = signed_sum((sol.integer(f'{x}:{i}:{j}:{k}'), f'{x}_{{{i},{j}}}') for x in 'cd' for i in dims for j in dims)
        print(f'm_{k} = ({ab_sum}) * ({cd_sum})')

    print('')

    for i in dims:
        for j in dims:
            real_sum = signed_sum((sol.integer(f'CR:{i}:{j}:{k}'), f'm_{k}') for k in range(m))
            imag_sum = signed_sum((sol.integer(f'CI:{i}:{j}:{k}'), f'm_{k}') for k in range(m))
            print(f'C_{{{i},{j}}} = {real_sum} + ({imag_sum})*I')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a scheme to matrix multiplication with limited element multiplications")
    parser.add_argument('m', type=int, help='Max element multiplications allowed.')
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode(args.m)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_args=[args.m])
