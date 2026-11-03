"""Helpers for inspecting the CPython object model."""
from __future__ import annotations

import dis
import gc
import io
import sys
from typing import Any, Callable


def refcount(obj: Any) -> int:
    """Return the reference count, minus the temporary reference held by the call."""
    return sys.getrefcount(obj) - 1


def same_object(a: Any, b: Any) -> bool:
    """Return True when both names point at one object (identity, not equality)."""
    return a is b


def deep_size(obj: Any, _seen: set[int] | None = None) -> int:
    """Return the size in bytes of a container and everything it references."""
    seen = _seen if _seen is not None else set()
    if id(obj) in seen:
        return 0
    seen.add(id(obj))
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(deep_size(k, seen) + deep_size(v, seen) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(deep_size(i, seen) for i in obj)
    return size


def opnames(func: Callable[..., Any]) -> list[str]:
    """Return the opcode names of a function in order."""
    return [ins.opname for ins in dis.get_instructions(func)]


def disassemble(func: Callable[..., Any]) -> str:
    """Return the dis listing of a function as text."""
    buf = io.StringIO()
    dis.dis(func, file=buf)
    return buf.getvalue()


class Tracked:
    """Object that records when the interpreter reclaims it."""

    reclaimed: list[str] = []

    def __init__(self, name: str) -> None:
        self.name = name

    def __del__(self) -> None:
        Tracked.reclaimed.append(self.name)


def make_cycle(name: str) -> None:
    """Create a reference cycle that only the cyclic collector can free."""
    a, b = Tracked(name + "-a"), Tracked(name + "-b")
    a.other, b.other = b, a  # type: ignore[attr-defined]


def collect() -> int:
    """Run a full collection and return the number of unreachable objects found."""
    return gc.collect()
