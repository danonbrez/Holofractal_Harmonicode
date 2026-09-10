"""Pass 219 RML18 frozen-RML17 transport conservation acceleration.

RML18 does not modify RML17. It accelerates the dominant repeated global
address-manifold validation by replacing a fresh 1,492,992-address traversal
with an exact certificate bound to the frozen RML17 source blob, frozen RML17
receipt blob, and the deterministic exhaustive RML17 audit digest established
by the RML18 profiling run.

The user-specified admission invariant 1.001 is represented exactly as
1001/1000 plus the canonical decimal string "1.001". It is not a binary float,
threshold, residual, or timing score. A candidate that does not satisfy every
required frozen-RML17 equality predicate receives NULL/UNDEFINED immediately.

Timing remains observational. RML18 has no VM81 mutation, Hash72 mint,
Hash216 persistence, scalar-projection substitution, or route-selection
authority.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_runtime.pass219 import discrete_transport_conservation as rml17

PASS = 219
ITERATION = "RML18_TRANSPORT_CONSERVATION_ACCELERATION"
SCHEMA = "HHS_PASS219_RML18_TRANSPORT_CONSERVATION_ACCELERATION_V1"
NULL_UNDEFINED = "NULL/UNDEFINED"
ADMITTED = "ADMITTED"

INVARIANT_NUMERATOR = 1001
INVARIANT_DENOMINATOR = 1000
INVARIANT_DECIMAL = "1.001"

FROZEN_RML17_MERGE_COMMIT = "eea9fcf5fa90589cb9adf2b26260af50e10fb377"
FROZEN_RML17_TREE_SHA = "7f6271f39bda52a24946ac7d2786f8be8b93a3dd"
FROZEN_RML17_MODULE_GIT_BLOB_SHA1 = "1a257cf8cae245d71336a0f507e0a8e39b482c65"
FROZEN_RML17_RECEIPT_GIT_BLOB_SHA1 = "4e10c6e3443ad2b67752782b4776b28b2e263d29"
FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256 = "f5710359f5439d0bac98b5c8c01ddc64044d30744b9b4c874cf2095d1b56904a"

ROOT = Path(__file__).resolve().parents[2]
RML17_MODULE_PATH = ROOT / "hhs_runtime" / "pass219" / "discrete_transport_conservation.py"
RML17_RECEIPT_PATH = ROOT / "evidence" / "pass219_rml17" / "PASS_219_RML17_DISCRETE_TRANSPORT_CONSERVATION_RECEIPT.json"

_EXPECTED_DIRECTIONS = (
    "operation_forward",
    "operation_reverse",
    "phase_forward",
    "phase_reverse",
    "cell_forward",
    "cell_reverse",
)
_EXPECTED_INVERSE = {
    "operation_forward": "operation_reverse",
    "operation_reverse": "operation_forward",
    "phase_forward": "phase_reverse",
    "phase_reverse": "phase_forward",
    "cell_forward": "cell_reverse",
    "cell_reverse": "cell_forward",
}
_EXPECTED_FLUX = {
    "operation_forward": 1,
    "operation_reverse": -1,
    "phase_forward": 1,
    "phase_reverse": -1,
    "cell_forward": 1,
    "cell_reverse": -1,
}


class RML18TransportAccelerationError(RuntimeError):
    pass


def _git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _invariant_token() -> dict[str, Any]:
    return {
        "numerator": INVARIANT_NUMERATOR,
        "denominator": INVARIANT_DENOMINATOR,
        "decimal": INVARIANT_DECIMAL,
        "binary_floating_point_used": False,
    }


def exact_invariant_1001(value: Any) -> bool:
    """Return true only for the exact typed 1001/1000 == "1.001" token."""
    if not isinstance(value, Mapping):
        return False
    numerator = value.get("numerator")
    denominator = value.get("denominator")
    return (
        isinstance(numerator, int)
        and not isinstance(numerator, bool)
        and numerator == INVARIANT_NUMERATOR
        and isinstance(denominator, int)
        and not isinstance(denominator, bool)
        and denominator == INVARIANT_DENOMINATOR
        and value.get("decimal") == INVARIANT_DECIMAL
        and value.get("binary_floating_point_used") is False
    )


def _undefined(surface: str, reason: str, **context: Any) -> dict[str, Any]:
    result = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "surface": surface,
        "status": NULL_UNDEFINED,
        "defined": False,
        "omega_closure": True,
        "invariant": None,
        "rml17_equality_baseline_match": False,
        "reason": reason,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
        "route_selection_authority": False,
    }
    result.update(context)
    return result


def _admitted(surface: str, **context: Any) -> dict[str, Any]:
    result = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "surface": surface,
        "status": ADMITTED,
        "defined": True,
        "omega_closure": True,
        "invariant": _invariant_token(),
        "rml17_equality_baseline_match": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
        "route_selection_authority": False,
    }
    result.update(context)
    return result


def _receipt_equal_to_frozen_baseline(receipt: Mapping[str, Any]) -> tuple[bool, str]:
    if receipt.get("schema") != "HHS_PASS219_RML17_DISCRETE_TRANSPORT_CONSERVATION_RECEIPT_V1":
        return False, "RML17_RECEIPT_SCHEMA_MISMATCH"
    if receipt.get("iteration") != "RML17_DISCRETE_TRANSPORT_CONSERVATION":
        return False, "RML17_RECEIPT_ITERATION_MISMATCH"

    address = receipt.get("address_manifold")
    if not isinstance(address, Mapping):
        return False, "RML17_ADDRESS_MANIFOLD_RECEIPT_MISSING"
    if (
        address.get("lanes") != 4
        or address.get("operations_per_cell") != 64
        or address.get("phase_states") != 72
        or address.get("cells") != 81
        or address.get("addresses") != 1_492_992
        or address.get("exhaustive_validation") is not True
        or address.get("cross_lane_transition_authority_added") is not False
    ):
        return False, "RML17_ADDRESS_MANIFOLD_RECEIPT_MISMATCH"

    validated = receipt.get("validated_repair")
    if not isinstance(validated, Mapping):
        return False, "RML17_VALIDATED_REPAIR_RECEIPT_MISSING"
    required_gate_keys = (
        "discrete_divergence_gate",
        "reciprocal_edge_balance_gate",
        "admission_preservation_gate",
        "zero_canonical_diffusion_gate",
        "composed_reverse_closure_gate",
        "structural_information_loss_zero_gate",
    )
    if (
        validated.get("conclusion") != "success"
        or validated.get("rml17_tests_passed") != 13
        or validated.get("rml17_exhaustive_address_count") != 1_492_992
        or any(validated.get(key) != "pass" for key in required_gate_keys)
    ):
        return False, "RML17_VALIDATED_REPAIR_GATE_MISMATCH"

    authority = receipt.get("authority")
    if not isinstance(authority, Mapping):
        return False, "RML17_AUTHORITY_RECEIPT_MISSING"
    if (
        authority.get("rml17_additive_read_only_membrane") is not True
        or authority.get("rml16_operator_semantics_changed") is not False
        or authority.get("vm81_mutation_authority_added") is not False
        or authority.get("hash72_mint_authority_added") is not False
        or authority.get("hash216_persistence_authority_added") is not False
        or authority.get("floating_point_authority_added") is not False
        or authority.get("scalar_projection_substitution_authority_added") is not False
        or authority.get("hash216_cryptographic_inversion_used") is not False
    ):
        return False, "RML17_AUTHORITY_RECEIPT_MISMATCH"
    return True, "RML17_RECEIPT_EQUAL"


def verify_frozen_rml17_nucleus() -> dict[str, Any]:
    """Verify the exact repository-visible RML17 source/receipt nucleus."""
    if not RML17_MODULE_PATH.is_file():
        return _undefined("RML17_NUCLEUS", "RML17_MODULE_MISSING")
    if not RML17_RECEIPT_PATH.is_file():
        return _undefined("RML17_NUCLEUS", "RML17_RECEIPT_MISSING")

    module_bytes = RML17_MODULE_PATH.read_bytes()
    receipt_bytes = RML17_RECEIPT_PATH.read_bytes()
    module_blob = _git_blob_sha1(module_bytes)
    receipt_blob = _git_blob_sha1(receipt_bytes)
    if module_blob != FROZEN_RML17_MODULE_GIT_BLOB_SHA1:
        return _undefined(
            "RML17_NUCLEUS",
            "RML17_MODULE_BLOB_MISMATCH",
            observed_module_blob_sha1=module_blob,
        )
    if receipt_blob != FROZEN_RML17_RECEIPT_GIT_BLOB_SHA1:
        return _undefined(
            "RML17_NUCLEUS",
            "RML17_RECEIPT_BLOB_MISMATCH",
            observed_receipt_blob_sha1=receipt_blob,
        )

    try:
        receipt = json.loads(receipt_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _undefined("RML17_NUCLEUS", "RML17_RECEIPT_PARSE_FAILED")
    if not isinstance(receipt, Mapping):
        return _undefined("RML17_NUCLEUS", "RML17_RECEIPT_MAPPING_REQUIRED")

    receipt_ok, reason = _receipt_equal_to_frozen_baseline(receipt)
    if not receipt_ok:
        return _undefined("RML17_NUCLEUS", reason)

    runtime_shape_ok = (
        rml17.LANE_COUNT == 4
        and rml17.OPERATIONS_PER_CELL == 64
        and rml17.PHASE_COUNT == 72
        and rml17.CELL_COUNT == 81
        and rml17.ADDRESS_COUNT == 1_492_992
        and tuple(rml17.DIRECTIONS) == _EXPECTED_DIRECTIONS
        and dict(rml17.INVERSE_DIRECTION) == _EXPECTED_INVERSE
        and dict(rml17.DIRECTION_FLUX) == _EXPECTED_FLUX
    )
    if not runtime_shape_ok:
        return _undefined("RML17_NUCLEUS", "RML17_RUNTIME_SHAPE_MISMATCH")

    return _admitted(
        "RML17_NUCLEUS",
        frozen_rml17_merge_commit=FROZEN_RML17_MERGE_COMMIT,
        frozen_rml17_tree_sha=FROZEN_RML17_TREE_SHA,
        frozen_rml17_module_git_blob_sha1=module_blob,
        frozen_rml17_receipt_git_blob_sha1=receipt_blob,
        frozen_rml17_exhaustive_audit_sha256=FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256,
        frozen_address_count=rml17.ADDRESS_COUNT,
        frozen_exhaustive_validation=True,
    )


def accelerated_address_manifold_certificate() -> dict[str, Any]:
    """Return the O(1) prevalidated RML17 global conservation certificate."""
    nucleus = verify_frozen_rml17_nucleus()
    if nucleus.get("status") != ADMITTED or not exact_invariant_1001(nucleus.get("invariant")):
        return _undefined(
            "GLOBAL_ADDRESS_MANIFOLD",
            "FROZEN_RML17_NUCLEUS_NOT_1_001",
            nucleus_reason=nucleus.get("reason"),
        )

    return _admitted(
        "GLOBAL_ADDRESS_MANIFOLD",
        proof_method="FROZEN_RML17_EXHAUSTIVE_CERTIFICATE_REUSE",
        exhaustive_runtime_scan_executed=False,
        frozen_exhaustive_scan_address_count=1_492_992,
        frozen_rml17_exhaustive_audit_sha256=FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256,
        zero_discrete_divergence=True,
        reciprocal_edge_balance=True,
        admission_preservation=True,
        zero_canonical_diffusion=True,
        composed_reverse_closure=True,
        structural_information_loss_zero=True,
        latency_participates_in_viscosity_definition=False,
        rml17_source_blob_verified=True,
        rml17_receipt_blob_verified=True,
        optimized_runtime_path=True,
    )


def compare_accelerated_certificate_to_exhaustive() -> dict[str, Any]:
    """Validation-only direct equality comparison to a fresh frozen RML17 scan."""
    candidate = accelerated_address_manifold_certificate()
    if candidate.get("status") != ADMITTED:
        return _undefined(
            "GLOBAL_ADDRESS_MANIFOLD_DIFFERENTIAL",
            "ACCELERATED_CERTIFICATE_UNDEFINED",
        )
    exhaustive = rml17.audit_transport_address_manifold()
    gates_equal = (
        exhaustive.get("result") == "PASS"
        and exhaustive.get("visited_address_count") == 1_492_992
        and exhaustive.get("all_addresses_zero_discrete_divergence") is True
        and exhaustive.get("all_address_edges_reciprocal") is True
        and exhaustive.get("all_address_edge_fluxes_balanced") is True
        and exhaustive.get("all_addresses_encode_decode_bijective") is True
        and exhaustive.get("audit_sha256") == FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256
        and candidate.get("zero_discrete_divergence") is True
        and candidate.get("reciprocal_edge_balance") is True
        and candidate.get("admission_preservation") is True
        and candidate.get("zero_canonical_diffusion") is True
        and candidate.get("composed_reverse_closure") is True
        and candidate.get("structural_information_loss_zero") is True
    )
    if not gates_equal:
        return _undefined(
            "GLOBAL_ADDRESS_MANIFOLD_DIFFERENTIAL",
            "RML17_EXHAUSTIVE_EQUALITY_MISMATCH",
            observed_exhaustive_audit_sha256=exhaustive.get("audit_sha256"),
        )
    return _admitted(
        "GLOBAL_ADDRESS_MANIFOLD_DIFFERENTIAL",
        exhaustive_rml17_result="PASS",
        exhaustive_rml17_audit_sha256=exhaustive["audit_sha256"],
        accelerated_certificate_equal=True,
        exhaustive_address_count=exhaustive["visited_address_count"],
    )


def gate_transport_address_candidate(address: Any) -> dict[str, Any]:
    """Fail closed unless one transport address returns the frozen 1.001 invariant."""
    global_certificate = accelerated_address_manifold_certificate()
    if global_certificate.get("status") != ADMITTED:
        return _undefined("TRANSPORT_ADDRESS", "GLOBAL_RML17_CERTIFICATE_UNDEFINED")
    try:
        local = rml17.audit_transport_address(address)
    except Exception as exc:  # fail-closed membrane
        return _undefined(
            "TRANSPORT_ADDRESS",
            "RML17_LOCAL_ADDRESS_AUDIT_REJECTED",
            rejection_type=type(exc).__name__,
        )
    local_equal = (
        local.get("encode_decode_bijective") is True
        and local.get("zero_discrete_divergence") is True
        and local.get("reciprocal_neighbor_edges") is True
        and local.get("reciprocal_edge_flux_balance") is True
        and local.get("address_neighborhood_has_canonical_transition_authority") is False
    )
    if not local_equal:
        return _undefined(
            "TRANSPORT_ADDRESS",
            "RML17_LOCAL_ADDRESS_EQUALITY_MISMATCH",
            address=local.get("address"),
        )
    return _admitted(
        "TRANSPORT_ADDRESS",
        address=local["address"],
        coordinates=local["coordinates"],
        rml17_local_audit_sha256=local["audit_sha256"],
        global_certificate_reused=True,
    )


def _route_audit_equal(audit: Mapping[str, Any]) -> bool:
    return (
        audit.get("result") == "PASS"
        and audit.get("zero_discrete_route_divergence") is True
        and audit.get("reciprocal_edge_balance") is True
        and audit.get("admission_preserved") is True
        and audit.get("route_edge_chain_identity_preserved") is True
        and audit.get("nu_h") == 0
        and audit.get("l_h_equivalent_zero") is True
        and audit.get("canonical_diffusion_operator_present") is False
        and audit.get("composed_reverse_identity_for_route") is True
        and audit.get("delta_loss") == 0
        and audit.get("structural_information_loss_zero") is True
        and audit.get("hash216_cryptographic_inversion_used") is False
        and audit.get("latency_participates_in_viscosity_definition") is False
        and audit.get("rml16_cache_changes_operator_semantics") is False
        and audit.get("canonical_vm81_mutation_authority") is False
        and audit.get("canonical_hash72_mint_authority") is False
        and audit.get("canonical_hash216_persistence_authority") is False
        and audit.get("floating_point_authority") is False
        and audit.get("scalar_projection_substitution_authority") is False
    )


def gate_route_candidate(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    *,
    route_id: str,
) -> dict[str, Any]:
    """Return 1.001 only for a route exactly equal to every frozen RML17 gate."""
    global_certificate = accelerated_address_manifold_certificate()
    if global_certificate.get("status") != ADMITTED:
        return _undefined("ROUTE", "GLOBAL_RML17_CERTIFICATE_UNDEFINED")
    try:
        audit = rml17.audit_rml16_route_conservation(source, target, route_id=route_id)
    except Exception as exc:  # fail-closed membrane
        return _undefined(
            "ROUTE",
            "RML17_ROUTE_AUDIT_REJECTED",
            route_id=str(route_id),
            rejection_type=type(exc).__name__,
        )
    if not _route_audit_equal(audit):
        return _undefined(
            "ROUTE",
            "RML17_ROUTE_EQUALITY_MISMATCH",
            route_id=str(route_id),
            rml17_audit_sha256=audit.get("audit_sha256"),
        )
    return _admitted(
        "ROUTE",
        route_id=str(route_id),
        source_state_sha256=audit["source_state_sha256"],
        target_state_sha256=audit["target_state_sha256"],
        selected_route_sha256=audit["selected_route_sha256"],
        rml17_audit_sha256=audit["audit_sha256"],
        edge_count=audit["edge_count"],
        global_certificate_reused=True,
    )


def gate_composed_route_candidate(
    states: Sequence[Mapping[str, Any]],
    *,
    composition_id: str,
) -> dict[str, Any]:
    """Apply the exact 1.001 admission rule to an admitted route composition."""
    global_certificate = accelerated_address_manifold_certificate()
    if global_certificate.get("status") != ADMITTED:
        return _undefined("ROUTE_COMPOSITION", "GLOBAL_RML17_CERTIFICATE_UNDEFINED")
    try:
        audit = rml17.audit_composed_transport_conservation(
            states,
            composition_id=composition_id,
        )
    except Exception as exc:  # fail-closed membrane
        return _undefined(
            "ROUTE_COMPOSITION",
            "RML17_COMPOSITION_AUDIT_REJECTED",
            composition_id=str(composition_id),
            rejection_type=type(exc).__name__,
        )
    equal = (
        audit.get("result") == "PASS"
        and audit.get("all_prefix_states_admission_preserved") is True
        and audit.get("route_segments_chain_exactly") is True
        and audit.get("all_segments_zero_discrete_divergence") is True
        and audit.get("all_segments_reciprocal_edge_balanced") is True
        and audit.get("nu_h") == 0
        and audit.get("l_h_equivalent_zero_under_composition") is True
        and audit.get("reverse_composition_restores_origin_exactly") is True
        and audit.get("delta_loss") == 0
        and audit.get("structural_information_loss_zero_under_composition") is True
        and audit.get("canonical_transition_authority_expanded") is False
        and audit.get("canonical_vm81_mutation_authority") is False
        and audit.get("canonical_hash72_mint_authority") is False
        and audit.get("canonical_hash216_persistence_authority") is False
    )
    if not equal:
        return _undefined(
            "ROUTE_COMPOSITION",
            "RML17_COMPOSITION_EQUALITY_MISMATCH",
            composition_id=str(composition_id),
            rml17_audit_sha256=audit.get("audit_sha256"),
        )
    return _admitted(
        "ROUTE_COMPOSITION",
        composition_id=str(composition_id),
        origin_state_sha256=audit["origin_state_sha256"],
        terminal_state_sha256=audit["terminal_state_sha256"],
        segment_count=audit["segment_count"],
        rml17_audit_sha256=audit["audit_sha256"],
        global_certificate_reused=True,
    )


def enforce_candidate_1001(record: Any) -> dict[str, Any]:
    """Final closure membrane: anything without exact 1.001 becomes undefined."""
    if (
        isinstance(record, Mapping)
        and record.get("status") == ADMITTED
        and record.get("defined") is True
        and record.get("rml17_equality_baseline_match") is True
        and exact_invariant_1001(record.get("invariant"))
    ):
        return dict(record)
    return _undefined("CANDIDATE_CLOSURE", "EXACT_1_001_INVARIANT_REQUIRED")


__all__ = [
    "ADMITTED",
    "FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256",
    "FROZEN_RML17_MERGE_COMMIT",
    "FROZEN_RML17_MODULE_GIT_BLOB_SHA1",
    "FROZEN_RML17_RECEIPT_GIT_BLOB_SHA1",
    "FROZEN_RML17_TREE_SHA",
    "INVARIANT_DECIMAL",
    "INVARIANT_DENOMINATOR",
    "INVARIANT_NUMERATOR",
    "ITERATION",
    "NULL_UNDEFINED",
    "RML18TransportAccelerationError",
    "accelerated_address_manifold_certificate",
    "compare_accelerated_certificate_to_exhaustive",
    "enforce_candidate_1001",
    "exact_invariant_1001",
    "gate_composed_route_candidate",
    "gate_route_candidate",
    "gate_transport_address_candidate",
    "verify_frozen_rml17_nucleus",
]
