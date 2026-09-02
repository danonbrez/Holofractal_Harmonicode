from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping, Sequence

Q16_ONE = 1 << 16
MAX_NODES = 8192
MAX_DIMENSION = 1024


class ExactGraphicsValueError(ValueError):
    pass


def reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ExactGraphicsValueError(f"P179_FLOAT_CANONICAL_AUTHORITY_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            reject_float(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            reject_float(item, f"{path}[{index}]")


def q16(value: int | str | Fraction) -> int:
    if isinstance(value, bool):
        raise ExactGraphicsValueError("P179_BOOLEAN_NOT_NUMERIC")
    if isinstance(value, int):
        return value * Q16_ONE
    if isinstance(value, str):
        raw = value.strip()
        if "/" in raw:
            n, d = raw.split("/", 1)
            value = Fraction(int(n), int(d))
        else:
            value = Fraction(int(raw), 1)
    if isinstance(value, Fraction):
        scaled = value * Q16_ONE
        if scaled.denominator != 1:
            raise ExactGraphicsValueError("P179_Q16_VALUE_NOT_EXACTLY_REPRESENTABLE")
        return int(scaled.numerator)
    raise ExactGraphicsValueError("P179_UNSUPPORTED_EXACT_VALUE")


def pixel_floor(value_q16: int) -> int:
    return int(value_q16) // Q16_ONE


@dataclass(frozen=True)
class RGBA16:
    r: int
    g: int
    b: int
    a: int = 65535

    def __post_init__(self) -> None:
        for name, value in zip(("r", "g", "b", "a"), self.as_tuple()):
            if not isinstance(value, int) or isinstance(value, bool) or not (0 <= value <= 65535):
                raise ExactGraphicsValueError(f"P179_RGBA16_RANGE:{name}")

    def as_tuple(self) -> tuple[int, int, int, int]:
        return (self.r, self.g, self.b, self.a)


@dataclass(frozen=True)
class GraphicsNode:
    node_id: str
    kind: str
    x_q16: int
    y_q16: int
    w_q16: int
    h_q16: int
    color: RGBA16
    layer: int = 0

    def __post_init__(self) -> None:
        if not self.node_id or len(self.node_id) > 128:
            raise ExactGraphicsValueError("P179_NODE_ID_INVALID")
        if self.kind not in {"RECT", "POINT"}:
            raise ExactGraphicsValueError("P179_NODE_KIND_INVALID")
        for value in (self.x_q16, self.y_q16, self.w_q16, self.h_q16, self.layer):
            if not isinstance(value, int) or isinstance(value, bool):
                raise ExactGraphicsValueError("P179_NODE_INTEGER_REQUIRED")
        if self.w_q16 < 0 or self.h_q16 < 0:
            raise ExactGraphicsValueError("P179_NODE_NEGATIVE_EXTENT")


def rgba16(value: Sequence[int]) -> RGBA16:
    if len(value) != 4:
        raise ExactGraphicsValueError("P179_RGBA16_ARITY")
    return RGBA16(*(int(v) for v in value))
