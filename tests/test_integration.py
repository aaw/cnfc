"""Integration tests that run example scripts end-to-end.

These tests:
1. Generate CNF + extractor by running the example script
2. Solve the CNF using millisat
3. Run the extractor to produce output
4. Validate the output
"""

import os
import re
import subprocess
import sys
import tempfile
import unittest
from itertools import combinations

# Path to the examples directory
EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'examples')
MILLISAT_PATH = os.path.join(os.path.dirname(__file__), '..', 'cnfc', 'millisat.py')


def run_example(example_name, args):
    """Run an example script to generate CNF and extractor files.

    Args:
        example_name: Name of the example (e.g., 'xkcd287')
        args: List of command-line arguments to pass to the example

    Returns:
        subprocess.CompletedProcess result
    """
    example_path = os.path.join(EXAMPLES_DIR, example_name, f'{example_name}.py')

    result = subprocess.run(
        [sys.executable, example_path] + args,
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"Example {example_name} failed: {result.stderr}")
    return result


def solve_cnf(cnf_path, solver_output_path):
    """Solve a CNF file using millisat and write output to file.

    Args:
        cnf_path: Path to DIMACS CNF file
        solver_output_path: Path to write solver output
    """
    result = subprocess.run(
        [sys.executable, MILLISAT_PATH, cnf_path],
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.returncode not in (10, 20):
        raise RuntimeError(f"Solver failed: {result.stderr}")
    # Write combined stdout to file (millisat outputs both 'v' lines and 's' line to stdout)
    with open(solver_output_path, 'w') as f:
        f.write(result.stdout)


def run_extractor(extractor_path, cnf_path, solver_output_path):
    """Run the extractor script to get the solution.

    Args:
        extractor_path: Path to the generated extractor script
        cnf_path: Path to the CNF file
        solver_output_path: Path to file containing solver output

    Returns:
        String output from the extractor
    """
    result = subprocess.run(
        [sys.executable, extractor_path, cnf_path, solver_output_path],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode != 0:
        if result.returncode != 1 or result.stdout.strip() != 'UNSATISFIABLE' or result.stderr:
            raise RuntimeError(f"Extractor failed: {result.stderr}")
    return result.stdout + result.stderr


class TestExamplesIntegration(unittest.TestCase):
    """Integration tests for example scripts."""

    def run_example_end_to_end(self, example_name, example_args):
        """Run an example end-to-end and return the extractor output.

        Args:
            example_name: Name of the example
            example_args: Function that takes (cnf_path, extractor_path) and returns args list

        Returns:
            String output from the extractor
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            cnf_path = os.path.join(tmpdir, 'out.cnf')
            extractor_path = os.path.join(tmpdir, 'extractor.py')
            solver_output_path = os.path.join(tmpdir, 'solver_output.txt')

            # Generate CNF and extractor
            args = example_args(cnf_path, extractor_path)
            run_example(example_name, args)

            # Solve CNF
            solve_cnf(cnf_path, solver_output_path)

            # Run extractor
            return run_extractor(extractor_path, cnf_path, solver_output_path)

    def test_scheduling(self):
        output = run_example('scheduling', []).stdout
        self.assertTrue(output.strip())
        self.assertNotIn('UNSATISFIABLE', output)

    def test_six_variable_logic_puzzle(self):
        output = self.run_example_end_to_end(
            'six-variable-logic-puzzle',
            lambda cnf, ext: [cnf, ext]
        )
        values = dict((name, int(value)) for name, value in re.findall(r'([A-F]) = (\d+)', output))
        self.assertEqual(set(values), {'A', 'B', 'C', 'D', 'E', 'F'})
        self.assertEqual(len(set(values.values())), 6)
        for value in values.values():
            self.assertGreaterEqual(value, 1)
            self.assertLessEqual(value, 10)

        a,b,c,d,e,f = [values[name] for name in 'ABCDEF']
        self.assertEqual(b - d, 2)
        self.assertEqual(f + a, 11)
        self.assertLess(d, a)
        self.assertLess(a, c)
        self.assertEqual(c - a, 1)
        for first, second in combinations(values.values(), 2):
            self.assertNotEqual(first + second, 14)
            self.assertNotEqual(first + second, 5)

    def test_superpermutation_three_symbols(self):
        output = self.run_example_end_to_end(
            'superpermutation',
            lambda cnf, ext: ['3', '9', cnf, ext]
        )
        word = output.strip()
        self.assertEqual(len(word), 9)
        self.assertEqual(set(word), {'1', '2', '3'})
        self.assertIn('123', word)
        self.assertIn('132', word)
        self.assertIn('213', word)
        self.assertIn('231', word)
        self.assertIn('312', word)
        self.assertIn('321', word)

    def test_superpermutation_eight_positions_is_too_short(self):
        output = self.run_example_end_to_end(
            'superpermutation',
            lambda cnf, ext: ['3', '8', cnf, ext]
        )
        self.assertEqual(output.strip(), 'UNSATISFIABLE')

    def test_trifference_four_words(self):
        output = self.run_example_end_to_end(
            'trifference',
            lambda cnf, ext: ['2', '4', cnf, ext]
        )
        self.assertTrue(output.strip().startswith('{'))
        self.assertTrue(output.strip().endswith('}'))
        words = output.strip()[1:-1].split(', ')
        self.assertEqual(len(words), 4)
        self.assertEqual(len(set(words)), 4)
        for word in words:
            self.assertEqual(len(word), 2)
            self.assertTrue(set(word) <= {'0', '1', '2'})
        for first, second, third in combinations(words, 3):
            different_first = len({first[0], second[0], third[0]}) == 3
            different_second = len({first[1], second[1], third[1]}) == 3
            self.assertTrue(different_first or different_second)

    def test_trifference_five_words_is_impossible(self):
        output = self.run_example_end_to_end(
            'trifference',
            lambda cnf, ext: ['2', '5', cnf, ext]
        )
        self.assertEqual(output.strip(), 'UNSATISFIABLE')

    def test_no_three_in_line(self):
        output = self.run_example_end_to_end(
            'no-three-in-line',
            lambda cnf, ext: ['4', cnf, ext]
        )
        rows = [line.split('───') for line in output.splitlines() if '●' in line or '┼' in line]
        self.assertEqual(len(rows), 4)
        positions = []
        for r, row in enumerate(rows):
            self.assertEqual(len(row), 4)
            for c, cell in enumerate(row):
                self.assertIn(cell, ['●', '┼'])
                if cell == '●':
                    positions.append((r, c))
        self.assertEqual(len(positions), 8)
        for (r1,c1), (r2,c2), (r3,c3) in combinations(positions, 3):
            # Equal slopes mean the three points lie on a line.
            self.assertNotEqual((r2-r1)*(c3-c1), (r3-r1)*(c2-c1))

    def test_strongly_regular_graph_five_cycle(self):
        output = self.run_example_end_to_end(
            'strongly-regular-graph',
            lambda cnf, ext: ['5', '2', '0', '1', cnf, ext]
        )
        edges = [(int(u), int(v)) for u, v in re.findall(r'\{(\d+),(\d+)\}', output)]
        self.assertEqual(len(edges), 5)
        self.assertEqual(len(set(edges)), 5)
        neighbors = [set() for _ in range(5)]
        for u, v in edges:
            self.assertIn(u, range(5))
            self.assertIn(v, range(5))
            self.assertNotEqual(u, v)
            neighbors[u].add(v)
            neighbors[v].add(u)
        for adjacent in neighbors:
            self.assertEqual(len(adjacent), 2)
        for u, v in combinations(range(5), 2):
            common_neighbors = neighbors[u] & neighbors[v]
            if v in neighbors[u]:
                self.assertEqual(len(common_neighbors), 0)
            else:
                self.assertEqual(len(common_neighbors), 1)

    def test_strongly_regular_graph_odd_degree_sum_is_impossible(self):
        output = self.run_example_end_to_end(
            'strongly-regular-graph',
            lambda cnf, ext: ['5', '3', '0', '1', cnf, ext]
        )
        self.assertEqual(output.strip(), 'UNSATISFIABLE')

    def test_minesweeper_four_by_four_is_too_small(self):
        # Nine numbered cells leave seven mines, so an 8 cannot appear.
        output = self.run_example_end_to_end(
            'minesweeper',
            lambda cnf, ext: ['1', '4', cnf, ext]
        )
        self.assertEqual(output.strip(), 'UNSATISFIABLE')

    def test_cuboid_three_bits_has_no_solution(self):
        output = self.run_example_end_to_end(
            'cuboid',
            lambda cnf, ext: ['3', cnf, ext]
        )
        self.assertEqual(output.strip(), 'UNSATISFIABLE')

    def test_complex_matrix_one_product_is_insufficient(self):
        output = self.run_example_end_to_end(
            'complex-matrix-multiplications',
            lambda cnf, ext: ['1', cnf, ext]
        )
        self.assertEqual(output.strip(), 'UNSATISFIABLE')

    def test_matrix_multiplications_two_by_two(self):
        output = self.run_example_end_to_end(
            'matrix-multiplications',
            lambda cnf, ext: ['2', '8', cnf, ext]
        )
        a = [[1, 2], [3, 4]]
        b = [[5, 6], [7, 8]]
        products = {}
        for number, a_terms, b_terms in re.findall(r'm_(\d+) = \((.*)\) \* \((.*)\)', output):
            a_sum = 0
            for sign, row, col in re.findall(r'(-?)a_\{([12]),([12])\}', a_terms):
                value = a[int(row)-1][int(col)-1]
                a_sum += -value if sign == '-' else value
            b_sum = 0
            for sign, row, col in re.findall(r'(-?)b_\{([12]),([12])\}', b_terms):
                value = b[int(row)-1][int(col)-1]
                b_sum += -value if sign == '-' else value
            products[int(number)] = a_sum * b_sum
        self.assertEqual(set(products), set(range(8)))

        result = {}
        for row, col, terms in re.findall(r'C_\{([12]),([12])\} = (.*)', output):
            total = 0
            for sign, number in re.findall(r'(-?)m_(\d+)', terms):
                value = products[int(number)]
                total += -value if sign == '-' else value
            result[(int(row), int(col))] = total
        self.assertEqual(result, {(1,1): 19, (1,2): 22, (2,1): 43, (2,2): 50})

    def test_tournament_scheduling(self):
        output = self.run_example_end_to_end(
            'tournament-scheduling',
            lambda cnf, ext: [cnf, ext, '--teams', '4', '--rounds', '2', '--players', '8']
        )
        pattern = (r'Round (\d+): \((\d+), (\d+)\) vs \((\d+), (\d+)\), '
                   r'\((\d+), (\d+)\) vs \((\d+), (\d+)\)')
        rounds = re.findall(pattern, output)
        self.assertEqual([int(round_[0]) for round_ in rounds], [1, 2])
        teammates = set()
        opponents = set()
        for round_ in rounds:
            players = [int(player) for player in round_[1:]]
            self.assertEqual(set(players), set(range(1, 9)))
            teams = [players[0:2], players[2:4], players[4:6], players[6:8]]
            for team in teams:
                pair = tuple(sorted(team))
                self.assertNotIn(pair, teammates)
                teammates.add(pair)
            for first, second in [(teams[0], teams[1]), (teams[2], teams[3])]:
                for player1 in first:
                    for player2 in second:
                        pair = tuple(sorted((player1, player2)))
                        self.assertNotIn(pair, opponents)
                        opponents.add(pair)

    def test_boggle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            words_path = os.path.join(tmpdir, 'words.txt')
            with open(words_path, 'w') as f:
                f.write('cat\ncar\n')
            output = self.run_example_end_to_end(
                'boggle',
                lambda cnf, ext: ['2', '--dice', 'classic', '--rows', '2', '--cols', '2',
                                 '--words', words_path, cnf, ext]
            )
        self.assertIn('CAT: 1 points', output)
        self.assertIn('CAR: 1 points', output)
        self.assertIn('Total score: 2', output)
        board = [row.split() for row in output.strip().splitlines()[-2:]]
        self.assertEqual(len(board[0]), 2)
        self.assertEqual(len(board[1]), 2)
        # Every cell in a 2x2 board touches every other cell, so both words exist.
        self.assertEqual(set(board[0] + board[1]), {'C', 'A', 'T', 'R'})

    def test_xkcd287(self):
        """Test the xkcd287 Diophantine equation example."""
        output = self.run_example_end_to_end(
            'xkcd287',
            lambda cnf, ext: [cnf, ext]
        )

        # Output should be: (2.15 * X) + (2.75 * Y) + ... = 15.05
        # Verify the equation format and that it's a valid solution
        match = re.search(
            r'\(2\.15 \* (\d+)\) \+ \(2\.75 \* (\d+)\) \+ \(3\.35 \* (\d+)\) \+ '
            r'\(3\.55 \* (\d+)\) \+ \(4\.20 \* (\d+)\) \+ \(5\.80 \* (\d+)\) = 15\.05',
            output
        )
        self.assertIsNotNone(match, f"Output did not match expected format: {output}")

        # Verify the solution is correct
        x1, x2, x3, x4, x5, x6 = [int(m) for m in match.groups()]
        total = 2.15*x1 + 2.75*x2 + 3.35*x3 + 3.55*x4 + 4.20*x5 + 5.80*x6
        self.assertAlmostEqual(total, 15.05, places=2)

    def test_prime_composite(self):
        """Test the prime factorization example with a composite number."""
        output = self.run_example_end_to_end(
            'prime',
            lambda cnf, ext: ['15', cnf, ext]
        )

        # Output should be: 15 can be factored into P * Q
        match = re.search(r'15 can be factored into (\d+) \* (\d+)', output)
        self.assertIsNotNone(match, f"Output did not match expected format: {output}")

        p, q = int(match.group(1)), int(match.group(2))
        self.assertEqual(p * q, 15)
        self.assertGreater(p, 1)
        self.assertGreater(q, 1)

    def test_prime_actual_prime(self):
        """Test the prime factorization example with an actual prime."""
        output = self.run_example_end_to_end(
            'prime',
            lambda cnf, ext: ['7', cnf, ext]
        )

        # Should be UNSATISFIABLE (no factorization exists)
        self.assertIn('UNSATISFIABLE', output)

    def test_nqueens_4(self):
        """Test the n-queens example with n=4."""
        output = self.run_example_end_to_end(
            'nqueens',
            lambda cnf, ext: ['4', cnf, ext]
        )

        # Output should be a 4x4 board with exactly 4 queens
        # Count queens (Q characters)
        queens = output.count('Q')
        self.assertEqual(queens, 4, f"Expected 4 queens, got {queens}. Output:\n{output}")

        # Verify board structure (should have grid lines)
        self.assertIn('+---', output)
        self.assertIn('|', output)

        # Extract queen positions and verify no two attack each other
        rows = [line for line in output.split('\n') if '|' in line and 'Q' in line or ' ' in line]
        positions = []
        for r, row in enumerate(rows):
            if '|' not in row:
                continue
            cells = row.split('|')[1:-1]  # Remove empty strings from split
            for c, cell in enumerate(cells):
                if 'Q' in cell:
                    positions.append((r, c))

        # Check no two queens share row, column, or diagonal
        for i, (r1, c1) in enumerate(positions):
            for r2, c2 in positions[i+1:]:
                self.assertNotEqual(r1, r2, "Two queens in same row")
                self.assertNotEqual(c1, c2, "Two queens in same column")
                self.assertNotEqual(abs(r1-r2), abs(c1-c2), "Two queens on same diagonal")

    def test_nonagram(self):
        """Test the nonagram (picross) example with a simple pattern."""
        # Simple 3x3 pattern that makes a cross:
        #   X
        # X X X
        #   X
        # hclues (columns): 1; 3; 1
        # vclues (rows): 1; 3; 1
        output = self.run_example_end_to_end(
            'nonagram',
            lambda cnf, ext: [
                '--out', cnf,
                '--extractor', ext,
                '--hclues', '1;3;1',
                '--vclues', '1;3;1'
            ]
        )

        # Should have X's in the output
        self.assertIn('X', output, f"Expected X in output: {output}")

        # Count X's - should be 5 for a cross pattern
        x_count = output.count('X')
        self.assertEqual(x_count, 5, f"Expected 5 X's for cross pattern, got {x_count}")

    def test_sudoku(self):
        """Test the sudoku solver with a known puzzle."""
        # A simple sudoku puzzle (. = empty)
        # This is a well-known "easy" puzzle
        puzzle = (
            "53..7...."
            "6..195..."
            ".98....6."
            "8...6...3"
            "4..8.3..1"
            "7...2...6"
            ".6....28."
            "...419..5"
            "....8..79"
        )

        output = self.run_example_end_to_end(
            'sudoku',
            lambda cnf, ext: [cnf, ext, puzzle]
        )

        # Should contain "Solution:" and a valid board
        self.assertIn('Solution:', output)

        # Extract digits from the solution part
        solution_start = output.find('Solution:')
        solution_text = output[solution_start:]

        # Extract all digits from the solution
        digits = re.findall(r'\d', solution_text)

        # Should have 81 digits in a complete sudoku
        self.assertEqual(len(digits), 81, f"Expected 81 digits, got {len(digits)}")

        # Verify all digits 1-9 (no zeros)
        for d in digits:
            self.assertIn(d, '123456789')

        # Reconstruct the board and verify it's valid
        board = [int(d) for d in digits]

        # Check rows
        for r in range(9):
            row = board[r*9:(r+1)*9]
            self.assertEqual(set(row), set(range(1, 10)), f"Invalid row {r}")

        # Check columns
        for c in range(9):
            col = [board[r*9 + c] for r in range(9)]
            self.assertEqual(set(col), set(range(1, 10)), f"Invalid column {c}")

        # Check 3x3 boxes
        for box_r in range(3):
            for box_c in range(3):
                box = []
                for r in range(3):
                    for c in range(3):
                        box.append(board[(box_r*3 + r)*9 + (box_c*3 + c)])
                self.assertEqual(set(box), set(range(1, 10)), f"Invalid box ({box_r}, {box_c})")


if __name__ == '__main__':
    unittest.main()
