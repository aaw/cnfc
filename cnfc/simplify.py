# This module collects some common simplifications that can decrease the size of
# a CNF formula. So that generated extractors will still work on simplified
# formulas, we only use simplifications that can preserve logical equivalence
# and we never remove variables. In practice, the "never remove variables"
# condition just means that we don't reset the max variable in the DIMACS CNF
# file header, even though the variable may no longer appear in any clauses.

from .buffer import *
from collections import defaultdict
from functools import reduce

# Do any easy simplifications in two passes. This includes:
# (1) eliminating tautologies
# (2) removing duplicate literals from clauses
# (3) removing duplicate clauses
# (4) removing pure literals
def simplify(b):
    def hashlit(lit):
        return (lit * 1022201) % 64

    def sig(clause):
        bits = [1 << hashlit(lit) for lit in clause]
        return reduce(lambda x,y: x | y, bits, 0)

    new_b = b.__class__(maxvar=b.maxvar)
    signs = defaultdict(set)  # Maps var to lits seen
    sigs = set()
    possible_dups = set()
    for clause in b.AllClauses():
        # Check for tautology, suppress clause if so.
        abslits = sorted(clause, key=lambda x: abs(x))
        if any(plit == -nlit for (plit, nlit) in zip(abslits, abslits[1:])):
            continue
        # Remove duplicate literals from clause.
        lits = set(lit for lit in clause)
        # Register sign of variable seen (to check for pure lits at the end).
        for lit in lits:
            signs[abs(lit)].add(lit)
        sclause = tuple(lit for lit in lits)
        # Check for duplicate clause
        s = sig(sclause)
        if s in sigs:
            possible_dups.add(sclause)
        sigs.add(s)
        new_b.Append(sclause)
    pure_lits = set(next(iter(lits)) for (v, lits) in signs.items() if len(lits) == 1)

    # One final pass to remove pure literals and duplicate clauses
    final_b = b.__class__(maxvar=b.maxvar)
    for comment in b.AllComments():
        final_b.AddComment(comment)
    seen = {}
    for lit in pure_lits:
        final_b.Append((lit,))
    for clause in new_b.AllClauses():
        if clause in possible_dups:
            if seen.get(clause) is None:
                seen[clause] = True
            else:
                continue  # Suppress duplicate clauses
        if any(lit in pure_lits for lit in clause):
            continue
        final_b.Append(clause)

    return final_b

def propagate_units(b, max_iterations=None):
    if max_iterations is None:
        max_iterations = 2**10
    iterations = 0
    prev_unit_count = -1
    units = set()

    while len(units) > prev_unit_count:
        prev_unit_count = len(units)
        new_b = b.__class__(maxvar=b.maxvar)
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
        strengthened = 0
        for i, lit in enumerate(clauses[ci]):
            cc = list(clauses[ci])
            cc[i] = -cc[i]
            for si in find_subsumed(cc):
                st = strengthen(clauses[si], cc[i])
                occur[cc[i]].remove(si)
                clauses[si] = st
                strengthened += 1
        return strengthened

    while True:
        strengthened = sum(self_subsume(i) for i in range(len(clauses)))
        if strengthened == 0:
            break

    new_b = b.__class__(maxvar=b.maxvar)
    for comment in b.AllComments():
        new_b.AddComment(comment)
    for clause in clauses:
        new_b.Append(clause)
    return new_b
