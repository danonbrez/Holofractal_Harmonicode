from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass175 import InstructionRequest, Pass175Runtime, ReciprocalLane
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice import (
    hhs_pass191_integrated_proof_engine_v1 as inherited_engine,
)
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_manifold_kernel_v1 import (
    CONTEXTUAL_CARDINALITY,
    MANIFOLD_SOURCE,
    ORDERED_BASIS,
    OUTER_ENVELOPE_MODULUS,
    PROJECTED_CARDINALITY,
    run_native_manifold_scan,
    verify_native_manifold_scan,
)

SCHEMA = "HHS_PASS_191_INTEGRATED_MANIFOLD_PROOF_SEARCH_V2"
CLASSIFICATION = "HHS_PASS_191_UNIFIED_MANIFOLD_VM81_PROOF_SEARCH_EXECUTED"


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _frontier_instruction_requests(
    certificates: Sequence[Mapping[str, Any]],
) -> list[InstructionRequest]:
    encodings = (
        b"\x90",
        b"\x31\xc0",
        b"\x0f\xa2",
        b"\x48\xb8\x01\x00\x00\x00\x00\x00\x00\x00",
    )
    requests: list[InstructionRequest] = []
    for index, certificate in enumerate(certificates):
        address = int(certificate["address"])
        basis = str(certificate["ordered_basis"])
        parameters = certificate["parameters"]
        residuals = certificate["residuals"]
        cell = int(address // (64 * 243 * 41)) % 81
        residual = int(residuals["cubic_minus_delta"]) + int(
            residuals["delta_minus_idempotent"]
        )
        delta = 1 if residual >= 0 else -1
        request_payload = {
            "address": address,
            "basis": basis,
            "parameters": parameters,
            "candidate_hash72": certificate["candidate_hash72"],
            "manifold_source_sha256": sha256(
                MANIFOLD_SOURCE.encode("utf-8")
            ).hexdigest(),
        }
        requests.append(
            InstructionRequest(
                exact_bytes=encodings[index % len(encodings)],
                ordered_operands=(
                    basis,
                    f"MANIFOLD::{address}::{certificate['candidate_hash72']}",
                ),
                parenthesization=(
                    "PASS191_UNIFIED_MANIFOLD::"
                    + hash72_digest(
                        {"domain": "HHS-PASS-191-FRONTIER-REQUEST-V1"},
                        request_payload,
                    )
                ),
                read_set=(cell,),
                write_set=(cell,),
                thread_id=index,
                sequence=index,
                explicit_delta=((cell, delta),),
            )
        )
    return requests


def hydrate_manifold_frontier(
    certificates: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if not certificates:
        raise ValueError("manifold frontier must contain at least one candidate")
    runtime = Pass175Runtime()
    status_before = runtime.status()
    bootstrap = runtime.cold_hydrate_bootstrap(seal=True)
    requests = _frontier_instruction_requests(certificates)
    execution = runtime.execute_batch(requests, max_workers=min(8, len(requests)))
    replay = runtime.replay()
    status_after = runtime.status()

    source_root = runtime.permanent_instructions[0].identity.source_bytes_sha256
    xy_lane = ReciprocalLane(
        opcode="xy",
        phase=0,
        magnitude_numerator=1,
        magnitude_denominator=2,
        source_root_sha256=source_root,
        provenance_root_sha256=sha256(b"PASS191-MANIFOLD-XY").hexdigest(),
    )
    yx_lane = ReciprocalLane(
        opcode="yx",
        phase=36,
        magnitude_numerator=1,
        magnitude_denominator=2,
        source_root_sha256=source_root,
        provenance_root_sha256=sha256(b"PASS191-MANIFOLD-YX").hexdigest(),
    )
    reciprocal_projection = runtime.project_ab(xy_lane, yx_lane)
    waves = execution.get("waves", [])
    candidates = [
        candidate for wave in waves for candidate in wave.get("candidates", [])
    ]
    frontier_links = [
        {
            "rank": index,
            "address": int(certificate["address"]),
            "ordered_basis": certificate["ordered_basis"],
            "candidate_hash72": certificate["candidate_hash72"],
        }
        for index, certificate in enumerate(certificates)
    ]
    checks = {
        "permanent_instruction_fabric_5184": status_before.get(
            "permanent_instruction_count"
        )
        == 5184,
        "projected_address_space_1259712": status_before.get(
            "projected_address_count"
        )
        == PROJECTED_CARDINALITY,
        "cold_hydration_sealed_through_vm81": bootstrap.get(
            "sealed_through_vm81"
        )
        is True,
        "frontier_candidate_batch_committed": execution.get("classification")
        == "HHS_PASS_175_CANDIDATES_VM81_COMMITTED",
        "all_frontier_candidates_committed": execution.get("candidate_count")
        == len(requests)
        and len(candidates) == len(requests),
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
        raise AssertionError(f"manifold frontier hydration failed: {checks}")
    core = {
        "frontier_links": frontier_links,
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
        "frontier_hydration_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-MANIFOLD-FRONTIER-HYDRATION-V1"},
            core,
        ),
    }


def run_integrated_manifold_search(
    repo_root: str | Path,
    native_library: str | Path,
    scanner_path: str | Path,
    *,
    epoch: int = 0,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    native = inherited_engine.Pass186NativeABI(native_library)
    pass186_receipt = inherited_engine._load_pass186_receipt(root)
    native_witnesses = inherited_engine.native_tensor_witnesses(native)
    reflection_obstruction = inherited_engine.exact_reflection_obstruction()
    symmetry_diagnostic = inherited_engine.hydrated_symmetry_search(native)
    manifold = run_native_manifold_scan(scanner_path, epoch=epoch)
    frontier = manifold["deep_candidate_certificates"]
    hydration = hydrate_manifold_frontier(frontier)
    manifold_verification = verify_native_manifold_scan(manifold)

    theorem_decision = {
        "target": "RIEMANN_HYPOTHESIS",
        "status": "OBSTRUCTED",
        "scope": "CURRENT_REGISTERED_RULE_GRAPH",
        "proved_results": [
            manifold["finite_epoch_decision"]["proposition"],
            reflection_obstruction["theorem"],
        ],
        "obstruction": {
            "missing_bridge": (
                "ZETA_ZERO(sigma,t) => 2*sigma-1=0, or an exact nontrivial "
                "off-axis zeta-zero witness satisfying 2*sigma-1!=0"
            ),
            "why_required": (
                "The registered reflection and quartic closure rules admit both "
                "critical fixed points and off-axis two-cycles. The complete finite "
                "contextual epoch therefore cannot transfer closure alone into a "
                "zeta-zero location theorem."
            ),
            "reopen_condition": (
                "Register and validate a zeta-zero-specific exact rule eliminating "
                "all off-axis cycles, or produce an exact off-axis zero certificate."
            ),
        },
    }
    core = {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "authority_path": [
            "PASS_189_HQLH_51648192_CONTEXTUAL_FABRIC",
            "PASS_191_EXACT_MANIFOLD_RESIDUAL_KERNEL",
            "PASS_186_X86_64_Q144_NONCOMMUTATIVE_ABI",
            "PASS_175_HASH216_VM5184_G243_HYDRATION",
            "PASS_174_SINGLETON_VM81_COMMIT_AUTHORITY",
            "HASH72_DETERMINISTIC_REPLAY",
        ],
        "cardinality": {
            "vm81": 81,
            "operations64": 64,
            "g243": 243,
            "reciprocal_coordinates41": 41,
            "projected": PROJECTED_CARDINALITY,
            "contextual": CONTEXTUAL_CARDINALITY,
            "outer_envelope_modulus": OUTER_ENVELOPE_MODULUS,
        },
        "pass186_exhaustive_validation": pass186_receipt,
        "native_tensor_witnesses": native_witnesses,
        "unified_manifold_epoch": manifold,
        "unified_manifold_verification": manifold_verification,
        "vm81_hash216_frontier_hydration": hydration,
        "reflection_obstruction": reflection_obstruction,
        "symmetric_grid_diagnostic": {
            **symmetry_diagnostic,
            "role": "REGISTERED_SUBROUTINE_DIAGNOSTIC_NOT_DECISION_SURFACE",
        },
        "theorem_decision": theorem_decision,
        "continuation": {
            "snapshot": manifold["continuation"]["snapshot"],
            "next_epoch": manifold["continuation"]["snapshot"]["next_epoch"],
            "frontier_hash72": [
                item["candidate_hash72"] for item in frontier
            ],
            "policy": "SERIALIZED_EPOCH_WITH_PARALLEL_IMMUTABLE_FRONTIER_EVALUATION",
        },
    }
    return {
        **core,
        "integrated_manifold_search_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-INTEGRATED-MANIFOLD-SEARCH-V2"}, core
        ),
    }


def verify_integrated_manifold_search(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("integrated manifold schema mismatch")
    if payload.get("classification") != CLASSIFICATION:
        raise AssertionError("integrated manifold classification mismatch")
    cardinality = payload.get("cardinality", {})
    if cardinality.get("projected") != PROJECTED_CARDINALITY:
        raise AssertionError("projected cardinality mismatch")
    if cardinality.get("contextual") != CONTEXTUAL_CARDINALITY:
        raise AssertionError("contextual cardinality mismatch")
    if cardinality.get("outer_envelope_modulus") != OUTER_ENVELOPE_MODULUS:
        raise AssertionError("outer envelope mismatch")
    manifold = payload.get("unified_manifold_epoch", {})
    manifold_verification = verify_native_manifold_scan(manifold)
    if payload.get("unified_manifold_verification") != manifold_verification:
        raise AssertionError("manifold verification receipt mismatch")
    hydration = payload.get("vm81_hash216_frontier_hydration", {})
    if not all(hydration.get("checks", {}).values()):
        raise AssertionError("frontier VM81 hydration checks failed")
    if not all(
        payload.get("native_tensor_witnesses", {}).get("checks", {}).values()
    ):
        raise AssertionError("native tensor checks failed")
    decision = payload.get("theorem_decision", {})
    if decision.get("status") != "OBSTRUCTED":
        raise AssertionError("theorem decision must be formal OBSTRUCTED")
    if decision.get("scope") != "CURRENT_REGISTERED_RULE_GRAPH":
        raise AssertionError("theorem decision scope mismatch")
    core = {
        key: value
        for key, value in payload.items()
        if key != "integrated_manifold_search_hash72"
    }
    expected = hash72_digest(
        {"domain": "HHS-PASS-191-INTEGRATED-MANIFOLD-SEARCH-V2"}, core
    )
    if payload.get("integrated_manifold_search_hash72") != expected:
        raise AssertionError("integrated manifold search Hash72 mismatch")
    return {
        "ok": True,
        "classification": CLASSIFICATION,
        "integrated_manifold_search_hash72": expected,
        "projected_cardinality": PROJECTED_CARDINALITY,
        "contextual_cardinality": CONTEXTUAL_CARDINALITY,
        "visited": manifold_verification["visited"],
        "exact_chain_hits": manifold_verification["exact_chain_hits"],
        "theorem_status": decision["status"],
        "frontier_size": manifold_verification["frontier_size"],
    }


__all__ = [
    "SCHEMA",
    "CLASSIFICATION",
    "hydrate_manifold_frontier",
    "run_integrated_manifold_search",
    "verify_integrated_manifold_search",
]
