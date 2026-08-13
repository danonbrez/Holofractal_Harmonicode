from __future__ import annotations

import pytest

from hhs_runtime.hhs_cumulative_execution_authority_v1 import (
    ACTIVE_IN_PATH,
    EXPLICITLY_SUPERSEDED,
    HHSCumulativeExecutionAuthorityError,
    NOT_APPLICABLE,
    build_authority_reachability,
    load_inherited_core_authorities,
    validate_authority_reachability,
)


def _active(authority_id: str):
    return {
        "observed": True,
        "path": ["canonical_execution_composer", authority_id],
        "traversal_witness": {"authority_id": authority_id, "visited": True},
        "witness_root": f"root:{authority_id}",
    }


def _not_applicable(authority_id: str):
    return {
        "mechanically_proven": True,
        "predicate": f"requires_{authority_id} == false",
        "observed_facts": {f"requires_{authority_id}": False},
        "reason": f"operation facts mechanically exclude {authority_id}",
    }


def test_inventory_comes_from_required_pass215_profile() -> None:
    inventory = load_inherited_core_authorities()
    ids = {row["authority_id"] for row in inventory["authorities"]}

    assert inventory["authority_count"] == len(ids)
    assert inventory["authority_count"] > 20
    assert "semantic_composition_cache" in ids
    assert "conformance_decision_cache" in ids
    assert "predictive_continuation_cache" in ids
    assert "compiled_rom_reuse" in ids
    assert "native_dispatch" in ids
    assert "interruption_recovery" in ids
    assert "dense_reference" not in ids
    assert "exact_integer_reference" not in ids
    assert "accelerator_batching" not in ids
    assert "gpu_execution" not in ids
    assert inventory["optional_profile_classes_promoted_to_core"] is False
    assert inventory["experimental_profile_classes_promoted_to_core"] is False


def test_all_active_required_authorities_admit() -> None:
    required = ("conformance_decision_cache", "native_dispatch")
    record = build_authority_reachability(
        "test.operation",
        active_in_path={authority_id: _active(authority_id) for authority_id in required},
        required_authorities=required,
    )
    decision = validate_authority_reachability(record)

    assert record["admitted"] is True
    assert decision["ok"] is True
    assert {row["state"] for row in record["decisions"]} == {ACTIVE_IN_PATH}


def test_missing_authority_is_not_implicitly_not_applicable() -> None:
    record = build_authority_reachability(
        "test.missing",
        active_in_path={"conformance_decision_cache": _active("conformance_decision_cache")},
        required_authorities=("conformance_decision_cache", "native_dispatch"),
    )

    assert record["admitted"] is False
    native = next(row for row in record["decisions"] if row["authority_id"] == "native_dispatch")
    assert native["state"] is None
    assert "REJECT_INHERITED_AUTHORITY_DISPOSITION_MISSING" in native["reasons"]
    assert validate_authority_reachability(record)["ok"] is False


def test_not_applicable_requires_mechanical_proof() -> None:
    authority_id = "predictive_continuation_cache"
    admitted = build_authority_reachability(
        "test.no_parent",
        not_applicable={authority_id: _not_applicable(authority_id)},
        required_authorities=(authority_id,),
    )
    weak = build_authority_reachability(
        "test.weak",
        not_applicable={
            authority_id: {
                "mechanically_proven": False,
                "reason": "caller says it is unnecessary",
            }
        },
        required_authorities=(authority_id,),
    )

    assert admitted["admitted"] is True
    assert admitted["decisions"][0]["state"] == NOT_APPLICABLE
    assert weak["admitted"] is False
    assert weak["decisions"][0]["state"] is None


def test_explicit_supersession_requires_later_contract_and_equality() -> None:
    authority_id = "compiled_rom_reuse"
    admitted = build_authority_reachability(
        "test.superseded",
        explicitly_superseded={
            authority_id: {
                "later_pass": 217,
                "replacement_authority": "compiled_rom_reuse_v2",
                "validation_root": "hash216:replacement-validation",
                "explicit_contract": "HHS-P217-EXPLICIT-COMPILED-ROM-REUSE-SUPERSESSION",
                "semantic_equality_proven": True,
            }
        },
        required_authorities=(authority_id,),
    )
    stale = build_authority_reachability(
        "test.stale_supersession",
        explicitly_superseded={
            authority_id: {
                "later_pass": 214,
                "replacement_authority": "compiled_rom_reuse_v2",
                "validation_root": "hash216:replacement-validation",
                "explicit_contract": "HHS-P214-NOT-LATER",
                "semantic_equality_proven": True,
            }
        },
        required_authorities=(authority_id,),
    )

    assert admitted["admitted"] is True
    assert admitted["decisions"][0]["state"] == EXPLICITLY_SUPERSEDED
    assert stale["admitted"] is False


def test_ambiguous_disposition_fails_closed() -> None:
    authority_id = "native_dispatch"
    record = build_authority_reachability(
        "test.ambiguous",
        active_in_path={authority_id: _active(authority_id)},
        not_applicable={authority_id: _not_applicable(authority_id)},
        required_authorities=(authority_id,),
    )

    assert record["admitted"] is False
    assert record["decisions"][0]["state"] is None
    assert "REJECT_INHERITED_AUTHORITY_DISPOSITION_AMBIGUOUS" in record["decisions"][0]["reasons"]


def test_optional_available_is_forbidden_even_as_nested_evidence() -> None:
    with pytest.raises(
        HHSCumulativeExecutionAuthorityError,
        match="REJECT_OPTIONAL_AVAILABLE_IN_INHERITED_CORE_EXECUTION_PATH",
    ):
        build_authority_reachability(
            "test.optional",
            active_in_path={
                "native_dispatch": {
                    **_active("native_dispatch"),
                    "legacy_state": "OPTIONAL_AVAILABLE",
                }
            },
            required_authorities=("native_dispatch",),
        )


def test_float_authority_evidence_is_rejected() -> None:
    with pytest.raises(
        HHSCumulativeExecutionAuthorityError,
        match="REJECT_FLOAT_IN_CUMULATIVE_EXECUTION_AUTHORITY",
    ):
        build_authority_reachability(
            "test.float",
            active_in_path={
                "native_dispatch": {
                    **_active("native_dispatch"),
                    "score": 1.0,
                }
            },
            required_authorities=("native_dispatch",),
        )
