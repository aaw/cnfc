from collections import defaultdict
from cnfc import *
from itertools import product, zip_longest

import argparse

def encode(n, m, max_additions_per_term, max_total_additions):
    dims = range(1, n+1)
    formula = Formula()

    avarz, bvarz = {}, {}
    # There are m products that each look like:
    #
    # (a_{1,1} + a_{2,3} - a_{3,3}) * (-b_{1,1} - b_{2,2} + b_{2,3})
    #
    # The variables below capture the a's and b's in each of these m products
    total_additions = []
    for k in range(m):
        all_a_in_term, all_b_in_term = [], []
        for i in dims:
            for j in dims:
                # a:i:j:k is true iff a_{i,j} is part of product k
                pos_a = formula.AddVar(f'a:{i}:{j}:{k}')
                # -a:i:j:k is true iff -a_{i,j} is part of product k
                neg_a = formula.AddVar(f'-a:{i}:{j}:{k}')
                formula.Add(~pos_a | ~neg_a)  # Can only use one of a_{i,j} and -a_{i,j}
                avarz[(1,i,j,k)] = pos_a
                avarz[(-1,i,j,k)] = neg_a
                all_a_in_term.append(pos_a)
                all_a_in_term.append(neg_a)

                # b:i:j:k is true iff b_{i,j} is part of product k
                pos_b = formula.AddVar(f'b:{i}:{j}:{k}')
                # -b:i:j:k is true iff -b_{i,j} is part of product k
                neg_b = formula.AddVar(f'-b:{i}:{j}:{k}')
                formula.Add(~pos_b | ~neg_b)   # Can only use one of a_{i,j} and -a_{i,j}
                bvarz[(1,i,j,k)] = pos_b
                bvarz[(-1,i,j,k)] = neg_b
                all_b_in_term.append(pos_b)
                all_b_in_term.append(neg_b)

        if max_additions_per_term != -1:
            formula.Add(NumTrue(*all_a_in_term) <= max_additions_per_term + 1)
            formula.Add(NumTrue(*all_b_in_term) <= max_additions_per_term + 1)

        # NumTrue(*all_a_in_term) > 0 and NumTrue(*all_b_in_term) > 0 so both
        # terms below should be non-negative.
        total_additions.append(NumTrue(*all_a_in_term) - 1)
        total_additions.append(NumTrue(*all_b_in_term) - 1)

    # Generate constraints that specify which of the m_k's are used by which of the
    # sums that define the final matrix product elements.
    cs = {}
    for i in dims:
        for j in dims:
            mks = []
            for k in range(m):
                # C:i:j:k is true iff entry i,j of the final matrix uses subproduct m_k
                uses_mk = formula.AddVar(f'C:{i}:{j}:{k}')
                cs[(i,j,k)] = uses_mk
                mks.append(uses_mk)
            # NumTrue(mks) > 0 so this term is non-negative.
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
                            pos_abs = [cs[(i,j,kk)] & ((avarz[(1,i_prime,k,kk)] & bvarz[(1,l,j_prime,kk)]) | (avarz[(-1,i_prime,k,kk)] & bvarz[(-1,l,j_prime,kk)])) for kk in range(m)]
                            neg_abs = [cs[(i,j,kk)] & ((avarz[(-1,i_prime,k,kk)] & bvarz[(1,l,j_prime,kk)]) | (avarz[(1,i_prime,k,kk)] & bvarz[(-1,l,j_prime,kk)])) for kk in range(m)]
                            if k == l and i == i_prime and j == j_prime:
                                formula.Add(NumTrue(*pos_abs) == NumTrue(*neg_abs) + 1)
                            else:
                                formula.Add(NumTrue(*pos_abs) == NumTrue(*neg_abs))

    return formula

def print_solution(sol, *extra_args):
    n, m = extra_args
    dims = range(1,n+1)
    # a:i:j:k is true iff a_{i,j} is part of product k
    for k in range(m):
        a, b = [], []
        for i in dims:
            for j in dims:
                if sol[f'a:{i}:{j}:{k}']:
                    a.append(f'a_{{{i},{j}}}')
                if sol[f'-a:{i}:{j}:{k}']:
                    a.append(f'-a_{{{i},{j}}}')
                if sol[f'b:{i}:{j}:{k}']:
                    b.append(f'b_{{{i},{j}}}')
                if sol[f'-b:{i}:{j}:{k}']:
                    b.append(f'-b_{{{i},{j}}}')
        a_sum = ' + '.join(a)
        b_sum = ' + '.join(b)
        print(f'm_{k} = ({a_sum}) * ({b_sum})')

    print('')

    for i in dims:
        for j in dims:
            ms = []
            for k in range(m):
                if sol[f'C:{i}:{j}:{k}']:
                    ms.append(f'm_{k}')
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
