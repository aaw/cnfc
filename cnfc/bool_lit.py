class BooleanLiteral:
    def __init__(self, val):
        assert type(val) == bool
        self.val = val

    def __repr__(self):
        return 'BooleanLiteral({})'.format(self.val)

    def __invert__(self):
        return BooleanLiteral(not self.val)

    def generate_var(self, formula):
        return self

    def generate_cnf(self, formula):
        yield (self,)

def zero_pad(x, y):
    if len(x) == len(y): return x,y
    if len(x) < len(y):
        return [BooleanLiteral(False) for i in range(len(y) - len(x))] + x, y
    else:  # len(x) > len(y)
        return x, [BooleanLiteral(False) for i in range(len(x) - len(y))] + y

def lpad(x, n):
    return [BooleanLiteral(False) for i in range(n)] + x

def rpad(x, n):
    return x + [BooleanLiteral(False) for i in range(n)]
