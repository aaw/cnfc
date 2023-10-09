# https://en.wikipedia.org/wiki/Tseytin_transformation#Gate_sub-expressions

def gen_and(a, b, v):
    yield (~a, ~b, v)
    yield (a, ~v)
    yield (b, ~v)

def gen_or(a, b, v):
    yield (a, b, ~v)
    yield (~a, v)
    yield (~b, v)

# TODO: replace gen_or usage with this, same for gen_and
def gen_or_multi(xs, v):
    yield (~v, *xs)
    for x in xs:
        yield (v, ~x)

def gen_xor(a, b, v):
    yield (~a, ~b, ~v)
    yield (a, b, ~v)
    yield (a, ~b, v)
    yield (~a, b, v)

def gen_xnor(a, b, v):
    yield (~a, ~b, v)
    yield (a, b, v)
    yield (a, ~b, ~v)
    yield (~a, b, ~v)

def gen_neq(a, b, v):
    yield from gen_xor(a, b, v)

def gen_eq(a, b, v):
    yield from gen_xnor(a, b, v)
