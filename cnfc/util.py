from collections import deque

# Generator wrapper, allows simple access to a generator plus a return value.
# Pattern described here: https://stackoverflow.com/a/34073559/14236095.
class Generator:
    def __init__(self, gen):
        self.gen = gen

    def __iter__(self):
        self.result = yield from self.gen

# Given one of the various forms of variables/literals, return an integer
# representation of the underlying literal.
def raw_lit(expr):
    if isinstance(expr, Var): return expr.vid
    elif isinstance(expr, Literal): return expr.sign*expr.var.vid
    elif isinstance(expr, BooleanLiteral): return expr.val
    else: raise ValueError("Expected Var, BooleanLiteral or Literal, got {}".format(expr))

# When you chain together a large number of operands in an associative operation
# the resulting parse tree is deeply nested. For example, sum(x for x in y)
# generates TupleAdd(TupleAdd(TupleAdd(...))). Using such a parse tree as-is and
# evaluting the n-1 operations on n operands one-by-one has at least two
# drawbacks:
# 1. It's easy to hit the max recursion limit (default: 1000) when analyzing or
#    evaluating these trees.
# 2. We get bad bounds on the number of bits required for the result of several
#    operations if we consider them one-by-one: for x-bit operands, you need
#    x+1 bits for the sum of two, so O(x*n) for n sums. But you can get by with
#    O(x*log n) for the sum of n by arranging the sum in a balanced tree.
#
# These next two functions let us gather all operands for a nested associative
# operation and then reduce them in a balanced tree.

def gather_common_operands(clazz, args):
    result = []
    queue = deque(args)
    while queue:
        arg = queue.popleft()
        if arg.__class__ != clazz:
            result.append(arg)
        else:
            queue.extend(arg.args)
    return result

def reduce_evaluated(reducer, args, formula):
    while len(args) > 1:
        reduced = []
        for i in range(0, len(args) - 1, 2):
            gen = Generator(reducer(formula, args[i], args[i+1]))
            for clause in gen:
                formula.AddClause(*clause)
            reduced.append(gen.result)
        if len(args) % 2 == 1:
            reduced.append(args[-1])
        args = reduced
    return args[0]
