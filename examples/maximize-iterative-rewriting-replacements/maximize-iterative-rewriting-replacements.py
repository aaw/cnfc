from collections import defaultdict
from cnfc import *
from itertools import product

import argparse

F = {'000', '001', '010', '011', '100', '101', '110', '111', '112', '121', '122', '211', '212', '221', '222', '333'}

# DOMAIN is F x {0,1,2}
DOMAIN = sorted(list(product(F, range(3))))

# RANGE is all strings of length 3 over {0,1,2,3} that don't end in 0
RANGE = sorted(list(''.join(str(x) for x in xs) for xs in product(range(4), range(4), range(1,4))))

assert len(DOMAIN) == len(RANGE)  # Sanity check.

def leftmost_forbidden_block(word):
    if word[0:3] in F: return 0
    if word[1:4] in F: return 1
    if word[2:] in F: return 2
    return None

WORDS = [word for word in list(''.join(str(ch) for ch in word) for word in product(range(4),range(4),range(4),range(4),range(4))) if leftmost_forbidden_block(word) is not None]

def encode(n):
    formula = Formula()

    # Variable phi:d:r is true iff phi maps (x,y) to r.
    phi = {}
    for d in DOMAIN:
        for r in RANGE:
            phi[(d,r)] = formula.AddVar(f'phi:{d}:{r}')

    # Constraint: phi is a bijection.
    for r in RANGE:
        domain_values_mapping_to_r = [phi[(d,r)] for d in DOMAIN]
        formula.Add(NumTrue(*domain_values_mapping_to_r) == 1)

    for d in DOMAIN:
        range_values_mapped_from_d = [phi[(d,r)] for r in RANGE]
        formula.Add(NumTrue(*range_values_mapped_from_d) == 1)

    # Variable trace:i:x is true iff the ith element of the trace is x.
    trace = {}
    for i in range(n):
        for w in WORDS:
            trace[(i,w)] = formula.AddVar(f'trace:{i}:{w}')

    # Constraint: element i of the trace is associated with exactly one word.
    for i in range(n):
        trace_assignments = [trace[(i,w)] for w in WORDS]
        formula.Add(NumTrue(*trace_assignments) == 1)

    # Constraint: first element of the trace ends with 0.
    for w in WORDS:
        if not w.endswith('0'):
            formula.Add(~trace[(0,w)])

    # Constraint: Each application of phi agrees with consecutive trace entries.
    for i in range(n-1):
        disjunction = []
        for w1 in WORDS:
            idx = leftmost_forbidden_block(w1)
            forbidden = w1[idx:idx+3]
            for w2 in WORDS:
                # First two characters of w2 should be w1 with the forbidden string removed.
                if w2[:2] != w1[:idx] + w1[idx+3:]:
                    continue
                # Last three characters of w2 should be the image of the forbidden string under phi.
                forbidden_image = w2[2:]
                if forbidden_image not in RANGE:
                    continue
                disjunction.append(And(trace[(i,w1)], trace[(i+1,w2)], phi[((forbidden, idx), forbidden_image)]))
        # We've enumerated all the legal w1 -> w2 trace transitions above; one of them must
        # be used in the resulting formula.
        formula.Add(Or(*disjunction))

    return formula

def print_solution(sol, *extra_args):
    n, domain, range_, words = extra_args

    print('Definition of phi:')
    for d in domain:
        for r in range_:
            if sol[f'phi:{d}:{r}']:
                print(f'{d} -> {r}')

    print('')
    print('Trace:')
    for i in range(n):
        for w in words:
            if sol[f'trace:{i}:{w}']:
                print(w)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Determine if a sequence of rewriting rules of length n exists.")
    parser.add_argument('n', type=int, help="Length of the rewriting rule sequence")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode(args.n)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_args=[args.n, DOMAIN, RANGE, WORDS])
