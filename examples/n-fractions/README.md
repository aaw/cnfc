n-Fractions
===========

The [n-Fractions puzzle](https://www.csplib.org/Problems/prob041/) is a generalization of the following puzzle:

Find 9 distinct non-zero digits that satisfy:

```
A    D    G
-- + -- + -- == 1
BC   EF   HI
```

where `BC` means `10*B + C`, `EF` means `10*E + F`, and `HI` means `10*H + I`. In the generalized n-Fractions
puzzle, we're looking instead for 3n non-zero digits x_i, y_i, z_i (1 &le; i &le; n) such that the
sum of x_i / (y_i * 10 + z_i) from i=1 to n is equal to 1. Each digit is restricted to occur at least once
and at most `ceil(n/3)` times among x's, y's and z's.

In 2017, [Malapert and Provillard showed](https://pubsonline.informs.org/doi/10.1287/ited.2017.0193)
that the n-Fractions puzzle is unsolvable for n &ge; 45 and found solutions for other values of n except
36, 39, 41, 42, 43, and 44. In 2018, [Codish found](https://arxiv.org/abs/1807.00507) solutions for
n = 36 and 39. The script in this directory generates an encoding using cnfc that replicates most of Codish's
encoding. In 2025, this can resolve the remaining three of the remaining four cases with a modern SAT solver,
which leaves only the case of n=44 unresolved.

To solve, you must pass the value of n and an upper bound on the LCM of the `y_i z_i`'s:

```
$ poetry run python3 examples/n-fractions/n-fractions.py 41 8400 /tmp/out.cnf /tmp/extractor.py
$ cadical /tmp/out.cnf > /tmp/cadical.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/cadical.out
1/35 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 7/76 + 1/84 + 2/84 + 2/84 + 2/84 + 2/84 + 2/84 + 2/84 + 2/84 + 2/84 + 2/84 + 2/84 + 2/84 + 2/84 + 2/84 + 2/95 + 3/95 + 3/95 + 3/95 + 3/95 + 3/95 + 3/95 + 3/95 + 3/95 + 3/95 + 3/95 + 3/95 + 3/95
LCM of ys and zs: 7980
```

```
$ poetry run python3 examples/n-fractions/n-fractions.py 42 8400 /tmp/out.cnf /tmp/extractor.py
$ cadical /tmp/out.cnf > /tmp/cadical.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/cadical.out
1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 2/76 + 2/76 + 2/76 + 2/76 + 2/76 + 2/76 + 2/76 + 2/76 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 1/95 + 1/95 + 1/95 + 1/95 + 1/95 + 1/95 + 1/95 + 1/95 + 2/95 + 2/95 + 2/95 + 2/95 + 2/95 + 2/95
LCM of ys and zs: 7980
```

```
$ poetry run python3 n-fractions.py 43 8400 /tmp/out.cnf /tmp/extractor.py
$ cadical /tmp/out.cnf > /tmp/cadical.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/cadical.out
1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 1/76 + 2/76 + 1/84 + 2/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 3/84 + 1/95 + 2/95 + 2/95 + 2/95 + 2/95 + 2/95 + 2/95 + 2/95 + 2/95 + 2/95 + 2/95 + 2/95 + 2/95 + 2/95 + 3/95
LCM of ys and zs: 7980
```

Cadical resolved the n=41 and n=43 cases in a few minutes each and the n=42 case in a few hours. I could also verify that there's no LCM below 32000 that works for this problem by letting cadical run for 4 days:

```
$ poetry run python3 n-fractions.py 44 32000 /tmp/out.cnf /tmp/extractor.py
$ cadical /tmp/out.cnf > /tmp/cadical.out
# 4 days later...
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/cadical.out
UNSATISFIABLE
```
