n-Queens Solver
===============

First, choose an n (say, n = 10) and generate the DIMACS CNF file and the extractor script for the n-Queens problem:

```
$ uv run python examples/nqueens/nqueens.py 10 /tmp/out.cnf /tmp/extractor.py
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