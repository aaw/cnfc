from cnfc import *
from itertools import combinations

import argparse

def generate_formula(num_teams, num_rounds, num_players):
    # Sanity check these params.
    assert num_teams % 2 == 0, "Impossible to match up teams each round."
    assert num_players % num_teams == 0, "Impossible to divide players evenly into teams."
    players_per_team = num_players // num_teams

    # Identify each player, team, and round with an integer from here on out.
    players = list(range(1,num_players+1))
    teams = list(range(1,num_teams+1))
    rounds = list(range(1,num_rounds+1))

    # This just pairs the teams up per round: [(1,2),(3,4),...] means team 1 plays
    # team 2, team 3 plays team 4, etc.
    matchups = list(zip(teams[::2],teams[1::2]))

    # Associate a boolean variable with each triple (p,t,r), where (p,t,r)
    # means player p is on team t in round r.
    formula = Formula()
    varz = dict(((player, team, rnd), formula.AddVar(f'{player}:{team}:{rnd}'))
                for player in players for team in teams for rnd in rounds)

    # Constraint: Exactly players_per_team players on each team in each round.
    for rnd in rounds:
        for team in teams:
            on_team = [varz[(player,team,rnd)] for player in players]
            formula.Add(NumTrue(*on_team) == players_per_team)

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
        face_offs = [Or(And(varz[(player1,team1,rnd)],varz[(player2,team2,rnd)]),
                        And(varz[(player1,team2,rnd)],varz[(player2,team1,rnd)])) for rnd in rounds for team1,team2 in matchups]
        formula.Add(NumTrue(*face_offs) <= 1)

    # Symmetry breaking: Assume (1,2,3) vs (4,5,6), (7,8,9) vs. (10,11,12), etc. for first round.
    players_per_team = num_players // num_teams
    player, team = 1,1
    while player <= num_players:
        for i in range(players_per_team):
            formula.Add(varz[(player,team,1)])
            player += 1
        team += 1

    # Symmetry breaking: Assume 1 always on team 1 in each round (already assume this for first round).
    for rnd in rounds[1:]:
        formula.Add(varz[(1,1,rnd)])

    # Symmetry breaking: Assume 4 always on team 3 in each round after the first (since it can never be paired with 1 again).
    for rnd in rounds[1:]:
        formula.Add(varz[(4,3,rnd)])

    formula.Simplify()
    return formula


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
    parser.add_argument('--teams', type=int, help='Number of teams.', default=8)
    parser.add_argument('--rounds', type=int, help='Number of rounds.', default=7)
    parser.add_argument('--players', type=int, help='Number of players.', default=24)
    args = parser.parse_args()

    formula = generate_formula(args.teams, args.rounds, args.players)

    # Write the resulting CNF file to /tmp/cnf.
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    # Write an extractor script to /tmp/extractor.py.
    with open(args.extractor, 'w') as f:
        players = range(1,args.players+1)
        teams = range(1,args.teams+1)
        rounds = range(1,args.rounds+1)
        formula.WriteExtractor(f, print_solution, extra_args=[players, teams, rounds])
