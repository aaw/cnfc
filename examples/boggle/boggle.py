import argparse
import string
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
    # 3, is upper case only, and has any Qu replace by Q.
    word_length = len(word) + sum(1 for ch in word if ch == 'Q')
    if len(word) in [3,4]: return Integer(1)
    if len(word) == 5: return Integer(2)
    if len(word) == 6: return Integer(3)
    if len(word) == 7: return Integer(5)
    if len(word) >= 8: return Integer(11)
    raise ValueError(f"Invalid word: {word}, can't calculate score.")

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
        rolls = {}
        for i,d in enumerate(ds):
            for j,x in enumerate(d):
                rolls[(i,j)] = formula.AddVar(f'rolls:{i}:{j}')

        # Constraint: die i has exactly one roll result.
        for i,d in enumerate(ds):
            roll_results = [rolls[(i,j)] for j in range(len(d))]
            formula.Add(NumTrue(*roll_results) == 1)

        # Variable die_match:i:r:c is true iff die i is rolled into board position (r,c)
        die_match = {}
        for r in rows:
            for c in cols:
                for i in range(len(ds)):
                    die_match[(i,r,c)] = formula.AddVar(f'die_match:{i}:{r}:{c}')

        # Constraint: board position (r,c) is matched to exactly one die.
        for r in rows:
            for c in cols:
                die_matches = [die_match[(i,r,c)] for i in range(len(ds))]
                formula.Add(NumTrue(*die_matches) == 1)

        # TODO: I guess boards like 5-by-5 with more than 16 dice just allow re-use???
        if len(rows) == 4 and len(cols) == 4:
            # Constraint: each die is matched to at most one board position.
            for i in range(len(ds)):
                die_matches = [die_match[(i,r,c)] for r in rows for c in cols]
                formula.Add(NumTrue(*die_matches) <= 1)

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
    word_found = {}
    for i,word in enumerate(words):
        word_found[i] = formula.AddVar(f'word_found:{i}')

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

        elapsed_sec = time.time() - start_time
        elapsed_hr = elapsed_sec / 3600
        avg_time_per_item = elapsed_sec / (i + 1)
        remaining_sec = avg_time_per_item * (len(words) - i - 1)
        remaining_hr = remaining_sec / 3600

        print(f'Generated clauses for {word} ({i}/{len(words)}) | Elapsed: {elapsed_hr:.2f}h | Remaining: {remaining_hr:.2f}h', flush=True)

    # Constraint: total score is at least the desired score
    scores = [If(word_found[i], word_score(words[i]), Integer(0)) for i in range(len(words))]
    formula.Add(sum(scores) >= score)

    if len(rows) <= 4 and len(cols) <= 4:
        # Symmetry breaking: Under reflections and rotations of a board with at most 4 rows and
        # at most 4 columns, there are only 3 unique positions. So constrain the first die to
        # one of these (diagrammed with X's below):
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

    def ws(word):
        word_length = len(word) + sum(1 for ch in word if ch == 'Q')
        if len(word) in [3,4]: return 1
        if len(word) == 5: return 2
        if len(word) == 6: return 3
        if len(word) == 7: return 5
        if len(word) >= 8: return 11

    total = 0
    for i,word in enumerate(words):
        if sol[f'word_found:{i}']:
            points = ws(word)
            total += points
            print(f'{word}: {points} points')
    print('')
    print(f'Total score: {total}')
    print('')

    for r in rows:
        row = []
        for c in cols:
            for x in alphabet:
                if sol[f'board:{r}:{c}:{x}']:
                    row.append(x)
        print(' '.join(row))

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
        import sys; sys.exit(1)
    words = open(args.words).read().strip().split('\n')

    # The Boggle dice have a "Qu" and no "Q". So we'll clean the words by
    # removing anything that has a "QX" for X != U or ends with Q, then replace
    # any "Qu" with "Q" since our dice just have "Q" on them. We'll just need to
    # remember to account for this when scoring since "Qu" counts as 2 letters.
    # Words with less than 3 letters don't score in Boggle, so we'll just remove
    # those.
    cleaned_words = []
    for word in words:
        if len(word) < 3: continue
        word = word.upper()
        if any(ch not in ALPHABET for ch in word): continue
        if 'QU' in word or word.endswith('Q'): continue
        word = word.replace("QU", "Q")
        if len(word) > 16: continue
        cleaned_words.append(word)

    rows, cols = list(range(args.rows)), list(range(args.cols))

    formula = encode(args.score, args.dice, rows, cols, cleaned_words)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, [], extra_args=[args.score, rows, cols, ALPHABET, cleaned_words])
