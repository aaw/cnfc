Maximize Iterative Rewriting Replacements
=========================================

[This CS StackExchange question](https://cs.stackexchange.com/questions/173715/how-to-find-a-bijection-phi-that-maximizes-the-number-of-iterative-replacemen)
asks for a particular bijection that can be used in a string replacement rule which maximizes the sequence of possible replacements. To discover a
bijection and trace of length at least N, generate a formula for that value of N (below, we use 60):

```
$ poetry run python3 examples/maximize-iterative-rewriting-replacements/maximize-iterative-rewriting-replacements.py 60 /tmp/out.cnf /tmp/extractor.py
```

Next, solve the CNF file using [kissat](https://github.com/arminbiere/kissat) or any other SAT solver that accepts DIMACS CNF input files:

```
$ kissat /tmp/out.cnf > /tmp/kissat-out.txt
```

(For N=60, solving with kissat took a little under a day on my laptop.)

Finally, use the generated extractor to decode and print the solution:

```
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat-out.txt
Definition of phi:
('000', 0) -> 233
('000', 1) -> 303
('000', 2) -> 033
('001', 0) -> 213
('001', 1) -> 301
('001', 2) -> 123
('010', 0) -> 211
('010', 1) -> 232
('010', 2) -> 032
('011', 0) -> 112
('011', 1) -> 231
('011', 2) -> 103
('100', 0) -> 203
('100', 1) -> 201
('100', 2) -> 022
('101', 0) -> 223
('101', 1) -> 202
('101', 2) -> 332
('110', 0) -> 221
('110', 1) -> 321
('110', 2) -> 023
('111', 0) -> 001
('111', 1) -> 313
('111', 2) -> 323
('112', 0) -> 222
('112', 1) -> 322
('112', 2) -> 031
('121', 0) -> 121
('121', 1) -> 002
('121', 2) -> 331
('122', 0) -> 011
('122', 1) -> 012
('122', 2) -> 102
('211', 0) -> 111
('211', 1) -> 013
('211', 2) -> 131
('212', 0) -> 122
('212', 1) -> 302
('212', 2) -> 311
('221', 0) -> 333
('221', 1) -> 021
('221', 2) -> 003
('222', 0) -> 133
('222', 1) -> 132
('222', 2) -> 312
('333', 0) -> 212
('333', 1) -> 101
('333', 2) -> 113

Trace:
12200
00011
11233
33222
33312
12212
12011
12103
03121
03331
01101
01112
12112
12121
21121
21111
11111
11001
01221
01012
12211
11011
11221
21222
22122
22333
22113
13333
13101
13332
12101
01121
21112
12111
11121
21001
21201
01122
22112
12333
12113
13121
13331
11101
01001
01211
01002
02211
01021
21211
11122
22001
22123
23333
23101
23332
22101
01333
01113
13112
```
