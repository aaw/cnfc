# https://en.wikipedia.org/wiki/Tseytin_transformation#Gate_sub-expressions

def gen_and(xs, v):
    yield (v, *[~x for x in xs])
    for x in xs:
        yield (~v, x)

def gen_or(xs, v):
    yield (~v, *xs)
    for x in xs:
        yield (v, ~x)

def gen_xor(xs, v):
    if len(xs) != 2:
        raise ValueError("Only binary XOR currently supported.")
    a, b = xs
    yield (~a, ~b, ~v)
    yield (a, b, ~v)
    yield (a, ~b, v)
    yield (~a, b, v)

def gen_xnor(xs, v):
    if len(xs) != 2:
        raise ValueError("Only binary XNOR currently supported.")
    a, b = xs
    yield (~a, ~b, v)
    yield (a, b, v)
    yield (a, ~b, ~v)
    yield (~a, b, ~v)

def gen_neq(xs, v):
    yield from gen_xor(xs, v)

def gen_eq(xs, v):
    yield from gen_xnor(xs, v)
