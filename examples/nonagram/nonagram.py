from cnfc import *

import argparse

def parse_clues(clue_string):
    return [[int(y.strip()) for y in x.strip().split(',')] for x in clue_string.strip().split(';')]

def clues_to_regex(clues):
    return '0*' + ['1'*n for n in clues].join('0+') + '0*'

assert(clues_to_regex([1]) == '0*10*')
assert(clues_to_regex([2,1,3]) == '0*110+10+1110*')

def encode_nonagram_as_sat(hclues, vclues, formula):
    # We have an hclues-by-vclues bitmap. Variable i:j is true if
    # position (i,j) on the bitmap is set. hclues[j] are clues
    # about column j, vclues[i] are clues about row i.
    vs = dict(((i,j), formula.AddVar('{}:{}'.format(i,j)))
              for i in range(len(vclues))
              for j in range(len(hclues)))

    # Add column clues.
    for j, clues in enumerate(hclues):
        col = Tuple(*[vs[(i,j)] for i in range(len(vclues))])
        regex = clues_to_regex(clues)
        formula.Add(RegexMatch(col, regex))

    # Add row clues.
    for i, clues in enumerate(vclues):
        row = Tuple(*[vs[(i,j)] for j in range(len(hclues))])
        regex = clues_to_regex(clues)
        formula.Add(RegexMatch(row, regex))

def extract_board_from_solution(sol, *extra_args):
    rows, cols = extra_args
    board = [[False for c in range(cols)] for r in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if sol['{}:{}'.format(r,c)]:
                print('X', end='')
            else:
                print(' ', end='')
        print('')
            board[r][c] = sol['{}:{}'.format(r,c)]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a Sudoku solver")
    parser.add_argument('--out', type=str, help='Path to output CNF file.', required=True)
    parser.add_argument('--extractor', type=str, help='Path to output extractor script.', required=True)
    parser.add_argument('--hclues', type=str, help='Clues on the horizontal axis, starting from top left. Clues are separated by commas, columns separated by semicolons', required=True)
    parser.add_argument('--vclues', type=str, help='Clues on the vorizontal axis, starting from top left. Clues are separated by commas, rows separated by semicolons', required=True)
    args = parser.parse_args()

    hclues = parse_clues(args.hclues)
    vclues = parse_clues(args.vclues)

    formula = Formula()
    encode_nonagram_as_sat(hclues, vclues, formula)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, extract_board_from_solution, [print_board], extra_args=[len(vclues), len(hclues)])
