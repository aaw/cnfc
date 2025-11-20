from cnfc import *
import argparse

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
    # The variables below capture the a's, b's, c's and d's in each of these m products.
    varz = {}
    mk_vars = [[] for i in range(m)]
    for k in range(m):
        for i in dims:
            for j in dims:
                for x in ('a','b','c','d'):
                    # {x}:i:j:k is true iff x_{i,j} is part of product k
                    pos = formula.AddVar(f'{x}:{i}:{j}:{k}')
                    # -{x}:i:j:k is true iff -x_{i,j} is part of product k
                    neg = formula.AddVar(f'-{x}:{i}:{j}:{k}')
                    formula.Add(~pos | ~neg)  # Can only use one of x_{i,j} and -x_{i,j}
                    varz[(1,x,i,j,k)] = pos
                    varz[(-1,x,i,j,k)] = neg
                    mk_vars[k].append(pos)
                    mk_vars[k].append(neg)

    # Symmetry-breaking
    for i in range(m-1):
        formula.Add(Tuple(*mk_vars[i]) < Tuple(*mk_vars[i+1]))

    # Generate constraints that specify which of the m_k's are used by which of the
    # sums that define the final matrix product elements. m_k's can be positive or
    # negative, but it doesn't make sense to use both in the real or imaginary component
    # of a matrix element.
    rcs, nrcs = {}, {}
    ics, nics = {}, {}
    for i in dims:
        for j in dims:
            for k in range(m):
                # CR:i:j:k is true iff the real part of entry i,j of the final matrix uses subproduct m_k
                pos_real_uses_mk = formula.AddVar(f'CR:{i}:{j}:{k}')
                rcs[(i,j,k)] = pos_real_uses_mk
                # -CR:i:j:k is true iff the real part of entry i,j of the final matrix uses subproduct -m_k
                neg_real_uses_mk = formula.AddVar(f'-CR:{i}:{j}:{k}')
                nrcs[(i,j,k)] = neg_real_uses_mk
                formula.Add(Or(~pos_real_uses_mk,~neg_real_uses_mk))  # Pos and neg will just cancel each other, so disallow.

                # CI:i:j:k is true iff the imaginary part of entry i,j of the final matrix uses subproduct m_k
                pos_imag_uses_mk = formula.AddVar(f'CI:{i}:{j}:{k}')
                ics[(i,j,k)] = pos_imag_uses_mk
                # -CI:i:j:k is true iff the imaginary part of entry i,j of the final matrix uses subproduct -m_k
                neg_imag_uses_mk = formula.AddVar(f'-CI:{i}:{j}:{k}')
                nics[(i,j,k)] = neg_imag_uses_mk
                formula.Add(Or(~pos_imag_uses_mk,~neg_imag_uses_mk))  # Pos and neg will just cancel each other, so disallow.

    # Finally, we know what each element of the matrix product should be in
    # terms of a_{i,k}s and b_{k,j}s, so we add constraints that ensure that
    # these are what we expect.

    # Assert that C_{i,j}'s component, when simplified, has only <entries> set,
    # based on pos[(i,j,k)] and neg[(i,j,k)].
    # varz[(sign, v, i, j, k)] is true iff sign*x_{i,j} is part of subproduct m_k
    # pos[(i, j, k)] is true iff the (real, imaginary) component of C_{i,j} uses subproduct m_k
    def assert_final_product(i, j, entries, pos, neg):
        for v1 in ('a','b'):
            for v2 in ('c','d'):
                for i1 in range(1,3):
                    for i2 in range(1,3):
                        for j1 in range(1,3):
                            for j2 in range(1,3):
                                pos_uses = [pos[(i,j,kk)] & ((varz[(1,v1,i1,j1,kk)] & varz[(1,v2,i2,j2,kk)]) | varz[(-1,v1,i1,j1,kk)] & varz[(-1,v2,i2,j2,kk)]) for kk in range(m)] + \
                                           [neg[(i,j,kk)] & ((varz[(-1,v1,i1,j1,kk)] & varz[(1,v2,i2,j2,kk)]) | varz[(1,v1,i1,j1,kk)] & varz[(-1,v2,i2,j2,kk)]) for kk in range(m)]
                                neg_uses = [pos[(i,j,kk)] & ((varz[(1,v1,i1,j1,kk)] & varz[(-1,v2,i2,j2,kk)]) | varz[(-1,v1,i1,j1,kk)] & varz[(1,v2,i2,j2,kk)]) for kk in range(m)] + \
                                           [neg[(i,j,kk)] & ((varz[(1,v1,i1,j1,kk)] & varz[(1,v2,i2,j2,kk)]) | varz[(-1,v1,i1,j1,kk)] & varz[(-1,v2,i2,j2,kk)]) for kk in range(m)]
                                if (1,v1,i1,j1,v2,i2,j2) in entries:
                                    formula.Add(NumTrue(*pos_uses) == NumTrue(*neg_uses) + 1)
                                elif (-1,v1,i1,j1,v2,i2,j2) in entries:
                                    formula.Add(NumTrue(*pos_uses) + 1 == NumTrue(*neg_uses))
                                else:
                                    formula.Add(NumTrue(*pos_uses) == NumTrue(*neg_uses))

    # C_11 = (a11*c11 + a12*c21 - b11*d11 - b12*d21) + (a11*d11 + a12*d21 + b11*c11 + b12*c21)*I
    c_11_reals = [(1,'a',1,1,'c',1,1), (1,'a',1,2,'c',2,1), (-1,'b',1,1,'d',1,1), (-1,'b',1,2,'d',2,1)]
    c_11_imags = [(1,'a',1,1,'d',1,1), (1,'a',1,2,'d',2,1),  (1,'b',1,1,'c',1,1),  (1,'b',1,2,'c',2,1)]
    assert_final_product(1, 1, c_11_reals, rcs, nrcs)
    assert_final_product(1, 1, c_11_imags, ics, nics)

    # C_12 = (a11*c12 + a12*c22 - b11*d12 - b12*d22) + (a11*d12 + a12*d22 + b11*c12 + b12*c22)*I
    c_12_reals = [(1,'a',1,1,'c',1,2), (1,'a',1,2,'c',2,2), (-1,'b',1,1,'d',1,2), (-1,'b',1,2,'d',2,2)]
    c_12_imags = [(1,'a',1,1,'d',1,2), (1,'a',1,2,'d',2,2),  (1,'b',1,1,'c',1,2),  (1,'b',1,2,'c',2,2)]
    assert_final_product(1, 2, c_12_reals, rcs, nrcs)
    assert_final_product(1, 2, c_12_imags, ics, nics)

    # C_21 = (a21*c11 + a22*c21 - b21*d11 - b22*d21) + (a21*d11 + a22*d21 + b21*c11 + b22*c21)*I
    c_21_reals = [(1,'a',2,1,'c',1,1), (1,'a',2,2,'c',2,1), (-1,'b',2,1,'d',1,1), (-1,'b',2,2,'d',2,1)]
    c_21_imags = [(1,'a',2,1,'d',1,1), (1,'a',2,2,'d',2,1),  (1,'b',2,1,'c',1,1),  (1,'b',2,2,'c',2,1)]
    assert_final_product(2, 1, c_21_reals, rcs, nrcs)
    assert_final_product(2, 1, c_21_imags, ics, nics)

    # C_22 = (a21*c12 + a22*c22 - b21*d12 - b22*d22) + (a21*d12 + a22*d22 + b21*c12 + b22*c22)*I
    c_22_reals = [(1,'a',2,1,'c',1,2), (1,'a',2,2,'c',2,2), (-1,'b',2,1,'d',1,2), (-1,'b',2,2,'d',2,2)]
    c_22_imags = [(1,'a',2,1,'d',1,2), (1,'a',2,2,'d',2,2),  (1,'b',2,1,'c',1,2),  (1,'b',2,2,'c',2,2)]
    assert_final_product(2, 2, c_22_reals, rcs, nrcs)
    assert_final_product(2, 2, c_22_imags, ics, nics)

    return formula

def print_solution(sol, *extra_args):
    m = extra_args[0]
    dims = range(1,3)

    # {x}:i:j:k is true iff x_{i,j} is part of product k
    # -{x}:i:j:k is true iff -x_{i,j} is part of product k
    for k in range(m):
        enabled = {'a': [], 'b': [], 'c': [], 'd': []}
        for i in dims:
            for j in dims:
                for x in ('a','b','c','d'):
                    if sol[f'{x}:{i}:{j}:{k}']:
                        enabled[x].append(f'{x}_{{{i},{j}}}')
                    if sol[f'-{x}:{i}:{j}:{k}']:
                        enabled[x].append(f'-{x}_{{{i},{j}}}')
        ab_sum = ' + '.join(enabled['a'] + enabled['b'])
        cd_sum = ' + '.join(enabled['c'] + enabled['d'])
        print(f'm_{k} = ({ab_sum}) * ({cd_sum})')

    print('')

    for i in dims:
        for j in dims:
            reals, imags = [], []
            for k in range(m):
                if sol[f'CR:{i}:{j}:{k}']: reals.append(f'm_{k}')
                if sol[f'-CR:{i}:{j}:{k}']: reals.append(f'-m_{k}')
                if sol[f'CI:{i}:{j}:{k}']: imags.append(f'm_{k}')
                if sol[f'-CI:{i}:{j}:{k}']: imags.append(f'-m_{k}')
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
