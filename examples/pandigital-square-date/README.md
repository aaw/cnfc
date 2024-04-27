Pandigital Square Date
======================

Finds a date `DD/MM/YYYY` such that all the digits in the date are unique and the product `DD` * `MM` * `YYYY` is a square.
The original problem was posed [here](https://puzzling.stackexchange.com/questions/126447/next-future-date-such-that-the-all-8-digits-of-date-format-dd-mm-yyyy-is-all-dif).

You can verify that `13/09/2548` is the smallest future year by running:

```
$ poetry run python3 examples/pandigital-square-date/pandigital-square-date.py --max_year=2547 /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
UNSATISFIABLE

$ poetry run python3 examples/pandigital-square-date/pandigital-square-date.py --max_year=2548 /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
13/09/2548
```