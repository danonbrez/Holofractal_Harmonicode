from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .types import RGBA16


class MaterialError(ValueError):
    pass


@dataclass(frozen=True)
class GradientStop:
    position_q16: int
    color: RGBA16

    def __post_init__(self) -> None:
        if not isinstance(self.position_q16, int) or isinstance(self.position_q16, bool):
            raise MaterialError("P179_GRADIENT_POSITION_INTEGER_REQUIRED")
        if not 0 <= self.position_q16 <= 65536:
            raise MaterialError("P179_GRADIENT_POSITION_RANGE")


def phase_color(phase216: int) -> RGBA16:
    if not isinstance(phase216, int) or isinstance(phase216, bool) or not 0 <= phase216 <= 215:
        raise MaterialError("P179_PHASE216_RANGE")
    return RGBA16(
        (phase216 * 257) % 65536,
        ((phase216 * 109 + 72) * 257) % 65536,
        ((phase216 * 53 + 144) * 257) % 65536,
        65535,
    )


def sample_gradient(stops: Iterable[GradientStop], position_q16: int) -> RGBA16:
    ordered = sorted(stops, key=lambda stop: stop.position_q16)
    if not ordered:
        raise MaterialError("P179_GRADIENT_EMPTY")
    if position_q16 <= ordered[0].position_q16:
        return ordered[0].color
    if position_q16 >= ordered[-1].position_q16:
        return ordered[-1].color
    for left, right in zip(ordered, ordered[1:]):
        if left.position_q16 <= position_q16 <= right.position_q16:
            span = right.position_q16 - left.position_q16
            if span == 0:
                return right.color
            offset = position_q16 - left.position_q16
            values = []
            for a, b in zip(left.color.as_tuple(), right.color.as_tuple()):
                values.append(a + ((b - a) * offset + span // 2) // span)
            return RGBA16(*values)
    raise MaterialError("P179_GRADIENT_INTERNAL")
