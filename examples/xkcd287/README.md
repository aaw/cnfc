xkcd #287
=========

[xkcd.com/287](https://xkcd.com/287) asks for a solution to the following equation in integers:

2.15 _x_<sub>1</sub> + 2.75 _x_<sub>2</sub> + 3.35 _x_<sub>3</sub> + 3.55 _x_<sub>4</sub> + 4.20 _x_<sub>5</sub> + 5.80 _x_<sub>6</sub> = 15.05

Multiplying both sides by 100, this is just the Diophantine equation:

215 _x_<sub>1</sub> + 275 _x_<sub>2</sub> + 335 _x_<sub>3</sub> + 355 _x_<sub>4</sub> + 420 _x_<sub>5</sub> + 580 _x_<sub>6</sub> = 1505

The example in this subdirectory encodes this equation into SAT. To solve it, run:

```
$ uv run python examples/xkcd287/xkcd287.py /tmp/cnf /tmp/extractor.py
$ kissat /tmp/cnf > /tmp/solved
$ python3 /tmp/extractor.py /tmp/cnf /tmp/solved
(2.15 * 1) + (2.75 * 0) + (3.35 * 0) + (3.55 * 2) + (4.20 * 0) + (5.80 * 1) = 15.05
```
