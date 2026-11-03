"""Closures, decorators, generators and context managers."""
from __future__ import annotations

import contextlib
import functools
import time
from typing import Any, Callable, Iterator


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
