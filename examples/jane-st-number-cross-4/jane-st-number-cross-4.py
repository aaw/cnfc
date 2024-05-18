# This puzzle (https://www.janestreet.com/puzzles/number-cross-4-index) is an
# 11-by-11 grid of cells, each of which either contains an integer 0-9 or is
# shaded. Within a row, any run of integers uninterrupted by shaded cells
# must fit a pattern specific to that row like "palindrome and multiple of 23".
#
# Because the runs of integers have to be at least 2 cells long and because
# no two shaded cells can be adjacent, there are between 1 and 4 integers on
# each row that we need to test against specific patterns. Many of these
# patterns are easy to express algebraically with integer variables.
#
# The encoding below takes advantage of the fact that even though there are
# 2^11 = 2048 different ways to shade a row of 11 cells, only 54 of these
# shadings are valid given the constraints about consecutive shaded cells and
# unshaded run length. So we create a 4-bit integer variable for each cell
# that represents its contents (0-9, or 10 to represent "shaded"). Then, for
# each row, we create 4 integer variables representing the contents of the
# first, second, third, and fourth integers appearing in runs in that row.
# We also create 4 boolean variables representing whether there exists a
# first, second, third, and fourth integer in that row (there's always a
# first, so we don't strictly need all of these). Finally, we create 54
# different conjunctions, each one connecting a particular shading
# configuration with the variables described above, then OR all of those
# conjunctions together. This lets us separately describe the conditions that
# each integer pattern on each row must satisfy, since we can then just say
# "if the second integer on the 6th row exists, it is a square" using the
# variables we've defined.

from cnfc import *
from cnfc.funcs import IsPalindrome
from itertools import combinations, product

import argparse
import math

# 11 x 11 grid coordinates.
COORDS = [0,1,2,3,4,5,6,7,8,9,10]
# Cells can be 0-9, so we use 10 to indicate shading.
SHADED = Integer(10)
# Enough bits to represent 0-9, plus 10 to indicate shading.
CELL_BITS = 4
# The largest possible value of any row is 99999888776, which needs 36.5 bits.
ROW_BITS = 37
# A representation of the different groups on the board, needed since there
# are constraints about uniformity of numbers within groups and distinctness
# of numbers in neighboring groups.
BOARD = [
    ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'D', 'D', 'D'],
    ['A', 'E', 'E', 'E', 'B', 'B', 'C', 'D', 'D', 'D', 'F'],
    ['A', 'E', 'E', 'B', 'B', 'B', 'C', 'D', 'D', 'D', 'F'],
    ['A', 'E', 'E', 'B', 'B', 'G', 'G', 'D', 'F', 'F', 'F'],
    ['A', 'E', 'B', 'B', 'D', 'D', 'G', 'D', 'F', 'H', 'F'],
    ['A', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'H', 'H', 'I'],
    ['J', 'D', 'D', 'D', 'D', 'K', 'K', 'D', 'H', 'H', 'H'],
    ['J', 'J', 'L', 'D', 'L', 'K', 'K', 'D', 'D', 'H', 'D'],
    ['J', 'J', 'L', 'L', 'L', 'K', 'K', 'D', 'D', 'D', 'D'],
    ['J', 'L', 'L', 'J', 'J', 'J', 'K', 'D', 'D', 'D', 'M'],
    ['J', 'J', 'J', 'J', 'J', 'K', 'K', 'K', 'D', 'D', 'M']
]
# Enums for the row variables we maintain
VAL=0
EXISTS=1
SUM=2
PRODUCT=3

# Generates all 54 valid row patterns as a boolean list where True means
# unshaded and False means shaded.
def row_patterns():
    for mask in product([False,True], repeat=len(COORDS)):
        if any(not mask[i] and not mask[i+1] for i in range(len(COORDS)-1)): continue
        if any(not mask[i] and mask[i+1] and not mask[i+2] for i in range(len(COORDS)-2)): continue
        if mask[0] and not mask[1]: continue
        if not mask[len(COORDS)-2] and mask[len(COORDS)-1]: continue
        yield mask

# Returns a list of pairs representing all runs of unshaded cells in the given
# mask. See assertions immediately following for some examples.
def all_runs(mask):
    retval = []
    start = 0
    for i, (prev, curr) in enumerate(zip(mask, mask[1:])):
        if prev and not curr:
            retval.append((start, i))
        if not prev:
            start = i+1
    if mask[-1]:
        retval.append((start,len(mask)-1))
    return retval

assert(all_runs([True,True,True,True,True,True]) == [(0,5)])
assert(all_runs([True,True,True,True,True,False]) == [(0,4)])
assert(all_runs([False,True,True,True,True,True]) == [(1,5)])
assert(all_runs([True,True,True,False,True,True,True]) == [(0,2),(4,6)])
assert(all_runs([False,True,True,False,True,True,False]) == [(1,2),(4,5)])
assert(all_runs([False,True,True,False,True,True]) == [(1,2),(4,5)])

# Generates constraints for a row based on a particular mask of shaded/unshaded
# cells. This forms a big conjunction that we can OR together across all masks
# to connect cell variables with row variables.
def generate_mask_constraints(row, mask, cell_var, row_var):
    conjuncts = []
    shaded = [i for i, val in enumerate(mask) if not val]
    runs = all_runs(mask)

    # Constraint: Shaded cells are all set to 10.
    for i in shaded:
        conjuncts.append(cell_var[(row,i)] == SHADED)

    # We don't need to enforce "Every run is at least two cells" here, since
    # it's already enforced implicitly by the row pattern generation.
    for start, end in runs:
        # Constraint: No leading zeros in a run.
        conjuncts.append(cell_var[(row,start)] != Integer(0))
        # Constraint: No shaded cells in a run.
        for i in range(start, end+1):
            conjuncts.append(cell_var[(row,i)] != SHADED)

    # Connect row integers to individual cells
    for i, (start, end) in enumerate(runs):
        num = Integer(0)
        for j in range(start, end+1):
            num = num * Integer(10) + cell_var[(row,j)]
        conjuncts.append(row_var[(row,i)][VAL] == num)

    # Set the row existence variables appropriately, given the number of
    # runs in this particular mask.
    for i in [0,1,2,3]:
        if i < len(runs):
            conjuncts.append(row_var[(row,i)][EXISTS])
        else:
            conjuncts.append(~row_var[(row,i)][EXISTS])

    # Connect the cell values to a sum-of-digits variable. We really
    # only need this for row 3 in the puzzle.
    for i, (start, end) in enumerate(runs):
        num = cell_var[(row,start)]
        for j in range(start+1, end+1):
            num = num + cell_var[(row,j)]
        conjuncts.append(row_var[(row,i)][SUM] == num)

    # Connect the cell values to a product-of-digits variable. We really
    # only need this for row 8 in the puzzle.
    for i, (start, end) in enumerate(runs):
        num = cell_var[(row,start)]
        for j in range(start+1, end+1):
            num = num * cell_var[(row,j)]
        conjuncts.append(row_var[(row,i)][PRODUCT] == num)

    return And(*conjuncts)

# Encodes the Number Cross 4 puzzle into a Formula.
def encode():
    formula = Formula(FileBuffer)

    # Cell vars are integers representing the choice of number or shaded for any
    # cell in the grid.
    cell_var = {}
    for r in COORDS:
        for c in COORDS:
            # v:r:c:i is the ith bit of the number in row r, column c.
            i = Integer(*(formula.AddVar('v:{}:{}:{}'.format(r, c, i)) for i in range(CELL_BITS)))
            formula.Add(i <= SHADED)
            cell_var[(r,c)] = i

    # Row vars are tuples representing the integer value of a run, whether that
    # run exists in a row, and the sum and product of a run. They're indexed by
    # a (row, run) tuple, where row ranges from 0 to 3.
    row_var = {}
    for j in [0,1,2,3]:
        for r in COORDS:
            # n:r:j:i is the ith bit of the jth run in row r, for j in [0,1,2,3]
            val = Integer(*(formula.AddVar('n:{}:{}:{}'.format(r, j, i)) for i in range(ROW_BITS)))
            # b:r:j is true iff there is a jth run in row r for j in [0,1,2,3]
            exists = formula.AddVar('b:{}:{}'.format(r,j))
            # sod:r:j:i is the ith bit of the sum of digits of the jth run in row r for j in [0,1,2,3].
            # The sum of all numbers in a row is at most 99, so we only need 7 bits.
            rsum = Integer(*(formula.AddVar('sod:{}:{}:{}'.format(r,j,i)) for i in range(7)))
            # pod:r:j:i is the ith bit of the product of digits of the jth run in row r for j in [0,1,2,3]
            rprod = Integer(*(formula.AddVar('pod:{}:{}:{}'.format(r,j,i)) for i in range(ROW_BITS)))
            # row_var is a tuple of (VAL, EXISTS, SUM, PRODUCT)
            row_var[(r,j)] = (val, exists, rsum, rprod)

    # Constraint: No two shaded cells can share an edge. We already enforce this
    # implicitly for adjacent cells in a row when generating masks, so we only
    # need to enforce it explicitly for columns here.
    for x in COORDS:
        for y1, y2 in zip(COORDS, COORDS[1:]):
            formula.Add(Or(cell_var[(x,y1)] != SHADED, cell_var[(x,y2)] != SHADED))

    # Constraint: Each row matches some valid mask of shaded cells, each run in
    # a row is connected to individual cell values appropriately.
    for row in COORDS:
        print('Generating row {} cell constraints...'.format(row))
        disjuncts = []
        for mask in row_patterns():
            disjuncts.append(generate_mask_constraints(row, mask, cell_var, row_var))
        formula.Add(Or(*disjuncts))

    # Constraint: adjacent cells in the same region contain the same digit unless one is shaded.
    for r in COORDS:
        for c in COORDS[:-1]:
            if BOARD[r][c] == BOARD[r][c+1]:
                formula.Add(Or(cell_var[(r,c)] == SHADED, cell_var[(r,c+1)] == SHADED, cell_var[(r,c)] == cell_var[(r,c+1)]))

    for r in COORDS[:-1]:
        for c in COORDS:
            if BOARD[r][c] == BOARD[r+1][c]:
                formula.Add(Or(cell_var[(r,c)] == SHADED, cell_var[(r+1,c)] == SHADED, cell_var[(r,c)] == cell_var[(r+1,c)]))

    # Constraint: adjacent cells in adjacent regions contain different digits unless one is shaded.
    for r in COORDS:
        for c in COORDS[:-1]:
            if BOARD[r][c] != BOARD[r][c+1]:
                formula.Add(Or(cell_var[(r,c)] == SHADED, cell_var[(r,c+1)] == SHADED, cell_var[(r,c)] != cell_var[(r,c+1)]))

    for r in COORDS[:-1]:
        for c in COORDS:
            if BOARD[r][c] != BOARD[r+1][c]:
                formula.Add(Or(cell_var[(r,c)] == SHADED, cell_var[(r+1,c)] == SHADED, cell_var[(r,c)] != cell_var[(r+1,c)]))

    # At this point, we've connected all cell vars to row vars and asserted all
    # constraints about individual cell values and adjacent cell values. So we
    # can now focus on constraints about the runs in each row, most of which are
    # algebraic.

    # Constraint: Row 0 is a square.
    print('Generating row 0 run constraints...')
    row00, row00on, _, _ = row_var[(0,0)]
    row01, row01on, _, _ = row_var[(0,1)]
    row02, row02on, _, _ = row_var[(0,2)]
    row03, row03on, _, _ = row_var[(0,3)]
    x0 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    formula.Add(If(row00on, x0 * x0 == row00))
    x1 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    formula.Add(If(row01on, x1 * x1 == row01))
    x2 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    formula.Add(If(row02on, x2 * x2 == row02))
    x3 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    formula.Add(If(row03on, x3 * x3 == row03))

    # Constraint: Row 1 is one more than a palindrome.
    print('Generating row 1 run constraints...')
    row10, row10on, _, _ = row_var[(1,0)]
    row11, row11on, _, _ = row_var[(1,1)]
    row12, row12on, _, _ = row_var[(1,2)]
    row13, row13on, _, _ = row_var[(1,3)]
    p0 = Integer(*(formula.AddVar() for i in range(ROW_BITS)))
    formula.Add(If(row10on, And(IsPalindrome(p0), p0 + Integer(1) == row10)))
    p1 = Integer(*(formula.AddVar() for i in range(ROW_BITS)))
    formula.Add(If(row11on, And(IsPalindrome(p1), p1 + Integer(1) == row11)))
    p2 = Integer(*(formula.AddVar() for i in range(ROW_BITS)))
    formula.Add(If(row12on, And(IsPalindrome(p2), p2 + Integer(1) == row12)))
    p3 = Integer(*(formula.AddVar() for i in range(ROW_BITS)))
    formula.Add(If(row13on, And(IsPalindrome(p3), p3 + Integer(1) == row13)))

    # Constraint: Row 2 is a prime raised to a prime.
    # This is the trickiest run constraint, since you can encode "not a prime" easily
    # with SAT but it's difficult to encode "is a prime". Maybe there's a simple
    # algebraic test for a prime raised to a prime that I don't know about using some
    # variant of Fermat's little theorem, but since I don't know one and prime powers
    # are relatively sparse, I'm just going to enumerate all prime powers that are
    # less than 12 digits and test against those explicitly in a big disjunction.
    print('Generating row 2 run constraints...')
    def prime(a):
        return not (a < 2 or any(a % x == 0 for x in range(2, int(math.sqrt(a)) + 1)))
    def num_digits(a):
        count = 0
        while a > 0:
            a //= 10
            count += 1
        return count
    # 316228 is the first number whose square is 12 digits, so we only need to consider prime
    # bases below that.
    primes = [x for x in range(316228) if prime(x)]
    # The first 12-digit power of 2 is 2**37, so we only need to consider exponents below that.
    exps = [x for x in range(37) if prime(x)]
    # The final set of possible prime powers has 27981 elements and only takes a second or
    # two to calculate.
    ptop = [x**y for x in primes for y in exps if 2 <= num_digits(x**y) <= 11]
    row20, row20on, _, _ = row_var[(2,0)]
    row21, row21on, _, _ = row_var[(2,1)]
    row22, row22on, _, _ = row_var[(2,2)]
    row23, row23on, _, _ = row_var[(2,3)]
    formula.Add(If(row20on, Or(*(row20 == x for x in ptop))))
    formula.Add(If(row21on, Or(*(row21 == x for x in ptop))))
    formula.Add(If(row22on, Or(*(row22 == x for x in ptop))))
    formula.Add(If(row23on, Or(*(row23 == x for x in ptop))))

    # Constraint: Sum of Row 3 digits is 7.
    print('Generating row 3 run constraints...')
    _, row30on, sod30, _ = row_var[(3,0)]
    _, row31on, sod31, _ = row_var[(3,1)]
    _, row32on, sod32, _ = row_var[(3,2)]
    _, row33on, sod33, _ = row_var[(3,3)]
    formula.Add(If(row30on, sod30 == Integer(7)))
    formula.Add(If(row31on, sod31 == Integer(7)))
    formula.Add(If(row32on, sod32 == Integer(7)))
    formula.Add(If(row33on, sod33 == Integer(7)))

    # Constraint: Row 4 is a Fibonacci number.
    # Uses Gessel's test: n is a Fibonacci number iff 5n^2 + 4 or 5n^2 - 4 is a square.
    print('Generating row 4 run constraints...')
    row40, row40on, _, _ = row_var[(4,0)]
    row41, row41on, _, _ = row_var[(4,1)]
    row42, row42on, _, _ = row_var[(4,2)]
    row43, row43on, _, _ = row_var[(4,3)]
    five_n_squared0 = Integer(5) * row40 * row40
    x4a0 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    x4b0 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    formula.Add(If(row40on, Or(x4a0 * x4a0 == five_n_squared0 + Integer(4), x4b0 * x4b0 + Integer(4) == five_n_squared0)))
    five_n_squared1 = Integer(5) * row41 * row41
    x4a1 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    x4b1 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    formula.Add(If(row41on, Or(x4a1 * x4a1 == five_n_squared1 + Integer(4), x4b1 * x4b1 + Integer(4) == five_n_squared1)))
    five_n_squared2 = Integer(5) * row42 * row42
    x4a2 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    x4b2 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    formula.Add(If(row42on, Or(x4a2 * x4a2 == five_n_squared2 + Integer(4), x4b2 * x4b2 + Integer(4) == five_n_squared2)))
    five_n_squared3 = Integer(5) * row43 * row43
    x4a3 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    x4b3 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    formula.Add(If(row43on, Or(x4a3 * x4a3 == five_n_squared3 + Integer(4), x4b3 * x4b3 + Integer(4) == five_n_squared3)))

    # Constraint: Row 5 is a square.
    # print('Generating row 5 run constraints...')
    row50, row50on, _, _ = row_var[(5,0)]
    row51, row51on, _, _ = row_var[(5,1)]
    row52, row52on, _, _ = row_var[(5,2)]
    row53, row53on, _, _ = row_var[(5,3)]
    x50 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    formula.Add(If(row50on, x50 * x50 == row50))
    x51 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    formula.Add(If(row51on, x51 * x51 == row51))
    x52 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    formula.Add(If(row52on, x52 * x52 == row52))
    x53 = Integer(*(formula.AddVar() for i in range(math.ceil(ROW_BITS/2))))
    formula.Add(If(row53on, x53 * x53 == row53))

    # Constraint: Row 6 is a multiple of 37.
    print('Generating row 6 run constraints...')
    row60, row60on, _, _ = row_var[(6,0)]
    row61, row61on, _, _ = row_var[(6,1)]
    row62, row62on, _, _ = row_var[(6,2)]
    row63, row63on, _, _ = row_var[(6,3)]
    formula.Add(If(row60on, row60 % Integer(37) == Integer(0)))
    formula.Add(If(row61on, row61 % Integer(37) == Integer(0)))
    formula.Add(If(row62on, row62 % Integer(37) == Integer(0)))
    formula.Add(If(row63on, row63 % Integer(37) == Integer(0)))

    # Constraint: Row 7 is a palindrome and a multiple of 23
    print('Generating row 7 run constraints...')
    row70, row70on, _, _ = row_var[(7,0)]
    row71, row71on, _, _ = row_var[(7,1)]
    row72, row72on, _, _ = row_var[(7,2)]
    row73, row73on, _, _ = row_var[(7,3)]
    formula.Add(If(row70on, And(IsPalindrome(row70), row70 % Integer(23) == 0)))
    formula.Add(If(row71on, And(IsPalindrome(row71), row71 % Integer(23) == 0)))
    formula.Add(If(row72on, And(IsPalindrome(row72), row72 % Integer(23) == 0)))
    formula.Add(If(row73on, And(IsPalindrome(row73), row73 % Integer(23) == 0)))

    # Constraint: Product of Row 8 digits ends in 1.
    print('Generating row 8 run constraints...')
    _, row80on, _, pod80 = row_var[(8,0)]
    _, row81on, _, pod81 = row_var[(8,1)]
    _, row82on, _, pod82 = row_var[(8,2)]
    _, row83on, _, pod83 = row_var[(8,3)]
    formula.Add(If(row80on, pod80 % Integer(10) == Integer(1)))
    formula.Add(If(row81on, pod81 % Integer(10) == Integer(1)))
    formula.Add(If(row82on, pod82 % Integer(10) == Integer(1)))
    formula.Add(If(row83on, pod83 % Integer(10) == Integer(1)))

    # Constraint: Row 9 is a multiple of 88.
    print('Generating row 9 run constraints...')
    row90, row90on, _, _ = row_var[(9,0)]
    row91, row91on, _, _ = row_var[(9,1)]
    row92, row92on, _, _ = row_var[(9,2)]
    row93, row93on, _, _ = row_var[(9,3)]
    formula.Add(If(row90on, row90 % Integer(88) == Integer(0)))
    formula.Add(If(row91on, row91 % Integer(88) == Integer(0)))
    formula.Add(If(row92on, row92 % Integer(88) == Integer(0)))
    formula.Add(If(row93on, row93 % Integer(88) == Integer(0)))

    # Constraint: Row 10 is 1 less than a palindrome
    print('Generating row 10 run constraints...')
    row100, row100on, _, _ = row_var[(10,0)]
    row101, row101on, _, _ = row_var[(10,1)]
    row102, row102on, _, _ = row_var[(10,2)]
    row103, row103on, _, _ = row_var[(10,3)]
    p100 = Integer(*(formula.AddVar() for i in range(ROW_BITS)))
    formula.Add(If(row100on, And(IsPalindrome(p100), p100 == row100 + Integer(1))))
    p101 = Integer(*(formula.AddVar() for i in range(ROW_BITS)))
    formula.Add(If(row101on, And(IsPalindrome(p101), p101 == row101 + Integer(1))))
    p102 = Integer(*(formula.AddVar() for i in range(ROW_BITS)))
    formula.Add(If(row102on, And(IsPalindrome(p102), p102 == row102 + Integer(1))))
    p103 = Integer(*(formula.AddVar() for i in range(ROW_BITS)))
    formula.Add(If(row103on, And(IsPalindrome(p103), p103 == row103 + Integer(1))))

    return formula

# Helper function for solution printing: convert a boolean list to an integer.
def bin_to_int(blist):
    result = 0
    for b in blist:
        result *= 2
        result += 1 if b else 0
    return result

def print_solution(sol, *extra_args):
    def solchr(x):
        if x == 10:
            return 'X'
        else:
            return x
    coords, value_bits = extra_args[0], extra_args[1]
    for r in coords:
        for c in coords:
            print(' {} '.format(solchr(bin_to_int([sol['v:{}:{}:{}'.format(r,c,i)] for i in range(value_bits)]))), end='')
        print('')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve Jane Street's Number Cross 4 puzzle")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    formula = encode()
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, [bin_to_int], extra_args=[COORDS, CELL_BITS])
