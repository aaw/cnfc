from cnfc.cache import Cache
import unittest

class TestCache(unittest.TestCase):
    def test_put_get(self):
        c = Cache()
        self.assertEqual(c.get('a'), None)
        c.put('a',1)
        self.assertEqual(c.get('a'), 1)
        c.put('b',2)
        self.assertEqual(c.get('b'), 2)
        c.put('a',3)
        self.assertEqual(c.get('a'), 3)

    def test_pop(self):
        c = Cache()
        c.put('a',1)
        c.put('b',2)
        c.put('c',3)
        self.assertEqual(c.pop(), ('a',1))
        self.assertEqual(c.pop(), ('b',2))
        self.assertEqual(c.pop(), ('c',3))

        c.put('a',1)
        c.put('b',2)
        c.put('c',3)
        c.get('a')
        self.assertEqual(c.pop(), ('b',2))
        self.assertEqual(c.pop(), ('c',3))
        self.assertEqual(c.pop(), ('a',1))
