Nonagram solver
===============

Example: https://www.nonograms.org/nonograms/i/66515

```
$ uv run python examples/nonagram/nonagram.py \
--out /tmp/out.cnf \
--extractor /tmp/extractor.py \
--hclues="4;2,2,1;2,2,2;3,4,3,1;10,3;2,2,3,2;2,1,1,1,2;3,2,2,1,4;1,9,4,1;3,4,1,3;1,2,3,1,4;6,1,1,1,2;2,2,2,1,4,1;2,3,1,1,4;2,4,2,1,1;4,6,4;3,2,2,2,1;2,1,2,2;4,2,2;6" \
--vclues="2,4;2,4;4,1,3;2,4,3;3,4,4;4,2,2,2,2;2,2,2,3,2;1,5,2,4;1,2,2,5,1;2,2,5,1,1;4,4,2,2;6,10;3,3;11;1,1;1,1,1,1;1,2,1,2,2;2,1,2,1,1,1;2,4,3,1,1,2;16"
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out

                      X  X     X  X  X  X
                   X  X           X  X  X  X
                X  X  X  X        X        X  X  X
             X  X        X  X  X  X           X  X  X
       X  X  X           X  X  X  X           X  X  X  X
    X  X  X  X           X  X     X  X     X  X        X  X
 X  X     X  X        X  X           X  X  X           X  X
 X           X  X  X  X  X              X  X     X  X  X  X
 X           X  X        X  X        X  X  X  X  X        X
 X  X     X  X           X  X  X  X  X        X           X
    X  X  X  X        X  X  X  X           X  X        X  X
       X  X  X  X  X  X     X  X  X  X  X  X  X  X  X  X
          X  X  X                             X  X  X
                X  X  X  X  X  X  X  X  X  X  X
                         X           X
          X              X           X           X
          X           X  X     X     X  X     X  X
          X  X        X     X  X        X     X        X
    X  X     X  X  X  X     X  X  X     X     X     X  X
       X  X  X  X  X  X  X  X  X  X  X  X  X  X  X  X
```
