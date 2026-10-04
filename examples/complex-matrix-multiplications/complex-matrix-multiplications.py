from cnfc import *
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
    def assert_final_product(i, j, entries, component):
        expected_coefficients = {tuple(entry[1:]): entry[0] for entry in entries}
        for v1 in ('a','b'):
            for v2 in ('c','d'):
                for i1 in range(1,3):
                    for i2 in range(1,3):
                        for j1 in range(1,3):
                            for j2 in range(1,3):
                                coefficient = sum(
                                    (coefficient_product(component[(i,j,kk)], varz[(v1,i1,j1,kk)], varz[(v2,i2,j2,kk)]) for kk in range(m)),
                                    Integer(0),
                                )
                                expected = expected_coefficients.get((v1,i1,j1,v2,i2,j2), 0)
                                formula.Add(coefficient == expected)

    # C_11 = (a11*c11 + a12*c21 - b11*d11 - b12*d21) + (a11*d11 + a12*d21 + b11*c11 + b12*c21)*I
    c_11_reals = [(1,'a',1,1,'c',1,1), (1,'a',1,2,'c',2,1), (-1,'b',1,1,'d',1,1), (-1,'b',1,2,'d',2,1)]
    c_11_imags = [(1,'a',1,1,'d',1,1), (1,'a',1,2,'d',2,1),  (1,'b',1,1,'c',1,1),  (1,'b',1,2,'c',2,1)]
    assert_final_product(1, 1, c_11_reals, rcs)
    assert_final_product(1, 1, c_11_imags, ics)

    # C_12 = (a11*c12 + a12*c22 - b11*d12 - b12*d22) + (a11*d12 + a12*d22 + b11*c12 + b12*c22)*I
    c_12_reals = [(1,'a',1,1,'c',1,2), (1,'a',1,2,'c',2,2), (-1,'b',1,1,'d',1,2), (-1,'b',1,2,'d',2,2)]
    c_12_imags = [(1,'a',1,1,'d',1,2), (1,'a',1,2,'d',2,2),  (1,'b',1,1,'c',1,2),  (1,'b',1,2,'c',2,2)]
    assert_final_product(1, 2, c_12_reals, rcs)
    assert_final_product(1, 2, c_12_imags, ics)

    # C_21 = (a21*c11 + a22*c21 - b21*d11 - b22*d21) + (a21*d11 + a22*d21 + b21*c11 + b22*c21)*I
    c_21_reals = [(1,'a',2,1,'c',1,1), (1,'a',2,2,'c',2,1), (-1,'b',2,1,'d',1,1), (-1,'b',2,2,'d',2,1)]
    c_21_imags = [(1,'a',2,1,'d',1,1), (1,'a',2,2,'d',2,1),  (1,'b',2,1,'c',1,1),  (1,'b',2,2,'c',2,1)]
    assert_final_product(2, 1, c_21_reals, rcs)
    assert_final_product(2, 1, c_21_imags, ics)

    # C_22 = (a21*c12 + a22*c22 - b21*d12 - b22*d22) + (a21*d12 + a22*d22 + b21*c12 + b22*c22)*I
    c_22_reals = [(1,'a',2,1,'c',1,2), (1,'a',2,2,'c',2,2), (-1,'b',2,1,'d',1,2), (-1,'b',2,2,'d',2,2)]
    c_22_imags = [(1,'a',2,1,'d',1,2), (1,'a',2,2,'d',2,2),  (1,'b',2,1,'c',1,2),  (1,'b',2,2,'c',2,2)]
    assert_final_product(2, 2, c_22_reals, rcs)
    assert_final_product(2, 2, c_22_imags, ics)

    return formula

def print_solution(sol, *extra_args):
    m = extra_args[0]
    dims = range(1,3)

    for k in range(m):
        enabled = {'a': [], 'b': [], 'c': [], 'd': []}
        for i in dims:
            for j in dims:
                for x in ('a','b','c','d'):
                    coefficient = sol.integer(f'{x}:{i}:{j}:{k}')
                    if coefficient == 1:
                        enabled[x].append(f'{x}_{{{i},{j}}}')
                    if coefficient == -1:
                        enabled[x].append(f'-{x}_{{{i},{j}}}')
        ab_sum = ' + '.join(enabled['a'] + enabled['b'])
        cd_sum = ' + '.join(enabled['c'] + enabled['d'])
        print(f'm_{k} = ({ab_sum}) * ({cd_sum})')

    print('')

    for i in dims:
        for j in dims:
            reals, imags = [], []
            for k in range(m):
                real = sol.integer(f'CR:{i}:{j}:{k}')
                imag = sol.integer(f'CI:{i}:{j}:{k}')
                if real == 1: reals.append(f'm_{k}')
                if real == -1: reals.append(f'-m_{k}')
                if imag == 1: imags.append(f'm_{k}')
                if imag == -1: imags.append(f'-m_{k}')
            real_sum = ' + '.join(reals)
            imag_sum = ' + '.join(imags)
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
