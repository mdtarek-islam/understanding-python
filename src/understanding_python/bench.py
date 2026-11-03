"""Tiny timing helper used by the notebooks. Keeps benchmarks short and repeatable."""
from __future__ import annotations

import timeit
from typing import Callable


def best_time(fn: Callable[[], object], number: int = 1, repeat: int = 3) -> float:
    """Return the best wall time in seconds over `repeat` runs of `number` calls."""
    return min(timeit.repeat(fn, number=number, repeat=repeat))


def ratio(slow: Callable[[], object], fast: Callable[[], object], number: int = 1) -> float:
    """Return best_time(slow) / best_time(fast)."""
    return best_time(slow, number) / max(best_time(fast, number), 1e-9)
