Primality Test
==============

Generate a formula that's unsatisfiable exactly when the input number is prime:

```
$ poetry run python3 examples/prime/prime.py 100123456789 /tmp/out.cnf /tmp/extractor.py
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

If you run the same sequence of programs with a composite number, say, `100123456788`, you should instead see:

```
& python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat-out.txt
100123456788 can be factored into 2 * 50061728394
```