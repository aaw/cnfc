Matrix Multiplications
======================

If you multiply two n-by-n matrices following the usual algorithm for matrix multiplication, you'll perform <i>n<sup>3</sup></i> total
multiplications of matrix elements.
[Strassen's Algorithm](https://en.wikipedia.org/wiki/Strassen_algorithm) beats this bound, and in particular is a recipe for multiplying two 2-by-2 matrices
using only 7 multiplications, which is known to be the minimum number of possible multiplications. Laderman discovered an
[algorithm for multiplying two 3-by-3 matrices with only 23 multiplications](https://www.ams.org/journals/bull/1976-82-01/S0002-9904-1976-13988-2/S0002-9904-1976-13988-2.pdf),
but nobody knows if 23 is optimal for 3-by-3 matrices.

The script in this directory lets you discover algorithms to multiply square matrices with different constraints on total numbers
of multiplications or additions, assuming that multiplication of the underlying elements doesn't commute.

To discover a way to multiply two 2-by-2 matrices with only 7 multiplications, run:

```
$ poetry run python3 examples/matrix-multiplications/matrix-multiplications.py 2 7 /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
m_0 = (-a_{2,1}) * (b_{1,1} + -b_{1,2})
m_1 = (a_{1,1} + a_{1,2} + -a_{2,1}) * (-b_{1,1} + b_{2,2})
m_2 = (-a_{1,1} + -a_{1,2} + a_{2,1} + a_{2,2}) * (b_{2,2})
m_3 = (a_{1,2}) * (-b_{1,1} + b_{2,1})
m_4 = (a_{1,1} + a_{1,2}) * (b_{1,1})
m_5 = (-a_{1,1} + a_{2,1}) * (-b_{1,2} + b_{2,2})
m_6 = (a_{2,2}) * (b_{2,1} + -b_{2,2})

C_{1,1} = m_3 + m_4
C_{1,2} = m_0 + m_1 + m_4 + m_5
C_{2,1} = m_1 + m_2 + m_4 + m_6
C_{2,2} = m_0 + m_1 + m_2 + m_4
```

The algorithm discovered above describes how to multiply a 2-by-2 matrix <i>A</i> (with elements <i>a<sub>1,1</sub>, a<sub>1,2</sub>, a<sub>2,1</sub></i>, and <i>a<sub>2,2</sub></i>) with a
2-by-2 matrix <i>B</i> to obtain the product <i>C</i>. The algorithm has 7 multiplications defined by terms <i>m<sub>0</sub>, m<sub>1</sub>, ..., m<sub>6</sub></i>, each of which
is a single product of a sum of <i>a</i>'s with a sum of <i>b</i>'s. Each coordinate in <i>C</i> is the sum of some of the <i>m</i>'s.

You might also want to minimize the number of element additions.
None of the <i>m</i>'s in Strassen's Algorithm has a sum with more than two <i>a</i>'s or two <i>b</i>'s, which helps it
use fewer additions than the algorithm we discovered above. You can pass the flag `--max_additions_per_term` to the SAT generation
script above to restrict the maximum number of <i>a</i>'s or <i>b</i>'s in any <i>m</i>. For example, restricting to at most
a single addition in any <i>a</i> sum or <i>b</i> sum like Strassen's algorithm:

```
$ poetry run python3 examples/matrix-multiplications/matrix-multiplications.py 2 7 --max_additions_per_term=1 /tmp/out.cnf /tmp/extractor.py
```

You can also minimize the total number of additions globally with the `--max_total_additions` flag. The current best total number of additions
for 2-by-2 matrices is 12, so to try to discover an algorithm that beats this, run:

```
$ poetry run python3 examples/matrix-multiplications/matrix-multiplications.py 2 7 --max_total_additions=11 /tmp/out.cnf /tmp/extractor.py
```

To try to discover a 3-by-3 algorithm that beats Laderman's 23 multiplications, run:

```
$ poetry run python3 examples/matrix-multiplications/matrix-multiplications.py 3 22 /tmp/out.cnf /tmp/extractor.py
```
