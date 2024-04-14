Pandigital Alphametic
=====================

Solves the equation `A x BC x DEF = GHIJ` using each number 0-9 exactly once,
presented in [this Puzzling StackExchange question](https://puzzling.stackexchange.com/questions/126266/a-pandigital-alphametic).

The script has a list of all 72 solutions and returns `UNSATISFIABLE` when run:

```
$ poetry run python3 examples/pandigital-alphametic/pandigital-alphametic.py /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat-out.txt
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat-out.txt
UNSATISFIABLE
```

But that's only because I generated the script by incrementally running, finding a solution, and adding it to the list. So
as is, the script just verifies that there are no additional solutions other than the 72 I've listed.
