Jane Street Puzzle: Somewhat Square Sudoku
==========================================

The [Somewhat Square Sudoku puzzle](https://www.janestreet.com/puzzles/somewhat-square-sudoku-index/)
asks you to solve a sudoku and maximize the resulting GCD of the rows in the solution.

Standard Sudokus use the numbers 1-9 and require that each row, column, and 3-by-3 box have all the
values 1-9. This Sudoku uses the numbers 0-9 with one value (your choice) excluded.

You can solve this puzzle with the script in this directory. The greatest common divisor is 12345679, so:

```
$ uv run python examples/somewhat-square-sudoku/somewhat-square-sudoku.py 12345679 /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out

3  9  5  0  6  1  7  2  8
0  6  1  7  2  8  3  9  5
7  2  8  3  9  5  0  6  1
9  5  0  6  1  7  2  8  3
2  8  3  9  5  0  6  1  7
6  1  7  2  8  3  9  5  0
8  3  9  5  0  6  1  7  2
5  0  6  1  7  2  8  3  9
1  7  2  8  3  9  5  0  6

Verified common divisor: 12345679
Actual GCD: 12345679
```

And trying any larger divisor doesn't work:

```
$ uv run python examples/somewhat-square-sudoku/somewhat-square-sudoku.py 12345680 /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
UNSATISFIABLE
```
