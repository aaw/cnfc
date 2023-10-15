# Generator wrapper, allows simple access to a generator plus a return value.
# Pattern described here: https://stackoverflow.com/a/34073559/14236095.
class Generator:
    def __init__(self, gen):
        self.gen = gen

    def __iter__(self):
        self.result = yield from self.gen
