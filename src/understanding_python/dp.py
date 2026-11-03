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


def fib_calls(n: int) -> int:
    """Number of calls the naive recursion makes: 2 * fib(n + 1) - 1."""
    return 2 * fib_table(n + 1) - 1


def min_coins(coins: list[int], amount: int) -> int:
    """Fewest coins that sum to `amount`, or -1. O(amount * len(coins)) time, O(amount) space.

    Greedy fails for sets such as (1, 3, 4): amount 6 is 3 + 3, not 4 + 1 + 1.
    """
    if amount < 0:
        raise ValueError("amount must be non-negative")
    inf = amount + 1
    best = [0] + [inf] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if 0 < c <= a:
                best[a] = min(best[a], best[a - c] + 1)
    return best[amount] if best[amount] != inf else -1


def lcs(a: str, b: str) -> str:
    """Longest common subsequence, as a diff tool finds it. O(len(a) * len(b)) time and space."""
    rows = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            rows[i][j] = rows[i + 1][j + 1] + 1 if a[i] == b[j] else max(rows[i + 1][j], rows[i][j + 1])
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            out.append(a[i])
            i, j = i + 1, j + 1
        elif rows[i + 1][j] >= rows[i][j + 1]:
            i += 1
        else:
            j += 1
    return "".join(out)


def word_break(text: str, words: set[str]) -> list[str] | None:
    """Split `text` into dictionary words, or return None. O(n * L) for max word length L."""
    longest = max(map(len, words), default=0)
    parts: list[list[str] | None] = [None] * (len(text) + 1)
    parts[0] = []
    for end in range(1, len(text) + 1):
        for start in range(max(0, end - longest), end):
            head = parts[start]
            if head is not None and text[start:end] in words:
                parts[end] = head + [text[start:end]]
                break
    return parts[len(text)]
