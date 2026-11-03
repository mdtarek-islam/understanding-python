"""Dunder protocols, descriptors, slots, records and registry/state patterns."""
from __future__ import annotations

from dataclasses import dataclass


class Playlist:
    """Sequence protocol in four dunders: len(), indexing, `in` and iteration follow."""

    def __init__(self, tracks: list[str]) -> None:
        self._tracks = list(tracks)

    def __len__(self) -> int:
        return len(self._tracks)

    def __getitem__(self, index: int | slice) -> "str | Playlist":
        if isinstance(index, slice):
            return Playlist(self._tracks[index])
        return self._tracks[index]

    def __contains__(self, track: object) -> bool:
        return track in self._tracks

    def __repr__(self) -> str:
        return f"Playlist({self._tracks!r})"


class Positive:
    """Data descriptor: validates on assignment for every instance of the owner class."""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = "_" + name

    def __get__(self, obj: object, objtype: type | None = None) -> float:
        if obj is None:
            return self  # type: ignore[return-value]
        return getattr(obj, self.name)

    def __set__(self, obj: object, value: float) -> None:
        if value <= 0:
            raise ValueError(f"{self.name[1:]} must be positive, got {value}")
        setattr(obj, self.name, value)


class LineItem:
    qty = Positive()
    unit_price = Positive()

    def __init__(self, sku: str, qty: int, unit_price: float) -> None:
        self.sku, self.qty, self.unit_price = sku, qty, unit_price

    @property
    def subtotal(self) -> float:
        return round(self.qty * self.unit_price, 2)


@dataclass(frozen=True, slots=True)
class OrderLine:
    sku: str
    qty: int
    unit_price: float


@dataclass(frozen=True, slots=True)
class Order:
    order_id: str
    customer: str
    lines: tuple[OrderLine, ...]

    def total(self) -> float:
        return round(sum(line.qty * line.unit_price for line in self.lines), 2)


class PlainPoint:
    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y


class SlotPoint:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y


class PaymentMethod:
    """Registry pattern: subclasses register themselves through `__init_subclass__`."""

    registry: dict[str, type["PaymentMethod"]] = {}

    def __init_subclass__(cls, key: str = "", **kw: object) -> None:
        super().__init_subclass__(**kw)
        if key:
            PaymentMethod.registry[key] = cls

    @classmethod
    def create(cls, key: str) -> "PaymentMethod":
        try:
            return cls.registry[key]()
        except KeyError:
            raise ValueError(f"unknown payment method {key!r}; known: {sorted(cls.registry)}") from None

    def fee(self, amount: float) -> float:
        raise NotImplementedError


class Card(PaymentMethod, key="card"):
    def fee(self, amount: float) -> float:
        return round(amount * 0.029 + 0.30, 2)


class BankTransfer(PaymentMethod, key="bank"):
    def fee(self, amount: float) -> float:
        return 0.80


class OrderStateMachine:
    """State pattern as a transition table: illegal moves raise instead of corrupting data."""

    TRANSITIONS = {
        "placed": {"paid", "cancelled"},
        "paid": {"shipped", "refunded"},
        "shipped": {"delivered"},
        "delivered": set(),
        "cancelled": set(),
        "refunded": set(),
    }

    def __init__(self) -> None:
        self.state = "placed"
        self.history = ["placed"]

    def move(self, new_state: str) -> None:
        if new_state not in self.TRANSITIONS[self.state]:
            raise ValueError(f"cannot move from {self.state} to {new_state}")
        self.state = new_state
        self.history.append(new_state)
