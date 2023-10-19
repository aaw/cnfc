from .buffer import Buffer, UnitClauses

def propagate_units(b, units, max_iterations=None):
    if max_iterations is None:
        max_iterations = 2**10
    iterations = 0
    while units:
        new_units = UnitClauses()
        new_b = Buffer(visitors=[new_units])
        for comment in b.AllComments():
            new_b.AddComment(comment)
        for clause in b.AllClauses():
            if any(lit for lit in clause if lit in units):
                continue
            new_clause = tuple(lit for lit in clause if -lit not in units)
            new_b.Append(new_clause)
        # Keep units so we retain their setting for solution extraction later.
        for unit in units:
            new_b.Append((unit,))
        units = new_units.units
        b = new_b
        iterations += 1
        if iterations >= max_iterations:
            break
    return b
