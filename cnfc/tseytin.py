# https://en.wikipedia.org/wiki/Tseytin_transformation#Gate_sub-expressions
# Extended with Plaisted-Greenbaum polarity optimization

# Polarity constants for Plaisted-Greenbaum transformation
POLARITY_POS = 1    # need upward implication: φ → v
POLARITY_NEG = -1   # need downward implication: v → φ
POLARITY_BOTH = 0   # need full equivalence (Tseytin)

def flip_polarity(polarity):
    """Flip polarity for negation: POS ↔ NEG, BOTH stays BOTH"""
    if polarity == POLARITY_BOTH:
        return POLARITY_BOTH
    return -polarity

def gen_and(xs, v, polarity=POLARITY_BOTH):
    # Upward (φ → v): if all xi are true, v must be true
    # Needed when polarity is NEG (v may be forced false, need to detect when children are all true)
    if polarity != POLARITY_POS:
        yield (v, *[~x for x in xs])
    # Downward (v → φ): if v is true, each xi must be true
    # Needed when polarity is POS (v may be forced true, need to propagate to children)
    if polarity != POLARITY_NEG:
        for x in xs:
            yield (~v, x)

def gen_or(xs, v, polarity=POLARITY_BOTH):
    # Downward (v → φ): if v is true, at least one xi must be true
    # Needed when polarity is POS (v may be forced true, need to propagate to children)
    if polarity != POLARITY_NEG:
        yield (~v, *xs)
    # Upward (φ → v): if any xi is true, v must be true
    # Needed when polarity is NEG (v may be forced false, need to detect when any child is true)
    if polarity != POLARITY_POS:
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

def gen_iff(a, b):
    yield (~a, b)
    yield (a, ~b)
