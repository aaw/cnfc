from collections import defaultdict
import re

def dpll_search(num_vars, clauses):
    # Build watch lists and unit list.
    watches = defaultdict(list)
    units = set()
    for i, clause in enumerate(clauses):
        for lit in clause:
            watches[lit].append(i)
        if len(clause) == 1:
            units.add(clause[0])
        if len(clause) == 0:
            return False

    # Unit propagation
    while len(units) > 0:
        new_units = set()
        for unit in units:
            for clause_id in watches[unit]:
                clauses[clause_id] = None  # Tombstone
            for clause_id in watches[-unit]:
                if clauses[clause_id] is None: continue  # Already tombstoned
                clauses[clause_id] = [lit for lit in clauses[clause_id] if lit != -unit]
                if len(clauses[clause_id]) == 0: return False
                if len(clauses[clause_id]) == 1: new_units.add(clauses[clause_id][0])
        units = new_units

    # Pure literal elimination
    for var in range(1, num_vars+1):
        if len(watches[-var]) == 0 and len(watches[var]) > 0:
            for clause_id in watches[var]: clauses[clause_id] = None
        elif len(watches[var]) == 0 and len(watches[-var]) > 0:
            for clause_id in watches[-var]: clauses[clause_id] = None

    if len([clause for clause in clauses if clause is not None]) == 0: return True
    if len([clause for clause in clauses if clause is not None and len(clause) == 0]) > 0: return False

    false_clauses, true_clauses = clauses[:], clauses[:]

    # Set variable num_var to true in true_clauses
    for clause_id in watches[num_vars]:
        true_clauses[clause_id] = None  # Tombstone
    for clause_id in watches[-num_vars]:
        if clauses[clause_id] is None: continue  # Already tombstoned
        true_clauses[clause_id] = [lit for lit in clauses[clause_id] if lit != -num_vars]

    # Set variable num_var to false in false_clauses
    for clause_id in watches[num_vars]:
        if clauses[clause_id] is None: continue  # Already tombstoned
        false_clauses[clause_id] = [lit for lit in clauses[clause_id] if lit != num_vars]
    for clause_id in watches[-num_vars]:
        false_clauses[clause_id] = None

    # Clean up tombstoned clauses
    true_clauses = [clause for clause in true_clauses if clause is not None]
    false_clauses = [clause for clause in false_clauses if clause is not None]

    # Recurse
    return dpll_search(num_vars-1, true_clauses) or dpll_search(num_vars-1, false_clauses)


def Satisfiable(cnf):
    # Parse the DIMACS input file, do some light error-checking.
    header = None
    clauses = []
    max_var = 0
    for i, line in enumerate(cnf.split('\n')):
        if line.startswith('c'): continue
        if header is None:
            header = re.match(r'p cnf (\d+) (\d+)', line)
            if header is not None: continue
            if header is None: raise ValueError('Line {}: Unexpected input: "{}"'.format(i, line))
        lits = line.split()
        if len(lits) == 0: continue
        if lits[-1] != '0': raise ValueError('Expected 0 as clause terminator, got "{}"'.format(line))
        lits = lits[:-1]
        max_var = max(max_var, *(abs(int(x)) for x in lits))
        clauses.append([int(l) for l in lits])
    num_vars, num_clauses = (int(x) for x in header.groups())
    if len(clauses) != num_clauses:
        raise ValueError('Inconsistent clause count in header vs. file ({} vs. {})'.format(num_clauses, len(clauses)))
    if max_var > num_vars:
        raise ValueError('Inconsistent number of variables in header vs. file ({} vs. {})'.format(num_vars, max_var))

    return dpll_search(num_vars, clauses)
