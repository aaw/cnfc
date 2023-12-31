Sudoku solver
=============

First, generate the DIMACS CNF file and the extractor script for a [hard Sudoku puzzle](http://magictour.free.fr/top95):

```
$ poetry run python3 examples/sudoku/sudoku.py /tmp/out.cnf /tmp/extractor.py 4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......
Board to solve:
+---------+---------+---------+
| 4       |         | 8     5 |
|    3    |         |         |
|         | 7       |         |
+---------+---------+---------+
|    2    |         |    6    |
|         |    8    | 4       |
|         |    1    |         |
+---------+---------+---------+
|         | 6     3 |    7    |
| 5       | 2       |         |
| 1     4 |         |         |
+---------+---------+---------+
```

Next, solve the CNF file using [kissat](https://github.com/arminbiere/kissat) or any other SAT solver that accepts DIMACS CNF input files:

```
$ kissat /tmp/out.cnf > /tmp/kissat-out.txt
```

Finally, use the generated extractor to decode and print the solution:

```
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat-out.txt
Solution:
+---------+---------+---------+
| 4  1  7 | 3  6  9 | 8  2  5 |
| 6  3  2 | 1  5  8 | 9  4  7 |
| 9  5  8 | 7  2  4 | 3  1  6 |
+---------+---------+---------+
| 8  2  5 | 4  3  7 | 1  6  9 |
| 7  9  1 | 5  8  6 | 4  3  2 |
| 3  4  6 | 9  1  2 | 7  5  8 |
+---------+---------+---------+
| 2  8  9 | 6  4  3 | 5  7  1 |
| 5  7  3 | 2  9  1 | 6  8  4 |
| 1  6  4 | 8  7  5 | 2  9  3 |
+---------+---------+---------+
```