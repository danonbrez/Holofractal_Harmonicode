from __future__ import annotations

from copy import deepcopy

from hhs_runtime.pass219 import discrete_transport_conservation as rml17
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.reciprocal_route_cache import clear_reciprocal_route_cache
from hhs_runtime.pass219.rml18_transport_conservation_acceleration import (
    ADMITTED,
    FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256,
    FROZEN_RML17_NATIVE_PARITY_AUDIT_SHA256,
    FROZEN_RML17_PARITY_VALIDATED_COMMIT,
    INVARIANT_DECIMAL,
    INVARIANT_DENOMINATOR,
    INVARIANT_NUMERATOR,
    NULL_UNDEFINED,
    accelerated_address_manifold_certificate,
    compare_accelerated_certificate_to_exhaustive,
    enforce_candidate_1001,
    exact_invariant_1001,
    gate_composed_route_candidate,
    gate_route_candidate,
    gate_transport_address_candidate,
    verify_frozen_rml17_nucleus,
)

SIGNS = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}


def _state(
    state_id: str,
    *,
    x: int = 7,
    y: int = 19,
    z: int = 31,
    w: int = 43,
) -> dict[str, object]:
    phases = {
        "x": x,
        "y": y,
        "z": z,
        "w": w,
        "xy": expected_product_phase(x, SIGNS["xy"]),
        "yx": expected_product_phase(y, SIGNS["yx"]),
        "zw": expected_product_phase(z, SIGNS["zw"]),
        "wz": expected_product_phase(w, SIGNS["wz"]),
    }
    return build_gyroscope_state(phases, SIGNS, state_id=state_id)


def test_1001_invariant_is_exact_rational_not_float() -> None:
    assert INVARIANT_NUMERATOR == 1001
    assert INVARIANT_DENOMINATOR == 1000
    assert INVARIANT_DECIMAL == "1.001"
    token = {
        "numerator": 1001,
        "denominator": 1000,
        "decimal": "1.001",
        "binary_floating_point_used": False,
    }
    assert exact_invariant_1001(token) is True
    assert exact_invariant_1001(1.001) is False
    assert exact_invariant_1001({**token, "numerator": 1000}) is False
    assert exact_invariant_1001({**token, "decimal": "1.0010"}) is False


def test_reconciled_rml17_native_parity_nucleus_returns_1001() -> None:
    nucleus = verify_frozen_rml17_nucleus()
    assert nucleus["status"] == ADMITTED
    assert nucleus["defined"] is True
    assert nucleus["omega_closure"] is True
    assert nucleus["rml17_equality_baseline_match"] is True
    assert exact_invariant_1001(nucleus["invariant"]) is True
    assert nucleus["frozen_address_count"] == 1_492_992
    assert nucleus["frozen_rml17_parity_validated_commit"] == FROZEN_RML17_PARITY_VALIDATED_COMMIT
    assert nucleus["frozen_rml17_native_parity_audit_sha256"] == FROZEN_RML17_NATIVE_PARITY_AUDIT_SHA256
    assert nucleus["native_cpp_parity_proven"] is True
    assert nucleus["native_abi_transition_authority_closed"] is True


def test_accelerated_global_certificate_reuses_reconciled_exhaustive_proof() -> None:
    candidate = accelerated_address_manifold_certificate()
    assert candidate["status"] == ADMITTED
    assert candidate["exhaustive_runtime_scan_executed"] is False
    assert candidate["frozen_exhaustive_scan_address_count"] == 1_492_992
    assert candidate["frozen_rml17_exhaustive_audit_sha256"] == FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256
    assert candidate["frozen_rml17_native_parity_audit_sha256"] == FROZEN_RML17_NATIVE_PARITY_AUDIT_SHA256
    assert candidate["proof_method"] == "RECONCILED_RML17_NATIVE_PARITY_CERTIFICATE_REUSE"
    assert candidate["zero_discrete_divergence"] is True
    assert candidate["reciprocal_edge_balance"] is True
    assert candidate["admission_preservation"] is True
    assert candidate["zero_canonical_diffusion"] is True
    assert candidate["composed_reverse_closure"] is True
    assert candidate["structural_information_loss_zero"] is True
    assert candidate["python_native_extensional_equality"] is True
    assert candidate["native_abi_transition_authority_closed"] is True
    assert candidate["optimized_runtime_path"] is True
    assert exact_invariant_1001(candidate["invariant"]) is True


def test_accelerated_certificate_equals_fresh_reconciled_rml17_scan() -> None:
    differential = compare_accelerated_certificate_to_exhaustive()
    assert differential["status"] == ADMITTED
    assert differential["accelerated_certificate_equal"] is True
    assert differential["exhaustive_address_count"] == 1_492_992
    assert differential["exhaustive_rml17_audit_sha256"] == FROZEN_RML17_EXHAUSTIVE_AUDIT_SHA256
    assert differential["native_parity_audit_sha256"] == FROZEN_RML17_NATIVE_PARITY_AUDIT_SHA256
    assert differential["native_cpp_parity_proven"] is True
    assert exact_invariant_1001(differential["invariant"]) is True


def test_transport_address_candidate_requires_native_aligned_1001_and_fails_closed() -> None:
    valid_address = rml17.encode_transport_address(3, 63, 71, 3)
    valid = gate_transport_address_candidate(valid_address)
    assert valid["status"] == ADMITTED
    assert valid["coordinates"] == [3, 63, 71, 3]
    assert valid["direction"] == "w"
    assert exact_invariant_1001(valid["invariant"]) is True

    invalid = gate_transport_address_candidate(rml17.ADDRESS_COUNT)
    assert invalid["status"] == NULL_UNDEFINED
    assert invalid["defined"] is False
    assert invalid["invariant"] is None
    assert invalid["omega_closure"] is True


def test_route_candidate_returns_1001_only_after_reconciled_rml17_equality() -> None:
    clear_reciprocal_route_cache()
    source = _state("rml18:route:source")
    target = _state("rml18:route:target", x=10, z=35)
    candidate = gate_route_candidate(source, target, route_id="rml18:route")
    assert candidate["status"] == ADMITTED
    assert candidate["rml17_equality_baseline_match"] is True
    assert candidate["edge_count"] > 0
    assert exact_invariant_1001(candidate["invariant"]) is True


def test_route_candidate_with_float_contamination_is_null_undefined() -> None:
    clear_reciprocal_route_cache()
    source = _state("rml18:route:bad:source")
    target = _state("rml18:route:bad:target", x=10)
    corrupt = deepcopy(source)
    corrupt["illegal_float"] = 0.5
    candidate = gate_route_candidate(corrupt, target, route_id="rml18:route:bad")
    assert candidate["status"] == NULL_UNDEFINED
    assert candidate["defined"] is False
    assert candidate["invariant"] is None
    assert candidate["rml17_equality_baseline_match"] is False


def test_composed_route_candidate_preserves_1001_under_admitted_composition() -> None:
    clear_reciprocal_route_cache()
    states = [
        _state("rml18:composition:s0"),
        _state("rml18:composition:s1", x=8),
        _state("rml18:composition:s2", x=8, y=23),
    ]
    candidate = gate_composed_route_candidate(
        states,
        composition_id="rml18:composition",
    )
    assert candidate["status"] == ADMITTED
    assert candidate["segment_count"] == 2
    assert exact_invariant_1001(candidate["invariant"]) is True


def test_final_closure_membrane_maps_non_1001_candidate_to_null_undefined() -> None:
    admitted = accelerated_address_manifold_certificate()
    assert enforce_candidate_1001(admitted)["status"] == ADMITTED

    corrupt = deepcopy(admitted)
    corrupt["invariant"]["numerator"] = 1000
    rejected = enforce_candidate_1001(corrupt)
    assert rejected["status"] == NULL_UNDEFINED
    assert rejected["invariant"] is None
    assert rejected["omega_closure"] is True


def test_native_direction_shape_mutation_fails_closed_without_weakening_rml17(monkeypatch) -> None:
    monkeypatch.setattr(
        rml17,
        "DIRECTION_FLUX",
        {**rml17.DIRECTION_FLUX, "x": 2},
    )
    candidate = accelerated_address_manifold_certificate()
    assert candidate["status"] == NULL_UNDEFINED
    assert candidate["invariant"] is None
    assert candidate["omega_closure"] is True


def test_rml18_has_no_authority_expansion() -> None:
    candidate = accelerated_address_manifold_certificate()
    assert candidate["canonical_transition_authority"] is False
    assert candidate["canonical_vm81_mutation_authority"] is False
    assert candidate["canonical_hash72_mint_authority"] is False
    assert candidate["canonical_hash216_persistence_authority"] is False
    assert candidate["floating_point_authority"] is False
    assert candidate["scalar_projection_substitution_authority"] is False
    assert candidate["route_selection_authority"] is False
    assert candidate["latency_participates_in_viscosity_definition"] is False
