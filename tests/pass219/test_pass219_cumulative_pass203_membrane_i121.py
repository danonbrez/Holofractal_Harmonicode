from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i121_pass203 import (
    EXPECTED_BLOBS,
    preflight_pass203_membrane,
)


def main() -> None:
    result = preflight_pass203_membrane()
    assert result["ok"] is True
    assert len(result["operations"]) == 8
    assert all(row["ok"] is True for row in result["operations"])
    manifest = result["manifest"]
    assert manifest["pass_number"] == 203
    assert manifest["classification"] == "WIRED"
    assert manifest["census_classification"] == "MISSING_MEMBRANE_EXPOSURE"
    assert manifest["historical_catalog_count"] == 2902
    assert manifest["historical_callable_count"] == 688
    assert manifest["historical_unbound_count"] == 2214
    assert manifest["renderer_record_count"] == 415
    assert manifest["pass204_replay_catalog_count"] == 2910
    assert manifest["pass204_standalone_replay_bound"] is True
    assert manifest["fail_closed_binding_gaps_bound"] is True
    assert manifest["renderer_subauthority_bound"] is True
    assert manifest["renderer_frontend_is_authority"] is False
    assert manifest["pass202_inheritance_bound"] is True
    assert manifest["pass204_successor_bound"] is True
    assert manifest["pass219_new_execution_authority"] is False
    assert manifest["pass219_new_canonical_mutation_authority"] is False
    assert manifest["pass219_new_persistence_authority"] is False
    assert manifest["pass219_new_hash72_clock"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_mutation_authority"] is False
    assert manifest["source_blobs"] == {str(path): blob for path, blob in EXPECTED_BLOBS.items()}


if __name__ == "__main__":
    main()
