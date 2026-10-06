# Solves the Jane St. Altered States 2 puzzle:
# https://www.janestreet.com/puzzles/altered-states-2-index/

from cnfc import *
import argparse

COORDS = [0,1,2,3,4]  # 5 x 5 grid.
VALS = list(range(26))  # Cell contents, numbers from 0-25.
# A map of each state to its 2020 Census population count.
STATES = {
    'California': 39538223,
    'Texas': 29145505,
    'Florida': 21538187,
    'NewYork': 20201249,
    'Pennsylvania': 13002700,
    'Illinois': 12812508,
    'Ohio': 11799448,
    'Georgia': 10711908,
    'NorthCarolina': 10439388,
    'Michigan': 10077331,
    'NewJersey': 9288994,
    'Virginia': 8631393,
    'Washington': 7705281,
    'Arizona': 7151502,
    'Massachusetts': 7029917,
    'Tennessee': 6910840,
    'Indiana': 6785528,
    'Maryland': 6177224,
    'Missouri': 6154913,
    'Wisconsin': 5893718,
    'Colorado': 5773714,
    'Minnesota': 5706494,
    'SouthCarolina': 5118425,
    'Alabama': 5024279,
    'Louisiana': 4657757,
    'Kentucky': 4505836,
    'Oregon': 4237256,
    'Oklahoma': 3959353,
    'Connecticut': 3605944,
    'Utah': 3271616,
    'Iowa': 3190369,
    'Nevada': 3104614,
    'Arkansas': 3011524,
    'Mississippi': 2961279,
    'Kansas': 2937880,
    'NewMexico': 2117522,
    'Nebraska': 1961504,
    'Idaho': 1839106,
    'WestVirginia': 1793716,
    'Hawaii': 1455271,
    'NewHampshire': 1377529,
    'Maine': 1362359,
    'RhodeIsland': 1097379,
    'Montana': 1084225,
    'Delaware': 989948,
    'SouthDakota': 886667,
    'NorthDakota': 779094,
    'Alaska': 733391,
    'Vermont': 643077,
    'Wyoming': 576851,
}

# State-to-state adjacencies. Note that the "Four Corners" states are not
# considered adjacent when they touch diagonally.
NEIGHBORS = {
    'California': ['Oregon', 'Nevada', 'Arizona'],
    'Texas': ['NewMexico', 'Oklahoma', 'Arkansas', 'Louisiana'],
    'Florida': ['Alabama', 'Georgia'],
    'NewYork': ['Pennsylvania', 'NewJersey', 'Connecticut', 'Massachusetts', 'Vermont'],
    'Pennsylvania': ['NewYork', 'NewJersey', 'Delaware', 'Maryland', 'WestVirginia', 'Ohio'],
    'Illinois': ['Indiana', 'Kentucky', 'Missouri', 'Iowa', 'Wisconsin'],
    'Ohio': ['Pennsylvania', 'WestVirginia', 'Kentucky', 'Indiana', 'Michigan'],
    'Georgia': ['Florida', 'Alabama', 'Tennessee', 'NorthCarolina', 'SouthCarolina'],
    'NorthCarolina': ['SouthCarolina', 'Virginia', 'Tennessee', 'Georgia'],
    'Michigan': ['Wisconsin', 'Indiana', 'Ohio'],
    'NewJersey': ['Delaware', 'Pennsylvania', 'NewYork'],
    'Virginia': ['NorthCarolina', 'Tennessee', 'Kentucky', 'WestVirginia', 'Maryland'],
    'Washington': ['Idaho', 'Oregon'],
    'Arizona': ['California', 'Nevada', 'Utah', 'NewMexico'],
    'Massachusetts': ['RhodeIsland', 'Connecticut', 'NewYork', 'NewHampshire', 'Vermont'],
    'Tennessee': ['Kentucky', 'Virginia', 'NorthCarolina', 'Georgia', 'Alabama', 'Mississippi', 'Arkansas', 'Missouri'],
    'Indiana': ['Michigan', 'Ohio', 'Kentucky', 'Illinois'],
    'Maryland': ['Virginia', 'WestVirginia', 'Pennsylvania', 'Delaware'],
    'Missouri': ['Iowa', 'Illinois', 'Kentucky', 'Tennessee', 'Arkansas', 'Oklahoma', 'Kansas', 'Nebraska'],
    'Wisconsin': ['Michigan', 'Minnesota', 'Iowa', 'Illinois'],
    'Colorado': ['Wyoming', 'Nebraska', 'Kansas', 'Oklahoma', 'NewMexico', 'Utah'],
    'Minnesota': ['NorthDakota', 'SouthDakota', 'Iowa', 'Wisconsin'],
    'SouthCarolina': ['Georgia', 'NorthCarolina'],
    'Alabama': ['Mississippi', 'Tennessee', 'Georgia', 'Florida'],
    'Louisiana': ['Texas', 'Arkansas', 'Mississippi'],
    'Kentucky': ['Indiana', 'Ohio', 'WestVirginia', 'Virginia', 'Tennessee', 'Missouri', 'Illinois'],
    'Oregon': ['Washington', 'Idaho', 'Nevada', 'California'],
    'Oklahoma': ['NewMexico', 'Colorado', 'Kansas', 'Missouri', 'Arkansas', 'Texas'],
    'Connecticut': ['NewYork', 'Massachusetts', 'RhodeIsland'],
    'Utah': ['Nevada', 'Idaho', 'Wyoming', 'Colorado', 'Arizona'],
    'Iowa': ['Minnesota', 'Wisconsin', 'Illinois', 'Missouri', 'Nebraska', 'SouthDakota'],
    'Nevada': ['California', 'Oregon', 'Idaho', 'Utah', 'Arizona'],
    'Arkansas': ['Missouri', 'Tennessee', 'Mississippi', 'Louisiana', 'Texas', 'Oklahoma'],
    'Mississippi': ['Louisiana', 'Arkansas', 'Tennessee', 'Alabama'],
    'Kansas': ['Nebraska', 'Missouri', 'Oklahoma', 'Colorado'],
    'NewMexico': ['Arizona', 'Colorado', 'Oklahoma', 'Texas'],
    'Nebraska': ['Wyoming', 'SouthDakota', 'Iowa', 'Missouri', 'Kansas', 'Colorado'],
    'Idaho': ['Washington', 'Montana', 'Wyoming', 'Utah', 'Nevada', 'Oregon'],
    'WestVirginia': ['Ohio', 'Pennsylvania', 'Maryland', 'Virginia', 'Kentucky'],
    'Hawaii': [],
    'NewHampshire': ['Vermont', 'Maine', 'Massachusetts'],
    'Maine': ['NewHampshire'],
    'RhodeIsland': ['Connecticut', 'Massachusetts'],
    'Montana': ['NorthDakota', 'SouthDakota', 'Wyoming', 'Idaho'],
    'Delaware': ['Maryland', 'Pennsylvania', 'NewJersey'],
    'SouthDakota': ['NorthDakota', 'Minnesota', 'Iowa', 'Nebraska', 'Wyoming', 'Montana'],
    'NorthDakota': ['Minnesota', 'SouthDakota', 'Montana'],
    'Alaska': [],
    'Vermont': ['NewYork', 'NewHampshire', 'Massachusetts'],
    'Wyoming': ['Idaho', 'Montana', 'SouthDakota', 'Nebraska', 'Colorado', 'Utah'],
}
EAST_COAST = [
    'Maine', 'NewHampshire', 'Massachusetts', 'RhodeIsland', 'Connecticut',
    'NewYork', 'NewJersey', 'Delaware', 'Maryland', 'Virginia', 'NorthCarolina',
    'SouthCarolina', 'Georgia', 'Florida'
]
WEST_COAST = ['California', 'Oregon', 'Washington']
# A max path of length 16 from the east coast to the west coast seems reasonable.
MAX_PATH = 16

def king_neighbors(r, c):
    return [(r+dr, c+dc) for dr in (-1,0,1) for dc in (-1,0,1)
            if (dr, dc) != (0, 0) and r+dr in COORDS and c+dc in COORDS]

# Encodes the Altered States 2 puzzle into a Formula.
def encode(min_score, extras, min_extras, num_states=None):
    formula = Formula()

    # varz[(r,c,v)] is true iff cell (r,c) has value v in VALS
    varz = {(r,c,v): formula.AddVar(f'v:{r}:{c}:{v}') for r in COORDS for c in COORDS for v in VALS}

    # Constraint: Each cell contains exactly one value.
    for r in COORDS:
        for c in COORDS:
            formula.Add(NumTrue(*(varz[(r,c,v)] for v in VALS)) == 1)

    # Maps state names to a variable that's true iff that state is matched.
    state_vars = {}
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

        # Constraint: svarz is consistent with varz BUT one letter in the state
        # is allowed not to match!
        pos_matches = [And(*(If(svarz[(r,c,i)], varz[(r,c,letter)]) for r in COORDS for c in COORDS))
                       for i, letter in enumerate(pattern)]
        sconj.append(NumFalse(*pos_matches) <= 1)

        # Constraint: Any consecutive i and i+1 in the svarz are connected by a
        # king's move.
        for i in range(1, len(pattern)):
            for r in COORDS:
                for c in COORDS:
                    sconj.append(If(svarz[(r,c,i)], Or(*(svarz[(rr,cc,i-1)] for rr, cc in king_neighbors(r,c)))))

        sconj.append(Or(*(svarz[(r,c,len(pattern)-1)] for r in COORDS for c in COORDS)))

        # Create a var named after each state that's true iff the state matches
        # the grid. Use these to calculate a conditional total score and to
        # figure out which extra achievements we've matched later.
        v = formula.AddVar(state)
        state_vars[state] = v
        formula.Add(v == And(*sconj))

    # The total score achieved.
    total = sum(If(v, Integer(STATES[state]), Integer(0)) for state, v in state_vars.items())
    formula.Add(total >= min_score)

    # Each extra achievement gets a variable named extra_{name} that's true iff
    # the achievement is satisfied. Achievements listed in extras are forced.
    extra_vars = {}
    def add_extra(name, achieved):
        v = formula.AddVar(f'extra_{name}')
        formula.Add(v == achieved)
        if name in extras:
            print(f'Forcing {name}.')
            formula.Add(v)
        extra_vars[name] = v

    add_extra('200M', total >= 200000000)
    add_extra('20S', NumTrue(*state_vars.values()) >= 20)
    add_extra('PA', state_vars['Pennsylvania'])
    add_extra('M8', And(*(state_vars[s] for s in ['Michigan', 'Massachusetts', 'Maryland', 'Missouri',
                                                  'Minnesota', 'Mississippi', 'Maine', 'Montana'])))
    add_extra('4C', And(*(state_vars[s] for s in ['Colorado', 'Utah', 'Arizona', 'NewMexico'])))
    add_extra('NOCAL', ~state_vars['California'])
    # CRT was not part of the original problem statement, it was mentioned after all submissions had been received.
    add_extra('CRT', And(state_vars['Connecticut'], state_vars['RhodeIsland'], ~state_vars['Texas']))

    # C2C: there's a path of adjacent matched states from the east coast to the west coast.
    # reached[(s,i)] means state s is reachable by a path of length i from the east coast.
    reached = {(state,i): formula.AddVar(f'g:{state}:{i}') for state in NEIGHBORS for i in range(MAX_PATH)}

    # Initialize paths of length 0.
    for state in NEIGHBORS:
        if state in EAST_COAST:
            formula.Add(reached[(state,0)] == state_vars[state])
        else:
            formula.Add(~reached[(state,0)])

    # Define paths of length i in terms of paths of length (i-1).
    for i in range(1, MAX_PATH):
        for state, neighbors in NEIGHBORS.items():
            neighbor_reached = [reached[(neighbor,i-1)] for neighbor in neighbors]
            formula.Add(reached[(state,i)] == And(state_vars[state], Or(*neighbor_reached)))

    add_extra('C2C', Or(*(reached[(state,i)] for state in WEST_COAST for i in range(MAX_PATH))))

    # Constraint: force a desired number of extras. CRT doesn't count since it wasn't part of the original puzzle.
    formula.Add(NumTrue(*(v for name, v in extra_vars.items() if name != 'CRT')) >= min_extras)

    # (Optional) Constraint: force a fixed number of states.
    if num_states is not None:
        formula.Add(NumTrue(*state_vars.values()) == num_states)

    return formula

def print_solution(sol, *extra_args):
    coords, vals, states = extra_args
    for r in coords:
        print(''.join(f' {chr(v + ord("A"))} ' for c in coords for v in vals if sol[f'v:{r}:{c}:{v}']))
    matches = [state for state in states if sol[state]]
    score = sum(states[state] for state in matches)

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
    print('Extras:')
    for extra in ['20S', '200M', 'PA', 'M8', '4C', 'NOCAL', 'CRT', 'C2C']:
        if sol[f'extra_{extra}']:
            print(f'  {extra}')
    print(f'Score: {score}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve Jane Street's Altered States 2 puzzle")
    parser.add_argument('min_score', type=int, help='Minimum score. Puzzle uses 165,379,868')
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    parser.add_argument('--extras', type=str, help='Extras: comma-separated list of 20S, 200M, PA, M8, 4C, NOCAL, C2C, or CRT', default='')
    parser.add_argument('--min_extras', type=int, help='Minimum number of extras achieved', default=0)
    parser.add_argument('--num_states', type=int, help='Total number of state matches on board. WARNING: This may conflict with extras', default=None)
    args = parser.parse_args()

    extras = [extra.strip() for extra in args.extras.split(',')]

    formula = encode(args.min_score, extras, args.min_extras, args.num_states)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_args=[COORDS, VALS, STATES])
