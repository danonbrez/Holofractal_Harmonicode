"""Pass 219 I154 real-authority four-lane exhaustion planner.

The planner consumes I153 local/global equation-filter candidates only when their
gate witnesses are bound to a real Pass169/VM81 authority packet.  It never
manufactures gate truth and it never treats test fixtures as production
authority unless an explicit test-only override is supplied.
"""
from __future__ import annotations

import hashlib
import json
import string
from typing import Any, Iterable, Mapping

from hhs_runtime.pass219.fixed_cardinality_optimization import (
    EXHAUSTION_RATIO_DENOMINATOR,
    EXHAUSTION_RATIO_NUMERATOR,
    ROUTE_MULTIPLICITY_PER_TARGET,
    TARGET_CARDINALITY,
    WORKING_MANIFOLD_CARDINALITY,
    encode_working_route,
    validate_fixed_cardinalities,
)
from hhs_runtime.pass219.local_global_equation_search_filter import (
    GATE_OFFSETS,
    make_candidate,
    normalize_snapshot,
    evaluate_candidate,
)

PASS = 219
ITERATION = "I154"
SCHEMA = "HHS_PASS219_I154_AUTHORIZED_FOUR_LANE_EXHAUSTION_PLAN_V1"
AUTHORITY_SCHEMA = "HHS_PASS219_I154_PASS169_VM81_AUTHORITY_PACKET_V1"
WORKLOAD_SCHEMA = "HHS_PASS219_I154_FOUR_LANE_WORKLOAD_V1"

PRODUCTION_AUTHORITY_ORIGIN = "REPOSITORY_PRODUCTION_PASS169_VM81_PROVIDER"
TEST_FIXTURE_AUTHORITY_ORIGIN = "TEST_FIXTURE_PASS169_VM81_PROVIDER"

LANES = (
    "RAW5184_X86_64",
    "VM81_HASH72_HASH216",
    "OCTONION_DUAL_STEREO_TERNARY",
    "HARMONIC36_144X36",
)

HEX = frozenset(string.hexdigits)


class AuthorizedPlannerError(RuntimeError):
    pass


def _int(value: Any, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise AuthorizedPlannerError(f"{name}_EXACT_INTEGER_REQUIRED")
    if minimum is not None and value < minimum:
        raise AuthorizedPlannerError(f"{name}_OUT_OF_RANGE")
    return value


def _bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise AuthorizedPlannerError(f"{name}_BOOLEAN_REQUIRED")
    return value


def _hex64(value: Any, name: str, *, nonzero: bool = True) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in HEX for ch in value):
        raise AuthorizedPlannerError(f"{name}_SHA256_HEX_REQUIRED")
    value = value.lower()
    if nonzero and value == "0" * 64:
        raise AuthorizedPlannerError(f"{name}_ZERO_FORBIDDEN")
    return value


def _identity(value: Any, length: int, name: str) -> str:
    if not isinstance(value, str) or len(value) != length:
        raise AuthorizedPlannerError(f"{name}_LENGTH_{length}_REQUIRED")
    if any(ord(ch) < 33 or ord(ch) > 126 for ch in value):
        raise AuthorizedPlannerError(f"{name}_PRINTABLE_ASCII_REQUIRED")
    return value


def _stable_sha256(value: Mapping[str, Any]) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def normalize_authority_packet(
    packet: Mapping[str, Any],
    *,
    allow_test_authority: bool = False,
) -> dict[str, Any]:
    if packet.get("schema") != AUTHORITY_SCHEMA:
        raise AuthorizedPlannerError("AUTHORITY_PACKET_SCHEMA_MISMATCH")

    origin = packet.get("authority_origin")
    if origin not in (PRODUCTION_AUTHORITY_ORIGIN, TEST_FIXTURE_AUTHORITY_ORIGIN):
        raise AuthorizedPlannerError("AUTHORITY_ORIGIN_UNSUPPORTED")
    test_fixture = origin == TEST_FIXTURE_AUTHORITY_ORIGIN
    if test_fixture and not allow_test_authority:
        raise AuthorizedPlannerError("TEST_FIXTURE_AUTHORITY_FORBIDDEN")

    provider_available = _bool(packet.get("runtime_provider_available"), "RUNTIME_PROVIDER_AVAILABLE")
    authority_verified = _bool(packet.get("pass169_authority_verified"), "PASS169_AUTHORITY_VERIFIED")
    boolean_results_available = _bool(
        packet.get("boolean_gate_results_available"),
        "BOOLEAN_GATE_RESULTS_AVAILABLE",
    )
    membrane_ready = _bool(packet.get("membrane_input_ready"), "MEMBRANE_INPUT_READY")
    canonical_proof = _bool(packet.get("canonical_monolithic_proof"), "CANONICAL_MONOLITHIC_PROOF")
    local_snapshot_bound = _bool(
        packet.get("local_snapshot_binding_verified"),
        "LOCAL_SNAPSHOT_BINDING_VERIFIED",
    )

    decision = packet.get("decision")
    if decision not in ("PROPAGATE", "REJECT"):
        raise AuthorizedPlannerError("AUTHORITY_DECISION_UNSUPPORTED")

    P = _int(packet.get("P"), "P", minimum=1)
    snapshot_binding = _hex64(packet.get("local_snapshot_binding_sha256"), "LOCAL_SNAPSHOT_BINDING")
    global_root = _hex64(packet.get("canonical_global_symbol_environment_root"), "GLOBAL_ENVIRONMENT_ROOT")

    gates = packet.get("gate_results")
    if not isinstance(gates, list) or len(gates) != len(GATE_OFFSETS):
        raise AuthorizedPlannerError("GATE_RESULTS_COUNT_DRIFT")
    gate_results = [_bool(value, "GATE_RESULT") for value in gates]

    proof = _identity(packet.get("proof_hash216"), 216, "PROOF_HASH216")
    transition = _identity(packet.get("transition_hash216"), 216, "TRANSITION_HASH216")
    receipt = _identity(packet.get("receipt_hash72"), 72, "RECEIPT_HASH72")
    replay = _identity(packet.get("replay_hash72"), 72, "REPLAY_HASH72")
    vm81_steps = _int(packet.get("vm81_steps"), "VM81_STEPS", minimum=1)
    replay_steps = _int(packet.get("replay_vm81_steps"), "REPLAY_VM81_STEPS", minimum=1)

    if not (
        provider_available
        and authority_verified
        and boolean_results_available
        and membrane_ready
        and canonical_proof
        and local_snapshot_bound
    ):
        raise AuthorizedPlannerError("AUTHORITY_PACKET_INCOMPLETE")

    if decision == "PROPAGATE" and not all(gate_results):
        raise AuthorizedPlannerError("PROPAGATE_REQUIRES_ALL_GATES_TRUE")
    if decision == "REJECT" and all(gate_results):
        raise AuthorizedPlannerError("REJECT_REQUIRES_AT_LEAST_ONE_FALSE_GATE")

    normalized = {
        "schema": AUTHORITY_SCHEMA,
        "authority_origin": origin,
        "canonical_evidence_eligible": not test_fixture,
        "runtime_provider_available": provider_available,
        "pass169_authority_verified": authority_verified,
        "boolean_gate_results_available": boolean_results_available,
        "membrane_input_ready": membrane_ready,
        "canonical_monolithic_proof": canonical_proof,
        "local_snapshot_binding_verified": local_snapshot_bound,
        "decision": decision,
        "P": P,
        "local_snapshot_binding_sha256": snapshot_binding,
        "canonical_global_symbol_environment_root": global_root,
        "gate_results": gate_results,
        "proof_hash216": proof,
        "transition_hash216": transition,
        "receipt_hash72": receipt,
        "replay_hash72": replay,
        "vm81_steps": vm81_steps,
        "replay_vm81_steps": replay_steps,
        "i12111_binding_verified": _bool(packet.get("i12111_binding_verified"), "I12111_BINDING_VERIFIED"),
        "source_identity_exact": _bool(packet.get("source_identity_exact"), "SOURCE_IDENTITY_EXACT"),
        "pipeline_identity_exact": _bool(packet.get("pipeline_identity_exact"), "PIPELINE_IDENTITY_EXACT"),
        "deterministic_replay_verified": _bool(
            packet.get("deterministic_replay_verified"),
            "DETERMINISTIC_REPLAY_VERIFIED",
        ),
        "floating_point_authority": _bool(
            packet.get("floating_point_authority"),
            "FLOATING_POINT_AUTHORITY",
        ),
    }

    if not normalized["i12111_binding_verified"]:
        raise AuthorizedPlannerError("I12111_BINDING_NOT_VERIFIED")
    if not normalized["source_identity_exact"]:
        raise AuthorizedPlannerError("SOURCE_IDENTITY_NOT_EXACT")
    if not normalized["pipeline_identity_exact"]:
        raise AuthorizedPlannerError("PIPELINE_IDENTITY_NOT_EXACT")
    if not normalized["deterministic_replay_verified"]:
        raise AuthorizedPlannerError("DETERMINISTIC_REPLAY_NOT_VERIFIED")
    if normalized["floating_point_authority"]:
        raise AuthorizedPlannerError("FLOATING_POINT_AUTHORITY_FORBIDDEN")

    normalized["authority_packet_sha256"] = _stable_sha256(normalized)
    return normalized


def normalize_workload(
    workload: Mapping[str, Any],
    *,
    allow_test_authority: bool = False,
) -> dict[str, Any]:
    if workload.get("schema") != WORKLOAD_SCHEMA:
        raise AuthorizedPlannerError("WORKLOAD_SCHEMA_MISMATCH")
    lane = workload.get("lane")
    if lane not in LANES:
        raise AuthorizedPlannerError("WORKLOAD_LANE_UNSUPPORTED")

    snapshot_raw = workload.get("snapshot")
    authority_raw = workload.get("authority_packet")
    if not isinstance(snapshot_raw, Mapping) or not isinstance(authority_raw, Mapping):
        raise AuthorizedPlannerError("WORKLOAD_BINDINGS_REQUIRED")

    snapshot = normalize_snapshot(snapshot_raw)
    authority = normalize_authority_packet(
        authority_raw,
        allow_test_authority=allow_test_authority,
    )
    if authority["P"] != snapshot["P"]:
        raise AuthorizedPlannerError("AUTHORITY_P_SNAPSHOT_DRIFT")
    if authority["local_snapshot_binding_sha256"] != snapshot["snapshot_binding_sha256"]:
        raise AuthorizedPlannerError("AUTHORITY_LOCAL_SNAPSHOT_BINDING_DRIFT")

    block = _int(workload.get("target_block_index"), "TARGET_BLOCK_INDEX", minimum=0)
    route = _int(workload.get("route_index"), "ROUTE_INDEX", minimum=0)
    working_index = encode_working_route(block, route)
    if _int(workload.get("working_index"), "WORKING_INDEX", minimum=0) != working_index:
        raise AuthorizedPlannerError("WORKING_INDEX_DRIFT")

    baseline = _int(workload.get("baseline_work_units"), "BASELINE_WORK_UNITS", minimum=1)
    downstream = _int(
        workload.get("downstream_work_units_if_survives"),
        "DOWNSTREAM_WORK_UNITS_IF_SURVIVES",
        minimum=1,
    )

    return {
        "schema": WORKLOAD_SCHEMA,
        "workload_id": str(workload.get("workload_id")),
        "lane": lane,
        "snapshot": snapshot,
        "authority_packet": authority,
        "target_block_index": block,
        "route_index": route,
        "working_index": working_index,
        "baseline_work_units": baseline,
        "downstream_work_units_if_survives": downstream,
    }


def plan_authorized_four_lane_exhaustion(
    workloads: Iterable[Mapping[str, Any]],
    *,
    allow_test_authority: bool = False,
) -> dict[str, Any]:
    fixed = validate_fixed_cardinalities()
    normalized = [
        normalize_workload(item, allow_test_authority=allow_test_authority)
        for item in workloads
    ]
    if len(normalized) != len(LANES):
        raise AuthorizedPlannerError("EXACTLY_FOUR_REPRESENTATIVE_WORKLOADS_REQUIRED")
    if {item["lane"] for item in normalized} != set(LANES):
        raise AuthorizedPlannerError("ALL_FOUR_LANES_REQUIRED")
    if len({item["working_index"] for item in normalized}) != len(normalized):
        raise AuthorizedPlannerError("DUPLICATE_WORKING_INDEX")

    rows: list[dict[str, Any]] = []
    baseline_total = 0
    effective_total = 0
    all_production = True

    for item in normalized:
        authority = item["authority_packet"]
        snapshot = item["snapshot"]
        all_production = all_production and bool(authority["canonical_evidence_eligible"])

        candidate = make_candidate(
            snapshot=snapshot,
            target_block_index=item["target_block_index"],
            route_index=item["route_index"],
            global_symbol_environment_root=authority[
                "canonical_global_symbol_environment_root"
            ],
            gate_results=authority["gate_results"],
            global_symbol_environment_complete=True,
            cross_layer_revalidation_complete=True,
            local_symbol_shadowing_detected=False,
        )
        decision = evaluate_candidate(snapshot, candidate)

        provider_propagates = authority["decision"] == "PROPAGATE"
        if provider_propagates != bool(decision["survives_equation_filter"]):
            raise AuthorizedPlannerError("I153_PASS169_DECISION_DIVERGENCE")

        baseline = int(item["baseline_work_units"])
        selected = int(item["downstream_work_units_if_survives"]) if provider_propagates else 0
        baseline_total += baseline
        effective_total += selected

        rows.append(
            {
                "workload_id": item["workload_id"],
                "lane": item["lane"],
                "P": snapshot["P"],
                "snapshot_binding_sha256": snapshot["snapshot_binding_sha256"],
                "working_index": item["working_index"],
                "provider_decision": authority["decision"],
                "i153_survives": decision["survives_equation_filter"],
                "baseline_work_units": baseline,
                "effective_downstream_work_units": selected,
                "work_avoided": baseline - selected,
                "authority_packet_sha256": authority["authority_packet_sha256"],
                "proof_hash216": authority["proof_hash216"],
                "transition_hash216": authority["transition_hash216"],
                "receipt_hash72": authority["receipt_hash72"],
                "replay_hash72": authority["replay_hash72"],
                "canonical_evidence_eligible": authority["canonical_evidence_eligible"],
            }
        )

    within_ratio = (
        baseline_total * EXHAUSTION_RATIO_DENOMINATOR
        >= effective_total * EXHAUSTION_RATIO_NUMERATOR
    )
    canonical_evidence = all_production and not allow_test_authority

    if canonical_evidence:
        classification = (
            "AUTHORIZED_REPRESENTATIVE_WITHIN_81_OVER_7"
            if within_ratio
            else "AUTHORIZED_REPRESENTATIVE_OUTSIDE_81_OVER_7"
        )
    else:
        classification = (
            "TEST_ONLY_FOUR_LANE_PLUMBING_WITHIN_81_OVER_7"
            if within_ratio
            else "TEST_ONLY_FOUR_LANE_PLUMBING_OUTSIDE_81_OVER_7"
        )

    receipt = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "classification": classification,
        "lanes": list(LANES),
        "workloads": rows,
        "baseline_work_units": baseline_total,
        "effective_downstream_work_units": effective_total,
        "work_units_avoided": baseline_total - effective_total,
        "required_reduction_ratio": "81/7",
        "within_81_over_7_representative_work_budget": within_ratio,
        "canonical_evidence_eligible": canonical_evidence,
        "test_authority_override_used": allow_test_authority,
        "fixed_search_space": {
            "target_cardinality_decimal": str(TARGET_CARDINALITY),
            "working_manifold_cardinality_decimal": str(WORKING_MANIFOLD_CARDINALITY),
            "route_multiplicity_per_target_decimal": str(ROUTE_MULTIPLICITY_PER_TARGET),
        },
        "fixed_cardinality_receipt": fixed,
        "physical_full_target_exhaustion_claim": False,
        "physical_full_working_manifold_enumeration_claim": False,
        "global_exhaustion_bound_proven_from_sample": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "result": "PASS",
    }
    receipt["receipt_sha256"] = _stable_sha256(receipt)
    return receipt
