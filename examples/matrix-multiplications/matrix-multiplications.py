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

def encode(n, m, max_additions_per_term, max_total_additions):
    dims = range(1, n+1)
    formula = Formula()

    avarz, bvarz = {}, {}
    # There are m products that each look like:
    #
    # (a_{1,1} + a_{2,3} - a_{3,3}) * (-b_{1,1} - b_{2,2} + b_{2,3})
    #
    # Each coefficient is -1, 0, or 1: subtract, omit, or add the matrix element.
    total_additions = []
    for k in range(m):
        all_a_in_term, all_b_in_term = [], []
        for i in dims:
            for j in dims:
                a = Integer(formula.AddVars(f'a:{i}:{j}:{k}', COEFFICIENT_BITS))
                b = Integer(formula.AddVars(f'b:{i}:{j}:{k}', COEFFICIENT_BITS))
                formula.Add(-1 <= a <= 1)
                formula.Add(-1 <= b <= 1)
                avarz[(i,j,k)] = a
                bvarz[(i,j,k)] = b
                all_a_in_term.append(a != 0)
                all_b_in_term.append(b != 0)

        if max_additions_per_term != -1:
            formula.Add(NumTrue(*all_a_in_term) <= max_additions_per_term + 1)
            formula.Add(NumTrue(*all_b_in_term) <= max_additions_per_term + 1)

        # A sum of t matrix elements uses t - 1 additions.
        total_additions.append(NumTrue(*all_a_in_term) - 1)
        total_additions.append(NumTrue(*all_b_in_term) - 1)

    # Signed coefficients specify how each subproduct contributes to C_{i,j}.
    cs = {}
    for i in dims:
        for j in dims:
            mks = []
            for k in range(m):
                c = Integer(formula.AddVars(f'C:{i}:{j}:{k}', COEFFICIENT_BITS))
                formula.Add(-1 <= c <= 1)
                cs[(i,j,k)] = c
                mks.append(c != 0)
            total_additions.append(NumTrue(*mks) - 1)

    if max_total_additions != -1:
        formula.Add(sum(total_additions) <= max_total_additions)

    # Finally, we know what each element of the matrix product should be in
    # terms of a_{i,k}s and b_{k,j}s, so we add constraints that ensure that
    # these are what we expect.
    for i in dims:
        for j in dims:
            for i_prime in dims:
                for j_prime in dims:
                    for k in dims:
                        for l in dims:
                            # C_{i,j} = sum(a_{i,k} * b_{k,j} for k in dims)
                            # So we only want a contribution of a_{i_prime,k} * b_{l,j_prime} when k == l, i == i_prime, j == j_prime
                            coefficient = sum(
                                (coefficient_product(cs[(i,j,kk)], avarz[(i_prime,k,kk)], bvarz[(l,j_prime,kk)]) for kk in range(m)),
                                Integer(0),
                            )
                            expected = 1 if k == l and i == i_prime and j == j_prime else 0
                            formula.Add(coefficient == expected)

    return formula

def print_solution(sol, *extra_args):
    n, m = extra_args
    dims = range(1,n+1)
    for k in range(m):
        a, b = [], []
        for i in dims:
            for j in dims:
                a_coefficient = sol.integer(f'a:{i}:{j}:{k}')
                b_coefficient = sol.integer(f'b:{i}:{j}:{k}')
                if a_coefficient == 1:
                    a.append(f'a_{{{i},{j}}}')
                if a_coefficient == -1:
                    a.append(f'-a_{{{i},{j}}}')
                if b_coefficient == 1:
                    b.append(f'b_{{{i},{j}}}')
                if b_coefficient == -1:
                    b.append(f'-b_{{{i},{j}}}')
        a_sum = ' + '.join(a)
        b_sum = ' + '.join(b)
        print(f'm_{k} = ({a_sum}) * ({b_sum})')

    print('')

    for i in dims:
        for j in dims:
            ms = []
            for k in range(m):
                coefficient = sol.integer(f'C:{i}:{j}:{k}')
                if coefficient == 1: ms.append(f'm_{k}')
                if coefficient == -1: ms.append(f'-m_{k}')
            m_sum = ' + '.join(ms)
            print(f'C_{{{i},{j}}} = {m_sum}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a scheme to matrix multiplication with limited element multiplications")
    parser.add_argument('n', type=int, help='Dimension of the square matrices.')
    parser.add_argument('m', type=int, help='Max element multiplications allowed.')
    parser.add_argument('--max_additions_per_term', type=int, help="Max additions (of a's or b's) per m term (default is -1, which is unconstrained).", default=-1)
    parser.add_argument('--max_total_additions', type=int, help='Max additions in entire formula (default is -1, which is unconstrained).', default=-1)
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode(args.n, args.m, args.max_additions_per_term, args.max_total_additions)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_args=[args.n, args.m])
