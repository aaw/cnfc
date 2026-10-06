from itertools import combinations
import math

from .model import *

def IsPalindrome(num, base=10):
    digits = []

    max_digits = math.floor(math.log(2**len(num) - 1, base)) + 1
    for i in range(max_digits):
        digits.append(num % Integer(base))
        num = num // Integer(base)

    disjuncts = []
    for i in range(max_digits):
        # Assert digits up to & including index i form a palindrome and the rest are all 0.
        conjuncts = []
        for j in range((i+1)//2):
            conjuncts.append(digits[j] == digits[i-j])
        # Last digit of a 2+ digit palindrome can't be 0, that would mean we match a leading zero.
        if i > 0:
            conjuncts.append(digits[i] != Integer(0))
        for d in digits[i+1:]:
            conjuncts.append(d == Integer(0))
        disjuncts.append(And(*conjuncts))

    return Or(*disjuncts)

def Max(*args):
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        args = list(args[0])
    else:
        args = list(args)
    assert(len(args) > 1)
    while len(args) > 1:
        a, b = args.pop(), args.pop()
        args.append(TupleMax(a,b))
    return args[0]

def Min(*args):
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        args = list(args[0])
    else:
        args = list(args)
    assert(len(args) > 1)
    while len(args) > 1:
        a, b = args.pop(), args.pop()
        args.append(TupleMin(a,b))
    return args[0]

# True iff no two arguments are equal. If you know every argument's value lies
# in values, passing it usually gives a smaller encoding: one "at most one
# argument equals v" constraint per value instead of one constraint per pair.
# values is only an encoding hint; it doesn't constrain the arguments.
def AllDifferent(*args, values=None):
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        args = list(args[0])
    if values is None:
        return And(*(x != y for x, y in combinations(args, 2)))
    return And(*(NumTrue(*(x == v for x in args)) <= 1 for v in values))
