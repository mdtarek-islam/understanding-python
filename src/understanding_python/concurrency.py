"""Workloads and runners for the concurrency notebook.

Worker functions live here, not in the notebook, so `multiprocessing` can import
them in a spawned child process (the only start method on Windows and macOS).
"""
from __future__ import annotations

import asyncio
import math
import sys
import threading
import time
from collections.abc import Callable, Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    for d in range(3, math.isqrt(n) + 1, 2):
        if n % d == 0:
            return False
    return True


def count_primes(bounds: tuple[int, int]) -> int:
    """CPU-bound: count primes in [lo, hi). Takes one tuple so pools can map it."""
    lo, hi = bounds
    return sum(1 for n in range(lo, hi) if is_prime(n))


def blocking_io(seconds: float) -> float:
    """Stand-in for a network call. `time.sleep` releases the GIL like a socket read."""
    time.sleep(seconds)
    return seconds


async def async_io(seconds: float) -> float:
    await asyncio.sleep(seconds)
    return seconds


async def gather_io(delays: Sequence[float], limit: int | None = None) -> list[float]:
    """Run all delays concurrently. `limit` caps in-flight tasks with a semaphore."""
    sem = asyncio.Semaphore(limit) if limit else None

    async def one(d: float) -> float:
        if sem is None:
            return await async_io(d)
        async with sem:
            return await async_io(d)

    return await asyncio.gather(*(one(d) for d in delays))


async def ticker(interval: float, stop: asyncio.Event) -> int:
    """Count loop wake-ups. A blocking call elsewhere starves this counter."""
    ticks = 0
    while not stop.is_set():
        await asyncio.sleep(interval)
        ticks += 1
    return ticks


async def ticks_during(blocking: Callable[[], object], offload: bool) -> int:
    """Run `blocking` while a ticker runs. Offloading to a thread keeps the loop alive."""
    stop = asyncio.Event()
    task = asyncio.create_task(ticker(0.01, stop))
    await asyncio.sleep(0)
    if offload:
        await asyncio.to_thread(blocking)
    else:
        blocking()
    stop.set()
    return await task


def sleep_blocking_100ms() -> None:
    time.sleep(0.1)


def timed[T](fn: Callable[[], T]) -> tuple[T, float]:
    start = time.perf_counter()
    result = fn()
    return result, time.perf_counter() - start


def run_sequential(fn: Callable, jobs: Iterable) -> list:
    return [fn(j) for j in jobs]


def run_threads(fn: Callable, jobs: Sequence, workers: int) -> list:
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fn, jobs))


def run_processes(fn: Callable, jobs: Sequence, workers: int) -> list:
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fn, jobs))


class Counter:
    value = 0


def racy_increment(counter: Counter, times: int, pause: bool = False) -> None:
    """Read, add, write as three separate steps: a thread switch between them loses updates.

    `pause` adds `time.sleep(0)` between read and write. It stands in for any call that
    yields the GIL there (I/O, logging, a C call) and widens the race window.
    """
    for _ in range(times):
        current = counter.value
        if pause:
            time.sleep(0)
        counter.value = current + 1


def locked_increment(counter: Counter, times: int, lock: threading.Lock, pause: bool = False) -> None:
    for _ in range(times):
        with lock:
            current = counter.value
            if pause:
                time.sleep(0)
            counter.value = current + 1


def hammer(threads: int, times: int, locked: bool, pause: bool = False, switch_interval: float = 1e-6) -> int:
    """Return the final counter value. Anything below threads * times is a lost update."""
    counter, lock = Counter(), threading.Lock()
    old = sys.getswitchinterval()
    sys.setswitchinterval(switch_interval)
    try:
        if locked:
            ts = [threading.Thread(target=locked_increment, args=(counter, times, lock, pause)) for _ in range(threads)]
        else:
            ts = [threading.Thread(target=racy_increment, args=(counter, times, pause)) for _ in range(threads)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
    finally:
        sys.setswitchinterval(old)
    return counter.value


def split_range(lo: int, hi: int, parts: int) -> list[tuple[int, int]]:
    """Split [lo, hi) into `parts` contiguous, near-equal ranges."""
    if parts < 1:
        raise ValueError("parts must be at least 1")
    step, extra = divmod(hi - lo, parts)
    out, start = [], lo
    for i in range(parts):
        end = start + step + (1 if i < extra else 0)
        out.append((start, end))
        start = end
    return out
