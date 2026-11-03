"""Priority-queue applications built on `heapq`."""
from __future__ import annotations

import heapq
import itertools
from collections.abc import Iterable, Iterator
from typing import Any


def top_k(items: Iterable[tuple[str, float]], k: int) -> list[tuple[str, float]]:
    """Return the k highest-scored items in O(n log k) time and O(k) memory."""
    if k < 1:
        return []
    heap: list[tuple[float, str]] = []
    for name, score in items:
        if len(heap) < k:
            heapq.heappush(heap, (score, name))
        elif score > heap[0][0]:
            heapq.heapreplace(heap, (score, name))
    return [(name, score) for score, name in sorted(heap, reverse=True)]


class RunningMedian:
    """Two heaps: a max-heap (negated) for the lower half, a min-heap for the upper half."""

    def __init__(self) -> None:
        self._low: list[float] = []
        self._high: list[float] = []

    def add(self, x: float) -> None:
        if self._low and x > -self._low[0]:
            heapq.heappush(self._high, x)
        else:
            heapq.heappush(self._low, -x)
        if len(self._low) > len(self._high) + 1:
            heapq.heappush(self._high, -heapq.heappop(self._low))
        elif len(self._high) > len(self._low):
            heapq.heappush(self._low, -heapq.heappop(self._high))

    def median(self) -> float:
        if not self._low:
            raise ValueError("median of empty stream")
        if len(self._low) > len(self._high):
            return -self._low[0]
        return (-self._low[0] + self._high[0]) / 2


def merge_sorted_streams(*streams: Iterable[Any]) -> Iterator[Any]:
    """K-way merge of sorted streams in O(n log k). Same contract as `heapq.merge`."""
    heap: list[tuple[Any, int, Iterator[Any]]] = []
    for idx, stream in enumerate(streams):
        it = iter(stream)
        for first in it:
            heap.append((first, idx, it))
            break
    heapq.heapify(heap)
    while heap:
        value, idx, it = heap[0]
        yield value
        for nxt in it:
            heapq.heapreplace(heap, (nxt, idx, it))
            break
        else:
            heapq.heappop(heap)


class TaskScheduler:
    """Priority queue with FIFO order among equal priorities and lazy cancellation."""

    def __init__(self) -> None:
        self._heap: list[list[Any]] = []
        self._entries: dict[str, list[Any]] = {}
        self._counter = itertools.count()

    def add(self, task: str, priority: int) -> None:
        if task in self._entries:
            self.cancel(task)
        entry = [priority, next(self._counter), task]
        self._entries[task] = entry
        heapq.heappush(self._heap, entry)

    def cancel(self, task: str) -> None:
        entry = self._entries.pop(task)
        entry[2] = None  # tombstone, discarded when it reaches the top

    def pop(self) -> str:
        while self._heap:
            _, _, task = heapq.heappop(self._heap)
            if task is not None:
                del self._entries[task]
                return task
        raise IndexError("pop from empty scheduler")

    def __len__(self) -> int:
        return len(self._entries)
