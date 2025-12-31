Jane Street Puzzle: Altered States 2
====================================

The [Altered States 2 puzzle](https://www.janestreet.com/puzzles/altered-states-2-index/)
is an extension of the [Altered States puzzle](../jane-st-altered-states) with some
additional constraints and relaxations:

* States can now match the grid in all but one character: any of XTAH, UXAH, UTXH, or UTAX
count as a match for UTAH.
* The score for a state is the population of the state in the 2020 US Census.
* The total score must be at least 165,379,868 (half of the sum of all state populations).

In addition to trying to score the maximum number of points, there are some bonus
achievements spelled out in the full puzzle description like "contains all 8 states that
start with M" and "contains a coast-to-coast chain".

To solve this puzzle with the script in this directory, run:

```
$ uv run python examples/jane-st-number-altered-states-2/jane-st-altered-states-2.py 165379868 /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
 G  O  L  C  S
 R  I  A  I  M
 O  N  O  H  A
 L  W  U  C  S
 F  S  E  T  T
Matches:
  California : (0,3) (1,2) (0,2) (1,1) (1,0)* (2,0) (1,0) (2,1) (1,1) (1,2)
  Texas : (4,3) (4,2) (3,3)* (2,4) (3,4)
  Florida : (4,0) (3,0) (2,0) (1,0) (1,1) (2,2)* (1,2)
  Illinois : (1,3) (0,3)* (0,2) (1,1) (2,1) (2,2) (1,3) (0,4)
  Ohio : (0,1) (1,2)* (1,1) (0,1)
  Georgia : (0,0) (1,0)* (0,1) (1,0) (0,0) (1,1) (1,2)
  Virginia : (0,0)* (1,1) (1,0) (0,0) (1,1) (2,1) (1,1) (1,2)
  Massachusetts : (1,4) (2,4) (3,3)* (3,4) (2,4) (3,3) (2,3) (3,2) (4,1) (4,2) (4,3) (4,4) (3,4)
  Indiana : (1,1) (2,1) (2,2)* (1,3) (1,2) (2,1) (1,2)
  Alabama : (1,2) (0,2) (1,2) (2,3)* (2,4) (1,4) (2,4)
  Louisiana : (0,2) (0,1) (0,2)* (1,3) (0,4) (1,3) (1,2) (2,1) (1,2)
  Utah : (3,2) (4,3) (3,4)* (2,3)
  Iowa : (1,1) (0,1) (0,2)* (1,2)
  Idaho : (1,1) (2,2)* (1,2) (2,3) (2,2)
Extras:
Score: 165975744
```

The script requires a minimum score as a positional argument, but also accepts some optional
args to target bonus achievements:

* `extras`: A comma-separated list of extras to force. Can be any of the extras mentioned in the Altered States 2
  puzzle description: `20S`, `200M`, `PA`, `M8`, `4C`, `NOCAL`, or `C2C`
* `min_extras`: An integer specifying the minimum number of bonus achievements in the resulting grid (passing `7` here
  is redundant with just listing all extras in the `extras` arg.

For example, forcing the `C2C` bonus (a coast-to-coast chain) and the minimum allowable total score:

```
$ uv run python examples/jane-st-number-altered-states-2/jane-st-altered-states-2.py 165379868 /tmp/out.cnf /tmp/extractor.py --extras=C2C
Forcing C2C.
$ kissat /tmp/out.cnf > /tmp/kissat.out
# a few hours later...
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
 C  L  I  S  I
 O  A  S  A  M
 D  I  O  T  E
 E  R  N  I  U
 P  I  A  S  F
Matches:
  California : (0,0) (1,1) (0,1) (0,2) (1,1)* (2,2) (3,1) (3,2) (3,3) (4,2)
  Texas : (2,3) (2,4) (1,4)* (1,3) (0,3)
  Florida : (4,4) (3,3)* (2,2) (3,1) (2,1) (2,0) (1,1)
  Illinois : (0,2) (0,1) (1,1)* (2,1) (3,2) (2,2) (3,3) (4,3)
  Ohio : (2,2) (1,2)* (2,1) (2,2)
  Arizona : (4,2) (3,1) (2,1) (1,1)* (2,2) (3,2) (4,2)
  Indiana : (4,1) (3,2) (4,3)* (3,3) (4,2) (3,2) (4,2)
  Missouri : (1,4) (0,4) (0,3) (1,2) (2,2) (3,2)* (3,1) (4,1)
  Colorado : (0,0) (1,0) (0,1) (1,0) (0,0)* (1,1) (2,0) (1,0)
  Alabama : (1,1) (0,1) (1,1) (0,2)* (1,3) (1,4) (1,3)
  Oregon : (2,2) (3,1) (3,0) (3,1)* (2,2) (3,2)
  Utah : (3,4) (2,3) (1,3) (0,2)*
  Iowa : (2,1) (1,0) (0,0)* (1,1)
  Arkansas : (4,2) (3,1) (3,2)* (4,2) (3,2) (4,3) (4,2) (4,3)
  Mississippi : (1,4) (0,4) (0,3) (1,2) (0,2) (0,3) (1,2) (2,1) (3,1)* (4,0) (4,1)
  Kansas : (4,3)* (4,2) (3,2) (4,3) (4,2) (4,3)
  Idaho : (2,1) (2,0) (1,1) (1,2)* (2,2)
Extras:
  C2C
Score: 167172837
```

which contains the coast-to-coast chain:

```
Florida
Alabama
Mississippi
Arkansas
Missouri
Kansas
Colorado
Utah
Idaho
Oregon
```
