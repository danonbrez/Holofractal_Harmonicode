"""Pass 219 RML3 production binding for raw5184 octonion phase geometry.

RML3 connects three already-existing surfaces without creating a new authority:

1. I150/I148 exact 648-byte / 81x64 raw5184 hydration, which exposes twenty
   ordered octonion phase quads with exact x,y,z,w,xy,yx,zw,wz phase72 values.
2. RML2 two-plane phase geometry and recursively nested octonion circuits.
3. The canonical Pass169 Runtime ABI evidence record, which exposes the admitted
   proof/transition Hash216 identities plus Hash72 receipt/replay witnesses.

The binding is deliberately sidecar-only.  It never rewrites or remints an
existing Hash216/Hash72 value.  Instead it deterministically binds the physical
raw frame hash and RML2 phase-circuit root to the already-authoritative
transition/replay identities while retaining the fact that the current Pass169
record does not expose a native raw-frame digest inside its Hash216 payload.
"""
from __future__ import annotations

import hashlib
import json
import string
from typing import Any, Mapping

from hhs_runtime.core_sandbox.hhs_octonion_digital_dna_u72_table_v1 import (
    OCTONION_DNA_BASIS,
    PHASE_RING,
    table_receipt,
)
from hhs_runtime.hhs_pass219_global_raw5184_serialization_hydration_v1 import (
    RAW_BYTES,
    hydrate_raw5184_bytes,
    validation_receipt as raw5184_validation_receipt,
)
from hhs_runtime.hhs_pass219_raw5184_octonion_audio_hydration_v1 import (
    PHASE_CHANNELS as I148_PHASE_CHANNELS,
    PHASE_QUADS,
)
from hhs_runtime.pass219.phase_geometry_learning import (
    GEOMETRY_WITNESS_SCHEMA,
    OCTONION_STRING_SCHEMA,
    PHASE_CANDIDATE_SCHEMA,
    PHASE_CHANNELS,
    PHASE_CIRCUIT_SCHEMA,
    evaluate_phase_circuit,
    evaluate_phase_geometric_candidate,
)
from hhs_runtime.pass219.recursive_manifold_learning import LANES

PASS = 219
ITERATION = "RML3_PRODUCTION_PHASE_BINDING"
SCHEMA = "HHS_PASS219_RML3_PRODUCTION_PHASE_RUNTIME_BINDING_V1"
SOURCE_SCHEMA = "HHS_PASS219_RML3_RAW5184_PHASE_SOURCE_V1"
TRANSITION_BINDING_SCHEMA = "HHS_PASS219_RML3_PHASE_TRANSITION_SIDECAR_V1"
REPLAY_BINDING_SCHEMA = "HHS_PASS219_RML3_PHASE_REPLAY_SIDECAR_V1"
PASS169_RUNTIME_SCHEMA = "HHS_PASS219_I168_RUNTIME_BINDING_RECORD_V1"

PHASE_BANKS = 4
QUADS_PER_BANK = PHASE_QUADS // PHASE_BANKS
GEOMETRIC_FOLD_TREE = [["x", "z"], ["y", "w"]]
HEX = frozenset(string.hexdigits)


class ProductionPhaseBindingError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ProductionPhaseBindingError(f"FLOAT_CANONICAL_AUTHORITY_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _bytes_sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProductionPhaseBindingError(f"{label}_NONEMPTY_STRING_REQUIRED")
    return value


def _hex64(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in HEX for ch in value):
        raise ProductionPhaseBindingError(f"{label}_SHA256_REQUIRED")
    lowered = value.lower()
    if lowered == "0" * 64:
        raise ProductionPhaseBindingError(f"{label}_ZERO_HASH_FORBIDDEN")
    return lowered


def _identity(value: Any, length: int, label: str) -> str:
    if not isinstance(value, str) or len(value) != length:
        raise ProductionPhaseBindingError(f"{label}_LENGTH_{length}_REQUIRED")
    if any(ord(ch) < 33 or ord(ch) > 126 for ch in value):
        raise ProductionPhaseBindingError(f"{label}_PRINTABLE_ASCII_REQUIRED")
    return value


def _exact_int(value: Any, label: str, *, minimum: int = 0, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProductionPhaseBindingError(f"{label}_EXACT_INTEGER_REQUIRED")
    if value < minimum or (maximum is not None and value > maximum):
        raise ProductionPhaseBindingError(f"{label}_OUT_OF_RANGE")
    return value


def _candidate_lane_map(candidate: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = candidate.get("lane_witnesses")
    if not isinstance(rows, list) or len(rows) != len(LANES):
        raise ProductionPhaseBindingError("RML1_EXACTLY_FOUR_LANE_WITNESSES_REQUIRED")
    by_lane: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise ProductionPhaseBindingError("RML1_LANE_WITNESS_MAPPING_REQUIRED")
        lane = row.get("lane")
        if lane not in LANES or lane in by_lane:
            raise ProductionPhaseBindingError("RML1_LANE_TOPOLOGY_DRIFT")
        phase_nodes = row.get("ordered_phase_node_ids")
        if not isinstance(phase_nodes, Mapping) or tuple(phase_nodes.keys()) != PHASE_CHANNELS:
            raise ProductionPhaseBindingError(f"RML1_{lane}_ORDERED_PHASE_NODES_REQUIRED")
        if len(set(str(phase_nodes[channel]) for channel in PHASE_CHANNELS)) != len(PHASE_CHANNELS):
            raise ProductionPhaseBindingError(f"RML1_{lane}_PHASE_NODE_COLLAPSE")
        _identity(row.get("candidate_transition_hash216"), 216, f"RML1_{lane}_CANDIDATE_TRANSITION")
        by_lane[str(lane)] = row
    if set(by_lane) != set(LANES):
        raise ProductionPhaseBindingError("RML1_ALL_FOUR_LANES_REQUIRED")
    return by_lane


def _normalize_pass169_runtime_record(record: Mapping[str, Any]) -> dict[str, Any]:
    _reject_float(record)
    if record.get("schema") != PASS169_RUNTIME_SCHEMA:
        raise ProductionPhaseBindingError("PASS169_RUNTIME_SCHEMA_MISMATCH")

    required_true = (
        "source_identity_exact",
        "pass159_frontend_chain_complete",
        "typed_proof_verified",
        "interpreter_compiler_equality_verified",
        "exact_vm81_admission_verified",
        "atomic_commit_verified",
        "hash72_receipts_verified",
        "hash216_identities_verified",
        "deterministic_replay_verified",
        "reverse_restores_prior_state_verified",
        "live_runtime_abi_verified",
        "canonical_computation_through_runtime_abi",
        "single_vm81_commit_authority",
    )
    for name in required_true:
        if record.get(name) is not True:
            raise ProductionPhaseBindingError(f"PASS169_{name.upper()}_REQUIRED")

    forbidden_true = (
        "fallback_used",
        "floating_point_canonical_authority",
        "hash216_persistence_authority",
    )
    for name in forbidden_true:
        if record.get(name) is not False:
            raise ProductionPhaseBindingError(f"PASS169_{name.upper()}_FORBIDDEN")

    normalized = {
        "schema": PASS169_RUNTIME_SCHEMA,
        "canonical_source_sha256": _hex64(
            record.get("canonical_source_sha256"),
            "PASS169_CANONICAL_SOURCE",
        ),
        "proof_hash216": _identity(record.get("proof_hash216"), 216, "PASS169_PROOF_HASH216"),
        "transition_hash216": _identity(
            record.get("transition_hash216"), 216, "PASS169_TRANSITION_HASH216"
        ),
        "reverse_hash216": _identity(record.get("reverse_hash216"), 216, "PASS169_REVERSE_HASH216"),
        "receipt_hash72": _identity(record.get("receipt_hash72"), 72, "PASS169_RECEIPT_HASH72"),
        "replay_hash72": _identity(record.get("replay_hash72"), 72, "PASS169_REPLAY_HASH72"),
        "reverse_hash72": _identity(record.get("reverse_hash72"), 72, "PASS169_REVERSE_HASH72"),
        "vm5184_address": _exact_int(
            record.get("vm5184_address"), "PASS169_VM5184_ADDRESS", maximum=5183
        ),
        "forward_vm81_steps": _exact_int(
            record.get("forward_vm81_steps"), "PASS169_FORWARD_VM81_STEPS", minimum=1
        ),
        "replay_vm81_steps": _exact_int(
            record.get("replay_vm81_steps"), "PASS169_REPLAY_VM81_STEPS", minimum=1
        ),
        "reverse_vm81_steps": _exact_int(
            record.get("reverse_vm81_steps"), "PASS169_REVERSE_VM81_STEPS", minimum=1
        ),
        "candidate_id": _nonempty(record.get("candidate_id"), "PASS169_CANDIDATE_ID"),
        "transition_id": _nonempty(record.get("transition_id"), "PASS169_TRANSITION_ID"),
        "proof_id": _nonempty(record.get("proof_id"), "PASS169_PROOF_ID"),
        **{name: True for name in required_true},
        **{name: False for name in forbidden_true},
    }
    normalized["runtime_binding_sha256"] = _sha256(normalized)
    return normalized


def _quad_channel_map(quad: Any) -> dict[str, int]:
    bases = tuple(channel.basis for channel in quad.channels)
    if bases != tuple(I148_PHASE_CHANNELS) or bases != tuple(PHASE_CHANNELS):
        raise ProductionPhaseBindingError("I148_ORDERED_OCTONION_CHANNEL_DRIFT")
    values = {channel.basis: int(channel.phase72) for channel in quad.channels}
    if any(value < 0 or value >= PHASE_RING for value in values.values()):
        raise ProductionPhaseBindingError("I148_PHASE72_RANGE_DRIFT")
    if values["xy"] != (values["x"] + values["y"]) % PHASE_RING:
        raise ProductionPhaseBindingError("I148_XY_PHASE_DRIFT")
    if values["yx"] != (values["y"] + values["x"] + 36) % PHASE_RING:
        raise ProductionPhaseBindingError("I148_YX_PHASE_DRIFT")
    if values["zw"] != (values["z"] + values["w"]) % PHASE_RING:
        raise ProductionPhaseBindingError("I148_ZW_PHASE_DRIFT")
    if values["wz"] != (values["w"] + values["z"] + 36) % PHASE_RING:
        raise ProductionPhaseBindingError("I148_WZ_PHASE_DRIFT")
    return values


def build_raw5184_phase_source(payload: bytes | bytearray | memoryview) -> dict[str, Any]:
    raw = bytes(payload)
    if len(raw) != RAW_BYTES:
        raise ProductionPhaseBindingError("RAW5184_BYTE_COUNT")

    hydration = hydrate_raw5184_bytes(raw)
    if len(hydration.quads) != PHASE_QUADS:
        raise ProductionPhaseBindingError("I148_PHASE_QUAD_COUNT_DRIFT")
    if PHASE_QUADS % PHASE_BANKS:
        raise ProductionPhaseBindingError("RML3_PHASE_BANK_FACTOR_DRIFT")

    raw_sha = _bytes_sha256(raw)
    root_id = f"raw5184-phase:{raw_sha}"
    channel_ledger: list[dict[str, Any]] = []
    bank_circuits: list[dict[str, Any]] = []

    for bank_index in range(PHASE_BANKS):
        bank_id = f"{root_id}:bank:{bank_index}"
        children: list[dict[str, Any]] = []
        start = bank_index * QUADS_PER_BANK
        stop = start + QUADS_PER_BANK
        for quad in hydration.quads[start:stop]:
            phases = _quad_channel_map(quad)
            leaf_id = f"{bank_id}:quad:{quad.index}"
            node_ids = {
                basis: f"raw5184:q{quad.index}:cells:{'-'.join(str(v) for v in quad.cells)}:{basis}"
                for basis in PHASE_CHANNELS
            }
            leaf = {
                "schema": OCTONION_STRING_SCHEMA,
                "string_id": leaf_id,
                "parent_circuit_id": bank_id,
                "phase_steps": {
                    "x": phases["x"],
                    "y": phases["y"],
                    "z": phases["z"],
                    "w": phases["w"],
                },
                "ordered_phase_node_ids": node_ids,
                "fold_tree": GEOMETRIC_FOLD_TREE,
            }
            children.append(leaf)
            channel_ledger.append(
                {
                    "quad_index": int(quad.index),
                    "cells": list(quad.cells),
                    "ordered_channel_phase72": {
                        basis: phases[basis] for basis in PHASE_CHANNELS
                    },
                    "source_stereo_xy_cells": list(quad.stereo_xy),
                    "source_stereo_zw_cells": list(quad.stereo_zw),
                    "geometric_plane_pairs": [["x", "z"], ["y", "w"]],
                    "left_mono_phase72": list(quad.stereo_ternary.left_mono_phase72),
                    "right_mono_phase72": list(quad.stereo_ternary.right_mono_phase72),
                    "typed_quotient_only": bool(quad.stereo_ternary.typed_quotient_only),
                    "scalar_projection_runtime_authority": bool(
                        quad.stereo_ternary.scalar_projection_runtime_authority
                    ),
                }
            )
        bank_circuits.append(
            {
                "schema": PHASE_CIRCUIT_SCHEMA,
                "circuit_id": bank_id,
                "parent_circuit_id": root_id,
                "children": children,
            }
        )

    root_circuit = {
        "schema": PHASE_CIRCUIT_SCHEMA,
        "circuit_id": root_id,
        "parent_circuit_id": None,
        "children": bank_circuits,
    }
    evaluated = evaluate_phase_circuit(root_circuit)
    if evaluated["leaf_string_count"] != PHASE_QUADS:
        raise ProductionPhaseBindingError("RML3_PHASE_LEAF_COUNT_DRIFT")
    if evaluated["nested_circuit_count"] != PHASE_BANKS:
        raise ProductionPhaseBindingError("RML3_PHASE_BANK_COUNT_DRIFT")

    basis_receipt = table_receipt()
    if tuple(basis_receipt.get("basis", ())) != tuple(OCTONION_DNA_BASIS):
        raise ProductionPhaseBindingError("OCTONION_BASIS_RECEIPT_DRIFT")
    if int(basis_receipt.get("phase_ring", -1)) != PHASE_RING:
        raise ProductionPhaseBindingError("OCTONION_PHASE_RING_RECEIPT_DRIFT")

    source = {
        "schema": SOURCE_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "raw5184_sha256": raw_sha,
        "raw_bytes": len(raw),
        "vm81_cells": len(hydration.pcm64_bits),
        "pilot_cell_index": 80,
        "pilot_cell_uint64": int(hydration.pilot_pcm64_bits),
        "phase_quad_count": len(hydration.quads),
        "phase_bank_count": PHASE_BANKS,
        "quads_per_bank": QUADS_PER_BANK,
        "phase_channel_order": list(PHASE_CHANNELS),
        "phase_ring": PHASE_RING,
        "geometric_fold_tree": GEOMETRIC_FOLD_TREE,
        "root_circuit": root_circuit,
        "phase_circuit_root_sha256": evaluated["circuit_root_sha256"],
        "phase_circuit_evaluation_sha256": _sha256(evaluated),
        "channel_ledger": channel_ledger,
        "i150_validation_receipt": raw5184_validation_receipt(raw),
        "octonion_basis_receipt_hash72": basis_receipt["receipt_hash72"],
        "raw_frame_replayed_bit_identically": True,
        "scalar_projection_runtime_authority": False,
        "floating_point_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    source["source_receipt_sha256"] = _sha256(source)
    return source


def build_production_phase_candidate(
    rml_candidate: Mapping[str, Any],
    payload: bytes | bytearray | memoryview,
) -> dict[str, Any]:
    source = build_raw5184_phase_source(payload)
    by_lane = _candidate_lane_map(rml_candidate)
    geometry = {
        "schema": GEOMETRY_WITNESS_SCHEMA,
        "candidate_manifold_root_sha256": _hex64(
            rml_candidate.get("candidate_manifold_root_sha256"),
            "RML1_CANDIDATE_MANIFOLD_ROOT",
        ),
        "root_circuit": source["root_circuit"],
        "lane_bindings": [
            {
                "lane": lane,
                "candidate_transition_hash216": by_lane[lane]["candidate_transition_hash216"],
                "ordered_phase_node_ids": dict(by_lane[lane]["ordered_phase_node_ids"]),
                "phase_circuit_root_sha256": source["phase_circuit_root_sha256"],
            }
            for lane in LANES
        ],
    }
    return {
        "schema": PHASE_CANDIDATE_SCHEMA,
        "candidate": dict(rml_candidate),
        "phase_geometry": geometry,
    }


def bind_production_phase_runtime_evidence(
    plan: Mapping[str, Any],
    rml_candidate: Mapping[str, Any],
    payload: bytes | bytearray | memoryview,
    pass169_runtime_record: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind physical phase geometry to canonical runtime identities read-only.

    This does not claim that the current Pass169 Hash216 byte payload contains
    the raw5184 digest or phase root.  It creates deterministic sidecars that
    preserve the association while leaving all canonical hashes unchanged.
    """

    source = build_raw5184_phase_source(payload)
    package = build_production_phase_candidate(rml_candidate, payload)
    phase_evaluation = evaluate_phase_geometric_candidate(plan, package)
    runtime = _normalize_pass169_runtime_record(pass169_runtime_record)
    by_lane = _candidate_lane_map(rml_candidate)

    lane_bindings = {
        lane: {
            "candidate_transition_hash216": by_lane[lane]["candidate_transition_hash216"],
            "phase_circuit_root_sha256": source["phase_circuit_root_sha256"],
            "raw5184_sha256": source["raw5184_sha256"],
        }
        for lane in LANES
    }
    for lane, value in lane_bindings.items():
        value["binding_sha256"] = _sha256({"lane": lane, **value})

    transition_sidecar = {
        "schema": TRANSITION_BINDING_SCHEMA,
        "canonical_transition_hash216": runtime["transition_hash216"],
        "canonical_proof_hash216": runtime["proof_hash216"],
        "canonical_receipt_hash72": runtime["receipt_hash72"],
        "vm5184_address": runtime["vm5184_address"],
        "raw5184_sha256": source["raw5184_sha256"],
        "phase_circuit_root_sha256": source["phase_circuit_root_sha256"],
        "source_receipt_sha256": source["source_receipt_sha256"],
        "phase_evaluation_sha256": _sha256(phase_evaluation),
        "lane_bindings": lane_bindings,
        "canonical_transition_hash216_modified": False,
        "phase_root_embedded_inside_hash216_payload_claimed": False,
        "phase_root_preserved_with_transition_identity": True,
    }
    transition_sidecar["binding_sha256"] = _sha256(transition_sidecar)

    replay_sidecar = {
        "schema": REPLAY_BINDING_SCHEMA,
        "canonical_transition_hash216": runtime["transition_hash216"],
        "canonical_replay_hash72": runtime["replay_hash72"],
        "replay_vm81_steps": runtime["replay_vm81_steps"],
        "raw5184_sha256": source["raw5184_sha256"],
        "phase_circuit_root_sha256": source["phase_circuit_root_sha256"],
        "transition_binding_sha256": transition_sidecar["binding_sha256"],
        "deterministic_replay_verified": True,
        "canonical_replay_hash72_modified": False,
        "phase_root_preserved_with_replay_identity": True,
    }
    replay_sidecar["binding_sha256"] = _sha256(replay_sidecar)

    receipt = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "raw5184_phase_source": source,
        "phase_candidate_evaluation": phase_evaluation,
        "pass169_runtime_binding": runtime,
        "transition_phase_sidecar": transition_sidecar,
        "replay_phase_sidecar": replay_sidecar,
        "binding_semantics": {
            "physical_phase_source": "I150/I148_RAW5184_VM81_COMPATIBLE_HYDRATION",
            "phase_geometry": "RML2_TWO_PLANE_OCTONION_NESTED_CIRCUIT",
            "canonical_runtime_identity": "PASS169_RUNTIME_ABI_HASH216_HASH72",
            "hash216_reminted_or_modified": False,
            "hash72_reminted_or_modified": False,
            "native_raw_frame_digest_inside_pass169_hash216_proven": False,
            "read_only_sidecar_preserves_phase_root_with_transition_and_replay": True,
        },
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
        "result": "BOUND_READ_ONLY_PRODUCTION_PHASE_EVIDENCE",
    }
    receipt["receipt_sha256"] = _sha256(receipt)
    return receipt


__all__ = [
    "GEOMETRIC_FOLD_TREE",
    "PHASE_BANKS",
    "QUADS_PER_BANK",
    "REPLAY_BINDING_SCHEMA",
    "SCHEMA",
    "SOURCE_SCHEMA",
    "TRANSITION_BINDING_SCHEMA",
    "ProductionPhaseBindingError",
    "bind_production_phase_runtime_evidence",
    "build_production_phase_candidate",
    "build_raw5184_phase_source",
]
