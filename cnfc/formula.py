from model import Var
from buffer import Buffer

def literal(expr):
    if isinstance(expr, Not) and isinstance(expr.expr, Var):
        return -expr.expr.vid
    elif isinstance(expr, Var):
        return expr.vid
    else:
        raise ValueError("{} can't be converted to a literal".format(expr))

class Formula:
    def __init__(self):
        self.vars = {}
        self.buffer = Buffer()
        self.clauses = []
        self.nextvar = 1

    def AddVar(self, name=None):
        if name is None:
            name = '_' + str(self.nextvar)
        if self.vars.get(name) is not None:
            raise ValueError('Variable already exists in formula')
        vid = self.nextvar
        self.vars[name] = vid
        self.nextvar += 1
        return Var(name, vid)

    def AddVars(self, names):
        return (self.AddVar(name.strip()) for name in names.split(','))

    # TODO: perform light optimizations like removing duplicate literals,
    # suppressing tautologies, and supressing duplicate clauses
    def AddClause(self, clause):
        # TODO: ensure all variables exist in self.vars
        buffer.Append(tuple(literal(expr) for expr in clause))

    def AddClauses(self, clauses):
        for clause in clauses:
            self.AddClause(clause)

    def WriteCNF(self, fd):
        self.buffer.Flush(fd)
