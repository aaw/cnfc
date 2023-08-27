# cnfc
A Python package that generates DIMACS CNF files.

A [CNF](https://en.wikipedia.org/wiki/Conjunctive_normal_form) compiler that generates
compact encodings from higher-level primitives that are commonly used for solving
combinatorial problems.

Instead of providing an integrated encoder-solver environment, this package generates
DIMACS CNF files only. This is a useful intermediate step for difficult problems that
might take hours or days to solve, since having a DIMACS CNF input allows one to
move to a more powerful machine or cluster and experiment with different preprocessors
and solvers.

Example:

```python
from cnfc import *

f = Formula()
x, y, z, w = f.AddVars('x y z w')

f.AddClause(~x,y)  # Equivalent to f.Add(Or(~x,y)).
f.AddClause(~y,z)
f.AddClause(~z,x)

# Equivalent to f.Add(Or(Implies(x,y),Not(And(z,w)))).
f.Add(Implies(x,y) | ~(z & w))

# Assert that at least one of x,y, or z is true.
f.Add(NumTrue(x,y,z) >= 1)

# Assert that the tuple (x,y) is lexicographically less than (z,w).
f.Add(Tuple(x,y) < Tuple(z,w))

# Write the resulting CNF file to /tmp/output.cnf.
with open('/tmp/output.cnf', 'w') as fd:
    f.WriteCNF(fd)
```

The above script will generate:

```
p cnf 11 28
-1 2 0
-2 3 0
-3 1 0
-1 2 -5 0
5 1 0
5 -2 0
-3 -4 6 0
-6 3 0
-6 4 0
5 -6 0
-8 1 2 0
-1 8 0
-2 8 0
7 -1 -2 0
1 -7 0
2 -7 0
-10 7 3 0
-7 10 0
-3 10 0
9 -7 -3 0
7 -9 0
3 -9 0
8 10 0
-1 3 0
-1 11 0
3 11 0
-2 -11 0
4 -11 0
```

Status
======

Basic functionality (boolean operations, cardinality tests, lexicographic tuple comparisons) and arbitrary nesting of expressions is implemented.

Installation
============

```
pip install cnfc
```

Development
===========

Install [poetry](https://python-poetry.org/docs/#installation) and run `poetry install`. Then you can bring up a shell, etc. Run tests with:

```
poetry run python3 -m unittest discover
```