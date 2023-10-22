from .buffer import *
from collections import defaultdict

def propagate_units(b, max_iterations=None):
    if max_iterations is None:
        max_iterations = 2**10
    iterations = 0
    prev_unit_count = -1
    units = set()

    while len(units) > prev_unit_count:
        prev_unit_count = len(units)
        new_b = b.__class__()
        for comment in b.AllComments():
            new_b.AddComment(comment)
        for clause in b.AllClauses():
            if len(clause) > 1 and any(lit for lit in clause if lit in units):
                continue
            new_clause = tuple(lit for lit in clause if -lit not in units)
            if len(new_clause) == 1:
                units.add(new_clause[0])
            new_b.Append(new_clause)
        b = new_b
        iterations += 1
        if iterations >= max_iterations:
            break
    return b

def strengthen_self_subsumed(b):
    # Map literals to a list of clause indices where they occur.
    occur = defaultdict(list)
    clauses = []
    for clause in b.AllClauses():
        clauses.append(clause)
        for lit in clause:
            occur[lit].append(len(clauses)-1)

    # Is c1 a strict subset of c2?
    def subset(c1, c2):
        if len(c1) >= len(c2): return False
        for lit in c1:
            if lit not in c2: return False
        return True

    # Find clauses that are subsumed by the given clause.
    def find_subsumed(clause):
        # l is the lit in clause with the shortest occur list.
        l = clause[0]
        for lit in clause[1:]:
            if len(occur[lit]) < len(occur[l]):
                l = lit

        for i in occur[l]:
            if clauses[i] != clause and subset(clause, clauses[i]):
                yield i

    def strengthen(clause, lit):
        return tuple(l for l in clause if l != lit)

    def self_subsume(ci):
        any_strengthened = False
        for i, lit in enumerate(clauses[ci]):
            cc = list(clauses[ci])
            cc[i] = -cc[i]
            for si in find_subsumed(cc):
                st = strengthen(clauses[si], cc[i])
                occur[cc[i]].remove(si)
                clauses[si] = st
                any_strengthened = True
        return any_strengthened

    while True:
        if not any(self_subsume(i) for i in range(len(clauses))):
            break

    new_b = b.__class__()
    for comment in b.AllComments():
        new_b.AddComment(comment)
    for clause in clauses:
        new_b.Append(clause)
    return new_b
