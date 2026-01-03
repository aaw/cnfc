import hashlib
from .tseytin import POLARITY_BOTH

def cached_generate_var(method):
    def wrapper(self, formula, polarity=POLARITY_BOTH):
        if formula.expression_cache is None:
            return method(self, formula, polarity)
        key = hashlib.sha256(f"{repr(self)}:{polarity}".encode()).hexdigest()
        cached = formula.expression_cache.get(key)
        if cached is not None: return cached
        v = method(self, formula, polarity)
        formula.expression_cache[key] = v
        return v
    return wrapper
