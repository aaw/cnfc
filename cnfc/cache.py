import hashlib

def cached_evaluate(method):
    def wrapper(self, formula):
        if formula.expression_cache is None:
            return method(self, formula)
        key = hashlib.sha256(repr(self).encode()).hexdigest()
        cached = formula.expression_cache.get(key)
        if cached is not None: return cached
        v = method(self, formula)
        formula.expression_cache[key] = v
        return v
    return wrapper

def cached_evaluate_bits(method):
    def wrapper(self, formula):
        if formula.expression_cache is None:
            return method(self, formula)
        key = ('tuple', hashlib.sha256(repr(self).encode()).hexdigest())
        cached = formula.expression_cache.get(key)
        if cached is None:
            cached = tuple(method(self, formula))
            formula.expression_cache[key] = cached
        # Return a fresh list so callers can reorder the bits.
        return list(cached)
    return wrapper
