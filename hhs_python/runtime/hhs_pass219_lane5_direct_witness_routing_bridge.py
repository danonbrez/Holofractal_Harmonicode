"""Python/native bridge for Pass 219 Lane 5 direct-witness routing 1.46.

The bridge exposes the already-proven exact native optimizer to the production
Lane 5 latency/composition dispatcher.  It does not grant canonical VM81,
Hash72, Hash216, persistence, PQC-key, or receipt-clock authority.  A selected
route remains a candidate until the inherited signed environmental VM81
admission succeeds.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from pathlib import Path
import os
import platform
import subprocess
from ctypes import POINTER, Structure, c_int8, c_uint8, c_uint32, c_uint64
from typing import Iterable, Sequence

VERSION = 0x0001002E
NAMESPACE = 0x0002192E
PHASE_CYCLE = 72
PHASE_HALF = 36
HHS_EXACT_STATUS_OK = 0


class HHSExactPass219Lane5DirectWitnessAuthorityV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("namespace_id", c_uint32),
        ("phase_cycle", c_uint32),
        ("phase_quarter", c_uint32),
        ("bigint_serialization_addressed", c_uint8),
        ("direct_composition_jump", c_uint8),
        ("intermediate_materialization_required", c_uint8),
        ("previous_current_witness_bound", c_uint8),
        ("goal_bound", c_uint8),
        ("contradiction_boundary_bound", c_uint8),
        ("exact_reciprocal_phase_inversion", c_uint8),
        ("balanced_trinary_collapse", c_uint8),
        ("binary_qubit_collapse", c_uint8),
        ("nested_zero_layer", c_uint8),
        ("integer_only_route_cost", c_uint8),
        ("deterministic_tie_break", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_vm81_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("pqc_key_authority", c_uint8),
        ("receipt_clock_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("floating_point_canonical_authority", c_uint8),
        ("reserved0", c_uint8 * 3),
    ]


class HHSExactPass219Lane5DirectWitnessRouteV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("previous_signature64", c_uint64),
        ("current_signature64", c_uint64),
        ("provenance_signature64", c_uint64),
        ("goal_signature64", c_uint64),
        ("forbidden_boundary_signature64", c_uint64),
        ("reciprocal_inverse_signature64", c_uint64),
        ("candidate_signature64", c_uint64),
        ("route_signature64", c_uint64),
        ("represented_span", c_uint64),
        ("integer_route_cost", c_uint64),
        ("evidence_count", c_uint32),
        ("contradiction_check_count", c_uint32),
        ("materialized_intermediate_states", c_uint32),
        ("phase_slot", c_uint32),
        ("inverse_phase_slot", c_uint32),
        ("trinary_collapse", c_int8),
        ("binary_collapse", c_uint8),
        ("nested_zero_slot", c_uint8),
        ("replay_witness_verified", c_uint8),
        ("exact_goal_reached", c_uint8),
        ("contradiction_free", c_uint8),
        ("goal_forbidden_conflict", c_uint8),
        ("reciprocal_phase_verified", c_uint8),
        ("bigint_serialization_addressed", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("pqc_key_authority", c_uint8),
        ("receipt_clock_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("reserved0", c_uint8 * 3),
    ]


class HHSExactPass219Lane5DirectWitnessReceiptV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("namespace_id", c_uint32),
        ("selected_candidate_index", c_uint32),
        ("represented_span", c_uint64),
        ("integer_route_cost", c_uint64),
        ("avoided_intermediate_states", c_uint64),
        ("descriptor_signature64", c_uint64),
        ("route_receipt_signature64", c_uint64),
        ("phase_slot", c_uint32),
        ("inverse_phase_slot", c_uint32),
        ("trinary_collapse", c_int8),
        ("binary_collapse", c_uint8),
        ("nested_zero_slot", c_uint8),
        ("accepted", c_uint8),
        ("optimizer_selected", c_uint8),
        ("replay_witness_verified", c_uint8),
        ("exact_goal_reached", c_uint8),
        ("contradiction_free", c_uint8),
        ("reciprocal_phase_verified", c_uint8),
        ("bigint_serialization_addressed", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("pqc_key_authority", c_uint8),
        ("receipt_clock_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("reserved0", c_uint8 * 3),
    ]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _runtime_path() -> Path:
    system = platform.system().lower()
    name = "hhs_runtime.dll" if system == "windows" else (
        "libhhs_runtime.dylib" if system == "darwin" else "libhhs_runtime.so"
    )
    return _repo_root() / "hhs_runtime" / "builds" / name


def _load_runtime() -> ctypes.CDLL:
    path = _runtime_path()
    disable = os.environ.get("HHS_DISABLE_C_AUTOBUILD", "").lower() in {
        "1", "true", "yes", "on"
    }
    if not path.exists() and not disable:
        subprocess.run(
            ["make", "c-abi"],
            cwd=_repo_root(),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    if not path.exists():
        raise FileNotFoundError(f"HHS exact runtime shared library not found: {path}")
    return ctypes.CDLL(str(path))


def _u64(value: int, field: str) -> int:
    value = int(value)
    if value < 0 or value > (1 << 64) - 1:
        raise ValueError(f"{field} must fit uint64")
    return value


@dataclass(frozen=True)
class Lane5DirectWitnessCandidate:
    previous_signature64: int
    current_signature64: int
    provenance_signature64: int
    goal_signature64: int
    forbidden_boundary_signature64: int
    reciprocal_inverse_signature64: int
    route_signature64: int
    represented_span: int
    phase_slot: int
    trinary_collapse: int
    binary_collapse: int
    evidence_count: int = 5
    contradiction_check_count: int = 1
    candidate_signature64: int | None = None

    @property
    def integer_route_cost(self) -> int:
        return int(self.evidence_count) + int(self.contradiction_check_count) + 1

    def to_native(self) -> HHSExactPass219Lane5DirectWitnessRouteV1:
        route = HHSExactPass219Lane5DirectWitnessRouteV1()
        route.struct_size = ctypes.sizeof(route)
        route.version = VERSION
        route.previous_signature64 = _u64(self.previous_signature64, "previous_signature64")
        route.current_signature64 = _u64(self.current_signature64, "current_signature64")
        route.provenance_signature64 = _u64(self.provenance_signature64, "provenance_signature64")
        route.goal_signature64 = _u64(self.goal_signature64, "goal_signature64")
        route.forbidden_boundary_signature64 = _u64(
            self.forbidden_boundary_signature64, "forbidden_boundary_signature64"
        )
        route.reciprocal_inverse_signature64 = _u64(
            self.reciprocal_inverse_signature64, "reciprocal_inverse_signature64"
        )
        route.candidate_signature64 = _u64(
            self.goal_signature64 if self.candidate_signature64 is None else self.candidate_signature64,
            "candidate_signature64",
        )
        route.route_signature64 = _u64(self.route_signature64, "route_signature64")
        route.represented_span = _u64(self.represented_span, "represented_span")
        route.integer_route_cost = _u64(self.integer_route_cost, "integer_route_cost")
        route.evidence_count = int(self.evidence_count)
        route.contradiction_check_count = int(self.contradiction_check_count)
        route.materialized_intermediate_states = 0
        route.phase_slot = int(self.phase_slot)
        route.inverse_phase_slot = (int(self.phase_slot) + PHASE_HALF) % PHASE_CYCLE
        route.trinary_collapse = int(self.trinary_collapse)
        route.binary_collapse = int(self.binary_collapse)
        route.nested_zero_slot = 1 if int(self.binary_collapse) == 0 else 0
        route.replay_witness_verified = 1
        route.exact_goal_reached = 1
        route.contradiction_free = 1
        route.goal_forbidden_conflict = 0
        route.reciprocal_phase_verified = 1
        route.bigint_serialization_addressed = 1
        route.candidate_only = 1
        route.requires_signed_environmental_vm81_admission = 1
        return route


class Pass219Lane5DirectWitnessRoutingBridge:
    def __init__(self) -> None:
        self.lib = _load_runtime()
        self.lib.hhs_exact_pass219_lane5_direct_witness_routing_version.argtypes = []
        self.lib.hhs_exact_pass219_lane5_direct_witness_routing_version.restype = c_uint32
        self.lib.hhs_exact_pass219_lane5_direct_witness_routing_authority.argtypes = [
            POINTER(HHSExactPass219Lane5DirectWitnessAuthorityV1)
        ]
        self.lib.hhs_exact_pass219_lane5_direct_witness_routing_authority.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_direct_witness_route_validate.argtypes = [
            POINTER(HHSExactPass219Lane5DirectWitnessRouteV1),
            POINTER(HHSExactPass219Lane5DirectWitnessReceiptV1),
        ]
        self.lib.hhs_exact_pass219_lane5_direct_witness_route_validate.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_direct_witness_route_optimize.argtypes = [
            POINTER(HHSExactPass219Lane5DirectWitnessRouteV1),
            c_uint32,
            POINTER(HHSExactPass219Lane5DirectWitnessReceiptV1),
        ]
        self.lib.hhs_exact_pass219_lane5_direct_witness_route_optimize.restype = ctypes.c_int

    def authority(self) -> dict[str, int | bool]:
        value = HHSExactPass219Lane5DirectWitnessAuthorityV1()
        status = self.lib.hhs_exact_pass219_lane5_direct_witness_routing_authority(
            ctypes.byref(value)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Lane 5 direct-witness authority failed: status={status}")
        return {
            "version": int(value.version),
            "namespace_id": int(value.namespace_id),
            "direct_composition_jump": bool(value.direct_composition_jump),
            "intermediate_materialization_required": bool(
                value.intermediate_materialization_required
            ),
            "exact_reciprocal_phase_inversion": bool(
                value.exact_reciprocal_phase_inversion
            ),
            "balanced_trinary_collapse": bool(value.balanced_trinary_collapse),
            "binary_qubit_collapse": bool(value.binary_qubit_collapse),
            "nested_zero_layer": bool(value.nested_zero_layer),
            "candidate_only": bool(value.candidate_only),
            "canonical_vm81_mutation_authority": bool(
                value.canonical_vm81_mutation_authority
            ),
            "canonical_hash72_authority": bool(value.canonical_hash72_authority),
            "canonical_hash216_authority": bool(value.canonical_hash216_authority),
            "canonical_persistence_authority": bool(
                value.canonical_persistence_authority
            ),
            "requires_signed_environmental_vm81_admission": bool(
                value.requires_signed_environmental_vm81_admission
            ),
            "floating_point_canonical_authority": bool(
                value.floating_point_canonical_authority
            ),
        }

    @staticmethod
    def _receipt(receipt: HHSExactPass219Lane5DirectWitnessReceiptV1) -> dict[str, int | bool]:
        return {
            "namespace_id": int(receipt.namespace_id),
            "selected_candidate_index": int(receipt.selected_candidate_index),
            "represented_span": int(receipt.represented_span),
            "integer_route_cost": int(receipt.integer_route_cost),
            "avoided_intermediate_states": int(receipt.avoided_intermediate_states),
            "descriptor_signature64": int(receipt.descriptor_signature64),
            "route_receipt_signature64": int(receipt.route_receipt_signature64),
            "phase_slot": int(receipt.phase_slot),
            "inverse_phase_slot": int(receipt.inverse_phase_slot),
            "trinary_collapse": int(receipt.trinary_collapse),
            "binary_collapse": int(receipt.binary_collapse),
            "nested_zero_slot": int(receipt.nested_zero_slot),
            "accepted": bool(receipt.accepted),
            "optimizer_selected": bool(receipt.optimizer_selected),
            "replay_witness_verified": bool(receipt.replay_witness_verified),
            "exact_goal_reached": bool(receipt.exact_goal_reached),
            "contradiction_free": bool(receipt.contradiction_free),
            "reciprocal_phase_verified": bool(receipt.reciprocal_phase_verified),
            "bigint_serialization_addressed": bool(
                receipt.bigint_serialization_addressed
            ),
            "candidate_only": bool(receipt.candidate_only),
            "canonical_vm81_mutation_authority": bool(
                receipt.canonical_mutation_authority
            ),
            "canonical_hash72_authority": bool(receipt.canonical_hash72_authority),
            "canonical_hash216_authority": bool(receipt.canonical_hash216_authority),
            "canonical_persistence_authority": bool(
                receipt.canonical_persistence_authority
            ),
            "requires_signed_environmental_vm81_admission": bool(
                receipt.requires_signed_environmental_vm81_admission
            ),
        }

    def validate(self, candidate: Lane5DirectWitnessCandidate) -> dict[str, int | bool]:
        route = candidate.to_native()
        receipt = HHSExactPass219Lane5DirectWitnessReceiptV1()
        status = self.lib.hhs_exact_pass219_lane5_direct_witness_route_validate(
            ctypes.byref(route), ctypes.byref(receipt)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError(f"Lane 5 direct-witness route rejected: status={status}")
        return self._receipt(receipt)

    def optimize(
        self,
        candidates: Sequence[Lane5DirectWitnessCandidate] | Iterable[Lane5DirectWitnessCandidate],
    ) -> dict[str, int | bool]:
        rows = list(candidates)
        if not rows:
            raise ValueError("at least one direct-witness candidate is required")
        native_type = HHSExactPass219Lane5DirectWitnessRouteV1 * len(rows)
        native = native_type(*(candidate.to_native() for candidate in rows))
        receipt = HHSExactPass219Lane5DirectWitnessReceiptV1()
        status = self.lib.hhs_exact_pass219_lane5_direct_witness_route_optimize(
            native,
            len(rows),
            ctypes.byref(receipt),
        )
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError(f"Lane 5 direct-witness optimization failed: status={status}")
        result = self._receipt(receipt)
        if not result["accepted"] or not result["optimizer_selected"]:
            raise RuntimeError("Lane 5 direct-witness optimizer returned non-selected receipt")
        if result["canonical_vm81_mutation_authority"]:
            raise RuntimeError("Lane 5 direct-witness optimizer escalated VM81 authority")
        if result["canonical_hash216_authority"]:
            raise RuntimeError("Lane 5 direct-witness optimizer escalated Hash216 authority")
        return result


__all__ = [
    "Lane5DirectWitnessCandidate",
    "Pass219Lane5DirectWitnessRoutingBridge",
]
