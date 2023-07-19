class Var:
    def __init__(self, name, vid):
        self.name = name
        self.vid = vid

class Formula:
    def __init__(self):
        self.vars = {}
        self.clauses = []
        self.nextvar = 1

    def AddVar(self, name):
        if self.vars.get(name) is not None:
            raise ValueError('Variable already exists in formula')
        vid = self.nextvar
        self.vars[name] = vid
        self.nextvar += 1
        return Var(name, vid)

    def AddVars(self, names):
        return (self.AddVar(name.strip()) for name in names.split(','))

    def AddClause(self, clause):
        pass

    def AddClauses(self, clauses):
        for clause in clauses:
            self.AddClause(clause)

class Eq:
    def __init__(self, *xs):
        pass

class IfThen:
    def __init__(self, x, y):
        pass

class Or:
    def __init__(self, *xs):
        pass

class And:
    def __init__(self, *xs):
        pass

class ExactlyKTrue:
    def __init__(self, k, *xs):
        pass

class AtMostKTrue:
    def __init__(self, k, *xs):
        pass

class AtLeastKTrue:
    def __init__(self, k, *xs):
        pass
