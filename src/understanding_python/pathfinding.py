"""Road network data and best-first search (A*, and Dijkstra as A* with a zero heuristic)."""
from __future__ import annotations

import heapq
import math
from collections.abc import Callable, Hashable, Iterable

CITY_COORDS: dict[str, tuple[float, float]] = {
    "London": (51.507, -0.128),
    "Bristol": (51.454, -2.587),
    "Cardiff": (51.481, -3.179),
    "Birmingham": (52.486, -1.890),
    "Nottingham": (52.954, -1.150),
    "Liverpool": (53.408, -2.992),
    "Manchester": (53.481, -2.243),
    "Sheffield": (53.381, -1.470),
    "Leeds": (53.800, -1.549),
    "Newcastle": (54.978, -1.618),
    "Carlisle": (54.892, -2.944),
    "Edinburgh": (55.953, -3.189),
    "Glasgow": (55.864, -4.252),
}

# Approximate driving distances in km. Each is at least the straight-line distance,
# which keeps the haversine heuristic admissible.
_ROADS = [
    ("London", "Bristol", 190), ("London", "Birmingham", 190), ("London", "Nottingham", 200),
    ("Bristol", "Cardiff", 70), ("Bristol", "Birmingham", 140), ("Cardiff", "Birmingham", 185),
    ("Birmingham", "Nottingham", 80), ("Birmingham", "Manchester", 140), ("Birmingham", "Sheffield", 115),
    ("Nottingham", "Sheffield", 55), ("Nottingham", "Leeds", 120),
    ("Liverpool", "Manchester", 55), ("Liverpool", "Birmingham", 150),
    ("Manchester", "Sheffield", 60), ("Manchester", "Leeds", 70), ("Manchester", "Carlisle", 190),
    ("Sheffield", "Leeds", 55), ("Leeds", "Newcastle", 150), ("Carlisle", "Newcastle", 90),
    ("Carlisle", "Glasgow", 155), ("Carlisle", "Edinburgh", 155),
    ("Newcastle", "Edinburgh", 170), ("Edinburgh", "Glasgow", 75),
]


def uk_road_graph() -> dict[str, list[tuple[str, float]]]:
    """Undirected weighted adjacency list for the road table above."""
    g: dict[str, list[tuple[str, float]]] = {c: [] for c in CITY_COORDS}
    for a, b, km in _ROADS:
        g[a].append((b, km))
        g[b].append((a, km))
    return g


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Great-circle distance between two (lat, lon) points in km."""
    (la1, lo1), (la2, lo2) = a, b
    p1, p2 = math.radians(la1), math.radians(la2)
    dphi, dlam = p2 - p1, math.radians(lo2 - lo1)
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def astar[N: Hashable](
    neighbours: Callable[[N], Iterable[tuple[N, float]]],
    start: N,
    goal: N,
    heuristic: Callable[[N], float],
) -> tuple[float, list[N], int]:
    """Return (cost, path, nodes_expanded). cost is inf and path empty when unreachable.

    The heuristic must never overestimate the true remaining cost, or the path may
    be suboptimal. A heuristic of `lambda n: 0` makes this exactly Dijkstra.
    """
    best: dict[N, float] = {start: 0.0}
    parent: dict[N, N] = {}
    tie = 0
    frontier: list[tuple[float, int, N]] = [(heuristic(start), tie, start)]
    closed: set[N] = set()
    expanded = 0
    while frontier:
        _, _, node = heapq.heappop(frontier)
        if node in closed:
            continue
        closed.add(node)
        expanded += 1
        if node == goal:
            path = [node]
            while path[-1] in parent:
                path.append(parent[path[-1]])
            return best[node], path[::-1], expanded
        for nxt, w in neighbours(node):
            if w < 0:
                raise ValueError("negative edge weight")
            cost = best[node] + w
            if cost < best.get(nxt, math.inf):
                best[nxt] = cost
                parent[nxt] = node
                tie += 1
                heapq.heappush(frontier, (cost + heuristic(nxt), tie, nxt))
    return math.inf, [], expanded


def grid_neighbours(grid: list[str]) -> Callable[[tuple[int, int]], Iterable[tuple[tuple[int, int], float]]]:
    """4-connected moves on a text grid where '#' is a wall. Each step costs 1."""
    rows, cols = len(grid), len(grid[0])

    def nb(pos: tuple[int, int]) -> Iterable[tuple[tuple[int, int], float]]:
        r, c = pos
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#":
                yield (nr, nc), 1.0

    return nb


def manhattan(goal: tuple[int, int]) -> Callable[[tuple[int, int]], float]:
    return lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])
