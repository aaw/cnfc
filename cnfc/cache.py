# An LRU cache mapping Expr -> Var

from collections import OrderedDict

class Cache:
    def __init__(self):
        self.d = OrderedDict()

    def __len__(self):
        return len(self.d)

    def get(self, key):
        value = self.d.get(key)
        if value is not None:
            self.d.move_to_end(key, last=False)
        return value

    def put(self, key, value):
        self.d[key] = value
        self.d.move_to_end(key, last=False)

    # Returns the least recently used (key, value) pair.
    def pop(self):
        return self.d.popitem()
