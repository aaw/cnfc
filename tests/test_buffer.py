from buffer import Buffer
import tempfile
import unittest

class TestBuffer(unittest.TestCase):
    def test_something(self):
        b = Buffer()
        b.Append((1,2,3))
        b.Append((-1,-2))
        # TODO: use io.StringIO here instead
        with tempfile.NamedTemporaryFile(mode='w+t') as f:
            b.Flush(f)
            f.seek(0)
            contents = f.read()

        expected = (
            'p cnf 3 2\n' +
            '1 2 3 0\n' +
            '-1 -2 0\n'
        )
        self.assertEqual(contents, expected)
