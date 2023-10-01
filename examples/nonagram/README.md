Nonagram solver
===============

Example: https://www.nonograms.org/nonograms/i/66825

```
$ poetry run python3 examples/nonagram/nonagram.py \
--out /tmp/out.cnf \
--extractor /tmp/extractor.py \
--hclues="6;3,2,1;3,1,3;2,1,1;1,2,2,1;1,1,1;4,4,1;2,1,3,1;1,8;2,2,3;3,2;2,1" \
--vclues="5;3,2;3,3;2,3,1;1,1,2;1,3,1;1,2,1,4;2,1,6;1,1,3;1,5;3,3;2,5"
```