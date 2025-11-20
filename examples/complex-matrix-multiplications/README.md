Complex Matrix Multiplications
==============================

[This Computer Science Stack Exchange post](https://cs.stackexchange.com/questions/86598/can-you-multiply-complex-2x2-matrices-in-fewer-than-21-real-multiplies)
asks for the minimum number of multiplications needed for two 2-by-2 complex matrices.

[Strassen's algorithm](https://en.wikipedia.org/wiki/Strassen_algorithm) gives a way to multiply two 2-by-2 real matrices using only 7 multiplications.
The [Karatsuba Algorithm](https://en.wikipedia.org/wiki/Karatsuba_algorithm) computes the product of two complex numbers (a + bi)(c + di) in
3 multiplications by precomputing x1 = ac, x2 = bd, and x3 = (a + b)(c + d), then rearranging the x's so that (a + bi)(c + di) is just (x1 - x2) + (x3 - x1 - x2)i.
So by combining the two techniques, it's possible to multiply two 2-by-2 complex matrices with only 21 multiplications. Can we do better?

The script in this directory lets you discover algorithms to multiply 2-by-2 complex matrices with exactly m multiplications. I was not able to
find an algorithm to uses 20 or fewer multiplications. This seems to be a hard problem, so I could only really solve uninteresting cases far above the known upper
bound of 21. For example:

```
$ poetry run python3 examples/complex-matrix-multiplications/complex-matrix-multiplications.py 40 /tmp/out.cnf /tmp/extractor.py
$ kissat /tmp/out.cnf > /tmp/kissat.out
$ python3 /tmp/extractor.py /tmp/out.cnf /tmp/kissat.out
m_0 = (-b_{1,2}) * (c_{2,2})
m_1 = (a_{1,2}) * (-d_{1,2} + -d_{2,2})
m_2 = (a_{2,1}) * (-d_{1,1} + -d_{2,1})
m_3 = (-a_{2,1}) * (c_{1,2} + -c_{2,1} + -c_{2,2} + -d_{1,1} + d_{1,2} + -d_{2,1})
m_4 = (b_{2,1}) * (c_{1,1} + c_{1,2} + c_{2,2} + d_{2,1})
m_5 = (a_{2,2} + -b_{1,1} + -b_{1,2} + -b_{2,2}) * (-c_{2,1} + d_{2,1})
m_6 = (-b_{1,1}) * (c_{1,1})
m_7 = (b_{1,1}) * (c_{2,2} + -d_{2,1} + d_{2,2})
m_8 = (a_{2,2} + b_{1,1}) * (-d_{2,1} + d_{2,2})
m_9 = (b_{1,1} + b_{2,2}) * (d_{2,1} + -d_{2,2})
m_10 = (-a_{2,2} + b_{1,1} + b_{2,2}) * (c_{2,1} + -d_{2,1})
m_11 = (b_{1,1} + -b_{2,2}) * (c_{2,1} + d_{2,1} + -d_{2,2})
m_12 = (b_{1,1} + -b_{2,1} + b_{2,2}) * (c_{2,2} + d_{2,1})
m_13 = (-a_{2,1} + b_{1,1} + b_{2,2}) * (c_{2,2} + -d_{2,1})
m_14 = (-a_{2,1} + a_{2,2} + b_{1,1} + b_{2,2}) * (c_{2,1})
m_15 = (-a_{2,1} + -a_{2,2} + b_{1,1}) * (c_{2,1} + c_{2,2} + -d_{2,1})
m_16 = (-a_{2,1} + b_{1,1} + -b_{2,1} + b_{2,2}) * (-c_{2,2} + d_{2,1})
m_17 = (-a_{2,1} + -a_{2,2} + b_{1,1} + -b_{2,1}) * (d_{2,1})
m_18 = (-a_{2,1} + a_{2,2} + b_{1,1} + b_{2,1}) * (-d_{2,1})
m_19 = (-a_{2,1} + b_{1,1} + b_{2,2}) * (-c_{2,1} + -d_{1,2})
m_20 = (b_{1,1} + b_{2,1} + b_{2,2}) * (d_{1,2} + d_{2,1})
m_21 = (b_{1,1}) * (-c_{1,2} + -c_{2,1} + -d_{2,1})
m_22 = (b_{1,1} + b_{2,2}) * (-c_{1,2} + -c_{2,1} + c_{2,2} + d_{1,2} + d_{2,1})
m_23 = (b_{1,1}) * (c_{1,2})
m_24 = (b_{1,1} + b_{2,2}) * (c_{1,2} + c_{2,1} + -c_{2,2} + -d_{2,2})
m_25 = (b_{1,1}) * (c_{1,2} + c_{2,1} + -c_{2,2} + -d_{2,1} + -d_{2,2})
m_26 = (b_{1,1} + b_{2,1} + b_{2,2}) * (c_{1,2})
m_27 = (b_{1,1} + -b_{2,1}) * (-c_{1,2} + c_{2,2} + d_{1,1} + d_{2,1})
m_28 = (a_{2,1} + b_{1,1} + b_{2,1}) * (c_{1,1} + c_{2,2})
m_29 = (b_{1,1}) * (c_{1,1} + d_{1,1})
m_30 = (-a_{1,1} + -a_{1,2}) * (c_{2,1} + d_{2,1})
m_31 = (-a_{1,1} + a_{1,2}) * (d_{1,2})
m_32 = (-a_{1,1}) * (-c_{1,1} + c_{2,1} + d_{1,1} + d_{2,1})
m_33 = (-a_{1,1} + -b_{1,1}) * (c_{1,2} + c_{2,2} + -d_{1,2} + -d_{2,2})
m_34 = (-a_{1,1} + a_{1,2} + -b_{1,1}) * (-c_{2,2})
m_35 = (-a_{1,1} + a_{1,2} + -b_{1,1} + -b_{2,1}) * (c_{2,2})
m_36 = (-a_{1,1} + a_{1,2} + -b_{1,1} + b_{1,2}) * (c_{2,2} + -d_{2,2})
m_37 = (-a_{1,1} + b_{1,1}) * (-d_{1,1} + d_{2,1})
m_38 = (-a_{1,1} + a_{2,1} + b_{1,1}) * (d_{1,1} + d_{2,1})
m_39 = (a_{1,1} + -a_{1,2} + -b_{1,1} + -b_{1,2}) * (d_{2,1})

C_{1,1} = -m_30 + m_32 + m_37 + m_39 + (-m_2 + m_5 + -m_10 + m_29 + -m_38 + -m_39)*I
C_{1,2} = m_0 + -m_1 + -m_23 + -m_31 + -m_33 + m_36 + (-m_0 + -m_1 + m_23 + -m_31)*I
C_{2,1} = -m_4 + -m_7 + -m_9 + -m_10 + -m_11 + -m_12 + m_13 + -m_18 + -m_21 + -m_23 + m_25 + m_27 + m_28 + -m_29 + (-m_2 + m_4 + -m_9 + m_12 + m_13 + m_16 + -m_18 + m_21 + m_23 + m_24 + -m_26 + m_34 + m_35)*I
C_{2,2} = -m_2 + -m_3 + m_7 + m_9 + -m_14 + -m_15 + -m_17 + -m_19 + -m_20 + -m_21 + -m_23 + (-m_7 + m_8 + m_10 + m_14 + m_19 + m_22 + m_26)*I
```

In the example above, one of the multiplications (`m6`) isn't used in the final results, so we've actually discovered an algorithm with 39 multiplication instead of the 40 we asked for.
This 39-multiplication solution took about a day to find on my laptop.