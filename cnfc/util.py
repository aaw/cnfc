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
