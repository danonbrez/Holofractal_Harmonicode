from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from hhs_runtime.pass219.fixed_cardinality_optimization import (
    ROUTE_MULTIPLICITY_PER_TARGET,
    TARGET_CARDINALITY,
    WORKING_MANIFOLD_CARDINALITY,
)
from hhs_runtime.pass219.local_global_equation_search_filter import (
    CANDIDATE_SCHEMA,
    GATE_OFFSETS,
    HASH216_FORMAT_GENOME_ROOT,
    HASH216_FORMAT_THREE_HASH72,
    HYDRATION_BITS,
    NUMERATOR_BYTES,
    NUMERATOR_PATH,
    NUMERATOR_SHA256,
    EquationSearchFilterError,
    evaluate_candidate,
    filter_search_space,
    make_candidate,
    make_snapshot,
    normalize_snapshot,
)


ROOT = Path(__file__).resolve().parents[2]


def _snapshot(P: int = 15) -> dict[str, object]:
    return make_snapshot(
        snapshot_hash216="a" * 64,
        snapshot_hash216_format=HASH216_FORMAT_GENOME_ROOT,
        P=P,
    )


def _candidate(
    snapshot: dict[str, object],
    route: int = 0,
    gates: tuple[bool, bool, bool, bool, bool] = (True, True, True, True, True),
) -> dict[str, object]:
    return make_candidate(
        snapshot=snapshot,
        target_block_index=0,
        route_index=route,
        global_symbol_environment_root="b" * 64,
        gate_results=gates,
    )


def test_i153_verbatim_equation_source_identity_is_inherited() -> None:
    path = ROOT / NUMERATOR_PATH
    raw = path.read_bytes()
    assert len(raw) == NUMERATOR_BYTES == 348
    assert hashlib.sha256(raw).hexdigest() == NUMERATOR_SHA256
    assert raw.decode("utf-8").startswith("P^2/{(t^3-t=")
    assert "where ∆/P=√(pq+u⁷²)^x²" in raw.decode("utf-8")


def test_i153_local_P_snapshot_does_not_change_i152_cardinality() -> None:
    snapshot = _snapshot(P=157)
    assert snapshot["P"] == 157
    assert snapshot["hydration_bits"] == HYDRATION_BITS == 5184
    assert snapshot["P_scope"] == "LOCAL_HASH216_5184_HYDRATION_PARAMETER_SNAPSHOT"
    assert snapshot["P_changes_global_cardinality"] is False
    assert snapshot["target_cardinality_decimal"] == str(72 ** 42)
    assert snapshot["working_manifold_cardinality_decimal"] == str(3 * (72 ** 72))
    assert snapshot["route_multiplicity_per_target_decimal"] == str(3 * (72 ** 30))
    assert TARGET_CARDINALITY == 72 ** 42
    assert WORKING_MANIFOLD_CARDINALITY == 3 * (72 ** 72)
    assert ROUTE_MULTIPLICITY_PER_TARGET == 3 * (72 ** 30)


def test_i153_supports_explicit_216_glyph_hash216_snapshot_format() -> None:
    snapshot = make_snapshot(
        snapshot_hash216="H" * 216,
        snapshot_hash216_format=HASH216_FORMAT_THREE_HASH72,
        P=19,
    )
    assert len(snapshot["snapshot_hash216"]) == 216
    assert snapshot["snapshot_hash216_format"] == HASH216_FORMAT_THREE_HASH72


def test_i153_all_true_shared_environment_survives_filter() -> None:
    snapshot = _snapshot()
    decision = evaluate_candidate(snapshot, _candidate(snapshot, route=9))
    assert decision["survives_equation_filter"] is True
    assert decision["decision"] == "SURVIVES_LOCAL_GLOBAL_EQUATION_FILTER"
    assert decision["gate_offsets"] == list(GATE_OFFSETS)
    assert decision["gate_results"] == [True] * 5
    assert decision["rejection_reasons"] == []
    assert decision["canonical_admission_claimed"] is False
    assert decision["pass169_whole_expression_authority_required"] is True


def test_i153_false_gate_rejects_with_provenance() -> None:
    snapshot = _snapshot()
    decision = evaluate_candidate(
        snapshot,
        _candidate(snapshot, route=10, gates=(True, True, False, True, True)),
    )
    assert decision["survives_equation_filter"] is False
    assert decision["first_false_gate"] == 2
    assert decision["rejection_reasons"] == ["BOOLEAN_GATE_FALSE"]


def test_i153_incomplete_global_environment_and_shadowing_reject() -> None:
    snapshot = _snapshot()
    candidate = make_candidate(
        snapshot=snapshot,
        target_block_index=0,
        route_index=11,
        global_symbol_environment_root="b" * 64,
        gate_results=[True] * 5,
        global_symbol_environment_complete=False,
        cross_layer_revalidation_complete=False,
        local_symbol_shadowing_detected=True,
    )
    decision = evaluate_candidate(snapshot, candidate)
    assert decision["survives_equation_filter"] is False
    assert decision["rejection_reasons"] == [
        "GLOBAL_ENVIRONMENT_INCOMPLETE",
        "CROSS_LAYER_REVALIDATION_INCOMPLETE",
        "LOCAL_SYMBOL_SHADOWING_DETECTED",
    ]


def test_i153_stale_witness_cannot_be_replayed_under_different_P() -> None:
    original = _snapshot(P=15)
    stale_candidate = _candidate(original, route=12)
    changed = _snapshot(P=16)
    with pytest.raises(EquationSearchFilterError, match="LOCAL_P_SNAPSHOT_BINDING_DRIFT"):
        evaluate_candidate(changed, stale_candidate)


def test_i153_route_working_index_drift_fails_closed() -> None:
    snapshot = _snapshot()
    candidate = _candidate(snapshot, route=13)
    assert candidate["schema"] == CANDIDATE_SCHEMA
    candidate["working_index"] = int(candidate["working_index"]) + 1
    with pytest.raises(EquationSearchFilterError, match="WORKING_INDEX_ROUTE_BINDING_DRIFT"):
        evaluate_candidate(snapshot, candidate)


def test_i153_gate_offset_or_environment_binding_drift_fails_closed() -> None:
    snapshot = _snapshot()
    candidate = _candidate(snapshot, route=14)
    candidate["equation_witness"]["gates"][1]["source_offset"] += 1
    with pytest.raises(EquationSearchFilterError, match="GATE_TOPOLOGY_DRIFT"):
        evaluate_candidate(snapshot, candidate)

    candidate = _candidate(snapshot, route=15)
    candidate["equation_witness"]["gates"][3]["global_symbol_environment_root"] = "c" * 64
    with pytest.raises(EquationSearchFilterError, match="GATE_GLOBAL_ENVIRONMENT_BINDING_DRIFT"):
        evaluate_candidate(snapshot, candidate)


def test_i153_batch_filter_is_deterministic_and_rejects_duplicate_routes() -> None:
    snapshot = _snapshot()
    candidates = [
        _candidate(snapshot, route=0, gates=(True, True, True, True, True)),
        _candidate(snapshot, route=1, gates=(True, False, True, True, True)),
        _candidate(snapshot, route=2, gates=(True, True, True, True, True)),
    ]
    first = filter_search_space(snapshot, candidates)
    second = filter_search_space(snapshot, candidates)
    assert first == second
    assert first["candidate_count"] == 3
    assert first["survivor_count"] == 2
    assert first["rejected_count"] == 1
    assert first["rejection_reason_counts"] == {"BOOLEAN_GATE_FALSE": 1}
    assert first["candidate_reduction_fraction"] == {"numerator": 3, "denominator": 2}
    assert first["candidate_reduction_x1000_floor"] == 1500
    assert len(first["receipt_sha256"]) == 64

    duplicate = [_candidate(snapshot, route=0), _candidate(snapshot, route=0)]
    with pytest.raises(EquationSearchFilterError, match="DUPLICATE_WORKING_INDEX"):
        filter_search_space(snapshot, duplicate)


def test_i153_float_and_invalid_hash216_inputs_fail_closed() -> None:
    with pytest.raises(EquationSearchFilterError, match="P_EXACT_INTEGER_REQUIRED"):
        normalize_snapshot(
            {
                "schema": "HHS_PASS219_I153_LOCAL_HASH216_5184_P_SNAPSHOT_V1",
                "snapshot_hash216": "a" * 64,
                "snapshot_hash216_format": HASH216_FORMAT_GENOME_ROOT,
                "P": 1.0,
                "hydration_bits": 5184,
            }
        )
    with pytest.raises(EquationSearchFilterError, match="SNAPSHOT_HASH216_SHA256_HEX_REQUIRED"):
        make_snapshot(
            snapshot_hash216="not-a-root",
            snapshot_hash216_format=HASH216_FORMAT_GENOME_ROOT,
            P=1,
        )


def test_i153_filter_never_promotes_canonical_authority() -> None:
    snapshot = _snapshot()
    result = filter_search_space(snapshot, [_candidate(snapshot, route=21)])
    assert result["pass169_whole_expression_authority_required"] is True
    assert result["filter_produces_boolean_gate_truth"] is False
    assert result["filter_produces_canonical_monolithic_proof"] is False
    assert result["canonical_vm81_mutation"] is False
    assert result["canonical_hash72_mint"] is False
    assert result["canonical_hash216_persistence"] is False
    assert result["physical_full_manifold_enumeration_claim"] is False
