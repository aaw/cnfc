from .millisat import parse_dimacs, Solver

import io

def write_cnf_to_string(f):
    out = io.StringIO()
    f.WriteCNF(out)
    final = io.StringIO()
    out.seek(0)
    for line in out:
        if line.startswith('c '): continue
        final.write(line)
    final.seek(0)
    return final.read()

def satisfiable(s):
    num_vars, clauses = parse_dimacs(s)
    return Solver().solve(num_vars, clauses) is not False

class SatTestCase:
    def assertSat(self, formula):
        self.assertTrue(satisfiable(write_cnf_to_string(formula)))

    def assertUnsat(self, formula):
        self.assertFalse(satisfiable(write_cnf_to_string(formula)))
