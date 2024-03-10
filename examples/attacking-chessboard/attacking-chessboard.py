from cnfc import *

import argparse

ALPHABET = ['a','b','c','d','e','f','g','h']
NUMS = range(1,9)
# E = empty, P = pawn, R = rook, B = bishop, N = knight, Q = queen, K = king
PIECES = ['E','P','R','B','N','Q','K']

def encode_as_sat(n, force_unique, formula):
    # Variable v:i:j:k is true if position (i,j) on the board is set to k.
    vs = dict(((i,j,k), formula.AddVar('v:{}:{}:{}'.format(i,j,k)))
              for i in ALPHABET
              for j in NUMS
              for k in PIECES)

    # A cell on the board can only be set to one option
    for i in ALPHABET:
        for j in NUMS:
            options = [vs[(i,j,p)] for p in PIECES]
            formula.Add(NumTrue(*options) == 1)

    # Variable x:i:j:k:l is true if position (i,j) is attacking position (k,l)
    xs = dict(((i,j,k,l), formula.AddVar('x:{}:{}:{}:{}'.format(i,j,k,l)))
              for i in ALPHABET
              for j in NUMS
              for k in ALPHABET
              for l in NUMS)

    def nothing_between(vs, i,j,k,l):
        if i != k and j != l and (abs(ord(i) - ord(k)) != abs(j-l)):
            return BooleanLiteral(False)
        i_inc = 0
        if ord(i) > ord(k):
            i_inc = -1
        elif ord(i) < ord(k):
            i_inc = 1
        j_inc = 0
        if j > l:
            j_inc = -1
        elif j < l:
            j_inc = 1
        ii, jj = chr(ord(i) + i_inc), j + j_inc
        betweens = []
        while (ii,jj) != (k,l):
            betweens.append(vs[(ii,jj,'E')])
            ii, jj = chr(ord(ii) + i_inc), jj + j_inc
        return And(*betweens)

    # Populate xs: For each cell, figure out who it can attack
    for i in ALPHABET:
        for j in NUMS:
            for k in ALPHABET:
                for l in NUMS:
                    if i == k and j == l: continue  # can't attack yourself
                    # (i,j) is attacking (k,l) if:
                    # * It's a pawn and one diagonal space below.
                    # * It's a rook and only vertical empty spaces exist between.
                    # * It's a bishop and only diagonal empty spaces exist between.
                    # * It's a knight and an L-shape distance away.
                    # * It's a king and one vertical or diagonal space away.
                    # * It's a queen and is rook-wise or bishop-wise attacking.
                    pawn = vs[(i,j,'P')] & BooleanLiteral(l - j == 1 and abs(ord(i) - ord(k)) == 1)
                    rook = vs[(i,j,'R')] & BooleanLiteral(l == j or i == k) & nothing_between(vs,i,j,k,l)
                    bishop = vs[(i,j,'B')] & BooleanLiteral(abs(l - j) == abs(ord(i) - ord(k))) & nothing_between(vs,i,j,k,l)
                    knight = vs[(i,j,'N')] & BooleanLiteral((abs(l - j) == 2 and abs(ord(i) - ord(k)) == 1) or (abs(l - j) == 1 and abs(ord(i) - ord(k)) == 2))
                    queen = vs[(i,j,'Q')] & BooleanLiteral((l == j or i == k) or (abs(l - j) == abs(ord(i) - ord(k)))) & nothing_between(vs,i,j,k,l)
                    king = vs[(i,j,'K')] & BooleanLiteral(abs(l - j) <= 1 and abs(ord(i) - ord(k)) <= 1)
                    formula.Add(((pawn | rook | bishop | knight | queen | king) & vs[(k,l,'E')]) == xs[(i,j,k,l)])

    # vs[(i,j,k)] is true if position (i,j) on the board is set to k.
    # xs[(i,j,k,l)] is true if if position (i,j) is attacking position (k,l)
    for nn in range(n+1):
        # There is some cell that's empty and attacked by nn cells
        attacked_by_n = []
        for k in ALPHABET:
            for l in NUMS:
                attacked_by_n.append((NumTrue(*[xs[(i,j,k,l)] for i in ALPHABET for j in NUMS if (i,j) != (k,l)]) == nn) & vs[(k,l,'E')])
        formula.Add(Or(*attacked_by_n))

    if force_unique:
        emptys = [vs[(i,j,'E')] for i in ALPHABET for j in NUMS]
        formula.Add(NumTrue(*emptys) == n+1)

def extract_board_from_solution(sol, *extra_args):
    board = [[None for c in range(8)] for r in range(8)]
    for r in range(8):
        for c in range(8):
            for p in ['E','P','R','B','N','Q','K']:
                if sol['v:{}:{}:{}'.format(chr(ord('a') + c),r+1,p)]:
                    board[7-r][c] = p
                    break
    print("Solution: ")
    print_board(board)

def print_board(board):
    for row in board:
        for x in row:
            print('{} '.format(x), end='')
        print('')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate an attacking chessboard")
    parser.add_argument('n', type=int, help="n.")
    parser.add_argument('--unique', action='store_true')
    parser.add_argument('--no-unique', dest='unique', action='store_false')
    parser.set_defaults(unique=False)
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = Formula()
    encode_as_sat(args.n, args.unique, formula)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, extract_board_from_solution, [print_board])
