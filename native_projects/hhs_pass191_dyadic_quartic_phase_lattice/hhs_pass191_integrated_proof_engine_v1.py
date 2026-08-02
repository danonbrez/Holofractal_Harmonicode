from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import ctypes
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass175 import (
    ORDERED_BASIS,
    InstructionRequest,
    Pass175Runtime,
    ReciprocalLane,
)

SCHEMA = "HHS_PASS_191_INTEGRATED_PROOF_SEARCH_V1"
CLASSIFICATION = "HHS_PASS_191_INTEGRATED_TENSOR_VM81_HYDRATION_PROOF_SEARCH_EXECUTED"
PASS186_RECEIPT_RELATIVE = Path(
    "native_projects/hhs_pass186_x64_vm81_q144/PASS_186_VALIDATION_RECEIPT.json"
)
HYDRATED_CARDINALITY = 5_184 * 243
OUTER_ENVELOPE_MODULUS = HYDRATED_CARDINALITY + 1
BASIS_TAGS = {
    "x": 0x0058,
    "y": 0x0059,
    "z": 0x005A,
    "w": 0x0057,
    "xy": 0x5859,
    "yx": 0x5958,
    "zw": 0x5A57,
    "wz": 0x575A,
}


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _fraction_text(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


@dataclass(frozen=True)
class SymmetryPoint:
    sigma: Fraction
    t: Fraction

    def reflect(self) -> "SymmetryPoint":
        return SymmetryPoint(Fraction(1, 1) - self.sigma, self.t)

    def is_critical_line_fixed_point(self) -> bool:
        return self.reflect() == self

    def to_dict(self) -> dict[str, str]:
        return {"sigma": _fraction_text(self.sigma), "t": _fraction_text(self.t)}


class HHS186Quantization(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("abi_version", ctypes.c_uint32),
        ("g243", ctypes.c_uint16),
        ("opcode_lane36", ctypes.c_uint8),
        ("root_row12", ctypes.c_uint8),
        ("root_col12", ctypes.c_uint8),
        ("reserved", ctypes.c_uint8 * 3),
    ]


class HHS186MappingResult(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("abi_version", ctypes.c_uint32),
        ("status", ctypes.c_uint32),
        ("instruction_state5184", ctypes.c_uint32),
        ("projected_state5184_243", ctypes.c_uint32),
        ("q144_index", ctypes.c_uint32),
        ("vm81_cell", ctypes.c_uint16),
        ("vm81_operation64", ctypes.c_uint8),
        ("ordered_basis", ctypes.c_uint8),
        ("operation_class8", ctypes.c_uint8),
        ("factorial_admitted", ctypes.c_uint8),
        ("closure_q144_lane", ctypes.c_uint8),
        ("u72_pair", ctypes.c_uint8),
        ("u72_index", ctypes.c_uint8),
        ("root_row12", ctypes.c_uint8),
        ("root_col12", ctypes.c_uint8),
        ("opcode_lane36", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8),
        ("g243", ctypes.c_uint16),
        ("ordered_tag", ctypes.c_uint16),
        ("ordered_left", ctypes.c_int64),
        ("ordered_right", ctypes.c_int64),
        ("ordered_product_witness", ctypes.c_int64),
        ("factorial7", ctypes.c_uint32),
        ("q144", ctypes.c_uint32),
        ("vm5184", ctypes.c_uint32),
        ("hydrated_cardinality", ctypes.c_uint32),
        ("outer_envelope_modulus", ctypes.c_uint32),
    ]


class Pass186NativeABI:
    def __init__(self, library_path: str | Path) -> None:
        self.library_path = Path(library_path).resolve()
        if not self.library_path.is_file():
            raise FileNotFoundError(f"Pass 186 native ABI not found: {self.library_path}")
        self.library = ctypes.CDLL(str(self.library_path))
        self.library.hhs186_x64_vm81_q144_map.argtypes = [
            ctypes.c_int64,
            ctypes.c_int64,
            ctypes.c_int64,
            ctypes.c_int64,
            ctypes.POINTER(HHS186Quantization),
            ctypes.POINTER(HHS186MappingResult),
        ]
        self.library.hhs186_x64_vm81_q144_map.restype = ctypes.c_int
        self.library.hhs186_x64_vm81_q144_unproject.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(HHS186Quantization),
            ctypes.POINTER(HHS186MappingResult),
        ]
        self.library.hhs186_x64_vm81_q144_unproject.restype = ctypes.c_int

    @staticmethod
    def _result_dict(result: HHS186MappingResult) -> dict[str, Any]:
        basis = ORDERED_BASIS[int(result.ordered_basis)]
        return {
            "instruction_state5184": int(result.instruction_state5184),
            "projected_state5184_243": int(result.projected_state5184_243),
            "q144_index": int(result.q144_index),
            "vm81_cell": int(result.vm81_cell),
            "vm81_operation64": int(result.vm81_operation64),
            "ordered_basis": basis,
            "ordered_tag": int(result.ordered_tag),
            "operation_class8": int(result.operation_class8),
            "factorial_admitted": bool(result.factorial_admitted),
            "closure_q144_lane": bool(result.closure_q144_lane),
            "u72_pair": int(result.u72_pair),
            "u72_index": int(result.u72_index),
            "root_row12": int(result.root_row12),
            "root_col12": int(result.root_col12),
            "opcode_lane36": int(result.opcode_lane36),
            "g243": int(result.g243),
            "ordered_left": int(result.ordered_left),
            "ordered_right": int(result.ordered_right),
            "ordered_product_witness": int(result.ordered_product_witness),
            "factorial7": int(result.factorial7),
            "q144": int(result.q144),
            "vm5184": int(result.vm5184),
            "hydrated_cardinality": int(result.hydrated_cardinality),
            "outer_envelope_modulus": int(result.outer_envelope_modulus),
        }

    def map(
        self,
        *,
        x: int,
        y: int,
        z: int,
        w: int,
        g243: int,
        opcode_lane36: int,
        root_row12: int,
        root_col12: int,
    ) -> dict[str, Any]:
        quantization = HHS186Quantization()
        quantization.struct_size = ctypes.sizeof(HHS186Quantization)
        quantization.abi_version = 1
        quantization.g243 = g243
        quantization.opcode_lane36 = opcode_lane36
        quantization.root_row12 = root_row12
        quantization.root_col12 = root_col12
        result = HHS186MappingResult()
        status = self.library.hhs186_x64_vm81_q144_map(
            x, y, z, w, ctypes.byref(quantization), ctypes.byref(result)
        )
        if status != 0 or result.status != 0:
            raise RuntimeError(f"Pass 186 map failed: status={status}/{result.status}")
        mapped = self._result_dict(result)
        if mapped["hydrated_cardinality"] != HYDRATED_CARDINALITY:
            raise AssertionError("Pass 186 hydrated cardinality mismatch")
        if mapped["outer_envelope_modulus"] != OUTER_ENVELOPE_MODULUS:
            raise AssertionError("Pass 186 outer envelope mismatch")
        return mapped

    def unproject(self, projected_state: int) -> dict[str, Any]:
        quantization = HHS186Quantization()
        result = HHS186MappingResult()
        status = self.library.hhs186_x64_vm81_q144_unproject(
            projected_state, ctypes.byref(quantization), ctypes.byref(result)
        )
        if status != 0 or result.status != 0:
            raise RuntimeError(f"Pass 186 unproject failed: status={status}/{result.status}")
        return {
            "quantization": {
                "g243": int(quantization.g243),
                "opcode_lane36": int(quantization.opcode_lane36),
                "root_row12": int(quantization.root_row12),
                "root_col12": int(quantization.root_col12),
            },
            "coordinates": self._result_dict(result),
        }


def exact_reflection_obstruction() -> dict[str, Any]:
    t = Fraction(141347, 10000)
    critical = SymmetryPoint(Fraction(1, 2), t)
    off_axis = SymmetryPoint(Fraction(1, 3), t)

    def trace(point: SymmetryPoint) -> list[dict[str, str]]:
        states = [point]
        for _ in range(4):
            states.append(states[-1].reflect())
        return [state.to_dict() for state in states]

    critical_trace = trace(critical)
    off_axis_trace = trace(off_axis)
    checks = {
        "reflection_is_involution_for_critical_point": critical.reflect().reflect()
        == critical,
        "reflection_is_involution_for_off_axis_point": off_axis.reflect().reflect()
        == off_axis,
        "critical_point_is_fixed": critical.is_critical_line_fixed_point(),
        "off_axis_point_is_not_fixed": not off_axis.is_critical_line_fixed_point(),
        "quartic_closure_accepts_both": critical_trace[-1] == critical_trace[0]
        and off_axis_trace[-1] == off_axis_trace[0],
    }
    if not all(checks.values()):
        raise AssertionError(f"reflection obstruction failed: {checks}")

    certificate_core = {
        "theorem": "PHASE_CLOSURE_ALONE_IS_NOT_A_FAITHFUL_CRITICAL_LINE_DISCRIMINATOR",
        "operator": "R(sigma,t)=(1-sigma,t)",
        "exact_derivation": [
            "R(R(sigma,t))=(1-(1-sigma),t)=(sigma,t)",
            "R(sigma,t)=(sigma,t) iff sigma=1/2",
            "therefore every point has two-step and four-step closure, while only sigma=1/2 is fixed",
        ],
        "critical_fixed_point_trace": critical_trace,
        "off_axis_two_cycle_trace": off_axis_trace,
        "checks": checks,
        "consequence": (
            "A proof transfer from zeta symmetry to the critical line requires a zero-specific "
            "invariant that eliminates nontrivial two-cycles; closure by itself cannot do so."
        ),
    }
    return {
        **certificate_core,
        "certificate_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-RH-REFLECTION-OBSTRUCTION-V1"},
            certificate_core,
        ),
    }


def _load_pass186_receipt(repo_root: Path) -> dict[str, Any]:
    path = repo_root / PASS186_RECEIPT_RELATIVE
    payload = json.loads(path.read_text(encoding="utf-8"))
    validation = payload.get("validation", {})
    invariants = payload.get("invariants", {})
    required = {
        "classification": payload.get("classification")
        == "HHS_PASS_186_X64_VM81_Q144_NONCOMMUTATIVE_ABI_VALIDATED",
        "strict_compile": validation.get("strict_compile") is True,
        "exhaustive_roundtrip": validation.get("exhaustive_roundtrip_states")
        == HYDRATED_CARDINALITY,
        "noncommutative_order": validation.get("noncommutative_order_tags_checked")
        is True,
        "no_float": validation.get("floating_point_opcode_scan") == "PASS",
        "cardinality": invariants.get("hydrated_cardinality")
        == HYDRATED_CARDINALITY,
        "outer_envelope": invariants.get("outer_envelope_modulus")
        == OUTER_ENVELOPE_MODULUS,
    }
    if not all(required.values()):
        raise AssertionError(f"Pass 186 receipt is not authoritative: {required}")
    return {
        "path": str(PASS186_RECEIPT_RELATIVE),
        "receipt_sha256": sha256(path.read_bytes()).hexdigest(),
        "classification": payload["classification"],
        "validation": validation,
        "invariants": invariants,
        "source_sha256": payload.get("source_sha256", {}),
        "checks": required,
    }


def native_tensor_witnesses(native: Pass186NativeABI) -> dict[str, Any]:
    cases = {
        "minimum": dict(g243=0, opcode_lane36=0, root_row12=0, root_col12=0),
        "factorial_last": dict(
            g243=242, opcode_lane36=34, root_row12=11, root_col12=11
        ),
        "closure_first": dict(
            g243=0, opcode_lane36=35, root_row12=0, root_col12=0
        ),
        "maximum": dict(
            g243=242, opcode_lane36=35, root_row12=11, root_col12=11
        ),
        "xy": dict(g243=72, opcode_lane36=0, root_row12=0, root_col12=4),
        "yx": dict(g243=72, opcode_lane36=0, root_row12=0, root_col12=5),
        "zw": dict(g243=144, opcode_lane36=0, root_row12=0, root_col12=6),
        "wz": dict(g243=144, opcode_lane36=0, root_row12=0, root_col12=7),
    }
    mapped = {
        name: native.map(x=2, y=3, z=5, w=7, **quantization)
        for name, quantization in cases.items()
    }
    roundtrips = {
        name: native.unproject(row["projected_state5184_243"])
        for name, row in mapped.items()
    }
    for name, row in mapped.items():
        coordinates = roundtrips[name]["coordinates"]
        if coordinates["instruction_state5184"] != row["instruction_state5184"]:
            raise AssertionError(f"native roundtrip state mismatch: {name}")
        if coordinates["g243"] != row["g243"]:
            raise AssertionError(f"native roundtrip control mismatch: {name}")

    checks = {
        "minimum_address_zero": mapped["minimum"]["projected_state5184_243"] == 0,
        "maximum_address_exact": mapped["maximum"]["projected_state5184_243"]
        == HYDRATED_CARDINALITY - 1,
        "factorial_boundary_5039": mapped["factorial_last"][
            "instruction_state5184"
        ]
        == 5039
        and mapped["factorial_last"]["factorial_admitted"],
        "closure_boundary_5040": mapped["closure_first"][
            "instruction_state5184"
        ]
        == 5040
        and mapped["closure_first"]["closure_q144_lane"],
        "xy_yx_order_retained": mapped["xy"]["ordered_tag"] == BASIS_TAGS["xy"]
        and mapped["yx"]["ordered_tag"] == BASIS_TAGS["yx"]
        and mapped["xy"]["ordered_tag"] != mapped["yx"]["ordered_tag"]
        and mapped["xy"]["ordered_product_witness"]
        == mapped["yx"]["ordered_product_witness"],
        "zw_wz_order_retained": mapped["zw"]["ordered_tag"] == BASIS_TAGS["zw"]
        and mapped["wz"]["ordered_tag"] == BASIS_TAGS["wz"]
        and mapped["zw"]["ordered_tag"] != mapped["wz"]["ordered_tag"]
        and mapped["zw"]["ordered_product_witness"]
        == mapped["wz"]["ordered_product_witness"],
        "all_roundtrips_exact": len(roundtrips) == len(mapped),
    }
    if not all(checks.values()):
        raise AssertionError(f"native tensor witness failure: {checks}")
    core = {"cases": mapped, "roundtrips": roundtrips, "checks": checks}
    return {
        **core,
        "native_tensor_witness_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-NATIVE-TENSOR-WITNESSES-V1"}, core
        ),
    }


def _runtime_instruction_requests() -> list[InstructionRequest]:
    encodings = (
        b"\x90",
        b"\x31\xc0",
        b"\x0f\xa2",
        b"\x48\xb8\x01\x00\x00\x00\x00\x00\x00\x00",
    )
    requests: list[InstructionRequest] = []
    for index, basis in enumerate(ORDERED_BASIS):
        requests.append(
            InstructionRequest(
                exact_bytes=encodings[index % len(encodings)],
                ordered_operands=(basis, "PASS191_INTEGRATED_PROOF_SEARCH"),
                parenthesization=f"ORDERED::{basis}::RH_REFLECTION",
                read_set=(index,),
                write_set=(index,),
                thread_id=index,
                sequence=index,
                explicit_delta=((index, 1 if index % 2 == 0 else -1),),
            )
        )
    return requests


def hydrate_integrated_candidates() -> dict[str, Any]:
    runtime = Pass175Runtime()
    status_before = runtime.status()
    bootstrap = runtime.cold_hydrate_bootstrap(seal=True)
    execution = runtime.execute_batch(_runtime_instruction_requests(), max_workers=8)
    replay = runtime.replay()
    status_after = runtime.status()

    source_root = runtime.permanent_instructions[0].identity.source_bytes_sha256
    xy_lane = ReciprocalLane(
        opcode="xy",
        phase=0,
        magnitude_numerator=1,
        magnitude_denominator=2,
        source_root_sha256=source_root,
        provenance_root_sha256=sha256(b"PASS191-XY-PROVENANCE").hexdigest(),
    )
    yx_lane = ReciprocalLane(
        opcode="yx",
        phase=36,
        magnitude_numerator=1,
        magnitude_denominator=2,
        source_root_sha256=source_root,
        provenance_root_sha256=sha256(b"PASS191-YX-PROVENANCE").hexdigest(),
    )
    reciprocal_projection = runtime.project_ab(xy_lane, yx_lane)

    waves = execution.get("waves", [])
    candidates = [
        candidate for wave in waves for candidate in wave.get("candidates", [])
    ]
    checks = {
        "permanent_instruction_fabric_5184": status_before.get(
            "permanent_instruction_count"
        )
        == 5184,
        "projected_address_space_5184_243": status_before.get(
            "projected_address_count"
        )
        == HYDRATED_CARDINALITY,
        "cold_hydration_sealed_through_vm81": bootstrap.get(
            "sealed_through_vm81"
        )
        is True,
        "candidate_batch_committed": execution.get("classification")
        == "HHS_PASS_175_CANDIDATES_VM81_COMMITTED",
        "eight_ordered_basis_candidates": execution.get("candidate_count") == 8
        and len(candidates) == 8,
        "all_candidates_have_hash216": all(
            len(str(candidate.get("instruction_hash216", ""))) == 216
            for candidate in candidates
        ),
        "singleton_vm81_authority": execution.get(
            "singleton_vm81_commit_authority"
        )
        is True,
        "deterministic_replay_verified": replay.get("classification")
        == "HHS_PASS_175_DETERMINISTIC_REPLAY_VERIFIED",
        "reciprocal_order_retained": reciprocal_projection.get(
            "instruction_identity_distinct"
        )
        is True
        and reciprocal_projection.get("witness_lanes_retained") is True,
        "hash72_single_commit_stream": status_after.get("hash72_commit_streams")
        == 1,
    }
    if not all(checks.values()):
        raise AssertionError(f"integrated VM81 hydration failed: {checks}")

    core = {
        "runtime_status_before": status_before,
        "cold_hydration": bootstrap,
        "candidate_execution": execution,
        "deterministic_replay": replay,
        "runtime_status_after": status_after,
        "reciprocal_projection": reciprocal_projection,
        "checks": checks,
    }
    return {
        **core,
        "hydration_receipt_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-VM81-HYDRATION-V1"}, core
        ),
    }


def _point_to_quantization(point: SymmetryPoint, index: int) -> dict[str, int]:
    payload = _canonical(
        {
            "sigma": _fraction_text(point.sigma),
            "t": _fraction_text(point.t),
            "index": index,
        }
    )
    digest = sha256(payload).digest()
    return {
        "g243": int.from_bytes(digest[0:2], "big") % 243,
        "opcode_lane36": digest[2] % 36,
        "root_row12": digest[3] % 12,
        "root_col12": digest[4] % 12,
    }


def hydrated_symmetry_search(native: Pass186NativeABI) -> dict[str, Any]:
    t = Fraction(141347, 10000)
    sigmas = (
        Fraction(1, 6),
        Fraction(1, 4),
        Fraction(1, 3),
        Fraction(2, 5),
        Fraction(1, 2),
        Fraction(3, 5),
        Fraction(2, 3),
        Fraction(3, 4),
        Fraction(5, 6),
    )
    rows: list[dict[str, Any]] = []
    for index, sigma in enumerate(sigmas):
        point = SymmetryPoint(sigma, t)
        reflected = point.reflect()
        source_quantization = _point_to_quantization(point, index * 2)
        reflected_quantization = _point_to_quantization(reflected, index * 2 + 1)
        source = native.map(x=2, y=3, z=5, w=7, **source_quantization)
        target = native.map(x=2, y=3, z=5, w=7, **reflected_quantization)
        rows.append(
            {
                "point": point.to_dict(),
                "reflected": reflected.to_dict(),
                "fixed_point": point.is_critical_line_fixed_point(),
                "two_step_closure": reflected.reflect() == point,
                "source_quantization": source_quantization,
                "reflected_quantization": reflected_quantization,
                "source_address": source["projected_state5184_243"],
                "reflected_address": target["projected_state5184_243"],
                "source_ordered_basis": source["ordered_basis"],
                "reflected_ordered_basis": target["ordered_basis"],
            }
        )

    checks = {
        "every_candidate_has_two_step_closure": all(
            row["two_step_closure"] for row in rows
        ),
        "exactly_one_fixed_point_in_symmetric_grid": sum(
            1 for row in rows if row["fixed_point"]
        )
        == 1,
        "off_axis_candidates_are_present": any(
            not row["fixed_point"] for row in rows
        ),
        "addresses_within_hydrated_space": all(
            0 <= row["source_address"] < HYDRATED_CARDINALITY
            and 0 <= row["reflected_address"] < HYDRATED_CARDINALITY
            for row in rows
        ),
    }
    if not all(checks.values()):
        raise AssertionError(f"hydrated symmetry search failed: {checks}")
    core = {"candidate_count": len(rows), "candidates": rows, "checks": checks}
    return {
        **core,
        "search_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-HYDRATED-SYMMETRY-SEARCH-V1"}, core
        ),
    }


def run_integrated_proof_search(
    repo_root: str | Path,
    native_library: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    native = Pass186NativeABI(native_library)
    pass186_receipt = _load_pass186_receipt(root)
    native_witnesses = native_tensor_witnesses(native)
    obstruction = exact_reflection_obstruction()
    hydrated_search = hydrated_symmetry_search(native)
    vm81_hydration = hydrate_integrated_candidates()

    core = {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "authority_path": [
            "PASS_186_X86_64_Q144_NONCOMMUTATIVE_ABI",
            "PASS_175_HASH216_VM5184_G243_HYDRATION",
            "PASS_174_SINGLETON_VM81_COMMIT_AUTHORITY",
            "HASH72_DETERMINISTIC_REPLAY",
        ],
        "cardinality": {
            "vm5184": 5184,
            "g243": 243,
            "hydrated": HYDRATED_CARDINALITY,
            "outer_envelope_modulus": OUTER_ENVELOPE_MODULUS,
        },
        "pass186_exhaustive_validation": pass186_receipt,
        "native_tensor_witnesses": native_witnesses,
        "vm81_hash216_hydration": vm81_hydration,
        "rh_symmetry_obstruction": obstruction,
        "hydrated_symmetry_search": hydrated_search,
        "theorem_decision": {
            "target": "RIEMANN_HYPOTHESIS",
            "status": "UNRESOLVED_BY_CURRENT_INTEGRATED_SEARCH",
            "proved_result": obstruction["theorem"],
            "interpretation": (
                "The integrated engine proves that involutive/quartic phase closure "
                "does not by itself distinguish critical-line fixed points from "
                "off-axis two-cycles. This is a structural proof obligation, not a "
                "falsification of the Riemann hypothesis."
            ),
            "next_search_kernel": {
                "required_property": (
                    "A zeta-zero-specific invariant whose zero set is exactly the "
                    "fixed-point condition sigma=1/2, or an exact off-axis zero witness."
                ),
                "candidate_discriminant": "D(sigma)=2*sigma-1",
                "remaining_transfer": (
                    "derive ZETA_ZERO(sigma,t) => D(sigma)=0 using registered exact "
                    "tensor and analytic rules, or produce ZETA_ZERO with D!=0"
                ),
            },
        },
        "legacy_literal_ledger_role": (
            "dependency-scoped parser and algebra unit evidence only; it is not the "
            "authoritative theorem-decision surface"
        ),
    }
    return {
        **core,
        "integrated_proof_search_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-INTEGRATED-PROOF-SEARCH-V1"}, core
        ),
    }


def verify_integrated_proof_search(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("integrated proof-search schema mismatch")
    if payload.get("classification") != CLASSIFICATION:
        raise AssertionError("integrated proof-search classification mismatch")
    if payload.get("cardinality", {}).get("hydrated") != HYDRATED_CARDINALITY:
        raise AssertionError("integrated proof-search cardinality mismatch")
    obstruction = payload.get("rh_symmetry_obstruction", {})
    if obstruction.get("theorem") != (
        "PHASE_CLOSURE_ALONE_IS_NOT_A_FAITHFUL_CRITICAL_LINE_DISCRIMINATOR"
    ):
        raise AssertionError("reflection obstruction theorem mismatch")
    if not all(obstruction.get("checks", {}).values()):
        raise AssertionError("reflection obstruction checks failed")
    vm81 = payload.get("vm81_hash216_hydration", {})
    if not all(vm81.get("checks", {}).values()):
        raise AssertionError("VM81 hydration checks failed")
    native = payload.get("native_tensor_witnesses", {})
    if not all(native.get("checks", {}).values()):
        raise AssertionError("native tensor checks failed")
    search = payload.get("hydrated_symmetry_search", {})
    if not all(search.get("checks", {}).values()):
        raise AssertionError("hydrated symmetry search checks failed")

    core = {
        key: value
        for key, value in payload.items()
        if key != "integrated_proof_search_hash72"
    }
    expected = hash72_digest(
        {"domain": "HHS-PASS-191-INTEGRATED-PROOF-SEARCH-V1"}, core
    )
    if payload.get("integrated_proof_search_hash72") != expected:
        raise AssertionError("integrated proof-search Hash72 mismatch")
    return {
        "ok": True,
        "classification": CLASSIFICATION,
        "integrated_proof_search_hash72": expected,
        "hydrated_cardinality": HYDRATED_CARDINALITY,
        "proved_result": obstruction["theorem"],
        "theorem_status": payload["theorem_decision"]["status"],
    }


__all__ = [
    "SCHEMA",
    "CLASSIFICATION",
    "HYDRATED_CARDINALITY",
    "OUTER_ENVELOPE_MODULUS",
    "SymmetryPoint",
    "Pass186NativeABI",
    "exact_reflection_obstruction",
    "native_tensor_witnesses",
    "hydrated_symmetry_search",
    "hydrate_integrated_candidates",
    "run_integrated_proof_search",
    "verify_integrated_proof_search",
]
