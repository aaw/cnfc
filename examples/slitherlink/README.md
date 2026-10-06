Slitherlink
===========

[Slitherlink](https://en.wikipedia.org/wiki/Slitherlink) asks you to draw a single loop along the edges of a grid
so that each numbered cell has exactly that many of its four edges on the loop.

By default, the script solves the example puzzle from the Wikipedia article:

```
$ uv run python examples/slitherlink/slitherlink.py /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
+---+---+---+   +   +   +
|           |     0
+   +---+   +   +   +---+
| 3 | 3 |   |     1 |   |
+---+   +   +---+   +   +
        | 1   2 |   |   |
+   +   +   +   +---+   +
        | 2   0         |
+   +   +---+   +   +   +
      1     |     1   1 |
+---+---+---+   +---+   +
|     2         |   |   |
+---+---+---+---+   +---+
```

Pass `--puzzle` with the rows of any other puzzle, separated by spaces, using `.` for cells without a clue.
