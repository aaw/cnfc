from cnfc import *

import argparse

FILES = 'abcdefgh'
RANKS = range(1, 9)
SQUARES = [(f, r) for f in FILES for r in RANKS]
# E = empty, P = pawn, R = rook, B = bishop, N = knight, Q = queen, K = king
PIECES = ['E','P','R','B','N','Q','K']

# Squares strictly between src and dst, which must share a rank, file, or diagonal.
def squares_between(src, dst):
    (f1, r1), (f2, r2) = src, dst
    df, dr = ord(f2) - ord(f1), r2 - r1
    steps = max(abs(df), abs(dr))
    step_f, step_r = (df > 0) - (df < 0), (dr > 0) - (dr < 0)
    return [(chr(ord(f1) + i*step_f), r1 + i*step_r) for i in range(1, steps)]

def encode_as_sat(n, force_unique, formula):
    # Variable v:f:r:p is true if square (f,r) on the board holds piece p.
    vs = {(f,r,p): formula.AddVar(f'v:{f}:{r}:{p}') for f, r in SQUARES for p in PIECES}

    # A square on the board can only be set to one option
    for f, r in SQUARES:
        formula.Add(NumTrue(*(vs[(f,r,p)] for p in PIECES)) == 1)

    # attacks[(src,dst)] is true if the piece on src is attacking the empty square dst.
    attacks = {}
    for src in SQUARES:
        for dst in SQUARES:
            if src == dst: continue  # can't attack yourself
            df, dr = abs(ord(dst[0]) - ord(src[0])), dst[1] - src[1]

            # Collect the pieces on src that would attack dst, given the geometry.
            attackers = []
            if dr == 1 and df == 1:
                attackers.append(vs[(*src,'P')])  # Pawns attack one rank ahead diagonally.
            if df == 0 or dr == 0 or df == abs(dr):
                slider = 'R' if df == 0 or dr == 0 else 'B'
                empty_between = [vs[(*sq,'E')] for sq in squares_between(src, dst)]
                attackers.append(And(Or(vs[(*src,slider)], vs[(*src,'Q')]), *empty_between))
            if {df, abs(dr)} == {1, 2}:
                attackers.append(vs[(*src,'N')])
            if df <= 1 and abs(dr) <= 1:
                attackers.append(vs[(*src,'K')])

            if attackers:
                attacks[(src,dst)] = And(Or(*attackers), vs[(*dst,'E')])

    # For each nn in 0..n, there is some empty square that's attacked by exactly nn pieces.
    for nn in range(n+1):
        attacked_by_nn = [And(vs[(*dst,'E')], NumTrue(*(attacks[(src,dst)] for src in SQUARES if (src,dst) in attacks)) == nn)
                          for dst in SQUARES]
        formula.Add(Or(*attacked_by_nn))

    if force_unique:
        formula.Add(NumTrue(*(vs[(f,r,'E')] for f, r in SQUARES)) == n+1)

def extract_board_from_solution(sol, *extra_args):
    print("Solution: ")
    for r in range(8, 0, -1):
        print(' '.join(p for f in 'abcdefgh' for p in 'EPRBNQK' if sol[f'v:{f}:{r}:{p}']))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate an attacking chessboard")
    parser.add_argument('n', type=int, help="Find empty squares attacked by exactly 0, 1, ..., n pieces.")
    parser.add_argument('--unique', action=argparse.BooleanOptionalAction, default=False,
                        help="Require exactly n+1 empty squares, so each attack count appears exactly once.")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = Formula()
    encode_as_sat(args.n, args.unique, formula)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, extract_board_from_solution)
