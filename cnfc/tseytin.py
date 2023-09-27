# https://en.wikipedia.org/wiki/Tseytin_transformation#Gate_sub-expressions

def gen_and(a, b, v):
    yield (~a, ~b, v)
    yield (a, ~v)
    yield (b, ~v)

def gen_or(a, b, v):
    yield (a, b, ~v)
    yield (~a, v)
    yield (~b, v)

def gen_xor(a, b, v):
    yield (~a, ~b, ~v)
    yield (a, b, ~v)
    yield (a, ~b, v)
    yield (~a, b, v)

def gen_neq(a, b, v):
    yield from gen_xor(a, b, v)
