from __future__ import annotations

from copy import deepcopy

from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.reciprocal_route_cache import clear_reciprocal_route_cache
from hhs_runtime.pass219 import rml18_transport_conservation_acceleration as rml18
from hhs_runtime.pass219 import rml19_route_composition_conservation_acceleration as rml19

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


def _assert_exact_parent_admission(record: dict[str, object]) -> None:
    assert record["status"] == rml18.ADMITTED
    assert record["defined"] is True
    assert record["omega_closure"] is True
    assert record["rml17_equality_baseline_match"] is True
    assert rml18.exact_invariant_1001(record["invariant"]) is True
    assert record["canonical_vm81_mutation_authority"] is False
    assert record["canonical_hash72_mint_authority"] is False
    assert record["canonical_hash216_persistence_authority"] is False
    assert record["floating_point_authority"] is False
    assert record["scalar_projection_substitution_authority"] is False
    assert record["route_selection_authority"] is False


def test_rml19_binds_exact_frozen_rml18_parent_without_editing_membrane() -> None:
    parent = rml19.verify_frozen_rml18_parent()
    assert parent["status"] == rml18.ADMITTED
    assert parent["frozen_rml18_parent_commit"] == "76cd6f995668dac3f1bfb10ae25a8301b2233237"
    assert parent["frozen_rml18_tree_sha"] == "3e1b1e3844cfa7757e49cc2112886fd09c9d40cd"
    assert parent["frozen_rml18_module_git_blob_sha1"] == "d7c38ce7807f8bff386a765fdb37cbc254b6cd49"
    assert rml18.exact_invariant_1001(parent["invariant"]) is True
    assert parent["cache_authority"] is False


def test_rml19_cache_capacity_is_bounded_to_vm81_operation_capacity() -> None:
    assert rml19.MAX_ROUTE_CERTIFICATES == 5184
    assert rml19.MAX_COMPOSITION_CERTIFICATES == 5184
    stats = rml19.cache_stats()
    assert stats["digest_participates_in_cache_lookup"] is False
    assert stats["timing_participates_in_admission"] is False
    assert stats["cache_authority"] is False


def test_route_first_evaluation_is_exactly_parent_rml18_output() -> None:
    clear_reciprocal_route_cache()
    rml19.clear_rml19_certificate_cache()
    source = _state("rml19:route:parity:source")
    target = _state("rml19:route:parity:target", x=10, z=35)

    expected = rml18.gate_route_candidate(source, target, route_id="rml19:route:parity")
    observed = rml19.gate_route_candidate(source, target, route_id="rml19:route:parity")

    assert observed == expected
    _assert_exact_parent_admission(observed)
    stats = rml19.cache_stats()
    assert stats["route_misses"] == 1
    assert stats["route_entries"] == 1


def test_route_repeat_reuses_exact_certificate_without_parent_route_reaudit(monkeypatch) -> None:
    clear_reciprocal_route_cache()
    rml19.clear_rml19_certificate_cache()
    source = _state("rml19:route:hit:source")
    target = _state("rml19:route:hit:target", x=10, z=35)

    original = rml18.gate_route_candidate
    calls = {"count": 0}

    def counted(*args, **kwargs):
        calls["count"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(rml18, "gate_route_candidate", counted)
    first = rml19.gate_route_candidate(source, target, route_id="rml19:route:hit")
    second = rml19.gate_route_candidate(source, target, route_id="rml19:route:hit")

    assert first == second
    _assert_exact_parent_admission(second)
    assert calls["count"] == 1
    stats = rml19.cache_stats()
    assert stats["route_misses"] == 1
    assert stats["route_hits"] == 1
    assert stats["route_entries"] == 1


def test_route_cache_key_includes_complete_state_and_route_id(monkeypatch) -> None:
    clear_reciprocal_route_cache()
    rml19.clear_rml19_certificate_cache()
    source = _state("rml19:route:key:source")
    target = _state("rml19:route:key:target", x=10)

    original = rml18.gate_route_candidate
    calls = {"count": 0}

    def counted(*args, **kwargs):
        calls["count"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(rml18, "gate_route_candidate", counted)
    rml19.gate_route_candidate(source, target, route_id="rml19:key:a")
    rml19.gate_route_candidate(source, target, route_id="rml19:key:b")
    changed_target = deepcopy(target)
    changed_target["rml19_exact_key_probe"] = 1
    rml19.gate_route_candidate(source, changed_target, route_id="rml19:key:a")

    assert calls["count"] == 3
    stats = rml19.cache_stats()
    assert stats["route_misses"] == 3
    assert stats["route_hits"] == 0


def test_route_float_rejection_remains_null_undefined_and_is_never_cached() -> None:
    clear_reciprocal_route_cache()
    rml19.clear_rml19_certificate_cache()
    source = _state("rml19:route:bad:source")
    target = _state("rml19:route:bad:target", x=10)
    corrupt = deepcopy(source)
    corrupt["illegal_float"] = 0.5

    first = rml19.gate_route_candidate(corrupt, target, route_id="rml19:route:bad")
    second = rml19.gate_route_candidate(corrupt, target, route_id="rml19:route:bad")

    assert first["status"] == rml18.NULL_UNDEFINED
    assert second["status"] == rml18.NULL_UNDEFINED
    assert first["defined"] is False
    assert first["invariant"] is None
    assert first["omega_closure"] is True
    stats = rml19.cache_stats()
    assert stats["route_entries"] == 0
    assert stats["route_hits"] == 0
    assert stats["route_rejections"] == 2


def test_cached_route_result_is_copy_isolated_from_caller_mutation() -> None:
    clear_reciprocal_route_cache()
    rml19.clear_rml19_certificate_cache()
    source = _state("rml19:route:copy:source")
    target = _state("rml19:route:copy:target", x=10)

    first = rml19.gate_route_candidate(source, target, route_id="rml19:route:copy")
    expected_invariant = deepcopy(first["invariant"])
    first["invariant"]["numerator"] = 0
    second = rml19.gate_route_candidate(source, target, route_id="rml19:route:copy")

    assert second["invariant"] == expected_invariant
    assert rml18.exact_invariant_1001(second["invariant"]) is True


def test_composition_first_evaluation_is_exactly_parent_rml18_output() -> None:
    clear_reciprocal_route_cache()
    rml19.clear_rml19_certificate_cache()
    states = [
        _state("rml19:composition:parity:s0"),
        _state("rml19:composition:parity:s1", x=8),
        _state("rml19:composition:parity:s2", x=8, y=23),
    ]

    expected = rml18.gate_composed_route_candidate(states, composition_id="rml19:composition:parity")
    observed = rml19.gate_composed_route_candidate(states, composition_id="rml19:composition:parity")

    assert observed == expected
    _assert_exact_parent_admission(observed)
    assert observed["segment_count"] == 2
    stats = rml19.cache_stats()
    assert stats["composition_misses"] == 1
    assert stats["composition_entries"] == 1


def test_composition_repeat_reuses_exact_certificate_without_parent_reaudit(monkeypatch) -> None:
    clear_reciprocal_route_cache()
    rml19.clear_rml19_certificate_cache()
    states = [
        _state("rml19:composition:hit:s0"),
        _state("rml19:composition:hit:s1", x=8),
        _state("rml19:composition:hit:s2", x=8, y=23),
    ]

    original = rml18.gate_composed_route_candidate
    calls = {"count": 0}

    def counted(*args, **kwargs):
        calls["count"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(rml18, "gate_composed_route_candidate", counted)
    first = rml19.gate_composed_route_candidate(states, composition_id="rml19:composition:hit")
    second = rml19.gate_composed_route_candidate(states, composition_id="rml19:composition:hit")

    assert first == second
    _assert_exact_parent_admission(second)
    assert calls["count"] == 1
    stats = rml19.cache_stats()
    assert stats["composition_misses"] == 1
    assert stats["composition_hits"] == 1
    assert stats["composition_entries"] == 1


def test_composition_float_rejection_is_null_undefined_and_never_cached() -> None:
    clear_reciprocal_route_cache()
    rml19.clear_rml19_certificate_cache()
    states = [
        _state("rml19:composition:bad:s0"),
        _state("rml19:composition:bad:s1", x=8),
    ]
    corrupt = deepcopy(states)
    corrupt[0]["illegal_float"] = 1.001

    candidate = rml19.gate_composed_route_candidate(
        corrupt,
        composition_id="rml19:composition:bad",
    )

    assert candidate["status"] == rml18.NULL_UNDEFINED
    assert candidate["defined"] is False
    assert candidate["invariant"] is None
    assert candidate["omega_closure"] is True
    stats = rml19.cache_stats()
    assert stats["composition_entries"] == 0
    assert stats["composition_rejections"] == 1


def test_rml18_parent_blob_mutation_fails_closed_before_cache_reuse(monkeypatch) -> None:
    clear_reciprocal_route_cache()
    rml19.clear_rml19_certificate_cache()
    source = _state("rml19:parent:source")
    target = _state("rml19:parent:target", x=10)

    admitted = rml19.gate_route_candidate(source, target, route_id="rml19:parent")
    _assert_exact_parent_admission(admitted)

    monkeypatch.setattr(rml19, "FROZEN_RML18_MODULE_GIT_BLOB_SHA1", "0" * 40)
    rejected = rml19.gate_route_candidate(source, target, route_id="rml19:parent")
    assert rejected["status"] == rml18.NULL_UNDEFINED
    assert rejected["defined"] is False
    assert rejected["invariant"] is None
    assert rejected["omega_closure"] is True
    assert rejected["reason"] == "RML18_MODULE_BLOB_MISMATCH"


def test_rml19_observability_has_no_transition_or_hash_authority() -> None:
    stats = rml19.cache_stats()
    assert stats["canonical_vm81_mutation_authority"] is False
    assert stats["canonical_hash72_mint_authority"] is False
    assert stats["canonical_hash216_persistence_authority"] is False
    assert stats["floating_point_authority"] is False
    assert stats["scalar_projection_substitution_authority"] is False
    assert stats["route_selection_authority"] is False
    assert stats["cache_authority"] is False
