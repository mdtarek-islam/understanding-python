"""Sorting and searching algorithms with their invariants."""
from __future__ import annotations

import random
from typing import Callable, Optional, Sequence


def insertion_sort(a: Sequence[int]) -> list[int]:
    """O(n^2) worst case, O(n) when sorted. Stable and in place on the copy."""
    a = list(a)
    for i in range(1, len(a)):
        key, j = a[i], i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def merge_sort(a: Sequence[int]) -> list[int]:
    """O(n log n) always. Stable. Uses O(n) extra space."""
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])
    out: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def quick_sort(a: Sequence[int], seed: int = 0) -> list[int]:
    """Randomised quicksort: expected O(n log n), worst O(n^2)."""
    rng = random.Random(seed)
    a = list(a)

    def go(lo: int, hi: int) -> None:
        while lo < hi:
            p = a[rng.randint(lo, hi)]
            i, j = lo, hi
            while i <= j:
                while a[i] < p:
                    i += 1
                while a[j] > p:
                    j -= 1
                if i <= j:
                    a[i], a[j] = a[j], a[i]
                    i, j = i + 1, j - 1
            if j - lo < hi - i:
                go(lo, j)
                lo = i
            else:
                go(i, hi)
                hi = j

    go(0, len(a) - 1)
    return a


def heap_sort(a: Sequence[int]) -> list[int]:
    """O(n log n) worst case, in place, not stable."""
    a = list(a)
    n = len(a)

    def sift(i: int, end: int) -> None:
        while True:
            c = 2 * i + 1
            if c >= end:
                return
            if c + 1 < end and a[c + 1] > a[c]:
                c += 1
            if a[i] >= a[c]:
                return
            a[i], a[c] = a[c], a[i]
            i = c

    for i in range(n // 2 - 1, -1, -1):
        sift(i, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift(0, end)
    return a


def counting_sort(a: Sequence[int], k: int) -> list[int]:
    """Sort values in range(k) in O(n + k). Beats the comparison bound."""
    counts = [0] * k
    for x in a:
        counts[x] += 1
    return [v for v, c in enumerate(counts) for _ in range(c)]


def is_sorted(a: Sequence[int]) -> bool:
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


def binary_search(a: Sequence[int], target: int) -> int:
    """Return an index of target or -1. Invariant: target lies in a[lo:hi]."""
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo if lo < len(a) and a[lo] == target else -1


def lower_bound(a: Sequence[int], target: int) -> int:
    """First index i with a[i] >= target."""
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def search_on_answer(pred: Callable[[int], bool], lo: int, hi: int) -> int:
    """Smallest x in [lo, hi] with pred(x) True, given pred is monotone. Else hi + 1."""
    hi += 1
    while lo < hi:
        mid = (lo + hi) // 2
        if pred(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def count_comparisons(sorter: Callable[[list], list], data: list[int]) -> Optional[int]:
    """Count element comparisons by wrapping values in a counting class."""
    counter = [0]

    class W:
        __slots__ = ("v",)

        def __init__(self, v: int) -> None:
            self.v = v

        def __lt__(self, o: "W") -> bool:
            counter[0] += 1
            return self.v < o.v

        def __gt__(self, o: "W") -> bool:
            counter[0] += 1
            return self.v > o.v

        def __le__(self, o: "W") -> bool:
            counter[0] += 1
            return self.v <= o.v

        def __ge__(self, o: "W") -> bool:
            counter[0] += 1
            return self.v >= o.v

    sorter([W(x) for x in data])
    return counter[0]
