"""Parameter config and exact VM5184 A/B branch evaluation for Pass 197."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping

from hhs_backend.runtime.pass197_exact_v1 import (
    ADDRESS_COUNT, CELL_COUNT, LANE_COUNT, Matrix, address, canonical_json,
    cell_index, compact_gate, decode_address, exact_fraction, fraction_payload,
    hash72, original_gate,
)


@dataclass(frozen=True)
class CalibrationConfig:
    x_values: tuple[Fraction, ...]
    y_values: tuple[Fraction, ...]
    xy_symbol_values: tuple[int, ...]
    include_domain_rejections: bool = True
    full_replay: bool = True

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None = None) -> "CalibrationConfig":
        data = dict(payload or {})
        axis = ("-3", "-2", "-1", "-1/2", "0", "1/2", "1", "2", "3")
        x_values = tuple(exact_fraction(v, field="x_values") for v in data.get("x_values", axis))
        y_values = tuple(exact_fraction(v, field="y_values") for v in data.get("y_values", axis))
        exponents: list[int] = []
        for value in data.get("xy_symbol_values", (-2, -1, 0, 1, 2)):
            if isinstance(value, (bool, float)):
                raise ValueError("xy_symbol_values requires exact integers")
            integer = int(value)
            if not -16 <= integer <= 16:
                raise ValueError("xy_symbol exponent must be in [-16,16]")
            exponents.append(integer)
        if not x_values or not y_values or not exponents:
            raise ValueError("calibration axes must be nonempty")
        if len(x_values) * len(y_values) * len(exponents) > 50_000:
            raise ValueError("bounded calibration permits at most 50,000 parameter states")
        return cls(x_values, y_values, tuple(exponents), bool(data.get("include_domain_rejections", True)), bool(data.get("full_replay", True)))

    def payload(self) -> dict[str, Any]:
        return {
            "x_values": [fraction_payload(v) for v in self.x_values],
            "y_values": [fraction_payload(v) for v in self.y_values],
            "xy_symbol_values": list(self.xy_symbol_values),
            "include_domain_rejections": self.include_domain_rejections,
            "full_replay": self.full_replay,
            "lexical_identity": {"xy_symbol": "MatrixPower exponent token", "x*y": "parameter product", "equal_by_default": False},
        }


def state_key(x: Fraction, y: Fraction, exponent: int) -> str:
    return canonical_json({"x": fraction_payload(x), "y": fraction_payload(y), "xy_symbol": exponent})


def evaluate_state(x: Fraction, y: Fraction, exponent: int, q: Matrix) -> dict[str, Any]:
    if not x or not y:
        body = {
            "status": "DOMAIN_REJECTED", "reason": "reciprocal x and y membranes require nonzero values",
            "x": fraction_payload(x), "y": fraction_payload(y), "xy_symbol": exponent,
            "x_times_y": fraction_payload(x * y), "lexical_identity_preserved": True,
            "address_count": 0, "exact_match_count": 0, "mismatch_count": 0,
            "singular_count": 0, "distinct_gate_values": 0,
            "useful_parameter_state": False, "cell_gate_hash72": None,
        }
        return {**body, "state_hash72": hash72("pass197.parameter.state", body)}

    cells, distinct = [], set()
    matches = mismatches = singular = 0
    first_mismatch = None
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    cell = cell_index(i, j, k, l)
                    try:
                        original = original_gate(x, y, q, i, j, k, l)
                        compact = compact_gate(x, y, q, i, j, k, l)
                    except ZeroDivisionError:
                        singular += LANE_COUNT
                        continue
                    same = original == compact
                    payload = original.payload()
                    distinct.add(canonical_json(payload))
                    for lane in range(LANE_COUNT):
                        state = address(cell, lane)
                        if decode_address(state) != (i, j, k, l, lane):
                            raise AssertionError("VM5184 address codec failed")
                        if same:
                            matches += 1
                        else:
                            mismatches += 1
                            if first_mismatch is None:
                                first_mismatch = {"state": state, "indices": [i, j, k, l, lane], "original": payload, "compact": compact.payload()}
                    cells.append({"cell": cell, "indices": [i, j, k, l], "gate": payload})
    status = "ADMITTED" if not mismatches and not singular else "SINGULAR" if singular else "MISMATCH"
    body = {
        "status": status, "x": fraction_payload(x), "y": fraction_payload(y),
        "xy_symbol": exponent, "x_times_y": fraction_payload(x * y),
        "lexical_identity_preserved": True, "address_count": ADDRESS_COUNT,
        "exact_match_count": matches, "mismatch_count": mismatches,
        "singular_count": singular, "distinct_gate_values": len(distinct),
        "useful_parameter_state": status == "ADMITTED" and len(distinct) > 1,
        "first_mismatch": first_mismatch,
        "cell_gate_hash72": hash72("pass197.cell.gates", cells),
        "simplification": {
            "original_leaf_evaluations": ADDRESS_COUNT,
            "factorized_cell_evaluations": CELL_COUNT,
            "lane_broadcast_factor": LANE_COUNT,
            "saved_leaf_evaluations": ADDRESS_COUNT - CELL_COUNT,
            "saved_fraction": fraction_payload(Fraction(ADDRESS_COUNT - CELL_COUNT, ADDRESS_COUNT)),
        },
    }
    return {**body, "state_hash72": hash72("pass197.parameter.state", body)}
