Jane Street Puzzle: Altered States
==================================

The [Altered States puzzle](https://www.janestreet.com/puzzles/altered-states-index/)
asks you to pack as many US state names as possible into a 5-by-5 grid. Names have to
follow a path that a chess king could take. The total score is the sum of all of the
lengths of state names that appear in the grid.

Given a minimum target score (60, for example), you can solve this puzzle with the script in this directory:

```
$ poetry run python3 examples/jane-st-altered-states/jane-st-altered-states.py 60 /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
 C  R  A  C  I
 O  D  K  S  H
 L  I  N  A  T
 M  D  N  O  U
 S  A  I  E  S
Matches:
  Indiana : (4,2) (3,2) (3,1) (4,2) (4,1) (3,2) (4,1)
  Colorado : (0,0) (1,0) (2,0) (1,0) (0,1) (0,2) (1,1) (1,0)
  Minnesota : (3,0) (2,1) (2,2) (3,2) (4,3) (4,4) (3,3) (2,4) (2,3)
  SouthCarolina : (4,4) (3,3) (3,4) (2,4) (1,4) (0,3) (0,2) (0,1) (1,0) (2,0) (2,1) (2,2) (2,3)
  Utah : (3,4) (2,4) (2,3) (1,4)
  Arkansas : (0,2) (0,1) (1,2) (2,3) (2,2) (1,3) (2,3) (1,3)
  Kansas : (1,2) (2,3) (2,2) (1,3) (2,3) (1,3)
  Maine : (3,0) (4,1) (4,2) (3,2) (4,3)
Score: 60
```

Or, if the score you've requested is not achievable, the final command will print `UNSATISFIABLE`.