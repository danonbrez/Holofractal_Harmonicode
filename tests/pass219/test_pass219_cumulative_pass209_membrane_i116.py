from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass209 import (
    PASS209_BIND_SYMBOL,
    PRODUCTION_STATUS_PATHS,
    REQUIRED_OPERATIONS,
    pass209_membrane_manifest,
    pass209_membrane_source_evidence,
    pass209_surface_declaration,
    preflight_pass209_membrane,
)


def main() -> None:
    source = pass209_membrane_source_evidence()
    assert source["main_merge_head"] == "c05cf860e4be5a0865813529baf9ad99e50dbe02"
    assert source["validated_branch_head"] == "f14a03d1d7dee552efd8133b01dda63063b4a32e"
    assert source["branch_validation_run"] == 31012056789
    assert source["branch_validation_job"] == 92326490304
    assert tuple(source["status_catalog"]) == PRODUCTION_STATUS_PATHS
    assert source["successor_pass210"]["contract"]["pass"] == 210

    declaration = pass209_surface_declaration()
    assert declaration["surface_id"] == "runtime:pass209.runtime-bootstrap-gateway"
    assert declaration["symbol"] == "ProductionRuntimeBootstrapGateway"
    assert declaration["mutation_policy"] == "NONCANONICAL_STATUS_PROJECTION_ONLY"
    assert tuple(declaration["declared_operations"]) == REQUIRED_OPERATIONS
    assert PASS209_BIND_SYMBOL in declaration["validators"]

    manifest = pass209_membrane_manifest()
    assert manifest["pass_number"] == 209
    assert manifest["classification"] == "WIRED"
    assert manifest["status_catalog_count"] == 9
    assert manifest["persistent_status_cache_bound"] is True
    assert manifest["isolated_sequential_probe_bound"] is True
    assert manifest["cold_miss_warming_projection_bound"] is True
    assert manifest["external_state_roots_bound"] is True
    assert manifest["canonical_backend_authority_preserved"] is True
    assert manifest["cache_projection_noncanonical"] is True
    assert manifest["pass210_successor_bound"] is True
    assert manifest["pass219_new_canonical_mutation_authority"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_mutation_authority"] is False
    assert manifest["next_pass_to_census"] == 208

    preflight = preflight_pass209_membrane()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(REQUIRED_OPERATIONS)
    assert all(row.get("ok") is True for row in preflight["operations"])


if __name__ == "__main__":
    main()
