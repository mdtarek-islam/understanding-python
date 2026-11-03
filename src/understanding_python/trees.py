"""Binary-tree utilities: construction, traversals and ancestor queries."""
from __future__ import annotations

from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(slots=True)
class TreeNode:
    key: int
    left: "TreeNode | None" = None
    right: "TreeNode | None" = None


def from_sorted(keys: Sequence[int]) -> TreeNode | None:
    """Build a height-balanced BST from sorted keys in O(n)."""

    def build(lo: int, hi: int) -> TreeNode | None:
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        return TreeNode(keys[mid], build(lo, mid - 1), build(mid + 1, hi))

    return build(0, len(keys) - 1)


def insert_unbalanced(root: TreeNode | None, key: int) -> TreeNode:
    """Plain BST insert, iterative. Duplicates are ignored."""
    node = TreeNode(key)
    if root is None:
        return node
    cur = root
    while True:
        if key == cur.key:
            return root
        side = "left" if key < cur.key else "right"
        nxt = getattr(cur, side)
        if nxt is None:
            setattr(cur, side, node)
            return root
        cur = nxt


def height(root: TreeNode | None) -> int:
    """Number of nodes on the longest root-to-leaf path. Iterative, so deep trees are safe."""
    return len(level_order(root))


def level_order(root: TreeNode | None) -> list[list[int]]:
    """Keys grouped by depth: the BFS view of a tree."""
    out: list[list[int]] = []
    q = deque([root] if root else [])
    while q:
        out.append([])
        for _ in range(len(q)):
            n = q.popleft()
            out[-1].append(n.key)
            q.extend(c for c in (n.left, n.right) if c)
    return out


def inorder(root: TreeNode | None) -> list[int]:
    """Iterative inorder traversal with an explicit stack."""
    out: list[int] = []
    stack: list[TreeNode] = []
    cur = root
    while stack or cur:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        out.append(cur.key)
        cur = cur.right
    return out


def is_valid_bst(root: TreeNode | None) -> bool:
    """Check every key against the open interval its ancestors allow."""
    stack = [(root, float("-inf"), float("inf"))]
    while stack:
        n, lo, hi = stack.pop()
        if n is None:
            continue
        if not lo < n.key < hi:
            return False
        stack.append((n.left, lo, n.key))
        stack.append((n.right, n.key, hi))
    return True


def lowest_common_ancestor(root: TreeNode | None, a: int, b: int) -> int | None:
    """LCA in a BST in O(h): walk down until the keys split."""
    n = root
    while n:
        if a < n.key and b < n.key:
            n = n.left
        elif a > n.key and b > n.key:
            n = n.right
        else:
            return n.key
    return None
