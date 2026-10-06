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
# unshaded run length. So we create a signed integer variable for each cell
# that represents its contents (0-9, or -1 to represent "shaded"). Then, for
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
from itertools import product

import argparse
import math

# 11 x 11 grid coordinates.
COORDS = list(range(11))
# Each row has at most 4 runs of unshaded cells.
RUNS = range(4)
# Cells contain digits 0-9, or -1 to indicate shading.
SHADED = Integer(-1)
CELL_BITS = Integer.bits_needed_for_range(-1, 9)
MAX_ROW_VALUE = 99999888776
ROW_BITS = Integer.bits_needed_for_range(0, MAX_ROW_VALUE)
ROOT_BITS = Integer.bits_needed_for_range(0, math.isqrt(MAX_ROW_VALUE))
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

    # Constraint: Shaded cells are all set to -1.
    for i in shaded:
        conjuncts.append(cell_var[(row,i)] == SHADED)

    # We don't need to enforce "Every run is at least two cells" here, since
    # it's already enforced implicitly by the row pattern generation.
    for start, end in runs:
        # Constraint: No leading zeros in a run.
        conjuncts.append(cell_var[(row,start)] != 0)
        # Constraint: No shaded cells in a run.
        for i in range(start, end+1):
            conjuncts.append(cell_var[(row,i)] != SHADED)

    # Connect each run's value, sum of digits, and product of digits to the
    # cells in the run. The sum and product of digits are only needed for
    # rows 3 and 8 in the puzzle, respectively.
    for i in RUNS:
        val, exists, digit_sum, digit_product = row_var[(row,i)]
        if i >= len(runs):
            conjuncts.append(~exists)
            continue
        start, end = runs[i]
        digits = [cell_var[(row,j)] for j in range(start, end+1)]
        conjuncts.append(exists)
        number = digits[0]
        for digit in digits[1:]:
            number = number * 10 + digit
        conjuncts.append(val == number)
        conjuncts.append(digit_sum == sum(digits))
        conjuncts.append(digit_product == math.prod(digits))

    return And(*conjuncts)

# All prime powers p^q (p, q prime) with 2 to 11 digits.
def prime_powers():
    def prime(a):
        return a >= 2 and all(a % x != 0 for x in range(2, math.isqrt(a) + 1))
    # 316228 is the first number whose square is 12 digits, so we only need to consider prime
    # bases below that.
    primes = [x for x in range(316228) if prime(x)]
    # The first 12-digit power of 2 is 2**37, so we only need to consider exponents below that.
    exps = [x for x in range(37) if prime(x)]
    # The final set of possible prime powers has 27981 elements and only takes a second or
    # two to calculate.
    return [x**y for x in primes for y in exps if 10 <= x**y < 10**11]

# Encodes the Number Cross 4 puzzle into a Formula.
def encode():
    formula = Formula(FileBuffer)

    # Cell vars are integers representing the choice of number or shaded for any
    # cell in the grid. v:r:c:i is the ith bit of the number in row r, column c.
    cell_var = {}
    for r in COORDS:
        for c in COORDS:
            cell = Integer(formula.AddVars(f'v:{r}:{c}', CELL_BITS))
            formula.Add(SHADED <= cell <= 9)
            cell_var[(r,c)] = cell

    # Row vars are tuples representing the integer value of a run, whether that
    # run exists in a row, and the sum and product of a run. They're indexed by
    # a (row, run) tuple, where run ranges from 0 to 3.
    row_var = {}
    for j in RUNS:
        for r in COORDS:
            # n:r:j:i is the ith bit of the jth run in row r.
            val = Integer(formula.AddVars(f'n:{r}:{j}', ROW_BITS))
            formula.Add(val >= 0)
            # b:r:j is true iff there is a jth run in row r.
            exists = formula.AddVar(f'b:{r}:{j}')
            # sod:r:j:i is the ith bit of the sum of digits of the jth run in row r.
            # The sum of all numbers in a row is at most 99.
            rsum = Integer(formula.AddVars(f'sod:{r}:{j}', Integer.bits_needed_for_range(0, 99)))
            formula.Add(rsum >= 0)
            # pod:r:j:i is the ith bit of the product of digits of the jth run in row r.
            rprod = Integer(formula.AddVars(f'pod:{r}:{j}', ROW_BITS))
            formula.Add(rprod >= 0)
            # row_var is a tuple of (value, exists, sum of digits, product of digits)
            row_var[(r,j)] = (val, exists, rsum, rprod)

    # Constraint: No two shaded cells can share an edge. We already enforce this
    # implicitly for adjacent cells in a row when generating masks, so we only
    # need to enforce it explicitly for columns here.
    for c in COORDS:
        for r1, r2 in zip(COORDS, COORDS[1:]):
            formula.Add(Or(cell_var[(r1,c)] != SHADED, cell_var[(r2,c)] != SHADED))

    # Constraint: Each row matches some valid mask of shaded cells, each run in
    # a row is connected to individual cell values appropriately.
    for row in COORDS:
        print(f'Generating row {row} cell constraints...')
        formula.Add(Or(*(generate_mask_constraints(row, mask, cell_var, row_var) for mask in row_patterns())))

    # Constraint: adjacent unshaded cells contain the same digit if they're in
    # the same region and different digits if they're in different regions.
    neighbors = ([((r,c), (r,c+1)) for r in COORDS for c in COORDS[:-1]] +
                 [((r,c), (r+1,c)) for r in COORDS[:-1] for c in COORDS])
    for same in (True, False):
        for (r1,c1), (r2,c2) in neighbors:
            if (BOARD[r1][c1] == BOARD[r2][c2]) != same: continue
            x, y = cell_var[(r1,c1)], cell_var[(r2,c2)]
            formula.Add(Or(x == SHADED, y == SHADED, x == y if same else x != y))

    # At this point, we've connected all cell vars to row vars and asserted all
    # constraints about individual cell values and adjacent cell values. So we
    # can now focus on constraints about the runs in each row, most of which are
    # algebraic.

    def is_square(n):
        root = Integer(*(formula.AddVar() for _ in range(ROOT_BITS)))
        formula.Add(root >= 0)
        return root * root == n

    # Row 2 is the trickiest run constraint, since you can encode "not a prime" easily
    # with SAT but it's difficult to encode "is a prime". Maybe there's a simple
    # algebraic test for a prime raised to a prime that I don't know about using some
    # variant of Fermat's little theorem, but since I don't know one and prime powers
    # are relatively sparse, I'm just going to enumerate all prime powers that are
    # less than 12 digits and test against those explicitly in a big disjunction.
    ptop = prime_powers()

    # Each row's constraint, applied to every run in the row. Each constraint
    # takes the run's value, sum of digits, and product of digits.
    run_constraints = [
        # Row 0 is a square.
        lambda n, sod, pod: is_square(n),
        # Row 1 is one more than a palindrome.
        lambda n, sod, pod: IsPalindrome(n - 1),
        # Row 2 is a prime raised to a prime.
        lambda n, sod, pod: Or(*(n == x for x in ptop)),
        # Sum of Row 3 digits is 7.
        lambda n, sod, pod: sod == 7,
        # Row 4 is a Fibonacci number.
        # Uses Gessel's test: n is a Fibonacci number iff 5n^2 + 4 or 5n^2 - 4 is a square.
        lambda n, sod, pod: Or(is_square(5*n*n + 4), is_square(5*n*n - 4)),
        # Row 5 is a square.
        lambda n, sod, pod: is_square(n),
        # Row 6 is a multiple of 37.
        lambda n, sod, pod: n % 37 == 0,
        # Row 7 is a palindrome and a multiple of 23.
        lambda n, sod, pod: And(IsPalindrome(n), n % 23 == 0),
        # Product of Row 8 digits ends in 1.
        lambda n, sod, pod: pod % 10 == 1,
        # Row 9 is a multiple of 88.
        lambda n, sod, pod: n % 88 == 0,
        # Row 10 is 1 less than a palindrome.
        lambda n, sod, pod: IsPalindrome(n + 1),
    ]
    for row, constraint in enumerate(run_constraints):
        print(f'Generating row {row} run constraints...')
        for j in RUNS:
            n, exists, sod, pod = row_var[(row,j)]
            formula.Add(If(exists, constraint(n, sod, pod)))

    return formula

def print_solution(sol, *extra_args):
    def solchr(x):
        if x == -1:
            return 'X'
        else:
            return x
    coords = extra_args[0]
    for r in coords:
        for c in coords:
            print(' {} '.format(solchr(sol.integer('v:{}:{}'.format(r,c)))), end='')
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
        formula.WriteExtractor(f, print_solution, extra_args=[COORDS])
