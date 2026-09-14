from __future__ import annotations

from copy import deepcopy

import pytest

from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.reciprocal_route_cache import (
    CACHE_CAPACITY,
    build_and_select_reciprocal_route_cached,
    clear_reciprocal_route_cache,
    reciprocal_route_cache_info,
)
from hhs_runtime.pass219.reciprocal_route_optimizer import (
    ReciprocalRouteOptimizerError,
    build_and_select_reciprocal_route,
)

SIGNS = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}


def _state(state_id: str, *, x: int = 7, y: int = 19, z: int = 31, w: int = 43) -> dict[str, object]:
    primitives = {"x": x, "y": y, "z": z, "w": w}
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


def test_cache_hit_is_exactly_equal_to_uncached_rml12_bundle() -> None:
    source = _state("rml16-cache:source")
    target = _state("rml16-cache:target", x=8)
    route_id = "rml16-cache:exact"
    expected = build_and_select_reciprocal_route(source, target, route_id=route_id)

    clear_reciprocal_route_cache()
    cold = build_and_select_reciprocal_route_cached(source, target, route_id=route_id)
    cold_info = reciprocal_route_cache_info()
    warm = build_and_select_reciprocal_route_cached(source, target, route_id=route_id)
    warm_info = reciprocal_route_cache_info()

    assert cold == expected
    assert warm == expected
    assert cold["bundle_sha256"] == expected["bundle_sha256"]
    assert warm["bundle_sha256"] == expected["bundle_sha256"]
    assert cold_info["misses"] == 1
    assert cold_info["hits"] == 0
    assert warm_info["misses"] == 1
    assert warm_info["hits"] == 1
    assert warm_info["size"] == 1


def test_caller_mutation_cannot_poison_cached_route_bundle() -> None:
    source = _state("rml16-cache:mutation-source")
    target = _state("rml16-cache:mutation-target", y=20)
    route_id = "rml16-cache:mutation"
    clear_reciprocal_route_cache()

    first = build_and_select_reciprocal_route_cached(source, target, route_id=route_id)
    pristine = deepcopy(first)
    first["shortest_candidate"]["edges"][0]["phase_transport_units"] = 999999
    first["selection"]["selected_route_id"] = "POISON"

    second = build_and_select_reciprocal_route_cached(source, target, route_id=route_id)
    assert second == pristine
    assert second["shortest_candidate"]["edges"][0]["phase_transport_units"] != 999999
    assert second["selection"]["selected_route_id"] != "POISON"
    assert reciprocal_route_cache_info()["hits"] == 1


def test_route_id_is_part_of_exact_cache_identity() -> None:
    source = _state("rml16-cache:id-source")
    target = _state("rml16-cache:id-target", z=32)
    clear_reciprocal_route_cache()

    first = build_and_select_reciprocal_route_cached(source, target, route_id="rml16-cache:id:a")
    second = build_and_select_reciprocal_route_cached(source, target, route_id="rml16-cache:id:b")
    info = reciprocal_route_cache_info()

    assert first["bundle_sha256"] != second["bundle_sha256"]
    assert info["misses"] == 2
    assert info["hits"] == 0
    assert info["size"] == 2


def test_endpoint_validation_still_runs_before_cache_lookup() -> None:
    source = _state("rml16-cache:validation-source")
    target = _state("rml16-cache:validation-target", w=44)
    route_id = "rml16-cache:validation"
    clear_reciprocal_route_cache()
    build_and_select_reciprocal_route_cached(source, target, route_id=route_id)

    invalid = deepcopy(source)
    invalid["phases"] = {
        channel: invalid["phases"][channel]
        for channel in reversed(CHANNELS)
    }
    with pytest.raises(ReciprocalRouteOptimizerError, match="ORDERED_EIGHT_PHASE_STATE_REQUIRED"):
        build_and_select_reciprocal_route_cached(invalid, target, route_id=route_id)

    info = reciprocal_route_cache_info()
    assert info["misses"] == 1
    assert info["hits"] == 0


def test_cache_is_bounded_process_local_and_has_no_canonical_authority() -> None:
    clear_reciprocal_route_cache()
    info = reciprocal_route_cache_info()
    assert info["capacity"] == CACHE_CAPACITY == 256
    assert info["process_local"] is True
    assert info["persistent_cache"] is False
    assert info["canonical_vm81_mutation_authority"] is False
    assert info["canonical_hash72_mint_authority"] is False
    assert info["canonical_hash216_persistence_authority"] is False
    assert info["timing_canonical_authority"] is False
