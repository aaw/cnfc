import argparse
from itertools import combinations

from cnfc import *


def make_edge(u,v):
    if u < v: return (u,v)
    return (v,u)


def encode(n, k, _lambda, mu):
    formula = Formula(FileBuffer)

    # edges[(u,v)] for (u < v) is true exactly when (u,v) is an edge in the graph.
    edges = {}
    for u,v in combinations(range(n), 2):
        edges[(u,v)] = formula.AddVar(f'edge:{u}:{v}')

    # Constraint: each vertex has degree k
    for u in range(n):
        edge_vars = [edges[(x,y)] for x,y in combinations(range(n), 2) if x == u or y == u]
        formula.Add(NumTrue(*edge_vars) == k)

    # Constraint: each pair of adjacent vertices has _lambda mutual neighbors.
    # Constraint: each pair of non-adjacent vertices has mu mutual neighbors.
    for u,v in combinations(range(n), 2):
        mutual_neighbors = [And(edges[make_edge(u,x)], edges[make_edge(v,x)]) for x in range(n) if x != u and x != v]
        formula.Add(If(edges[(u,v)], NumTrue(*mutual_neighbors) == _lambda))
        formula.Add(If(~edges[(u,v)], NumTrue(*mutual_neighbors) == mu))

    return formula


def print_solution(sol, *extra_args):
    from itertools import combinations
    n, k, _lambda, mu = extra_args
    print(f"Strongly regular graph with parameters ({n}, {k}, {_lambda}, {mu}):")
    for u,v in combinations(range(n), 2):
        if sol[f"edge:{u}:{v}"]:
            print(f"  {{{u},{v}}}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Search for strongly regular graphs.")
    parser.add_argument('n', type=int, help="Number of vertices.")
    parser.add_argument('k', type=int, help="Common degree of each vertex.")
    parser.add_argument('_lambda', type=int, help="Common number of mutual neighbors for every pair of adjacent vertices.")
    parser.add_argument('mu', type=int, help="Common number of mutual neighbors for every pair of non-adjacent vertices.")
    parser.add_argument('outfile', type=str, help='Path to output CNF file.')
    parser.add_argument('extractor', type=str, help='Path to output extractor script.')
    args = parser.parse_args()

    assert args.n > 0, "n must be positive"
    assert args.k >= 0, "k must be non-negative"
    assert args._lambda >= 0, "lambda must be non-negative"
    assert args.mu >= 0, "mu must be non-negatives"

    formula = encode(args.n, args.k, args._lambda, args.mu)
    with open(args.outfile, 'w') as f:
        formula.WriteCNF(f)
    with open(args.extractor, 'w') as f:
        formula.WriteExtractor(f, print_solution, [], extra_args=[args.n, args.k, args._lambda, args.mu])
