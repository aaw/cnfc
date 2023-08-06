from buffer import Buffer
import io
import tempfile
import unittest

def flush_buffer_to_str(b):
    f = io.StringIO()
    b.Flush(f)
    f.seek(0)
    return f.read()

class TestBuffer(unittest.TestCase):
    def test_basic(self):
        b = Buffer()
        b.Append((1,2,3))
        b.Append((-1,-2))

        expected = (
            'p cnf 3 2\n' +
            '1 2 3 0\n' +
            '-1 -2 0\n'
        )
        self.assertEqual(flush_buffer_to_str(b), expected)
