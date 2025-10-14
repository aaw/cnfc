import hashlib

def cached_generate_var(method):
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
