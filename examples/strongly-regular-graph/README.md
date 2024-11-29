Strongly Regular Graph
======================

A [Strongly Regular Graph](https://en.wikipedia.org/wiki/Strongly_regular_graph) with parameters _n_, _k_, _λ_, _μ_ has the following properties:

   * _n_ vertices
   * Degree _k_
   * Each pair of adjacent vertices has _λ_ common neighbors
   * Each pair of non-adjacent vertices has _μ_ common neighbors

This script generates a formula that satisfiable exactly when a strongly regular graph exists with the given parameters. The cycle of
length 5 is a strongly regular graph with parameters _n_=5, _k_=2, _λ_=0, _μ_=1, so generate the CNF file and extractor with:

```
$ poetry run python3 examples/strongly-regular-graph/strongly-regular-graph.py 5 2 0 1 /tmp/out.cnf /tmp/extractor.py
```

Next, solve the CNF file using [kissat](https://github.com/arminbiere/kissat) or any other SAT solver that accepts DIMACS CNF input files:

```
$ kissat /tmp/out.cnf > /tmp/kissat-out.txt
```

Finally, use the generated extractor to decode and print the solution:

```
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat-out.txt
Strongly regular graph with parameters (5, 2, 0, 1):
  {0,1}
  {0,4}
  {1,2}
  {2,3}
  {3,4}
```
