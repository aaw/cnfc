from cnfc import *
from .util import SatTestCase

import random
import unittest

# Present vertices reachable from starts in a graph given as (n, edges).
def bfs(n, edges, present, starts):
    adj = {i: set() for i in range(n)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    seen = {s for s in starts if present[s]}
    stack = list(seen)
    while stack:
        v = stack.pop()
        for u in adj[v] - seen:
            if present[u]:
                seen.add(u)
                stack.append(u)
    return seen

class TestGraph(unittest.TestCase, SatTestCase):
    def check(self, f, expr, expected, mode):
        # Asserting uses one encoding; negating or nesting uses the exact one.
        if mode == 'assert':
            f.Add(expr if expected else ~expr)
        elif mode == 'negate':
            f.Add(~expr if expected else expr)
        else:
            flag = f.AddVar('flag')
            f.Add(flag == expr)
            f.Add(flag if expected else ~flag)
        if mode == 'negate':
            self.assertUnsat(f)
        else:
            self.assertSat(f)

    def random_graph(self, rng, f, n):
        edges = [(a, b) for a in range(n) for b in range(a+1, n) if rng.random() < rng.choice([0.2, 0.5])]
        present = [rng.random() < rng.choice([0.4, 0.8]) for _ in range(n)]
        xs = f.AddVars('x', n) if n else ()
        # Vertices are a mix of variables and negated variables.
        vertices = [~x if rng.random() < 0.5 else x for x in xs]
        for x, v, p in zip(xs, vertices, present):
            f.Add(v if p else ~v)
        g = Graph()
        for v in vertices:
            g.AddVertex(v)
        for a, b in edges:
            g.AddEdge(vertices[a], vertices[b])
        return g, vertices, edges, present

    def test_connected_matches_bfs(self):
        rng = random.Random(0)
        for trial in range(150):
            f = Formula()
            n = rng.randint(0, 7)
            g, vertices, edges, present = self.random_graph(rng, f, n)
            on = [i for i in range(n) if present[i]]
            expected = not on or bfs(n, edges, present, [on[0]]) == set(on)
            self.check(f, Connected(g), expected, rng.choice(['assert', 'negate', 'nested']))

    def test_reachable_matches_bfs(self):
        rng = random.Random(1)
        for trial in range(150):
            f = Formula()
            n = rng.randint(1, 7)
            g, vertices, edges, present = self.random_graph(rng, f, n)
            sources = rng.sample(range(n), rng.randint(1, min(2, n)))
            targets = rng.sample(range(n), rng.randint(1, min(2, n)))
            expected = bool(bfs(n, edges, present, sources) & set(targets))
            expr = Reachable(g, [vertices[i] for i in sources], [vertices[i] for i in targets])
            self.check(f, expr, expected, rng.choice(['assert', 'negate', 'nested']))

    def test_single_source_and_target(self):
        f = Formula()
        a, b, c = f.AddVars('a b c')
        g = Graph()
        g.AddEdge(a, b)
        g.AddEdge(b, c)
        f.Add(a)
        f.Add(c)
        f.Add(Reachable(g, a, c))
        f.PushCheckpoint()
        f.Add(~b)
        self.assertUnsat(f)
        f.PopCheckpoint()
        self.assertSat(f)

    def test_empty_graph_is_connected(self):
        f = Formula()
        f.Add(Connected(Graph()))
        self.assertSat(f)
        f.Add(~Connected(Graph()))
        self.assertUnsat(f)

    def test_isolated_vertex_disconnects(self):
        f = Formula()
        a, b, c = f.AddVars('a b c')
        g = Graph()
        g.AddEdge(a, b)
        g.AddVertex(c)
        f.Add(Connected(g))
        f.Add(a)
        f.Add(c)
        self.assertUnsat(f)

    def test_unknown_vertex_is_rejected(self):
        a, b = Formula().AddVars('a b')
        g = Graph()
        g.AddVertex(a)
        with self.assertRaises(ValueError):
            Reachable(g, a, b)
