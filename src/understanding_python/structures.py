"""Core data structures built from first principles."""
from __future__ import annotations

from collections import deque
from typing import Any, Generic, Iterator, Optional, TypeVar

T = TypeVar("T")


class _Node(Generic[T]):
    __slots__ = ("val", "next")

    def __init__(self, val: T, nxt: "Optional[_Node[T]]" = None) -> None:
        self.val, self.next = val, nxt


class LinkedList(Generic[T]):
    """Singly linked list. push_front is O(1), find is O(n)."""

    def __init__(self) -> None:
        self.head: Optional[_Node[T]] = None
        self._n = 0

    def push_front(self, val: T) -> None:
        self.head = _Node(val, self.head)
        self._n += 1

    def __iter__(self) -> Iterator[T]:
        node = self.head
        while node:
            yield node.val
            node = node.next

    def __len__(self) -> int:
        return self._n

    def reverse(self) -> None:
        prev, cur = None, self.head
        while cur:
            cur.next, prev, cur = prev, cur, cur.next
        self.head = prev

    def remove(self, val: T) -> bool:
        prev, cur = None, self.head
        while cur:
            if cur.val == val:
                if prev:
                    prev.next = cur.next
                else:
                    self.head = cur.next
                self._n -= 1
                return True
            prev, cur = cur, cur.next
        return False


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._d: list[T] = []

    def push(self, x: T) -> None:
        self._d.append(x)

    def pop(self) -> T:
        if not self._d:
            raise IndexError("pop from empty stack")
        return self._d.pop()

    def peek(self) -> T:
        return self._d[-1]

    def __len__(self) -> int:
        return len(self._d)


class Queue(Generic[T]):
    """FIFO queue on collections.deque so that dequeue is O(1)."""

    def __init__(self) -> None:
        self._d: deque[T] = deque()

    def enqueue(self, x: T) -> None:
        self._d.append(x)

    def dequeue(self) -> T:
        if not self._d:
            raise IndexError("dequeue from empty queue")
        return self._d.popleft()

    def __len__(self) -> int:
        return len(self._d)


def balanced(text: str) -> bool:
    """Check bracket balance with a stack in O(n)."""
    pairs = {")": "(", "]": "[", "}": "{"}
    st: Stack[str] = Stack()
    for ch in text:
        if ch in "([{":
            st.push(ch)
        elif ch in pairs:
            if not len(st) or st.pop() != pairs[ch]:
                return False
    return len(st) == 0


class MinHeap:
    """Binary min-heap stored in a list. push and pop are O(log n)."""

    def __init__(self) -> None:
        self.a: list[Any] = []

    def push(self, x: Any) -> None:
        a = self.a
        a.append(x)
        i = len(a) - 1
        while i and a[(i - 1) // 2] > a[i]:
            a[(i - 1) // 2], a[i] = a[i], a[(i - 1) // 2]
            i = (i - 1) // 2

    def pop(self) -> Any:
        a = self.a
        if not a:
            raise IndexError("pop from empty heap")
        top, last = a[0], a.pop()
        if a:
            a[0] = last
            i, n = 0, len(a)
            while True:
                l, r, m = 2 * i + 1, 2 * i + 2, i
                if l < n and a[l] < a[m]:
                    m = l
                if r < n and a[r] < a[m]:
                    m = r
                if m == i:
                    break
                a[i], a[m] = a[m], a[i]
                i = m
        return top

    def __len__(self) -> int:
        return len(self.a)


class HashMap:
    """Separate-chaining hash map with doubling resize. Expected O(1) operations."""

    def __init__(self, cap: int = 8) -> None:
        self._b: list[list[tuple[Any, Any]]] = [[] for _ in range(cap)]
        self._n = 0

    def _bucket(self, k: Any) -> list[tuple[Any, Any]]:
        return self._b[hash(k) % len(self._b)]

    def put(self, k: Any, v: Any) -> None:
        b = self._bucket(k)
        for i, (kk, _) in enumerate(b):
            if kk == k:
                b[i] = (k, v)
                return
        b.append((k, v))
        self._n += 1
        if self._n > 0.75 * len(self._b):
            self._resize()

    def get(self, k: Any, default: Any = None) -> Any:
        for kk, v in self._bucket(k):
            if kk == k:
                return v
        return default

    def delete(self, k: Any) -> bool:
        b = self._bucket(k)
        for i, (kk, _) in enumerate(b):
            if kk == k:
                del b[i]
                self._n -= 1
                return True
        return False

    def _resize(self) -> None:
        old = [kv for b in self._b for kv in b]
        self._b = [[] for _ in range(2 * len(self._b))]
        for k, v in old:
            self._bucket(k).append((k, v))

    def __len__(self) -> int:
        return self._n

    @property
    def capacity(self) -> int:
        return len(self._b)


class BST:
    """Unbalanced binary search tree. O(h) per operation, h up to n."""

    class N:
        __slots__ = ("k", "l", "r")

        def __init__(self, k: Any) -> None:
            self.k, self.l, self.r = k, None, None

    def __init__(self) -> None:
        self.root: Any = None

    def insert(self, k: Any) -> None:
        if self.root is None:
            self.root = BST.N(k)
            return
        cur = self.root
        while True:
            if k == cur.k:
                return
            side = "l" if k < cur.k else "r"
            nxt = getattr(cur, side)
            if nxt is None:
                setattr(cur, side, BST.N(k))
                return
            cur = nxt

    def __contains__(self, k: Any) -> bool:
        cur = self.root
        while cur:
            if k == cur.k:
                return True
            cur = cur.l if k < cur.k else cur.r
        return False

    def inorder(self) -> list[Any]:
        out: list[Any] = []
        st, cur = [], self.root
        while st or cur:
            while cur:
                st.append(cur)
                cur = cur.l
            cur = st.pop()
            out.append(cur.k)
            cur = cur.r
        return out

    def height(self) -> int:
        # Iterative so that a degenerate chain does not hit the recursion limit.
        height, level = 0, [self.root] if self.root else []
        while level:
            height += 1
            level = [c for n in level for c in (n.l, n.r) if c is not None]
        return height


class AVLTree:
    """Self-balancing BST. Height stays below 1.44 log2(n + 2)."""

    class N:
        __slots__ = ("k", "l", "r", "h")

        def __init__(self, k: Any) -> None:
            self.k, self.l, self.r, self.h = k, None, None, 1

    def __init__(self) -> None:
        self.root: Any = None

    @staticmethod
    def _h(n: Any) -> int:
        return n.h if n else 0

    def _fix(self, n: Any) -> None:
        n.h = 1 + max(self._h(n.l), self._h(n.r))

    def _rot_r(self, y: Any) -> Any:
        x = y.l
        y.l, x.r = x.r, y
        self._fix(y)
        self._fix(x)
        return x

    def _rot_l(self, x: Any) -> Any:
        y = x.r
        x.r, y.l = y.l, x
        self._fix(x)
        self._fix(y)
        return y

    def _ins(self, n: Any, k: Any) -> Any:
        if n is None:
            return AVLTree.N(k)
        if k < n.k:
            n.l = self._ins(n.l, k)
        elif k > n.k:
            n.r = self._ins(n.r, k)
        else:
            return n
        self._fix(n)
        bal = self._h(n.l) - self._h(n.r)
        if bal > 1:
            if k > n.l.k:
                n.l = self._rot_l(n.l)
            return self._rot_r(n)
        if bal < -1:
            if k < n.r.k:
                n.r = self._rot_r(n.r)
            return self._rot_l(n)
        return n

    def insert(self, k: Any) -> None:
        self.root = self._ins(self.root, k)

    def __contains__(self, k: Any) -> bool:
        cur = self.root
        while cur:
            if k == cur.k:
                return True
            cur = cur.l if k < cur.k else cur.r
        return False

    def height(self) -> int:
        return self._h(self.root)

    def inorder(self) -> list[Any]:
        out: list[Any] = []

        def walk(n: Any) -> None:
            if n:
                walk(n.l)
                out.append(n.k)
                walk(n.r)

        walk(self.root)
        return out

    def is_balanced(self) -> bool:
        def ok(n: Any) -> bool:
            if n is None:
                return True
            return abs(self._h(n.l) - self._h(n.r)) <= 1 and ok(n.l) and ok(n.r)

        return ok(self.root)


class Trie:
    """Prefix tree. insert and search cost O(len(word))."""

    def __init__(self) -> None:
        self.root: dict[str, Any] = {}

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node["$"] = True

    def _walk(self, s: str) -> Optional[dict[str, Any]]:
        node = self.root
        for ch in s:
            if ch not in node:
                return None
            node = node[ch]
        return node

    def search(self, word: str) -> bool:
        n = self._walk(word)
        return bool(n and "$" in n)

    def starts_with(self, prefix: str) -> bool:
        return self._walk(prefix) is not None

    def with_prefix(self, prefix: str) -> list[str]:
        start = self._walk(prefix)
        out: list[str] = []

        def go(node: dict[str, Any], acc: str) -> None:
            for ch, nxt in sorted(node.items()):
                if ch == "$":
                    out.append(acc)
                else:
                    go(nxt, acc + ch)

        if start is not None:
            go(start, prefix)
        return out


class UnionFind:
    """Disjoint sets with path compression and union by size: O(alpha(n)) amortised."""

    def __init__(self, n: int) -> None:
        self.p = list(range(n))
        self.size = [1] * n
        self.components = n

    def find(self, x: int) -> int:
        root = x
        while self.p[root] != root:
            root = self.p[root]
        while self.p[x] != root:
            self.p[x], x = root, self.p[x]
        return root

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        self.size[ra] += self.size[rb]
        self.components -= 1
        return True
