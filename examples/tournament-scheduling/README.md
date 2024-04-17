Tournament Scheduling
=====================

[This Puzzling StackExchange question](https://puzzling.stackexchange.com/questions/126302/tournament-scheduling-puzzle) asks for a schedule for a tournament with a few constraints:

  1. 24 players competing in teams of 3, pairing up in 3-on-3 matches over 7 rounds.
  2. No two players can appear on the same team more than once.
  3. No two players can appear on competing teams more than once.

It doesn't look like 7 rounds is possible, but you can solve 5 rounds with the script in this directory:

```
$ poetry run python3 examples/tournament-scheduling/tournament-scheduling.py --rounds 5 /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat-out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat-out
```

Which prints the following schedule for me:

```
Round 1: (1, 2, 3) vs (4, 5, 6), (7, 8, 9) vs (10, 11, 12), (13, 14, 15) vs (16, 17, 18), (19, 20, 21) vs (22, 23, 24)
Round 2: (6, 13, 18) vs (8, 20, 22), (2, 11, 23) vs (1, 17, 24), (10, 14, 19) vs (4, 12, 15), (7, 16, 21) vs (3, 5, 9)
Round 3: (9, 11, 14) vs (2, 5, 20), (1, 8, 12) vs (15, 21, 22), (3, 10, 16) vs (18, 19, 23), (4, 13, 17) vs (6, 7, 24)
Round 4: (15, 16, 19) vs (6, 11, 20), (10, 13, 24) vs (1, 5, 14), (8, 18, 21) vs (2, 7, 17), (9, 12, 22) vs (3, 4, 23)
Round 5: (8, 14, 17) vs (1, 9, 19), (5, 11, 18) vs (6, 12, 23), (2, 15, 24) vs (3, 7, 22), (4, 10, 21) vs (13, 16, 20)
```