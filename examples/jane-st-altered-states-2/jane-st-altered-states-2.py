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

# Encodes the Altered States 2 puzzle into a Formula.
def encode(min_score, extras, min_extras):
    formula = Formula()

    # varz[(r,c,v)] is true iff cell (r,v) has value v in VALS
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

    # The total score achieved.
    total = Integer(0)
    # Maps state names to a variable that's true iff that state is matched.
    state_vars = {}

    for state in STATES.keys():
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

        # Constraint: svarz is consistent with varz BUT one letter in the state
        # is allowed not to match!
        pos_matches = []
        for i, _ in enumerate(pattern):
            conj = []
            for r in COORDS:
                for c in COORDS:
                    conj.append(If(svarz[(r,c,i)], varz[r,c,pattern[i]]))
            pos_matches.append(And(*conj))
        sconj.append(NumFalse(*pos_matches) <= 1)

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
        # the grid. Use these to calculate a conditional total score and to
        # figure out which extra achievements we've matched later.
        v = formula.AddVar(state)
        state_vars[state] = v
        formula.Add(v == And(*sconj))

        total = total + If(v, Integer(STATES[state]), Integer(0))

    formula.Add(total >= Integer(min_score))

    # Encode 200M, force it if requested.
    extra_200M = formula.AddVar('extra_200M')
    formula.Add((total >= Integer(200000000)) == extra_200M)
    if '200M' in extras:
        print('Forcing 200M.')
        formula.Add(extra_200M)

    # Encode 20S, force it if requested.
    extra_20S = formula.AddVar('extra_20S')
    formula.Add((NumTrue(*(v for v in state_vars.values())) >= 20) == extra_20S)
    if '20S' in extras:
        print('Forcing 20S.')
        formula.Add(extra_20S)

    # Encode PA, force it if requested.
    extra_PA = formula.AddVar('extra_PA')
    formula.Add(state_vars['Pennsylvania'] == extra_PA)
    if 'PA' in extras:
        print('Forcing PA.')
        formula.Add(extra_PA)

    # Encode M8, force it if requested.
    extra_M8 = formula.AddVar('extra_M8')
    formula.Add(And(state_vars['Michigan'], state_vars['Massachusetts'], state_vars['Maryland'], state_vars['Missouri'],
                    state_vars['Minnesota'], state_vars['Mississippi'], state_vars['Maine'], state_vars['Montana']) == extra_M8)
    if 'M8' in extras:
        print('Forcing M8.')
        formula.Add(extra_M8)

    # Encode 4C, force it if requested.
    extra_4C = formula.AddVar('extra_4C')
    formula.Add(And(state_vars['Colorado'],state_vars['Utah'],state_vars['Arizona'],state_vars['NewMexico']) == extra_4C)
    if '4C' in extras:
        print('Forcing 4C.')
        formula.Add(extra_4C)

    # Encode NOCAL, force it if requested.
    extra_NOCAL = formula.AddVar('extra_NOCAL')
    formula.Add(~state_vars['California'] == extra_NOCAL)
    if 'NOCAL' in extras:
        print('   Forcing NOCAL.')
        formula.Add(extra_NOCAL)

    # Encode C2C, force it if requested.
    extra_C2C = formula.AddVar('extra_C2C')
    # State-to-state adjacencies. Note that the "Four Corners" states are not
    # considered adjacent when they touch diagonally.
    g = {
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
        'Indiana': ['Mississippi', 'Ohio', 'Kentucky', 'Illinois'],
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
        'Wyoming': ['Idaho', 'Montana', 'NorthDakota', 'SouthDakota', 'Nebraska', 'Colorado', 'Utah'],
    }
    # gvarz[(s,i)] means state s is reachable by path of length i from east coast
    gvarz = {}
    # A max path of length 16 from the east coast to the west coast seems
    # reasonable.
    MAX_PATH = 16
    for state in g.keys():
        for i in range(MAX_PATH):
            gvarz[(state,i)] = formula.AddVar('g:{}:{}'.format(state,i))

    east_coast = [
        'Maine', 'NewHampshire', 'Massachusetts', 'RhodeIsland', 'Connecticut',
        'NewYork', 'NewJersey', 'Delaware', 'Maryland', 'Virginia', 'NorthCarolina',
        'SouthCarolina', 'Georgia', 'Florida'
    ]

    # Initialize paths of length 0.
    for state in east_coast:
        formula.Add(state_vars[state] == gvarz[(state,0)])
    for state in g.keys() - east_coast:
        formula.Add(~gvarz[(state,0)])

    # Define paths of length i in terms of paths of length (i-1).
    for i in range(1, MAX_PATH):
        for state, adj in g.items():
            adj_state_reached = [gvarz[(adj_state,i-1)] for adj_state in adj]
            formula.Add(gvarz[(state,i)] == And(state_vars[state], Or(*adj_state_reached)))

    got_to_west_coast = Or(*[gvarz[(state,i)] for state in ['California', 'Oregon', 'Washington'] for i in range(MAX_PATH)])
    formula.Add(got_to_west_coast == extra_C2C)
    if 'C2C' in extras:
        print('Forcing C2C.')
        formula.Add(extra_C2C)

    # Constraint: force a desired number of extras
    formula.Add(NumTrue(*[extra_200M, extra_20S, extra_PA, extra_M8, extra_4C, extra_NOCAL, extra_C2C]) >= min_extras)

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
    matches = [sname for sname in states.keys() if sol[sname]]
    score = sum(val for key, val in states.items() if sol[key])

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
    print('Extras:')
    for extra in ['extra_20S', 'extra_200M', 'extra_PA', 'extra_M8', 'extra_4C', 'extra_NOCAL', 'extra_C2C']:
        if sol[extra]:
            print('  {}'.format(extra[6:]))
    print('Score: {}'.format(score))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve Jane Street's Altered States 2 puzzle")
    parser.add_argument('min_score', type=int, help='Minimum score.')
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    parser.add_argument('--extras', type=str, help='Extras: comma-separated list of 20S, 200M, PA, M8, 4C, NOCAL, or C2C', default='')
    parser.add_argument('--min_extras', type=int, help='Minimum number of extras achieved', default=0)
    args = parser.parse_args()

    extras = [extra.strip() for extra in args.extras.split(',')]

    formula = encode(args.min_score, extras, args.min_extras)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, [], extra_args=[COORDS, VALS, STATES])
