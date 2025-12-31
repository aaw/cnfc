Perfect Cuboid
==============

Generate a formula that's satisfiable exactly when a [perfect cuboid](https://mathworld.wolfram.com/PerfectCuboid.html)
exists with side lengths and face diagonals representable with up to _n_ bits.

To prove, for example, that no perfect cuboid exists with side and face diagonal lengths < 1024:

```
$ uv run python examples/cuboid/cuboid.py 10 /tmp/out.cnf /tmp/extractor.py
```

Next, solve the CNF file using [kissat](https://github.com/arminbiere/kissat) or any other SAT solver that accepts DIMACS CNF input files:

```
$ kissat /tmp/out.cnf > /tmp/kissat-out.txt
```

Finally, use the generated extractor to decode and print the solution:

```
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat-out.txt
UNSATISFIABLE
```

If you find a perfect cuboid with some larger value of _n_, however, the extractor will instead print the side and face diagonal
lengths of the perfect cuboid. It is unknown whether a perfect cuboid actually exists for some _n_.
