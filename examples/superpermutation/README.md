Superpermutations
=================

A [superpermutation](https://en.wikipedia.org/wiki/Superpermutation) of order _n_ is a string
that contains all permutations of _n_ as substrings.

For example, to prove that you need a string of length [at least 33 for a superpermutation of
order 4](https://oeis.org/A180632):

```
$ uv run python examples/superpermutation/superpermutation.py 4 32 /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
UNSATISFIABLE
$ uv run python examples/superpermutation/superpermutation.py 4 33 /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
123412314231243121342132413214321
```

As of 2026, the best known upper bound for order 6 is 872. To improve this bound, run

```
$ uv run python examples/superpermutation/superpermutation.py 6 871 /tmp/out.cnf /tmp/extractor.py
# generates a CNF file with 642682 variables nd 4408916 clauses
$ kissat /tmp/out.cnf > /tmp/kissat.out
# wait a while...
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
# this will print UNSATISFIABLE if 872 is the smallest possible or print a superpermutation that
# proves a smaller upper bound of 871.
```