xkcd #287
=========

xkcd.com/287 asks for a solution to the following equation in integers:

2.15_x_<sub>1</sub> + 2.75_x_<sub>2</sub> + 3.35_x_<sub>3</sub> + 3.55_x_<sub>4</sub> + 4.20_x_<sub>5</sub> + 5.80_x_<sub>6</sub> = 15.05

Multiplying both sides by 100, this is just the Diophantine equation:

215_x_<sub>1</sub> + 275_x_<sub>2</sub> + 335_x_<sub>3</sub> + 355_x_<sub>4</sub> + 420_x_<sub>5</sub> + 580_x_<sub>6</sub> = 1505

The example in this subdirectory encodes this equation into SAT. To solve it, run:

```
$ poetry run python3 examples/xkcd287/xkcd287.py /tmp/cnf /tmp/extractor.py
$ kissat /tmp/cnf > /tmp/solved
$ python3 /tmp/extractor.py /tmp/cnf /tmp/solved
(2.15 * 1) + (2.75 * 0) + (3.35 * 0) + (3.55 * 2) + (4.20 * 0) + (5.80 * 1) = 15.05
```
