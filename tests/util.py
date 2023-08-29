from .dpll import Satisfiable

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

class SatTestCase:
    def assertSat(self, formula):
        self.assertTrue(Satisfiable(write_cnf_to_string(formula)))

    def assertUnsat(self, formula):
        self.assertFalse(Satisfiable(write_cnf_to_string(formula)))
