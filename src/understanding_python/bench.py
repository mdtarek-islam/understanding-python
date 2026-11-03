"""Timing helpers used by the notebooks. Keep benchmarks short and repeatable."""
from __future__ import annotations

import math
import timeit
from collections.abc import Callable, Sequence


def best_time(fn: Callable[[], object], number: int = 1, repeat: int = 3) -> float:
    """Return the best wall time in seconds over `repeat` runs of `number` calls."""
    return min(timeit.repeat(fn, number=number, repeat=repeat)) / number


def ratio(slow: Callable[[], object], fast: Callable[[], object], number: int = 1) -> float:
    """Return best_time(slow) / best_time(fast)."""
    return best_time(slow, number) / max(best_time(fast, number), 1e-9)


def scaling_table[T](
    fn: Callable[[T], object],
    make_input: Callable[[int], T],
    sizes: Sequence[int],
    number: int = 1,
    repeat: int = 3,
) -> list[tuple[int, float]]:
    """Time `fn(make_input(n))` for each n. Input construction is excluded from the timing."""
    rows = []
    for n in sizes:
        data = make_input(n)
        rows.append((n, best_time(lambda: fn(data), number=number, repeat=repeat)))
    return rows


def fit_exponent(rows: Sequence[tuple[int, float]]) -> float:
    """Least-squares slope of log(time) against log(n): about 1 for O(n), 2 for O(n^2)."""
    pts = [(math.log(n), math.log(t)) for n, t in rows if n > 0 and t > 0]
    if len(pts) < 2:
        raise ValueError("need at least two positive measurements")
    mx = sum(x for x, _ in pts) / len(pts)
    my = sum(y for _, y in pts) / len(pts)
    var = sum((x - mx) ** 2 for x, _ in pts)
    return sum((x - mx) * (y - my) for x, y in pts) / var


def classify(exponent: float) -> str:
    """Name the nearest common growth class for a fitted exponent."""
    if exponent < 0.25:
        return "O(1) or O(log n)"
    if exponent < 1.25:
        return "O(n) or O(n log n)"
    if exponent < 1.75:
        return "between O(n log n) and O(n^2)"
    return "about O(n^2) or worse"
