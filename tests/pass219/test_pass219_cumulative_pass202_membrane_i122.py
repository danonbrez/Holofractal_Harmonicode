from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i122_pass202 import (
    PASS202_CENSUS_CLASSIFICATION,
    PASS202_CLASSIFICATION,
    PASS202_NUMBER,
    REQUIRED_OPERATIONS,
    pass202_membrane_manifest,
    preflight_pass202_membrane,
)


def main() -> None:
    manifest = pass202_membrane_manifest()
    assert manifest["pass_number"] == PASS202_NUMBER == 202
    assert manifest["classification"] == PASS202_CLASSIFICATION == "WIRED"
    assert manifest["census_classification"] == PASS202_CENSUS_CLASSIFICATION == "MISSING_MEMBRANE_EXPOSURE"
    assert manifest["primary_pull_request"] == 143
    assert manifest["bootstrap_pull_request"] == 144
    assert manifest["bootstrap_dry_run_bound"] is True
    assert manifest["fast_forward_only_bound"] is True
    assert manifest["rollback_and_health_bound"] is True
    assert manifest["durable_receipt_boundary_bound"] is True
    assert manifest["successor_hardening_bound"] is True
    assert manifest["pass203_successor_bound"] is True
    assert manifest["pass219_new_deployment_authority"] is False
    assert manifest["pass219_new_canonical_mutation_authority"] is False
    assert manifest["pass219_new_persistence_authority"] is False
    assert manifest["pass219_new_hash72_clock"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_mutation_authority"] is False

    preflight = preflight_pass202_membrane()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(REQUIRED_OPERATIONS) == 7
    assert all(row["ok"] is True for row in preflight["operations"])


if __name__ == "__main__":
    main()
