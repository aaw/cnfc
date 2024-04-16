Tournament Scheduling
=====================

[This Puzzling StackExchange question](https://puzzling.stackexchange.com/questions/126302/tournament-scheduling-puzzle) asks for a schedule for a tournament with a few constraints:

  1. 24 players competing in teams of 3, pairing up in 3-on-3 matches over 7 rounds.
  2. No two players can appear on the same team more than once.
  3. No two players can appear on competing teams more than once.

To solve it with the script in this directory, run:

```
$ poetry run python3 examples/tournament-scheduling/tournament-scheduling.py /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat-out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat-out
```

Which prints the following schedule for me:

```
Round 1: (8, 16, 17) vs (7, 10, 19), (3, 6, 11) vs (13, 21, 22), (2, 9, 15) vs (18, 20, 24), (1, 4, 5) vs (12, 14, 23)
Round 2: (3, 4, 24) vs (1, 6, 12), (15, 21, 23) vs (14, 16, 20), (8, 18, 22) vs (11, 17, 19), (9, 10, 13) vs (2, 5, 7)
Round 3: (5, 9, 20) vs (3, 16, 19), (1, 8, 13) vs (4, 14, 22), (7, 17, 23) vs (2, 11, 24), (10, 12, 15) vs (6, 18, 21)
Round 4: (3, 22, 23) vs (2, 13, 18), (5, 10, 16) vs (9, 11, 12), (4, 19, 21) vs (6, 7, 24), (8, 15, 20) vs (1, 14, 17)
Round 5: (15, 16, 24) vs (2, 3, 14), (6, 10, 22) vs (18, 19, 23), (4, 13, 17) vs (1, 9, 21), (5, 8, 12) vs (7, 11, 20)
Round 6: (6, 9, 17) vs (11, 14, 15), (12, 13, 16) vs (8, 19, 24), (4, 7, 18) vs (10, 20, 23), (3, 5, 21) vs (1, 2, 22)
Round 7: (5, 13, 19) vs (2, 4, 6), (1, 3, 7) vs (15, 17, 18), (14, 21, 24) vs (8, 10, 11), (9, 16, 23) vs (12, 20, 22)
```