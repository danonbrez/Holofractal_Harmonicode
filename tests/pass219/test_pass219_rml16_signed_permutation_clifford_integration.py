from __future__ import annotations

import pytest

from hhs_runtime.pass219 import phase_clifford_intertwiner as clifford
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    PRODUCT_RELATIONS,
    advance_gyroscope,
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.real_clifford_morita_witness import build_cl08_generators
from hhs_runtime.pass219.reciprocal_route_optimizer import build_and_select_reciprocal_route
from hhs_runtime.pass219.rml16_signed_permutation_clifford import (
    DESCRIPTOR_CACHE_CAPACITY,
    RML11_FROZEN_SOURCE_COMMIT,
    _DENSE_RML11_MATMUL,
    _signed_permutation_descriptor,
    install_rml16_signed_permutation_clifford_acceleration,
    rml16_signed_permutation_clifford_info,
    signed_permutation_clifford_matmul,
)

SIGNS = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}
ROUTE_SHAPE = (("x", 1), ("y", -2), ("z", 17), ("w", -18))


def _identity(order: int) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(1 if i == j else 0 for j in range(order)) for i in range(order))


def _state(state_id: str, offset: int = 0) -> dict[str, object]:
    primitives = {
        "x": (7 + 5 * offset) % 72,
        "y": (19 + 7 * offset) % 72,
        "z": (31 + 11 * offset) % 72,
        "w": (43 + 13 * offset) % 72,
    }
    phases = {
        "x": primitives["x"],
        "y": primitives["y"],
        "z": primitives["z"],
        "w": primitives["w"],
        "xy": expected_product_phase(primitives["x"], SIGNS["xy"]),
        "yx": expected_product_phase(primitives["y"], SIGNS["yx"]),
        "zw": expected_product_phase(primitives["z"], SIGNS["zw"]),
        "wz": expected_product_phase(primitives["w"], SIGNS["wz"]),
    }
    return build_gyroscope_state(phases, SIGNS, state_id=state_id)


def _target(source: dict[str, object], tag: str) -> dict[str, object]:
    current = source
    for generator, delta in ROUTE_SHAPE:
        product = next(
            product
            for product, relation in PRODUCT_RELATIONS.items()
            if relation["generator"] == generator
        )
        steps = {channel: 0 for channel in CHANNELS}
        steps[generator] = delta
        steps[product] = delta
        current = advance_gyroscope(
            current,
            steps,
            transition_id=f"{tag}:{generator}:{delta}",
        )["next_state"]
    return current


def test_all_cl08_generator_products_match_frozen_dense_reference() -> None:
    generators = build_cl08_generators()
    matrices = tuple(generators) + (_identity(16),)
    assert len(matrices) == 9

    for left in matrices:
        assert _signed_permutation_descriptor(left) is not None
        for right in matrices:
            assert signed_permutation_clifford_matmul(left, right) == _DENSE_RML11_MATMUL(left, right)


def test_dense_fallback_preserves_general_exact_integer_matrix_product() -> None:
    left = ((2, 1), (0, 3))
    right = ((4, 0), (5, 6))
    assert _signed_permutation_descriptor(left) is None
    assert _signed_permutation_descriptor(right) is None
    assert signed_permutation_clifford_matmul(left, right) == ((13, 6), (15, 18))
    assert signed_permutation_clifford_matmul(left, right) == _DENSE_RML11_MATMUL(left, right)


def test_shape_errors_remain_identical_to_frozen_dense_rml11() -> None:
    malformed_left = ((1, 0),)
    malformed_right = ((1, 0),)
    with pytest.raises(clifford.PhaseCliffordIntertwinerError, match="MATRIX_PRODUCT_SHAPE_MISMATCH"):
        signed_permutation_clifford_matmul(malformed_left, malformed_right)


def test_install_is_idempotent_and_has_no_authority_expansion() -> None:
    first = install_rml16_signed_permutation_clifford_acceleration()
    second = install_rml16_signed_permutation_clifford_acceleration()
    info = rml16_signed_permutation_clifford_info()

    assert first["installed"] is True
    assert second["installed"] is True
    assert second["already_installed"] is True
    assert clifford._matmul is signed_permutation_clifford_matmul
    assert info["installed"] is True
    assert info["rml11_frozen_source_commit"] == RML11_FROZEN_SOURCE_COMMIT
    assert info["descriptor_cache"]["maxsize"] == DESCRIPTOR_CACHE_CAPACITY == 512
    assert info["dense_exact_fallback_preserved"] is True
    assert info["rml11_public_abi_changed"] is False
    assert info["rml12_public_abi_changed"] is False
    assert info["process_local"] is True
    assert info["persistent_cache"] is False
    assert info["canonical_vm81_mutation_authority"] is False
    assert info["canonical_hash72_mint_authority"] is False
    assert info["canonical_hash216_persistence_authority"] is False
    assert info["floating_point_canonical_authority"] is False
    assert info["scalar_projection_substitution_authority"] is False
    assert info["timing_canonical_authority"] is False


def test_full_rml12_route_bundle_is_exactly_equal_to_dense_rml11_reference() -> None:
    source = _state("rml16:integrated:source", 2)
    target = _target(source, "rml16:integrated:target")
    route_id = "rml16:integrated:differential"

    clifford._matmul = _DENSE_RML11_MATMUL
    try:
        dense = build_and_select_reciprocal_route(source, target, route_id=route_id)
    finally:
        clifford._matmul = signed_permutation_clifford_matmul

    accelerated = build_and_select_reciprocal_route(source, target, route_id=route_id)
    assert accelerated == dense
    assert accelerated["bundle_sha256"] == dense["bundle_sha256"]
