# Graph connectivity constraints.
#
# A Graph's vertices are boolean expressions, and a vertex is "present" when
# its expression is true. Connected(g) and Reachable(g, s, t) are boolean
# expressions about the subgraph of present vertices.

from .model import BoolExpr, And, Or, Tuple
from .bool_lit import BooleanLiteral
from .cache import cached_evaluate

__all__ = ['Graph', 'Connected', 'Reachable']

class Graph:
    def __init__(self):
        # Vertices are keyed by repr: == on expressions builds a new
        # expression, and ~x creates a new object each time, so neither
        # identity nor equality works as a key.
        self.vertices = {}   # key -> expression, in insertion order
        self.neighbors = {}  # key -> {neighbor key: None}, an ordered set

    def AddVertex(self, v):
        key = repr(v)
        if key not in self.vertices:
            self.vertices[key] = v
            self.neighbors[key] = {}
        return key

    def AddEdge(self, u, v):
        a, b = self.AddVertex(u), self.AddVertex(v)
        if a != b:
            self.neighbors[a][b] = None
            self.neighbors[b][a] = None

    def __repr__(self):
        return 'Graph({})'.format(';'.join('{}:{}'.format(k, ','.join(n)) for k, n in self.neighbors.items()))

    def _keys(self, vs):
        if not isinstance(vs, (list, tuple)):
            vs = [vs]
        keys = []
        for v in vs:
            key = repr(v)
            if key not in self.vertices:
                raise ValueError('{} is not a vertex of the graph'.format(v))
            keys.append(key)
        return keys

    # Number of edges on a shortest path from any of the starting keys to each
    # key, ignoring which vertices are present. Unreachable keys are omitted.
    def _hops(self, starts):
        hops = {k: 0 for k in starts}
        frontier = list(hops)
        while frontier:
            nxt = []
            for k in frontier:
                for n in self.neighbors[k]:
                    if n not in hops:
                        hops[n] = hops[k] + 1
                        nxt.append(n)
            frontier = nxt
        return hops

def _present(graph, formula):
    return {k: v.evaluate(formula) for k, v in graph.vertices.items()}

# roots[k] is true iff k is the first present vertex in insertion order.
def _roots(graph, formula, present):
    roots, none_before = {}, BooleanLiteral(True)
    for k in graph.vertices:
        roots[k] = And(present[k], none_before).evaluate(formula)
        none_before = And(none_before, ~present[k]).evaluate(formula)
    return roots

# Returns literals that are true iff each vertex is reachable from a vertex
# whose start literal is true, passing only through present vertices, in at
# most the given number of steps. hops[k] is a lower bound on the number of
# steps needed to reach k; vertices missing from hops can't be reached at all.
def _layered_reachability(graph, formula, present, start, hops, steps):
    reached = {k: start.get(k, BooleanLiteral(False)) for k in graph.vertices}
    for step in range(1, steps + 1):
        nxt = dict(reached)
        for k in graph.vertices:
            if hops.get(k, step + 1) > step: continue  # Can't be reached yet.
            sources = [reached[n] for n in graph.neighbors[k] if hops.get(n, step) < step]
            nxt[k] = And(present[k], Or(reached[k], *sources)).evaluate(formula)
        reached = nxt
    return reached

def _labels(formula, keys, n):
    bits = max(1, (n - 1).bit_length())
    return {k: Tuple(*(formula.AddVar() for _ in range(bits))) for k in keys}

class Connected(BoolExpr):
    def __init__(self, graph):
        self.graph = graph

    def __repr__(self):
        return 'Connected({!r})'.format(self.graph)

    @cached_evaluate
    def evaluate(self, formula):
        g = self.graph
        present = _present(g, formula)
        roots = _roots(g, formula, present)
        # Any vertex could be the root. A path from the root stays within its
        # component and visits each vertex at most once, so the largest
        # component's size bounds the number of steps.
        largest, seen = 0, set()
        for k in g.vertices:
            if k not in seen:
                component = g._hops([k])
                seen.update(component)
                largest = max(largest, len(component))
        reached = _layered_reachability(g, formula, present, roots, {k: 0 for k in g.vertices}, largest - 1)
        return And(*(Or(~present[k], reached[k]) for k in g.vertices)).evaluate(formula)

    def constraint_clauses(self, formula):
        g = self.graph
        present = _present(g, formula)
        roots = _roots(g, formula, present)
        label = _labels(formula, g.vertices, len(g.vertices))
        # Every present vertex other than the root has a present neighbor with
        # a smaller label.
        for k in g.vertices:
            parents = [And(present[n], label[n] < label[k]) for n in g.neighbors[k]]
            yield from Or(~present[k], roots[k], *parents).constraint_clauses(formula)

class Reachable(BoolExpr):
    def __init__(self, graph, sources, targets):
        self.graph = graph
        self.sources = graph._keys(sources)
        self.targets = graph._keys(targets)

    def __repr__(self):
        return 'Reachable({!r},{},{})'.format(self.graph, self.sources, self.targets)

    @cached_evaluate
    def evaluate(self, formula):
        g = self.graph
        present = _present(g, formula)
        start = {k: present[k] for k in self.sources}
        hops = g._hops(self.sources)
        reached = _layered_reachability(g, formula, present, start, hops, len(hops) - 1)
        return Or(*(reached[k] for k in self.targets)).evaluate(formula)

    def constraint_clauses(self, formula):
        g = self.graph
        present = _present(g, formula)
        # Only vertices connected to a source in the full graph can be on a path.
        candidates = g._hops(self.sources)
        on_path = {k: formula.AddVar() for k in candidates}
        label = _labels(formula, candidates, len(candidates))
        # Some target is on the path.
        yield from Or(*(on_path[k] for k in self.targets if k in candidates)).constraint_clauses(formula)
        sources = set(self.sources)
        for k in candidates:
            # Path vertices are present.
            yield (~on_path[k], present[k])
            # Every path vertex other than a source has a path neighbor with a smaller label.
            if k not in sources:
                parents = [And(on_path[n], label[n] < label[k]) for n in g.neighbors[k]]
                yield from Or(~on_path[k], *parents).constraint_clauses(formula)
