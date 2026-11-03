"""Generics and Protocols written with PEP 695 syntax (Python 3.12 and newer)."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import Protocol, runtime_checkable


class Comparable(Protocol):
    """Anything that supports `<`. Satisfied structurally, with no inheritance."""

    def __lt__(self, other: object, /) -> bool: ...


@runtime_checkable
class Closeable(Protocol):
    """Anything with a zero-argument `close` method."""

    def close(self) -> None: ...


type Pair[K, V] = tuple[K, V]
type Handler[E] = Callable[[E], None]


class TypedStack[T]:
    """LIFO stack. `TypedStack[int]` tells a checker the element type; runtime ignores it."""

    def __init__(self, items: Iterable[T] = ()) -> None:
        self._items: list[T] = list(items)

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return reversed(self._items)


def max_of[T: Comparable](items: Iterable[T]) -> T:
    """Return the largest item. Raise ValueError on empty input."""
    it = iter(items)
    try:
        best = next(it)
    except StopIteration:
        raise ValueError("max_of() of empty iterable") from None
    for item in it:
        if best < item:
            best = item
    return best


def first_or[T, D](items: Iterable[T], default: D) -> T | D:
    """Return the first item, or `default` when `items` is empty."""
    return next(iter(items), default)


def concat[S: (str, bytes)](a: S, b: S) -> S:
    """Constrained type variable: both arguments share one of the listed types."""
    return a + b


def close_all(resources: Iterable[object]) -> list[str]:
    """Close every resource that satisfies `Closeable`. Return the type names skipped."""
    skipped: list[str] = []
    for res in resources:
        if isinstance(res, Closeable):
            res.close()
        else:
            skipped.append(type(res).__name__)
    return skipped


class Repository[K, V](Protocol):
    """Storage contract the service layer depends on."""

    def get(self, key: K) -> V | None: ...
    def put(self, key: K, value: V) -> None: ...


class InMemoryRepository[K, V]:
    """Test double that satisfies `Repository` without inheriting from it."""

    def __init__(self) -> None:
        self._data: dict[K, V] = {}

    def get(self, key: K) -> V | None:
        return self._data.get(key)

    def put(self, key: K, value: V) -> None:
        self._data[key] = value


def cache_user[K, V](repo: Repository[K, V], key: K, value: V) -> V:
    """Store `value` once and return what the repository holds."""
    if (hit := repo.get(key)) is not None:
        return hit
    repo.put(key, value)
    return value
