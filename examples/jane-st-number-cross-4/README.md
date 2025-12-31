Jane Street Puzzle: Number Cross 4
==================================

The [Number Cross 4 puzzle](https://www.janestreet.com/puzzles/number-cross-4-index/)
asks for an assignment of the numbers 0-9 to cells on an 11 x 11  grid with a few
interesting restrictions:

  * "Spacers" can be placed in any cell to break a row into several numbers, but no
    two spacers can share a cell edge.
  * Runs of numbers in a row between spacers must be at least 2 digits and can't have
    leading zeros.
  * Each row has criteria that every run of numbers in that row must meet, ranging
    from simple ("sum of digits is 7") to complex ("prime raised to prime power",
    "palindrome and multiple of 23")
  * The entire grid is broken into irregular contiguous regions; all digits within a
    region must be equal but digits in adjacent regions must be different. Spacers
    can split regions.

To solve this puzzle with the script in this directory, run:

```
$ uv run python examples/jane-st-number-cross-4/jane-st-number-cross-4.py /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
```

The last command should print the solution. Generating the CNF and extractor takes several minutes and solving
the resulting SAT instance may take a couple of hours.
