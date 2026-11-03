"""Closures, decorators, generators and context managers."""
from __future__ import annotations

import contextlib
import functools
import time
from collections.abc import Callable, Iterable, Iterator
from typing import Any


def make_counter(start: int = 0) -> Callable[[], int]:
    """Return a counter closure. The cell variable `count` survives the call."""
    count = start

    def tick() -> int:
        nonlocal count
        count += 1
        return count

    return tick


def memoize(func: Callable[..., Any]) -> Callable[..., Any]:
    """Cache results by positional arguments."""
    cache: dict[tuple[Any, ...], Any] = {}

    @functools.wraps(func)
    def wrapper(*args: Any) -> Any:
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    wrapper.cache = cache  # type: ignore[attr-defined]
    return wrapper


def repeat(times: int) -> Callable[[Callable[..., Any]], Callable[..., list[Any]]]:
    """Decorator factory: call the wrapped function `times` times."""

    def deco(func: Callable[..., Any]) -> Callable[..., list[Any]]:
        @functools.wraps(func)
        def wrapper(*a: Any, **k: Any) -> list[Any]:
            return [func(*a, **k) for _ in range(times)]

        return wrapper

    return deco


def fib_gen(limit: int) -> Iterator[int]:
    """Yield Fibonacci numbers below `limit`."""
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b


def running_mean() -> Iterator[float]:
    """Coroutine-style generator: send values, receive the running mean."""
    total, n, mean = 0.0, 0, 0.0
    while True:
        value = yield mean
        total += value
        n += 1
        mean = total / n


class Countdown:
    """Iterator protocol with __iter__ and __next__."""

    def __init__(self, start: int) -> None:
        self.current = start

    def __iter__(self) -> "Countdown":
        return self

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1


@contextlib.contextmanager
def timer(out: dict[str, float]) -> Iterator[None]:
    """Store elapsed seconds in `out['elapsed']`, even when the body raises."""
    start = time.perf_counter()
    try:
        yield
    finally:
        out["elapsed"] = time.perf_counter() - start


class Suppress:
    """Class-based context manager that swallows one exception type."""

    def __init__(self, exc: type[BaseException]) -> None:
        self.exc = exc

    def __enter__(self) -> "Suppress":
        return self

    def __exit__(self, et: Any, ev: Any, tb: Any) -> bool:
        return et is not None and issubclass(et, self.exc)


def retry[**P, R](
    attempts: int = 3, exceptions: tuple[type[BaseException], ...] = (Exception,)
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Retry a call up to `attempts` times, re-raising the last failure.

    `ParamSpec` (`**P`) keeps the wrapped signature visible to type checkers.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    def deco(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last: BaseException | None = None
            for _ in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last = exc
            assert last is not None
            raise last

        return wrapper

    return deco


def chunked[T](items: Iterable[T], size: int) -> Iterator[list[T]]:
    """Yield lists of at most `size` items. The last chunk may be shorter."""
    if size < 1:
        raise ValueError("size must be at least 1")
    batch: list[T] = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def parse_log_line(line: str) -> dict[str, str] | None:
    """Parse `<date> <time> <LEVEL> <service> <message>`. Return None for malformed lines."""
    parts = line.split(maxsplit=4)
    if len(parts) < 5:
        return None
    date, clock, level, service, message = parts
    return {"ts": f"{date}T{clock}", "level": level, "service": service, "message": message}


def log_records(lines: Iterable[str], level: str | None = None) -> Iterator[dict[str, str]]:
    """Lazily parse log lines, skipping malformed ones and filtering by level."""
    for line in lines:
        rec = parse_log_line(line.rstrip("\n"))
        if rec is not None and (level is None or rec["level"] == level):
            yield rec


class Transaction:
    """Context manager over a dict: commit on success, roll back on any exception."""

    def __init__(self, store: dict[str, Any]) -> None:
        self.store = store
        self._snapshot: dict[str, Any] = {}

    def __enter__(self) -> dict[str, Any]:
        self._snapshot = dict(self.store)
        return self.store

    def __exit__(self, et: Any, ev: Any, tb: Any) -> bool:
        if et is not None:
            self.store.clear()
            self.store.update(self._snapshot)
        return False
