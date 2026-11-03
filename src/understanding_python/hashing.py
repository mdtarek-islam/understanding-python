"""Growable array, open-addressing hash map and LRU cache."""
from __future__ import annotations

from typing import Any


class DynamicArray:
    """Growable array over a fixed-size slot list. Geometric growth gives amortised O(1) append."""

    def __init__(self, growth: int = 2) -> None:
        if growth < 2:
            raise ValueError("growth factor must be at least 2")
        self._growth = growth
        self._slots: list[Any] = [None]
        self._n = 0
        self.resizes: list[int] = []  # capacity after each resize

    @property
    def capacity(self) -> int:
        return len(self._slots)

    def __len__(self) -> int:
        return self._n

    def __getitem__(self, i: int) -> Any:
        if not -self._n <= i < self._n:
            raise IndexError("index out of range")
        return self._slots[i % self._n]

    def append(self, x: Any) -> None:
        if self._n == len(self._slots):
            self._slots.extend([None] * (len(self._slots) * (self._growth - 1)))
            self.resizes.append(len(self._slots))
        self._slots[self._n] = x
        self._n += 1

    def insert(self, i: int, x: Any) -> None:
        """Insert before index i. O(n) because the tail shifts right."""
        if not 0 <= i <= self._n:
            raise IndexError("index out of range")
        self.append(None)
        for j in range(self._n - 1, i, -1):
            self._slots[j] = self._slots[j - 1]
        self._slots[i] = x


_EMPTY, _TOMB = object(), object()


class OpenAddressingMap:
    """Hash map with linear probing and tombstones. Resizes above 2/3 load."""

    def __init__(self, cap: int = 8) -> None:
        self._keys: list[Any] = [_EMPTY] * cap
        self._vals: list[Any] = [None] * cap
        self._used = 0  # live keys plus tombstones: both lengthen probe chains
        self._live = 0
        self.probes = 0

    def __len__(self) -> int:
        return self._live

    @property
    def capacity(self) -> int:
        return len(self._keys)

    def _find(self, k: Any) -> int:
        """Return the slot holding k, or the first reusable slot where k belongs."""
        cap = len(self._keys)
        i, first_tomb = hash(k) % cap, -1
        while True:
            self.probes += 1
            cur = self._keys[i]
            if cur is _EMPTY:
                return first_tomb if first_tomb >= 0 else i
            if cur is _TOMB:
                if first_tomb < 0:
                    first_tomb = i
            elif cur == k:
                return i
            i = (i + 1) % cap

    def _occupied(self, i: int) -> bool:
        return self._keys[i] is not _EMPTY and self._keys[i] is not _TOMB

    def put(self, k: Any, v: Any) -> None:
        if (self._used + 1) * 3 > len(self._keys) * 2:
            self._resize()
        i = self._find(k)
        if self._keys[i] is _EMPTY:
            self._used += 1
            self._live += 1
        elif self._keys[i] is _TOMB:
            self._live += 1
        self._keys[i], self._vals[i] = k, v

    def get(self, k: Any, default: Any = None) -> Any:
        i = self._find(k)
        return self._vals[i] if self._occupied(i) else default

    def delete(self, k: Any) -> bool:
        i = self._find(k)
        if not self._occupied(i):
            return False
        self._keys[i], self._vals[i] = _TOMB, None
        self._live -= 1
        return True

    def _resize(self) -> None:
        old = [(k, v) for i, (k, v) in enumerate(zip(self._keys, self._vals)) if self._occupied(i)]
        cap = len(self._keys) * 2
        self._keys, self._vals = [_EMPTY] * cap, [None] * cap
        self._used = self._live = 0
        for k, v in old:
            self.put(k, v)


class _DNode:
    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key: Any = None, val: Any = None) -> None:
        self.key, self.val = key, val
        self.prev = self.next = self


class LRUCache:
    """Least-recently-used cache: a dict for O(1) lookup, a circular doubly linked list for order."""

    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self._map: dict[Any, _DNode] = {}
        self._head = _DNode()  # sentinel: head.next is newest, head.prev is oldest
        self.hits = self.misses = 0

    @staticmethod
    def _unlink(n: _DNode) -> None:
        n.prev.next, n.next.prev = n.next, n.prev

    def _push_front(self, n: _DNode) -> None:
        n.prev, n.next = self._head, self._head.next
        self._head.next.prev = n
        self._head.next = n

    def get(self, key: Any, default: Any = None) -> Any:
        n = self._map.get(key)
        if n is None:
            self.misses += 1
            return default
        self.hits += 1
        self._unlink(n)
        self._push_front(n)
        return n.val

    def put(self, key: Any, val: Any) -> None:
        n = self._map.get(key)
        if n is not None:
            n.val = val
            self._unlink(n)
        else:
            if len(self._map) == self.capacity:
                oldest = self._head.prev
                self._unlink(oldest)
                del self._map[oldest.key]
            n = self._map[key] = _DNode(key, val)
        self._push_front(n)

    def keys(self) -> list[Any]:
        """Keys from most to least recently used."""
        out, n = [], self._head.next
        while n is not self._head:
            out.append(n.key)
            n = n.next
        return out

    def __len__(self) -> int:
        return len(self._map)
