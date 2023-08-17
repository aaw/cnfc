from .model import Var, Literal
from .buffer import Buffer

class Formula:
    def __init__(self):
        self.vars = {}
        self.buffer = Buffer()
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
        return (self.AddVar(name.strip()) for name in names.split(' '))

    def AddClause(self, *disjuncts):
        self.buffer.Append(tuple(self.__raw_lit(x) for x in disjuncts))

    # TODO: perform light optimizations like removing duplicate literals,
    # suppressing tautologies, and supressing duplicate clauses
    def Add(self, expr):
        for clause in expr.generate_cnf(self):
            self.buffer.Append(tuple(self.__raw_lit(x) for x in clause))

    def PushCheckpoint(self):
        self.buffer.PushCheckpoint()

    def PopCheckpoint(self):
        self.buffer.PopCheckpoint()

    def WriteCNF(self, fd):
        self.buffer.Flush(fd)

    def __raw_lit(self, expr):
        if isinstance(expr, Var): return expr.vid
        elif isinstance(expr, Literal): return expr.sign*expr.var.vid
        else: raise ValueError("Expected Var or Literal, got {}".format(expr))
