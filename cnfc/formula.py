from model import Var, Literal
from buffer import Buffer

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
    def AddClause(self, *expr):
        # TODO: ensure all variables exist in self.vars
        if len(expr) > 1:
            def raw_lit(expr):
                if isinstance(expr, Var): return expr.vid
                elif isinstance(expr, Literal): return expr.sign*expr.var.vid
                else: raise ValueError("Expected Var or Literal, got {}".format(expr))
            self.buffer.Append(tuple(raw_lit(x) for x in expr))
        else:
            for clause in expr[0].generate_cnf():
                self.buffer.Append(tuple(lit.sign*lit.var.vid for lit in clause))

    def WriteCNF(self, fd):
        self.buffer.Flush(fd)
