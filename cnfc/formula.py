from model import Var
from cache import Cache

class Formula:
    def __init__(self):
        self.vars = {}
        self.cache = Cache()
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

    def AddClause(self, clause):
        # TODO: ensure all variables exist in self.vars
        pass

    def AddClauses(self, clauses):
        for clause in clauses:
            self.AddClause(clause)
