from .model import Var, Literal, BooleanLiteral
from .buffer import Buffer, UnitClauses
from .extractor import generate_extractor
from .simplify import propagate_units

class Formula:
    def __init__(self, buffer=None):
        self.vars = {}
        self.buffer = Buffer() if buffer is None else buffer
        self.nextvar = 1

    def AddVar(self, name=None):
        if self.vars.get(name) is not None:
            raise ValueError('Variable already exists in formula')
        vid = self.nextvar
        if name is None:
            name = '_' + str(self.nextvar)
        else:
            self.buffer.AddComment("var {} : {}".format(vid, name))
        self.vars[name] = vid
        self.nextvar += 1
        return Var(name, vid)

    def AddVars(self, names):
        return (self.AddVar(name.strip()) for name in names.split(' '))

    def AddClause(self, *disjuncts):
        # Convert any BooleanLiterals to actual bools
        disjuncts = [(x.val if type(x) == BooleanLiteral else x) for x in  disjuncts]
        if any(b for b in disjuncts if b is True):
            return
        # Otherwise, any other bools are False and we can suppress them.
        self.buffer.Append(tuple(self.__raw_lit(x) for x in disjuncts if type(x) != bool))

    def Add(self, expr):
        for clause in expr.generate_cnf(self):
            self.AddClause(*clause)

    def PushCheckpoint(self):
        self.buffer.PushCheckpoint()

    def PopCheckpoint(self):
        self.buffer.PopCheckpoint()

    def WriteCNF(self, fd):
        self.buffer.Flush(fd)

    def WriteExtractor(self, fd, extractor_fn, extra_fns=None, extra_args=None):
        generate_extractor(fd, extractor_fn, extra_fns, extra_args)

    def __raw_lit(self, expr):
        if isinstance(expr, Var): return expr.vid
        elif isinstance(expr, Literal): return expr.sign*expr.var.vid
        elif isinstance(expr, BooleanLiteral): return expr.val
        else: raise ValueError("Expected Var, BooleanLiteral or Literal, got {}".format(expr))

class SimplifiedFormula(Formula):
    def __init__(self):
        self.units = UnitClauses()
        self.buffer = Buffer(visitors=[self.units])
        super(SimplifiedFormula, self).__init__(self.buffer)

    def WriteCNF(self, fd):
        self.buffer = propagate_units(self.buffer, self.units.units)
        # TODO: more preprocessing here: duplicate clause removal, subsumption test, etc.
        super(SimplifiedFormula, self).WriteCNF(fd)
