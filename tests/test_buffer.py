from cnfc.buffer import *
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

    def test_push_pop(self):
        b = Buffer()
        b.Append((1,))
        b.PushCheckpoint()
        b.Append((2,))
        b.Append((3,))
        b.PushCheckpoint()
        b.Append((4,))
        b.PushCheckpoint()
        b.Append((5,))

        expected = (
            'p cnf 5 5\n' +
            '1 0\n' +
            '2 0\n' +
            '3 0\n' +
            '4 0\n' +
            '5 0\n'
        )
        self.assertEqual(flush_buffer_to_str(b), expected)

        b.PopCheckpoint()

        expected = (
            'p cnf 4 4\n' +
            '1 0\n' +
            '2 0\n' +
            '3 0\n' +
            '4 0\n'
        )
        self.assertEqual(flush_buffer_to_str(b), expected)

        b.PopCheckpoint()

        expected = (
            'p cnf 3 3\n' +
            '1 0\n' +
            '2 0\n' +
            '3 0\n'
        )
        self.assertEqual(flush_buffer_to_str(b), expected)

        b.PopCheckpoint()

        expected = (
            'p cnf 1 1\n' +
            '1 0\n'
        )
        self.assertEqual(flush_buffer_to_str(b), expected)

        b.Append((2,))
        b.Append((3,))

        expected = (
            'p cnf 3 3\n' +
            '1 0\n' +
            '2 0\n' +
            '3 0\n'
        )
        self.assertEqual(flush_buffer_to_str(b), expected)

    def test_comments(self):
        b = Buffer()
        b.Append((1,))
        b.Append((2,))
        b.AddComment("hello, world")
        b.Append((3,))
        b.AddComment("that's all, folks!")

        expected = (
            'c hello, world\n' +
            "c that's all, folks!\n" +
            'p cnf 3 3\n' +
            '1 0\n' +
            '2 0\n' +
            '3 0\n'
        )
        self.assertEqual(flush_buffer_to_str(b), expected)

    def test_read_clauses_and_comments(self):
        b = Buffer()
        b.Append((1,2,3))
        b.AddComment("hello")
        b.Append((4,5,6))
        b.AddComment("world")
        b.Append((7,))

        for i in range(3):
            clauses = list(b.AllClauses())
            comments = list(b.AllComments())
            self.assertEqual(clauses, [(1,2,3), (4,5,6), (7,)])
            self.assertEqual(comments, ["hello", "world"])

        expected = (
            'c hello\n' +
            'c world\n' +
            'p cnf 7 3\n' +
            '1 2 3 0\n' +
            '4 5 6 0\n' +
            '7 0\n'
        )
        self.assertEqual(flush_buffer_to_str(b), expected)

    def test_unit_clause_visitor(self):
        v = UnitClauses()
        b = Buffer(visitors = [v])
        b.Append((1,2,3))
        b.Append((4,))
        b.Append((5,6,7))
        b.Append((-4,))
        b.Append(tuple())

        self.assertEqual(v.units, set((4,-4)))
