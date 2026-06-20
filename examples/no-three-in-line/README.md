No-three-in-line
================

The [no-three-in-line](https://en.wikipedia.org/wiki/No-three-in-line_problem)
problem asks you to place 2n points on an n-by-n grid such that no three points
are collinear. Achim Flammenkamp maintains a [leaderboard for solutions](https://wwwhomes.uni-bielefeld.de/achim/no3in/readme.html);
Marijin Heule recently solved n=70.

You can solve up to n=14 in a few seconds with the encoding here. n=15 and above start getting harder. First
generate a formula that's satisfiable exactly when there's a no-three-in-line configuration:

```
$ uv run python examples/no-three-in-line/no-three-in-line.py 14 /tmp/out.cnf /tmp/extractor.py
```

Next, solve the CNF file using [kissat](https://github.com/arminbiere/kissat) or any other SAT solver that accepts DIMACS CNF input files:

```
$ kissat /tmp/out.cnf > /tmp/kissat-out.txt
```

Finally, use the generated extractor to decode and print the solution:

```
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat-out.txt
┼───┼───┼───●───┼───●───┼───┼───┼───┼───┼───┼───┼───┼
│   │   │   │   │   │   │   │   │   │   │   │   │   │
●───┼───┼───┼───┼───┼───┼───┼───┼───●───┼───┼───┼───┼
│   │   │   │   │   │   │   │   │   │   │   │   │   │
┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───●───┼───●───┼
│   │   │   │   │   │   │   │   │   │   │   │   │   │
┼───┼───●───┼───┼───┼───●───┼───┼───┼───┼───┼───┼───┼
│   │   │   │   │   │   │   │   │   │   │   │   │   │
┼───┼───┼───┼───┼───●───┼───┼───┼───┼───┼───┼───┼───●
│   │   │   │   │   │   │   │   │   │   │   │   │   │
┼───●───●───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼
│   │   │   │   │   │   │   │   │   │   │   │   │   │
┼───┼───┼───┼───┼───┼───┼───┼───●───┼───┼───┼───●───┼
│   │   │   │   │   │   │   │   │   │   │   │   │   │
┼───┼───┼───┼───┼───┼───┼───┼───┼───●───┼───┼───┼───●
│   │   │   │   │   │   │   │   │   │   │   │   │   │
●───┼───┼───┼───●───┼───┼───┼───┼───┼───┼───┼───┼───┼
│   │   │   │   │   │   │   │   │   │   │   │   │   │
┼───┼───┼───┼───┼───┼───●───●───┼───┼───┼───┼───┼───┼
│   │   │   │   │   │   │   │   │   │   │   │   │   │
┼───┼───┼───●───┼───┼───┼───┼───┼───┼───┼───●───┼───┼
│   │   │   │   │   │   │   │   │   │   │   │   │   │
┼───┼───┼───┼───●───┼───┼───┼───┼───┼───┼───●───┼───┼
│   │   │   │   │   │   │   │   │   │   │   │   │   │
┼───●───┼───┼───┼───┼───┼───┼───┼───┼───●───┼───┼───┼
│   │   │   │   │   │   │   │   │   │   │   │   │   │
┼───┼───┼───┼───┼───┼───┼───●───●───┼───┼───┼───┼───┼
```
