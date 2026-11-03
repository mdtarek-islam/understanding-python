"""Dunder methods, dataclasses, ABCs and SOLID-style patterns."""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable


class Vector:
    """2D vector with arithmetic and comparison dunders."""

    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y

    def __repr__(self) -> str:
        return f"Vector({self.x!r}, {self.y!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Vector) and (self.x, self.y) == (other.x, other.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, k: float) -> "Vector":
        return Vector(self.x * k, self.y * k)

    __rmul__ = __mul__

    def __abs__(self) -> float:
        return math.hypot(self.x, self.y)

    def __bool__(self) -> bool:
        return bool(self.x or self.y)


@dataclass(frozen=True, order=True)
class Point:
    x: int
    y: int = 0


@dataclass
class Cart:
    items: list[str] = field(default_factory=list)

    def add(self, item: str) -> None:
        self.items.append(item)


class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...


class Rect(Shape):
    def __init__(self, w: float, h: float) -> None:
        self.w, self.h = w, h

    def area(self) -> float:
        return self.w * self.h


class Circle(Shape):
    def __init__(self, r: float) -> None:
        self.r = r

    def area(self) -> float:
        return math.pi * self.r**2


def total_area(shapes: list[Shape]) -> float:
    """Open/closed: new shapes need no change here."""
    return sum(s.area() for s in shapes)


class EventBus:
    """Observer pattern: publishers do not know their subscribers."""

    def __init__(self) -> None:
        self._subs: dict[str, list[Callable[[object], None]]] = {}

    def subscribe(self, topic: str, fn: Callable[[object], None]) -> None:
        self._subs.setdefault(topic, []).append(fn)

    def publish(self, topic: str, payload: object) -> int:
        for fn in self._subs.get(topic, []):
            fn(payload)
        return len(self._subs.get(topic, []))


class Discount(ABC):
    """Strategy interface. Every strategy returns a price at or below the input."""

    @abstractmethod
    def apply(self, price: float) -> float: ...


class NoDiscount(Discount):
    def apply(self, price: float) -> float:
        return price


class Percent(Discount):
    def __init__(self, pct: float) -> None:
        self.pct = pct

    def apply(self, price: float) -> float:
        return price * (1 - self.pct / 100)


class Checkout:
    """Dependency inversion: depends on the Discount abstraction."""

    def __init__(self, discount: Discount) -> None:
        self.discount = discount

    def total(self, prices: list[float]) -> float:
        return round(self.discount.apply(sum(prices)), 2)


class Singleton:
    _instance: "Singleton | None" = None

    def __new__(cls) -> "Singleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


def factory(kind: str) -> Shape:
    """Factory method keyed by name."""
    table: dict[str, Callable[[], Shape]] = {"rect": lambda: Rect(2, 3), "circle": lambda: Circle(1)}
    if kind not in table:
        raise ValueError(f"unknown shape: {kind}")
    return table[kind]()
