Tournament Scheduling
=====================

[This Puzzling StackExchange question](https://puzzling.stackexchange.com/questions/126302/tournament-scheduling-puzzle) asks for a schedule for a tournament with a few constraints:

  1. 24 players competing in teams of 3, pairing up in 3-on-3 matches over 7 rounds.
  2. No two players can appear on the same team more than once.
  3. No two players can appear on competing teams more than once.

It doesn't look like 7 rounds is possible, but you can solve 5 rounds with the script in this directory:

```
$ uv run python examples/tournament-scheduling/tournament-scheduling.py --rounds 5 /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat-out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat-out
```

Which prints the following schedule for me:

```
Round 1: (1, 2, 3) vs (4, 5, 6), (7, 8, 9) vs (10, 11, 12), (13, 14, 15) vs (16, 17, 18), (19, 20, 21) vs (22, 23, 24)
Round 2: (1, 5, 14) vs (9, 10, 20), (4, 11, 16) vs (12, 17, 21), (8, 13, 24) vs (6, 15, 23), (3, 7, 18) vs (2, 19, 22)
Round 3: (1, 13, 19) vs (8, 11, 14), (4, 18, 22) vs (5, 9, 16), (3, 6, 12) vs (17, 20, 23), (2, 7, 10) vs (15, 21, 24)
Round 4: (1, 6, 11) vs (15, 16, 22), (3, 4, 23) vs (10, 14, 18), (2, 5, 21) vs (8, 12, 19), (9, 13, 17) vs (7, 20, 24)
Round 5: (1, 12, 16) vs (3, 19, 24), (4, 10, 21) vs (6, 13, 20), (2, 8, 15) vs (9, 14, 22), (5, 18, 23) vs (7, 11, 17)
```
