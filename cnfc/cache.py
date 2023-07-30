# An LRU cache mapping Expr -> Var

class Cache:
    def __init__(self):
        pass

    # Returns value associated with key, or None if no (key, value) pair exists
    def get(self, key):
        pass

    def put(self, key, value):
        pass

    # Returns the least recently used (key, value) pair.
    def pop(self):
        pass
