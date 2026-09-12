"""Pass 219 RML18 reconciled-RML17 transport conservation acceleration.

RML18 does not modify RML17. It accelerates the dominant repeated global
address-manifold validation by replacing a fresh 1,492,992-address traversal
with an exact certificate bound to the reconciled RML17 source blob, the sealed
RML17 <-> native C++ parity receipt, and the deterministic exhaustive RML17
audit digest.

The user-specified admission invariant 1.001 is represented exactly as
1001/1000 plus the canonical decimal string "1.001". It is not a binary float,
threshold, residual, or timing score. A candidate that does not satisfy every
required reconciled-RML17 equality predicate receives NULL/UNDEFINED
immediately.

Timing remains observational. RML18 has no VM81 mutation, Hash72 mint,
Hash216 persistence, scalar-projection substitution, route-selection, or
canonical transition authority.
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

# Reconciled RML17/native parity nucleus. The compatibility names are retained
# for callers of the original RML18 surface, but now bind the validated parity
# successor rather than the superseded six-direction RML17-only certificate.
FROZEN_RML17_PARITY_VALIDATED_COMMIT = "b2cdd1d2fdea504224bbd597fc373cd827a27fd7"
FROZEN_RML17_MERGE_COMMIT = FROZEN_RML17_PARITY_VALIDATED_COMMIT
FROZEN_RML17_TREE_SHA = "445d62087b19ec737813c35b7dfd6308b073bf13"
FROZEN_RML17_MODULE_GIT_BLOB_SHA1 = "0658be67137027d7c4169540b8a99067577b8b37"
FROZEN_RML17_RECEIPT_GIT_BLOB_SHA1 = "e561c8f2e9827a4f550ca54e2c02e9c28a61a5aa"
FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256 = "b4ad90ee50eab47070b22118b7d3a120592ea1b750ce4e2725730d9ab49a8d67"
FROZEN_RML17_NATIVE_PARITY_AUDIT_SHA256 = "1b6e9edde3efee1ab6a779c4ef1ff540dbd35dfc796e27dacaf6c91f2542ef19"

ROOT = Path(__file__).resolve().parents[2]
RML17_MODULE_PATH = ROOT / "hhs_runtime" / "pass219" / "discrete_transport_conservation.py"
RML17_RECEIPT_PATH = (
    ROOT
    / "evidence"
    / "pass219_rml17_native_parity"
    / "PASS_219_RML17_NATIVE_CONSERVATION_PARITY_RECEIPT.json"
)

_EXPECTED_DIRECTIONS = ("x", "y", "z", "w")
_EXPECTED_INVERSE = {"x": "y", "y": "x", "z": "w", "w": "z"}
_EXPECTED_INVERSE_INDEX = (1, 0, 3, 2)
_EXPECTED_FLUX = {"x": 1, "y": -1, "z": -1, "w": 1}
_EXPECTED_FLUX_INDEX = (1, -1, -1, 1)
_EXPECTED_COORDINATE_ORDER = ("operation64", "phase72", "cell81", "direction4")


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
        "canonical_transition_authority": False,
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
        "canonical_transition_authority": False,
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
    """Validate the sealed RML17 <-> native C++ parity evidence exactly."""
    if receipt.get("schema") != "HHS_PASS219_RML17_NATIVE_CONSERVATION_PARITY_SEAL_V1":
        return False, "RML17_NATIVE_PARITY_RECEIPT_SCHEMA_MISMATCH"
    if receipt.get("iteration") != "RML17_DISCRETE_TRANSPORT_CONSERVATION":
        return False, "RML17_NATIVE_PARITY_RECEIPT_ITERATION_MISMATCH"
    if receipt.get("result") != "PASS" or receipt.get("omega") is not True:
        return False, "RML17_NATIVE_PARITY_RECEIPT_RESULT_MISMATCH"

    manifold = receipt.get("finite_manifold")
    if not isinstance(manifold, Mapping):
        return False, "RML17_NATIVE_PARITY_MANIFOLD_MISSING"
    if (
        manifold.get("operation_count") != 64
        or manifold.get("phase_count") != 72
        or manifold.get("cell_count") != 81
        or manifold.get("direction_count") != 4
        or manifold.get("node_count") != 373_248
        or manifold.get("address_count") != 1_492_992
        or tuple(manifold.get("coordinate_order", ())) != _EXPECTED_COORDINATE_ORDER
        or tuple(manifold.get("direction_order", ())) != _EXPECTED_DIRECTIONS
        or tuple(manifold.get("signed_flux", ())) != _EXPECTED_FLUX_INDEX
        or tuple(manifold.get("reciprocal_direction_index", ())) != _EXPECTED_INVERSE_INDEX
    ):
        return False, "RML17_NATIVE_PARITY_MANIFOLD_MISMATCH"

    parity = receipt.get("parity")
    if not isinstance(parity, Mapping):
        return False, "RML17_NATIVE_PARITY_PROOF_MISSING"
    mismatch_keys = (
        "source_encoding_mismatches",
        "target_encoding_mismatches",
        "successor_mismatches",
        "flux_orientation_mismatches",
        "reciprocal_alignment_mismatches",
        "zero_diffusion_classification_mismatches",
        "reverse_closure_mismatches",
        "mismatch_total",
    )
    if (
        parity.get("addresses_compared") != 1_492_992
        or parity.get("python_address_count") != 1_492_992
        or parity.get("native_address_count") != 1_492_992
        or any(parity.get(key) != 0 for key in mismatch_keys)
        or parity.get("python_native_extensional_equality") is not True
        or parity.get("native_exhaustive_contract_pass") is not True
        or parity.get("audit_sha256") != FROZEN_RML17_NATIVE_PARITY_AUDIT_SHA256
    ):
        return False, "RML17_NATIVE_PARITY_PROOF_MISMATCH"

    authority = receipt.get("authority")
    if not isinstance(authority, Mapping):
        return False, "RML17_NATIVE_PARITY_AUTHORITY_MISSING"
    if (
        authority.get("native_abi_beneath_rml17") is not True
        or authority.get("native_abi_transition_authority_closed") is not True
        or authority.get("canonical_transition_authority_expanded") is not False
        or authority.get("canonical_vm81_mutation_authority") is not False
        or authority.get("canonical_hash72_mint_authority") is not False
        or authority.get("canonical_hash216_persistence_authority") is not False
        or authority.get("existing_rna_uqcel_authority_preserved") is not True
    ):
        return False, "RML17_NATIVE_PARITY_AUTHORITY_MISMATCH"
    return True, "RML17_NATIVE_PARITY_RECEIPT_EQUAL"


def verify_frozen_rml17_nucleus() -> dict[str, Any]:
    """Verify the exact repository-visible reconciled RML17/native nucleus."""
    if not RML17_MODULE_PATH.is_file():
        return _undefined("RML17_NUCLEUS", "RML17_MODULE_MISSING")
    if not RML17_RECEIPT_PATH.is_file():
        return _undefined("RML17_NUCLEUS", "RML17_NATIVE_PARITY_RECEIPT_MISSING")

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
            "RML17_NATIVE_PARITY_RECEIPT_BLOB_MISMATCH",
            observed_receipt_blob_sha1=receipt_blob,
        )

    try:
        receipt = json.loads(receipt_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _undefined("RML17_NUCLEUS", "RML17_NATIVE_PARITY_RECEIPT_PARSE_FAILED")
    if not isinstance(receipt, Mapping):
        return _undefined("RML17_NUCLEUS", "RML17_NATIVE_PARITY_RECEIPT_MAPPING_REQUIRED")

    receipt_ok, reason = _receipt_equal_to_frozen_baseline(receipt)
    if not receipt_ok:
        return _undefined("RML17_NUCLEUS", reason)

    runtime_shape_ok = (
        rml17.OPERATIONS_PER_CELL == 64
        and rml17.PHASE_COUNT == 72
        and rml17.CELL_COUNT == 81
        and rml17.DIRECTION_COUNT == 4
        and rml17.NODE_COUNT == 373_248
        and rml17.ADDRESS_COUNT == 1_492_992
        and tuple(rml17.DIRECTIONS) == _EXPECTED_DIRECTIONS
        and dict(rml17.INVERSE_DIRECTION) == _EXPECTED_INVERSE
        and tuple(rml17.INVERSE_DIRECTION_INDEX) == _EXPECTED_INVERSE_INDEX
        and dict(rml17.DIRECTION_FLUX) == _EXPECTED_FLUX
        and tuple(rml17.DIRECTION_FLUX_INDEX) == _EXPECTED_FLUX_INDEX
    )
    if not runtime_shape_ok:
        return _undefined("RML17_NUCLEUS", "RML17_RUNTIME_SHAPE_MISMATCH")

    return _admitted(
        "RML17_NUCLEUS",
        frozen_rml17_merge_commit=FROZEN_RML17_MERGE_COMMIT,
        frozen_rml17_parity_validated_commit=FROZEN_RML17_PARITY_VALIDATED_COMMIT,
        frozen_rml17_tree_sha=FROZEN_RML17_TREE_SHA,
        frozen_rml17_module_git_blob_sha1=module_blob,
        frozen_rml17_receipt_git_blob_sha1=receipt_blob,
        frozen_rml17_exhaustive_audit_sha256=FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256,
        frozen_rml17_native_parity_audit_sha256=FROZEN_RML17_NATIVE_PARITY_AUDIT_SHA256,
        frozen_address_count=rml17.ADDRESS_COUNT,
        frozen_exhaustive_validation=True,
        native_cpp_parity_proven=True,
        native_abi_transition_authority_closed=True,
    )


def accelerated_address_manifold_certificate() -> dict[str, Any]:
    """Return the O(1) prevalidated reconciled-RML17 global certificate."""
    nucleus = verify_frozen_rml17_nucleus()
    if nucleus.get("status") != ADMITTED or not exact_invariant_1001(nucleus.get("invariant")):
        return _undefined(
            "GLOBAL_ADDRESS_MANIFOLD",
            "RECONCILED_RML17_NUCLEUS_NOT_1_001",
            nucleus_reason=nucleus.get("reason"),
        )

    return _admitted(
        "GLOBAL_ADDRESS_MANIFOLD",
        proof_method="RECONCILED_RML17_NATIVE_PARITY_CERTIFICATE_REUSE",
        exhaustive_runtime_scan_executed=False,
        frozen_exhaustive_scan_address_count=1_492_992,
        frozen_rml17_exhaustive_audit_sha256=FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256,
        frozen_rml17_native_parity_audit_sha256=FROZEN_RML17_NATIVE_PARITY_AUDIT_SHA256,
        zero_discrete_divergence=True,
        reciprocal_edge_balance=True,
        admission_preservation=True,
        zero_canonical_diffusion=True,
        composed_reverse_closure=True,
        structural_information_loss_zero=True,
        python_native_extensional_equality=True,
        latency_participates_in_viscosity_definition=False,
        rml17_source_blob_verified=True,
        rml17_native_parity_receipt_blob_verified=True,
        native_abi_transition_authority_closed=True,
        optimized_runtime_path=True,
    )


def compare_accelerated_certificate_to_exhaustive() -> dict[str, Any]:
    """Validation-only equality comparison to a fresh reconciled RML17 scan."""
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
        and exhaustive.get("unique_target_addresses") == 1_492_992
        and exhaustive.get("all_nodes_zero_discrete_divergence") is True
        and exhaustive.get("all_addresses_zero_discrete_divergence") is True
        and exhaustive.get("all_address_edges_reciprocal") is True
        and exhaustive.get("all_address_edge_fluxes_balanced") is True
        and exhaustive.get("all_addresses_zero_canonical_diffusion") is True
        and exhaustive.get("all_addresses_encode_decode_bijective") is True
        and exhaustive.get("target_map_bijective") is True
        and exhaustive.get("native_cell_wall_semantics") is True
        and exhaustive.get("lane_coordinate_present") is False
        and exhaustive.get("audit_sha256") == FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256
        and candidate.get("zero_discrete_divergence") is True
        and candidate.get("reciprocal_edge_balance") is True
        and candidate.get("admission_preservation") is True
        and candidate.get("zero_canonical_diffusion") is True
        and candidate.get("composed_reverse_closure") is True
        and candidate.get("structural_information_loss_zero") is True
        and candidate.get("python_native_extensional_equality") is True
        and candidate.get("native_abi_transition_authority_closed") is True
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
        native_parity_audit_sha256=FROZEN_RML17_NATIVE_PARITY_AUDIT_SHA256,
        accelerated_certificate_equal=True,
        exhaustive_address_count=exhaustive["visited_address_count"],
        native_cpp_parity_proven=True,
    )


def gate_transport_address_candidate(address: Any) -> dict[str, Any]:
    """Fail closed unless one transport address returns the reconciled 1.001 invariant."""
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
        and local.get("native_mixed_radix_order") is True
        and local.get("exact_phase_only_successor") is True
        and local.get("zero_discrete_divergence") is True
        and local.get("reciprocal_neighbor_edges") is True
        and local.get("reciprocal_edge_flux_balance") is True
        and local.get("zero_canonical_diffusion") is True
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
        direction=local["direction"],
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
    """Return 1.001 only for a route exactly equal to every reconciled RML17 gate."""
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
        and record.get("canonical_transition_authority") is False
        and exact_invariant_1001(record.get("invariant"))
    ):
        return dict(record)
    return _undefined("CANDIDATE_CLOSURE", "EXACT_1_001_INVARIANT_REQUIRED")


__all__ = [
    "ADMITTED",
    "FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256",
    "FROZEN_RML17_MERGE_COMMIT",
    "FROZEN_RML17_MODULE_GIT_BLOB_SHA1",
    "FROZEN_RML17_NATIVE_PARITY_AUDIT_SHA256",
    "FROZEN_RML17_PARITY_VALIDATED_COMMIT",
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
