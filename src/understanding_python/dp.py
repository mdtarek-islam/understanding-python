"""Dynamic programming classics."""
from __future__ import annotations

from bisect import bisect_left
from functools import lru_cache


def lis_length(a: list[int]) -> int:
    """Longest strictly increasing subsequence in O(n log n) with patience tails."""
    tails: list[int] = []
    for x in a:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def lis_quadratic(a: list[int]) -> int:
    """Reference O(n^2) table: best[i] = 1 + max(best[j]) for j < i, a[j] < a[i]."""
    best = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i]:
                best[i] = max(best[i], best[j] + 1)
    return max(best, default=0)


def knapsack(weights: list[int], values: list[int], cap: int) -> int:
    """0/1 knapsack in O(n * cap) time and O(cap) space."""
    dp = [0] * (cap + 1)
    for w, v in zip(weights, values):
        for c in range(cap, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[cap]


def knapsack_brute(weights: list[int], values: list[int], cap: int) -> int:
    best = 0
    n = len(weights)
    for mask in range(1 << n):
        w = sum(weights[i] for i in range(n) if mask >> i & 1)
        if w <= cap:
            best = max(best, sum(values[i] for i in range(n) if mask >> i & 1))
    return best


def edit_distance(s: str, t: str) -> int:
    """Levenshtein distance in O(len(s) * len(t)) time, O(len(t)) space."""
    prev = list(range(len(t) + 1))
    for i, a in enumerate(s, 1):
        cur = [i]
        for j, b in enumerate(t, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a != b)))
        prev = cur
    return prev[-1]


def fib_naive(n: int) -> int:
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)


@lru_cache(maxsize=None)
def fib_memo(n: int) -> int:
    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)


def fib_table(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
