"""Graph algorithms on adjacency-list dicts."""
from __future__ import annotations

import heapq
from collections import deque
from typing import Hashable

Graph = dict[Hashable, list[Hashable]]
WGraph = dict[Hashable, list[tuple[Hashable, float]]]


def bfs(g: Graph, src: Hashable) -> dict[Hashable, int]:
    """Shortest hop count from src. O(V + E)."""
    dist = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        for v in g.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def dfs(g: Graph, src: Hashable) -> list[Hashable]:
    """Iterative preorder DFS. O(V + E)."""
    seen, order, st = set(), [], [src]
    while st:
        u = st.pop()
        if u in seen:
            continue
        seen.add(u)
        order.append(u)
        st.extend(reversed(g.get(u, [])))
    return order


def dijkstra(g: WGraph, src: Hashable) -> tuple[dict[Hashable, float], dict[Hashable, Hashable]]:
    """Shortest paths for non-negative weights. O((V + E) log V) with a binary heap."""
    dist: dict[Hashable, float] = {src: 0}
    prev: dict[Hashable, Hashable] = {}
    pq: list[tuple[float, int, Hashable]] = [(0, 0, src)]
    tie = 1
    done = set()
    while pq:
        d, _, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        for v, w in g.get(u, []):
            if w < 0:
                raise ValueError("negative edge weight")
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, tie, v))
                tie += 1
    return dist, prev


def path_to(prev: dict[Hashable, Hashable], src: Hashable, dst: Hashable) -> list[Hashable]:
    out = [dst]
    while out[-1] != src:
        out.append(prev[out[-1]])
    return out[::-1]


def topological_sort(g: Graph) -> list[Hashable]:
    """Kahn's algorithm. Raises ValueError on a cycle. O(V + E)."""
    nodes = set(g) | {v for vs in g.values() for v in vs}
    indeg = {n: 0 for n in nodes}
    for vs in g.values():
        for v in vs:
            indeg[v] += 1
    q = deque(sorted((n for n in nodes if indeg[n] == 0), key=str))
    out = []
    while q:
        u = q.popleft()
        out.append(u)
        for v in g.get(u, []):
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    if len(out) != len(nodes):
        raise ValueError("graph has a cycle")
    return out


def kruskal(n: int, edges: list[tuple[int, int, float]]) -> tuple[float, list[tuple[int, int, float]]]:
    """Minimum spanning tree. O(E log E) for the sort."""
    from .structures import UnionFind

    uf = UnionFind(n)
    total, used = 0.0, []
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if uf.union(u, v):
            total += w
            used.append((u, v, w))
    return total, used
