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

# Path to the examples directory
EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'examples')
MILLISAT_PATH = os.path.join(os.path.dirname(__file__), 'millisat.py')


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
