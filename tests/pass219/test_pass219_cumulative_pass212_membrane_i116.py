from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass212 import (
    PASS212_BIND_SYMBOL,
    PASS212_CLASSIFICATION,
    PASS212_NUMBER,
    REQUIRED_OPERATIONS,
    pass212_membrane_manifest,
    pass212_membrane_source_evidence,
    pass212_surface_declaration,
    preflight_pass212_membrane,
)


def main() -> None:
    source = pass212_membrane_source_evidence()
    contract = source["contract"]
    evidence = source["evidence"]
    assert PASS212_NUMBER == 212
    assert PASS212_CLASSIFICATION == "WIRED"
    assert tuple(contract["required_operations"]) == REQUIRED_OPERATIONS
    assert contract["dimensions"]["full_hydration_bits"] == 50_388_480
    assert contract["dimensions"]["full_hydration_bytes"] == 6_298_560
    assert contract["physical_recovery"]["recoverable_erasures_per_stripe"] == 2
    assert contract["invariants"]["P212-I9"].startswith("No hash-only record")
    assert evidence["suite_summary"]["runtime_verified"] is True
    assert evidence["affine_full_hydration"]["compressed_payload_bytes"] == 2473
    assert evidence["arbitrary_full_hydration_fallback"]["strict_compression_claim"] is False
    manifest = pass212_membrane_manifest()
    assert manifest["classification"] == "WIRED"
    assert manifest["pass219_c_abi_surface"] == PASS212_BIND_SYMBOL
    assert manifest["pass213_recovery_successor_bound"] is True
    assert manifest["pass219_new_canonical_mutation_authority"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_mutation_authority"] is False
    assert manifest["next_pass_to_census"] == 211
    declaration = pass212_surface_declaration()
    assert declaration["mutation_policy"] == "NO_CANONICAL_RUNTIME_MUTATION"
    assert declaration["persistence_policy"] == "RECOVERABLE_PACKAGE_BYTES_ONLY"
    assert tuple(declaration["declared_operations"]) == REQUIRED_OPERATIONS
    result = preflight_pass212_membrane(cache={})
    assert result["ok"] is True
    assert len(result["operations"]) == 7
    for row, operation in zip(result["operations"], REQUIRED_OPERATIONS):
        assert row["status"] == "ADMIT_KERNEL_DERIVED_RUNTIME_PREFLIGHT"
        assert row["operation"] == operation
        assert row["composition_plan"]["composition_allowed"] is True
        assert row["composition_plan"]["pipeline"]["mutation_policy"] == "NO_CANONICAL_RUNTIME_MUTATION"


if __name__ == "__main__":
    main()
