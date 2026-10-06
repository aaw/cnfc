Hitori
======

[Hitori](https://en.wikipedia.org/wiki/Hitori) asks you to shade cells in a grid of numbers so that:

1. No number appears twice in a row or column among the unshaded cells,
2. No two shaded cells are adjacent, and
3. the unshaded cells form a single connected region.

By default, the script solves the example puzzle from the Wikipedia article:

```
$ uv run python examples/hitori/hitori.py /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
# 8 # 6 3 2 # 7
3 6 7 2 1 # 5 4
# 3 4 # 2 8 6 1
4 1 # 5 7 # 3 #
7 # 3 # 8 5 1 2
# 5 6 7 # 1 8 #
6 # 2 3 5 4 7 8
8 7 1 4 # 3 # 6
```

Pass `--puzzle` with the rows of any other puzzle, separated by spaces.
