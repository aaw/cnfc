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

def king_neighbors(r, c):
    return [(r+dr, c+dc) for dr in (-1,0,1) for dc in (-1,0,1)
            if (dr, dc) != (0, 0) and r+dr in COORDS and c+dc in COORDS]

# Encodes the Altered States puzzle into a Formula.
def encode(min_score):
    formula = Formula()

    # Variable varz[(r,c,v)] is true iff cell (r,c) has value v in VALS
    varz = {(r,c,v): formula.AddVar(f'v:{r}:{c}:{v}') for r in COORDS for c in COORDS for v in VALS}

    # Constraint: Each cell contains exactly one value.
    for r in COORDS:
        for c in COORDS:
            formula.Add(NumTrue(*(varz[(r,c,v)] for v in VALS)) == 1)

    # Variables that are true iff each state matches the grid.
    state_matches = []
    for state in STATES:
        # Convert the state name to a sequence of numbers.
        pattern = [ord(ch.upper()) - ord('A') for ch in state]

        # svarz[(r,c,i)] means (r,c) matches position i of this state
        svarz = {(r,c,i): formula.AddVar(f'{state}:{r}:{c}:{i}')
                 for r in COORDS for c in COORDS for i in range(len(pattern))}

        # Create a big conjunction that is true iff the current state has a
        # match on the grid.
        sconj = []

        # Constraint: For any position i in the state pattern, only one
        # svarz entry is set.
        for i in range(len(pattern)):
            sconj.append(NumTrue(*(svarz[(r,c,i)] for r in COORDS for c in COORDS)) == 1)

        # Constraint: All svarz are consistent with the varz.
        pos_matches = [And(*(If(svarz[(r,c,i)], varz[(r,c,letter)]) for r in COORDS for c in COORDS))
                       for i, letter in enumerate(pattern)]
        sconj.append(And(*pos_matches))

        # Constraint: Any consecutive i and i+1 in the svarz are connected by a
        # king's move.
        for i in range(1, len(pattern)):
            for r in COORDS:
                for c in COORDS:
                    sconj.append(If(svarz[(r,c,i)], Or(*(svarz[(rr,cc,i-1)] for rr, cc in king_neighbors(r,c)))))

        sconj.append(Or(*(svarz[(r,c,len(pattern)-1)] for r in COORDS for c in COORDS)))

        # Create a var named after each state that's true iff the state matches
        # the grid.
        v = formula.AddVar(state)
        formula.Add(v == And(*sconj))
        state_matches.append(v)

    # The total score achieved by the state configuration.
    total = sum(If(v, Integer(len(state)), Integer(0)) for v, state in zip(state_matches, STATES))
    formula.Add(total >= min_score)

    return formula

def print_solution(sol, *extra_args):
    coords, vals, states = extra_args
    for r in coords:
        print(''.join(f' {chr(v + ord("A"))} ' for c in coords for v in vals if sol[f'v:{r}:{c}:{v}']))
    matches = [state for state in states if sol[state]]
    score = sum(len(state) for state in matches)

    # Cells used to match a state, marking any cell whose letter doesn't match with a '*'.
    def path(state):
        p = []
        for i, letter in enumerate(state.upper()):
            r, c = next((r, c) for r in coords for c in coords if sol[f'{state}:{r}:{c}:{i}'])
            matched = sol[f'v:{r}:{c}:{ord(letter) - ord("A")}']
            p.append(f'({r},{c})' + ('' if matched else '*'))
        return ' '.join(p)

    print('Matches:')
    for match in matches:
        print(f'  {match} : {path(match)}')
    print(f'Score: {score}')

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
        formula.WriteExtractor(f, print_solution, extra_args=[COORDS, VALS, STATES])
