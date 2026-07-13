from hhs_runtime.hhs_conformance_decision_cache_v1 import (
    conformance_decision_cache_self_test,
    get_or_build_decision,
    validate_cache_entry,
)


def test_cache_self_test_passes():
    assert conformance_decision_cache_self_test()["ok"] is True


def test_repeated_validation_hits_cache():
    surface = {
        "surface_id": "service:cache.test",
        "surface_type": "SERVICE",
        "invariant_ids": ["HHS-I011", "HHS-I014"],
        "contract_schemas": ["HHS_CACHE_TEST_CONTRACT_V1"],
        "witness_schemas": ["HHS_KERNEL_DERIVATION_WITNESS_V1"],
        "validators": ["validate_cache_test"],
        "rejection_codes": ["REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT"],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
    }
    cache = {}
    first = get_or_build_decision(surface, conformance_root_hash72="r", cache=cache)
    second = get_or_build_decision(surface, conformance_root_hash72="r", cache=cache)
    assert first["cache_hit"] is False
    assert second["cache_hit"] is True
    assert validate_cache_entry(second["entry"], surface, conformance_root_hash72="r")["ok"] is True
