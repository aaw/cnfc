A Six-variable Logic Puzzle
===========================

[A Puzzling stack exchange question asks](https://puzzling.stackexchange.com/q/136796/84078)
for distinct integers _A,B,C,D,E_ and _F_ each from the set {1,2,...,10} satisfying the following:

1. B - D = 2
2. F + A = 11
3. A is between D and C
4. No two variables sum to 14
5. No two variables sum to 5
6. C - A = 1

You can solve this puzzle with the script in this directory. Just run:

```
$ uv run python examples/six-variable-logic-puzzle/six-variable-logic-puzzle.py /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
```

to see the solution.
