# https://en.wikipedia.org/wiki/Tseytin_transformation#Gate_sub-expressions

def gen_and(a, b, v):
    yield (~a, ~b, v)
    yield (a, ~v)
    yield (b, ~v)
