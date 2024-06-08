# Solves the Jane St. Altered States puzzle:
# https://www.janestreet.com/puzzles/altered-states-index/

from cnfc import *

import argparse

COORDS = [0,1,2,3,4]  # 5 x 5 grid.
VALS = list(range(26))  # A-Z, converted to 0-25
STATES = [
    'California', 'Texas', 'Florida', 'NewYork', 'Pennsylvania', 'Illinois',
    'Ohio', 'Georgia', 'NorthCarolina', 'Michigan', 'NewJersey', 'Virginia',
    'Washington', 'Arizona', 'Massachusetts', 'Tennessee', 'Indiana',
    'Maryland', 'Missouri', 'Wisconsin', 'Colorado', 'Minnesota',
    'SouthCarolina', 'Alabama', 'Louisiana', 'Kentucky', 'Oregon', 'Oklahoma',
    'Connecticut', 'Utah', 'Iowa', 'Nevada', 'Arkansas', 'Mississippi',
    'Kansas', 'NewMexico', 'Nebraska', 'Idaho', 'WestVirginia', 'Hawaii',
    'NewHampshire', 'Maine', 'RhodeIsland', 'Montana', 'Delaware',
    'SouthDakota', 'NorthDakota', 'Alaska', 'Vermont', 'Wyoming'
]

# Encodes the Altered States puzzle into a Formula.
def encode(min_score):
    formula = Formula()

    # Variable varz[(r,c,v)] is true iff cell (r,c) has value v in VALS
    varz = {}
    for r in COORDS:
        for c in COORDS:
            for v in VALS:
                varz[(r,c,v)] = formula.AddVar('v:{}:{}:{}'.format(r,c,v))

    # Constraint: Each cell contains exactly one value.
    for r in COORDS:
        for c in COORDS:
            cell_vars = (varz[(r,c,v)] for v in VALS)
            formula.Add(NumTrue(*cell_vars) == 1)

    # The total score achieved by the state configuration.
    total = Integer(0)
    for state in STATES:
        # Convert the state name to a sequence of numbers.
        pattern = [ord(ch.upper()) - ord('A') for ch in state]

        # svarz[(r,c,i)] means (r,c) matches position i of this state
        svarz = {}
        for r in COORDS:
            for c in COORDS:
                for i, _ in enumerate(pattern):
                    svarz[(r,c,i)] = formula.AddVar('{}:{}:{}:{}'.format(state,r,c,i))

        # Create a big conjunction that is true iff the current state has a
        # match on the grid.
        sconj = []

        # Constraint: For any position i in the state pattern, only one
        # svarz entry is set.
        for i, _ in enumerate(pattern):
            cell_vars = (svarz[(r,c,i)] for r in COORDS for c in COORDS)
            sconj.append(NumTrue(*cell_vars) == 1)

        # Constraint: All svarz are consistent with the varz.
        pos_matches = []
        for i, _ in enumerate(pattern):
            conj = []
            for r in COORDS:
                for c in COORDS:
                    conj.append(If(svarz[(r,c,i)], varz[r,c,pattern[i]]))
            pos_matches.append(And(*conj))
        sconj.append(And(*pos_matches))

        # Constraint: Any consecutive i and i+1 in the svarz are connected by a
        # king's move.
        def kings_moves(r,c):
            M = len(COORDS)-1
            if r > 0 and c > 0: yield (r-1,c-1)
            if r > 0: yield (r-1,c)
            if r > 0 and c < M: yield (r-1,c+1)
            if c > 0: yield (r,c-1)
            if c < M: yield (r,c+1)
            if r < M and c > 0: yield (r+1,c-1)
            if r < M: yield (r+1,c)
            if r < M and c < M: yield (r+1,c+1)

        for i, _ in enumerate(pattern):
            if i == 0: continue
            for r in COORDS:
                for c in COORDS:
                    sconj.append(If(svarz[(r,c,i)], Or(*(svarz[(rr,cc,i-1)] for (rr,cc) in kings_moves(r,c)))))

        sconj.append(Or(*(svarz[(r,c,len(pattern)-1)] for r in COORDS for c in COORDS)))

        # Create a var named after each state that's true iff the state matches
        # the grid. Use these to calculate a conditional total score.
        v = formula.AddVar(state)
        formula.Add(v == And(*sconj))

        total = total + If(v, Integer(len(state)), Integer(0))

    formula.Add(total >= Integer(min_score))

    return formula

def print_solution(sol, *extra_args):
    coords, vals, states = extra_args
    for r in coords:
        for c in coords:
            for v in vals:
                if sol['v:{}:{}:{}'.format(r,c,v)]:
                    print(' {} '.format(chr(v + ord('A'))), end='')
                    break
        print('')
    matches = [sname for sname in states if sol[sname]]
    score = sum(len(sname) for sname in matches)

    def path(state):
        pattern = [ord(ch.upper()) - ord('A') for ch in state]
        p = []
        for i, val in enumerate(pattern):
            for r in coords:
                for c in coords:
                    if sol['{}:{}:{}:{}'.format(state,r,c,i)]:
                        if sol['v:{}:{}:{}'.format(r,c,val)]:
                            p.append('({},{})'.format(r,c))
                        else:
                            p.append('({},{})*'.format(r,c))
                        break
        return ' '.join(p)

    print('Matches:')
    for match in matches:
        print('  {} : {}'.format(match, path(match)))
    print('Score: {}'.format(score))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve Jane Street's Altered States puzzle")
    parser.add_argument('min_score', type=int, help='Minimum score.')
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode(args.min_score)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, [], extra_args=[COORDS, VALS, STATES])
