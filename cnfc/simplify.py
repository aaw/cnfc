from .buffer import *

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
