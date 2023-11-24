The Trifference Problem
=======================

The [Trifference Problem](https://anuragbishnoi.wordpress.com/2023/01/23/the-trifference-problem/) asks for the
largest size _T(n)_ of any set _C_ of ternary strings of length _n_ such that any three strings in _C_ have a position
where they all differ. _T(5)_ = 10 and _T(6)_ = 13, which was only discovered in 2022 by
[Della Fiore, Gnutti, and Polak](https://www.sciencedirect.com/science/article/pii/S2666657X22000039).

The script in this directory will prove that _T(n)_ &ge; _k_ for any _n, k_. So you can re-prove _T(5)_ = 10 in
a few minutes on a laptop by running:

```
$ poetry run python3 examples/trifference/trifference.py 5 10 /tmp/cnf /tmp/extractor.py
$ kissat /tmp/cnf > /tmp/out
$ python3 /tmp/extractor.py /tmp/cnf /tmp/out
{00000, 01111, 11002, 11021, 11211, 12000, 20112, 20120, 20200, 22111}
```

and

```
$ poetry run python3 examples/trifference/trifference.py 5 11 /tmp/cnf /tmp/extractor.py
$ kissat /tmp/cnf > /tmp/out
$ python3 /tmp/extractor.py /tmp/cnf /tmp/out
UNSATISFIABLE
```
