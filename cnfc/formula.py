from .model import Var, Literal, BooleanLiteral
from .buffer import *
from .extractor import generate_extractor
from .simplify import *
from .log import logger

# Given one of the various forms of variables/literals, return an integer
# representation of the underlying literal.
def raw_lit(expr):
    if isinstance(expr, Var): return expr.vid
    elif isinstance(expr, Literal): return expr.sign*expr.var.vid
    elif isinstance(expr, BooleanLiteral): return expr.val
    else: raise ValueError("Expected Var, BooleanLiteral or Literal, got {}".format(expr))

class Formula:
    def __init__(self, buffer_class=None):
        if buffer_class is None:
            buffer_class = MemoryBuffer
        self.vars = {}
        self.buffer = buffer_class()
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
        self.buffer.Append(tuple(raw_lit(x) for x in disjuncts if type(x) != bool))

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

    def Simplify(self):
        log = logger()
        log.info('Running basic simplifications...')
        self.buffer = simplify(self.buffer)
        log.info('Strengthening self-subsumed...')
        self.buffer = strengthen_self_subsumed(self.buffer)
        log.info('Propagating units...')
        self.buffer = propagate_units(self.buffer)
        log.info('Running basic simplifications again...')
        self.buffer = simplify(self.buffer)
        log.info('Done simplifying.')
