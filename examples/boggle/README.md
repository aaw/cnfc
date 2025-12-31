Boggle
======

Generates a formula that's satisfiable exactly when there's a way to roll Boggle dice and score at least N points.

This is an experiment in verifying some of [Dan Vanderkam's optimal Boggle boards](https://github.com/danvk/hybrid-boggle),
including the [optimal 4-by-4 using the enable2k word list](https://www.danvk.org/2025/04/23/boggle-solved.html).

To verify Dan's result that the max score on a 4-by-4 board with the enable2k wordlist is 3625, you can download
[the enable2k wordlist](https://github.com/danvk/hybrid-boggle/tree/main/wordlists) and run:

```
$ uv run python examples/boggle/boggle.py 3626 --dice=new --rows=4 --cols=4 --words=enable2k.txt /tmp/out.cnf /tmp/extractor.py
```

This generates a 44 GB CNF file with 400 million variables and 1.5 billion clauses. The formula asserts that it's impossible
to score 3626. This CNF file is too big for most competitive CDCL SAT solvers which use signed 32-bit integers to index clauses.
But it'll run just fine on [IntelSAT](https://github.com/alexander-nadel/intel_sat_solver).

I attempted solving with `intel_sat_solver_static /tmp/out.cnf /topor_tool/solver_mode 2 > /tmp/solver-out.txt`, which used a
little less than 100 GB of memory and ran for a few days before I terminated it. If you have more patience than me and access
to a machine with a lot of RAM, you can do the same and leave it running until it terminates. After it does, you should be able
to run the extractor to see:

```
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/solver-out.txt
UNSATISFIABLE
```

If you run with numbers less than 3626, the extractor will instead print a board that achieves the desired score.

I also did some brief experiments with 5-by-5 instances, which generate CNF files with about the same number of variables but
generate about 70% more clauses and use 70% more RAM with IntelSAT.
