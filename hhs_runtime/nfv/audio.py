from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable

from .core import LOSHU_TRAVERSAL, NFVError, hash216

SURROUND_LANES = ("x", "y", "z", "w")
ALL_LANES = ("x", "y", "z", "w", "c")
RING_EDGES = (("x", "y"), ("y", "z"), ("z", "w"), ("w", "x"))
CROSS_LINKS = (("x", "z"), ("y", "w"))


@dataclass(frozen=True)
class ExactScalar:
    numerator: int
    denominator: int = 1

    def __post_init__(self) -> None:
        if self.denominator == 0:
            raise NFVError("NFV_ZERO_DENOMINATOR", "exact scalar denominator must not be zero")
        reduced = Fraction(self.numerator, self.denominator)
        object.__setattr__(self, "numerator", reduced.numerator)
        object.__setattr__(self, "denominator", reduced.denominator)

    @classmethod
    def from_fraction(cls, value: Fraction) -> "ExactScalar":
        return cls(value.numerator, value.denominator)

    @property
    def fraction(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)

    def add(self, other: "ExactScalar") -> "ExactScalar":
        return self.from_fraction(self.fraction + other.fraction)

    def subtract(self, other: "ExactScalar") -> "ExactScalar":
        return self.from_fraction(self.fraction - other.fraction)

    def multiply(self, other: "ExactScalar") -> "ExactScalar":
        return self.from_fraction(self.fraction * other.fraction)

    def divide(self, other: "ExactScalar") -> "ExactScalar":
        if other.numerator == 0:
            raise NFVError("NFV_DIVISION_BY_ZERO", "exact scalar divisor must not be zero")
        return self.from_fraction(self.fraction / other.fraction)

    def negate(self) -> "ExactScalar":
        return ExactScalar(-self.numerator, self.denominator)

    def to_dict(self) -> dict[str, int]:
        return {"numerator": self.numerator, "denominator": self.denominator}


ZERO = ExactScalar(0)
ONE = ExactScalar(1)


def _exact_tuple(values: Iterable[ExactScalar | int | tuple[int, int]]) -> tuple[ExactScalar, ...]:
    result: list[ExactScalar] = []
    for value in values:
        if isinstance(value, ExactScalar):
            result.append(value)
        elif isinstance(value, int):
            result.append(ExactScalar(value))
        else:
            numerator, denominator = value
            result.append(ExactScalar(int(numerator), int(denominator)))
    return tuple(result)


@dataclass(frozen=True)
class HarmonicLane:
    lane_id: str
    samples: tuple[ExactScalar, ...]
    phase_turns: ExactScalar
    relative_frequency: ExactScalar
    phase_lock_id: str
    recursive_scale: int = 0
    loshu_orientation: int = 5
    modulus: int = 72

    def __post_init__(self) -> None:
        if self.lane_id not in SURROUND_LANES:
            raise NFVError("NFV_INVALID_AUDIO_LANE", "surround lane must be x, y, z, or w")
        object.__setattr__(self, "samples", _exact_tuple(self.samples))
        if not self.samples:
            raise NFVError("NFV_EMPTY_AUDIO_LANE", "harmonic lane requires at least one sample")
        if self.relative_frequency.numerator <= 0:
            raise NFVError("NFV_INVALID_RELATIVE_FREQUENCY", "relative frequency must be positive")
        if not self.phase_lock_id:
            raise NFVError("NFV_MISSING_PHASE_LOCK", "phase lock identity is mandatory")
        if self.recursive_scale < 0 or self.modulus <= 0:
            raise NFVError("NFV_INVALID_AUDIO_PROFILE", "scale must be nonnegative and modulus positive")
        if self.loshu_orientation not in LOSHU_TRAVERSAL:
            raise NFVError("NFV_INVALID_LOSHU_ORIENTATION", "audio lane orientation must be Lo Shu bound")

    def to_dict(self) -> dict[str, Any]:
        return {
            "lane_id": self.lane_id,
            "samples": [sample.to_dict() for sample in self.samples],
            "phase_turns": self.phase_turns.to_dict(),
            "relative_frequency": self.relative_frequency.to_dict(),
            "phase_lock_id": self.phase_lock_id,
            "recursive_scale": self.recursive_scale,
            "loshu_orientation": self.loshu_orientation,
            "modulus": self.modulus,
        }


@dataclass(frozen=True)
class RationalCenterChannel:
    samples: tuple[ExactScalar, ...]
    reference_frequency: ExactScalar
    recursive_scale: int = 0
    loshu_orientation: int = 5
    modulus: int = 72

    def __post_init__(self) -> None:
        object.__setattr__(self, "samples", _exact_tuple(self.samples))
        if not self.samples:
            raise NFVError("NFV_EMPTY_CENTER_CHANNEL", "center channel requires at least one exact sample")
        if self.reference_frequency.numerator <= 0:
            raise NFVError("NFV_INVALID_REFERENCE_FREQUENCY", "center reference frequency must be positive")
        if self.recursive_scale < 0 or self.modulus <= 0:
            raise NFVError("NFV_INVALID_CENTER_PROFILE", "scale must be nonnegative and modulus positive")
        if self.loshu_orientation not in LOSHU_TRAVERSAL:
            raise NFVError("NFV_INVALID_LOSHU_ORIENTATION", "center orientation must be Lo Shu bound")

    def to_dict(self) -> dict[str, Any]:
        return {
            "lane_id": "c",
            "samples": [sample.to_dict() for sample in self.samples],
            "reference_frequency": self.reference_frequency.to_dict(),
            "recursive_scale": self.recursive_scale,
            "loshu_orientation": self.loshu_orientation,
            "modulus": self.modulus,
        }


@dataclass(frozen=True)
class HarmonicField:
    lane_x: HarmonicLane
    lane_y: HarmonicLane
    lane_z: HarmonicLane
    lane_w: HarmonicLane
    center: RationalCenterChannel
    source_receipt: str
    graph_index: str = ""

    def __post_init__(self) -> None:
        lanes = self.surround_lanes
        if tuple(lane.lane_id for lane in lanes) != SURROUND_LANES:
            raise NFVError("NFV_AUDIO_LANE_ORDER_MISMATCH", "harmonic field lane order must remain x,y,z,w")
        lengths = {len(lane.samples) for lane in lanes} | {len(self.center.samples)}
        if len(lengths) != 1:
            raise NFVError("NFV_AUDIO_LENGTH_MISMATCH", "all four lanes and center must have equal frame length")
        locks = {lane.phase_lock_id for lane in lanes}
        if len(locks) != 1:
            raise NFVError("NFV_AUDIO_PHASE_UNLOCKED", "four-lane field must share one phase-lock identity")
        if not self.source_receipt:
            raise NFVError("NFV_MISSING_SOURCE_RECEIPT", "harmonic field requires a source receipt")
        expected = hash216({
            "domain": "HHS-NFV-HARMONIC-FIELD-V1",
            "lanes": [lane.to_dict() for lane in lanes],
            "center": self.center.to_dict(),
            "source_receipt": self.source_receipt,
            "ring_edges": RING_EDGES,
            "cross_links": CROSS_LINKS,
        })
        if self.graph_index and self.graph_index != expected:
            raise NFVError("NFV_HARMONIC_FIELD_IDENTITY_MISMATCH", "harmonic field index is not canonical")
        object.__setattr__(self, "graph_index", expected)

    @property
    def surround_lanes(self) -> tuple[HarmonicLane, HarmonicLane, HarmonicLane, HarmonicLane]:
        return self.lane_x, self.lane_y, self.lane_z, self.lane_w

    @property
    def frame_length(self) -> int:
        return len(self.center.samples)

    def surround_sum(self, frame_index: int) -> ExactScalar:
        if not 0 <= frame_index < self.frame_length:
            raise NFVError("NFV_AUDIO_FRAME_OUT_OF_RANGE", "frame index is outside harmonic field")
        total = ZERO
        for lane in self.surround_lanes:
            total = total.add(lane.samples[frame_index])
        return total

    def encode_vm81_candidate(self, frame_index: int) -> dict[str, Any]:
        if not 0 <= frame_index < self.frame_length:
            raise NFVError("NFV_AUDIO_FRAME_OUT_OF_RANGE", "frame index is outside harmonic field")
        lane_values = []
        for lane in self.surround_lanes:
            lane_values.append({
                "lane": lane.lane_id,
                "amplitude": lane.samples[frame_index].to_dict(),
                "phase": lane.phase_turns.to_dict(),
                "relative_frequency": lane.relative_frequency.to_dict(),
                "recursive_scale": lane.recursive_scale,
                "loshu_orientation": lane.loshu_orientation,
                "modulus": lane.modulus,
            })
        return {
            "schema": "HHS_NFV_AUDIO_VM81_CANDIDATE_V1",
            "frame_index": frame_index,
            "source_receipt": self.source_receipt,
            "graph_index": self.graph_index,
            "surround": lane_values,
            "center": {
                "lane": "c",
                "amplitude": self.center.samples[frame_index].to_dict(),
                "reference_frequency": self.center.reference_frequency.to_dict(),
                "recursive_scale": self.center.recursive_scale,
                "loshu_orientation": self.center.loshu_orientation,
                "modulus": self.center.modulus,
            },
            "authoritative": False,
            "requires_vm81_admission": True,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "HHS_NFV_HARMONIC_FIELD_V1",
            "lane_x": self.lane_x.to_dict(),
            "lane_y": self.lane_y.to_dict(),
            "lane_z": self.lane_z.to_dict(),
            "lane_w": self.lane_w.to_dict(),
            "center": self.center.to_dict(),
            "source_receipt": self.source_receipt,
            "graph_index": self.graph_index,
            "ring_edges": [list(edge) for edge in RING_EDGES],
            "cross_links": [list(edge) for edge in CROSS_LINKS],
        }
