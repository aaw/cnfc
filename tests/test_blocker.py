import os
import subprocess
import sys
import tempfile
import unittest

from cnfc import Formula
from cnfc.millisat import Solver, parse_dimacs


def run_blocker(formula, variables, solution):
    with tempfile.TemporaryDirectory() as directory:
        cnf_path = os.path.join(directory, 'formula.cnf')
        blocker_path = os.path.join(directory, 'blocker.py')
        solution_path = os.path.join(directory, 'solution.txt')
        with open(cnf_path, 'w') as f:
            formula.WriteCNF(f)
        with open(blocker_path, 'w') as f:
            formula.WriteBlocker(f, variables)
        with open(solution_path, 'w') as f:
            f.write(solution)
        return subprocess.run(
            [sys.executable, '-I', blocker_path, cnf_path, solution_path],
            capture_output=True, text=True, timeout=5
        )


class TestBlocker(unittest.TestCase):
    def test_blocking_ignores_unselected_variables(self):
        f = Formula()
        x, y = f.AddVars('x y')
        auxiliary = f.AddVar()
        f.AddClause(x, y)
        f.AddClause(auxiliary, ~auxiliary)
        result = run_blocker(f, [x, y],
                             f's SATISFIABLE\nv {x.vid} {-y.vid} {-auxiliary.vid} 0\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        num_vars, clauses = parse_dimacs(result.stdout)

        self.assertFalse(Solver().solve(num_vars, clauses + [(x.vid,), (-y.vid,), (-auxiliary.vid,)]))
        self.assertFalse(Solver().solve(num_vars, clauses + [(x.vid,), (-y.vid,), (auxiliary.vid,)]))
        self.assertIsNot(Solver().solve(num_vars, clauses + [(-x.vid,), (y.vid,)]), False)
        self.assertFalse(Solver().solve(num_vars, clauses + [(-x.vid,), (-y.vid,)]))

        header = next(line for line in result.stdout.splitlines() if line.startswith('p '))
        self.assertEqual(int(header.split()[3]), len(clauses))

    def test_all_false_solution_can_be_blocked(self):
        f = Formula()
        x, y = f.AddVars('x y')
        f.AddClause(~x, ~y)
        result = run_blocker(f, [x, y],
                             f'v {-x.vid}\nv   {-y.vid}   0\ns SATISFIABLE\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        num_vars, clauses = parse_dimacs(result.stdout)

        self.assertFalse(Solver().solve(num_vars, clauses + [(-x.vid,), (-y.vid,)]))
        self.assertIsNot(Solver().solve(num_vars, clauses + [(x.vid,), (-y.vid,)]), False)
        self.assertIsNot(Solver().solve(num_vars, clauses + [(-x.vid,), (y.vid,)]), False)

    def test_unsatisfiable_result_cannot_be_blocked(self):
        f = Formula()
        x = f.AddVar('x')
        f.Add(x)
        result = run_blocker(f, [x], 's UNSATISFIABLE\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')

    def test_missing_selected_assignment_is_rejected(self):
        f = Formula()
        x, y = f.AddVars('x y')
        f.AddClause(x, y)
        result = run_blocker(f, [x, y], f's SATISFIABLE\nv {x.vid} 0\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')

    def test_empty_selection_blocks_every_solution(self):
        f = Formula()
        x = f.AddVar('x')
        f.Add(x)
        result = run_blocker(f, [], f's SATISFIABLE\nv {x.vid} 0\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        num_vars, clauses = parse_dimacs(result.stdout)
        self.assertFalse(Solver().solve(num_vars, clauses))
