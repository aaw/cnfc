from cnfc import *
from itertools import combinations

import argparse

TEAMS = 8
ROUNDS = 7
PLAYERS = 24

# Sanity check these params in case they change.
assert TEAMS % 2 == 0, "Impossible to match up teams each round."
assert PLAYERS % TEAMS == 0, "Impossible to divide players evenly into teams."

# Identify each player, team, and round with an integer from here on out.
players = list(range(1,PLAYERS+1))
teams = list(range(1,TEAMS+1))
rounds = list(range(1,ROUNDS+1))

# This just pairs the teams up per round: [(1,2),(3,4),...] means team 1 plays
# team 2, team 3 plays team 4, etc.
matchups = list(zip(teams[::2],teams[1::2]))

# Associate a boolean variable with each triple (p,t,r), where (p,t,r)
# means player p is on team t in round r.
formula = Formula()
varz = dict(((player, team, rnd), formula.AddVar(f'{player}:{team}:{rnd}'))
            for player in players for team in teams for rnd in rounds)

# Constraint: Exactly 3 players on each team in each round.
for rnd in rounds:
    for team in teams:
        on_team = [varz[(player,team,rnd)] for player in players]
        formula.Add(NumTrue(*on_team) == 3)

# Constraint: Each player is on exactly one team per round.
for rnd in rounds:
    for player in players:
        teams_for_player = [varz[(player,team,rnd)] for team in teams]
        formula.Add(NumTrue(*teams_for_player) == 1)

# Constraint: No two players can both appear on the same team more than once
for player1, player2 in combinations(players,2):
    same_team = [And(varz[(player1,team,rnd)],varz[(player2,team,rnd)]) for rnd in rounds for team in teams]
    formula.Add(NumTrue(*same_team) <= 1)

# Constraint: No two players can face off more than once
for player1, player2 in combinations(players,2):
    for team1, team2 in matchups:
        face_offs = [Or(And(varz[(player1,team1,rnd)],varz[(player2,team2,rnd)]),
                        And(varz[(player1,team2,rnd)],varz[(player2,team1,rnd)])) for rnd in rounds]
        formula.Add(NumTrue(*face_offs) <= 1)

# This function will be called to print the final tournament schedule.
def print_solution(sol, *extra_args):
    players, teams, rounds = extra_args
    matchups = list(zip(teams[::2],teams[1::2]))
    for rnd in rounds:
        print('Round {}: '.format(rnd), end='')
        for team1, team2 in matchups:
            first_team = tuple(sorted(player for player in players if sol['{}:{}:{}'.format(player,team1,rnd)]))
            second_team = tuple(sorted(player for player in players if sol['{}:{}:{}'.format(player,team2,rnd)]))
            print('{} vs {}'.format(first_team, second_team), end='')
            if team2 != teams[-1]:
                print(', ', end='')
            else:
                print('')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve a tournament matching problem")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    # Write the resulting CNF file to /tmp/cnf.
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    # Write an extractor script to /tmp/extractor.py.
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, extra_args=[players, teams, rounds])
