import argparse
import re
import string
import sys
import time

from pathlib import Path
from cnfc import *

# Dice definitions: https://www.bananagrammer.com/2013/10/the-boggle-cube-redesign-and-its-effect.html
CLASSIC_DICE = [
    'AACIOT', 'ABILTY', 'ABJMOQ', 'ACDEMP', 'ACELRS', 'ADENVZ', 'AHMORS', 'BIFORX',
    'DENOSW', 'DKNOTU', 'EEFHIY', 'EGKLUY', 'EGINTV', 'EHINPS', 'ELPSTU', 'GILRUW',
]

NEW_DICE = [
    'AAEEGN', 'ABBJOO', 'ACHOPS', 'AFFKPS', 'AOOTTW', 'CIMOTU', 'DEILRX', 'DELRVY',
    'DISTTY', 'EEGHNW', 'EEINSU', 'EHRTVW', 'EIOSST', 'ELRTTY', 'HIMNUQ', 'HLNNRZ',
]

ALPHABET = list(string.ascii_uppercase)

def word_score(word):
    # The input to this function is a cleaned word, so it has length at least
    # 3, is upper case only, and has any Qu replaced by Q. Since the "Qu" die
    # face counts as two letters, each Q adds one to the scored length.
    length = len(word) + word.count('Q')
    if length <= 4: return 1
    if length == 5: return 2
    if length == 6: return 3
    if length == 7: return 5
    return 11

def king_neighbors(r, c, rows, cols):
    return [
        (nr, nc)
        for dr in (-1, 0, 1)
        for dc in (-1, 0, 1)
        if (dr or dc) and (nr := r + dr) in rows and (nc := c + dc) in cols
    ]

def encode(score, dice, rows, cols, words):
    formula = Formula(FileBuffer)

    # Variable board:r:c:x is true iff row r, column c is the letter x.
    board = {}
    for r in rows:
        for c in cols:
            for x in ALPHABET:
                board[(r,c,x)] = formula.AddVar(f'board:{r}:{c}:{x}')

    # Constraint: Each board position (r,c) has exactly one letter assigned.
    for r in rows:
        for c in cols:
            cell_values = [board[(r,c,x)] for x in ALPHABET]
            formula.Add(NumTrue(*cell_values) == 1)

    # Constraint: Board assignments are feasible given the dice, if dice are specified.
    #             If dice are not specified, each die is effectively 26-sided, containing
    #             each letter in the English alphabet once.
    if dice != 'none':
        ds = CLASSIC_DICE if dice == 'classic' else NEW_DICE

        # Variable rolls:i:j is true iff die i rolls the jth face.
        rolls = {(i,j): formula.AddVar(f'rolls:{i}:{j}') for i,d in enumerate(ds) for j in range(len(d))}

        # Constraint: die i has exactly one roll result.
        for i,d in enumerate(ds):
            formula.Add(NumTrue(*(rolls[(i,j)] for j in range(len(d)))) == 1)

        # Variable die_match:i:r:c is true iff die i is rolled into board position (r,c)
        die_match = {(i,r,c): formula.AddVar(f'die_match:{i}:{r}:{c}')
                     for r in rows for c in cols for i in range(len(ds))}

        # Constraint: board position (r,c) is matched to exactly one die.
        for r in rows:
            for c in cols:
                formula.Add(NumTrue(*(die_match[(i,r,c)] for i in range(len(ds)))) == 1)

        # TODO: I guess boards like 5-by-5 with more than 16 dice just allow re-use???
        if len(rows) == 4 and len(cols) == 4:
            # Constraint: each die is matched to at most one board position.
            for i in range(len(ds)):
                formula.Add(NumTrue(*(die_match[(i,r,c)] for r in rows for c in cols)) <= 1)

        # Constraint: board position (r,c) agrees with a face on die i if it's matched to it
        for r in rows:
            for c in cols:
                for x in ALPHABET:
                    for i,d in enumerate(ds):
                        # We want:
                        #    (board[(r,c,x)] AND die_match[(i,r,c)]) => (x in d)
                        # But (x in d) is just a constant, so we optimize this a little:
                        if x not in d: formula.Add(Or(~board[(r,c,x)], ~die_match[(i,r,c)]))

    # Variable word_found:i is true iff word i can be found on the board.
    word_found = [formula.AddVar(f'word_found:{i}') for i in range(len(words))]

    start_time = time.time()
    word_vars = {}
    for i, word in enumerate(words):
        # Variable word:i:r:c:j is true iff word i's jth character is chosen for (r,c)
        for r in rows:
            for c in cols:
                for j in range(len(word)):
                    word_vars[(i,r,c,j)] = formula.AddVar(f'word:{i}:{r}:{c}:{j}')
                    # Constraint: word_vars agrees with board assignments.
                    formula.Add(word_vars[(i,r,c,j)] == board[(r,c,word[j])])

        # Constraint: exactly one position (r,c) is chosen for each word var.
        constraints = []
        for j in range(len(word)):
            positions = [word_vars[(i,r,c,j)] for r in rows for c in cols]
            constraints.append(NumTrue(*positions) == 1)

        # Constraint: word vars are arranged in a kings walk.
        for j in range(1, len(word)):
            for r in rows:
                for c in cols:
                    neighbor_set = [word_vars[(i,nr,nc,j-1)] for (nr,nc) in king_neighbors(r,c,rows,cols)]
                    # Could do: constraints.append(If(word_vars[(i,r,c,j)], Or(*neighbor_set)))
                    # here, simplifying a bit for compactness below:
                    neighbor_set.append(~word_vars[(i,r,c,j)])
                    constraints.append(Or(*neighbor_set))

        # Constraint: no position (r,c) is repeated (kings walk doesn't self-intersect).
        for r in rows:
            for c in cols:
                for j in range(len(word)-1):
                    constraints.append(If(word_vars[(i,r,c,j)], And(*[~word_vars[(i,r,c,k)] for k in range(j+1,len(word))])))

        # Finally, connect a full word match with word_found vars.
        formula.Add(word_found[i] == And(*constraints))

        # Generating the full enable2k formula takes hours, so report progress.
        elapsed_hr = (time.time() - start_time) / 3600
        remaining_hr = elapsed_hr / (i + 1) * (len(words) - i - 1)
        print(f'Generated clauses for {word} ({i+1}/{len(words)}) | Elapsed: {elapsed_hr:.2f}h | Remaining: {remaining_hr:.2f}h', flush=True)

    # Constraint: total score is at least the desired score
    scores = [If(found, Integer(word_score(word)), Integer(0)) for found, word in zip(word_found, words)]
    formula.Add(sum(scores) >= score)

    if dice != 'none' and len(rows) == 4 and len(cols) == 4:
        # Symmetry breaking: On a 4-by-4 board, every die is used, and under reflections and
        # rotations there are only 3 unique positions. So constrain the first die to one of
        # these (diagrammed with X's below):
        #
        #     X X . .
        #     . X . .
        #     . . . .
        #     . . . .
        #
        formula.Add(Or(die_match[(0,0,0)], die_match[(0,0,1)], die_match[(0,1,1)]))

    return formula

def print_solution(sol, *extra_args):
    score, rows, cols, alphabet, words = extra_args

    total = 0
    for i,word in enumerate(words):
        if sol[f'word_found:{i}']:
            points = word_score(word)
            total += points
            print(f"{word.replace('Q', 'QU')}: {points} points")
    print('')
    print(f'Total score: {total}')
    print('')

    for r in rows:
        print(' '.join(x for c in cols for x in alphabet if sol[f'board:{r}:{c}:{x}']))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search for Boggle boards.')
    parser.add_argument('score', type=int, help='Minimum score.')
    parser.add_argument('--dice', choices=['classic','new','none'], default='none', help='Validate dice using classic, new, or none (default) dice definitions')
    parser.add_argument('--words', type=str, help='Path to word list (one word per line)', default='/tmp/enable2k.txt')
    parser.add_argument('--rows', type=int, help='Number of rows on Boggle board', default=4)
    parser.add_argument('--cols', type=int, help='Number of columns on Boggle board', default=4)
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    assert args.score > 0, "score must be positive"

    if not Path(args.words).is_file():
        print(f"{args.words} does not exist. Download a file from https://github.com/danvk/hybrid-boggle/tree/main/wordlists if you're missing one.")
        sys.exit(1)
    words = Path(args.words).read_text().split()
    rows, cols = list(range(args.rows)), list(range(args.cols))

    # The Boggle dice have a "Qu" and no "Q". So we'll clean the words by
    # removing anything with a Q that isn't followed by a U, then replace any
    # "Qu" with "Q" since our dice just have "Q" on them. "Qu" counts as 2
    # letters, which word_score accounts for. Words with less than 3 letters
    # don't score in Boggle and words needing more dice than the board has
    # can't be found, so we'll just remove those.
    cleaned_words = []
    for word in words:
        word = word.upper()
        if any(ch not in ALPHABET for ch in word): continue
        if re.search('Q(?!U)', word): continue
        word = word.replace('QU', 'Q')
        if len(word) + word.count('Q') >= 3 and len(word) <= len(rows) * len(cols):
            cleaned_words.append(word)

    formula = encode(args.score, args.dice, rows, cols, cleaned_words)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, [word_score], extra_args=[args.score, rows, cols, ALPHABET, cleaned_words])
