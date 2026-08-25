from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i123_pass201 import (
    PASS201_CENSUS_CLASSIFICATION,
    PASS201_CLASSIFICATION,
    PASS201_NUMBER,
    REQUIRED_OPERATIONS,
    pass201_membrane_manifest,
    preflight_pass201_membrane,
)


def main() -> None:
    manifest = pass201_membrane_manifest()
    assert manifest["pass_number"] == PASS201_NUMBER == 201
    assert manifest["classification"] == PASS201_CLASSIFICATION == "WIRED"
    assert manifest["census_classification"] == PASS201_CENSUS_CLASSIFICATION == "MISSING_MEMBRANE_EXPOSURE"
    assert manifest["primary_pull_request"] == 142
    assert manifest["historical_squash_identity_bound"] is True
    assert manifest["immutable_source_identity_bound"] is True
    assert manifest["router_closure_bound"] is True
    assert manifest["deterministic_catalog_bound"] is True
    assert manifest["bounded_tool_boundary_bound"] is True
    assert manifest["native_route_authority_preserved_bound"] is True
    assert manifest["pass202_successor_bound"] is True
    assert manifest["historical_closure"]["api_import_failures"] == 0
    assert manifest["historical_closure"]["unexposed_router_routes"] == 0
    assert manifest["historical_closure"]["openapi_missing_operations"] == 0
    assert manifest["pass219_new_public_execution_authority"] is False
    assert manifest["pass219_new_canonical_mutation_authority"] is False
    assert manifest["pass219_new_persistence_authority"] is False
    assert manifest["pass219_new_hash72_clock"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_mutation_authority"] is False

    preflight = preflight_pass201_membrane()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(REQUIRED_OPERATIONS) == 7
    assert all(row["ok"] is True for row in preflight["operations"])


if __name__ == "__main__":
    main()
