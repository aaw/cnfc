n-Queens Solver
===============

First, choose an n (say, n = 10) and generate the DIMACS CNF file and the extractor script for the n-Queens problem:

```
$ uv run python examples/nqueens/nqueens.py 10 /tmp/out.cnf /tmp/extractor.py --blocker /tmp/blocker.py
```

Next, solve the CNF file using [kissat](https://github.com/arminbiere/kissat) or any other SAT solver that accepts DIMACS CNF input files:

```
$ kissat /tmp/out.cnf > /tmp/kissat-out.txt
```

Finally, use the generated extractor to decode and print the solution:

```
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat-out.txt
+---+---+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   | Q |   |   |   |
+---+---+---+---+---+---+---+---+---+---+
|   | Q |   |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+
|   |   |   |   |   | Q |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+
| Q |   |   |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |   |   | Q |
+---+---+---+---+---+---+---+---+---+---+
|   |   |   |   | Q |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+
|   |   | Q |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |   | Q |   |
+---+---+---+---+---+---+---+---+---+---+
|   |   |   | Q |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   | Q |   |   |
+---+---+---+---+---+---+---+---+---+---+
```

To find another board, block the solution and solve the updated CNF:

```
$ python3 /tmp/blocker.py /tmp/out.cnf /tmp/kissat-out.txt > /tmp/next.cnf
$ kissat /tmp/next.cnf > /tmp/next-solution.txt
$ python3 /tmp/extractor.py /tmp/next.cnf /tmp/next-solution.txt
```

Repeat using the latest CNF and solver output. With `n=4`, there are two boards; blocking both leaves the formula UNSAT.

With the built-in solver, you can enumerate boards directly in Python using this example's functions:

```python
formula, board_vars = encode(4)
while (sol := formula.Solve()) is not None:
    print_solution(sol, 4)
    formula.AddClause(*(~v if sol[v.name] else v for v in board_vars))
```
