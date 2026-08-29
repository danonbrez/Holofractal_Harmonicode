from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i137_pass189 import (
    PASS189_CLASSIFICATION,
    PASS189_CENSUS_CLASSIFICATION,
    execute_pass189_membrane_preflight,
    pass189_membrane_manifest,
    pass189_membrane_source_evidence,
    validate_pass189_calibration_causal_boundary,
    validate_pass189_deployment_dns_boundary,
    validate_pass189_device_adapter_boundary,
    validate_pass189_driver_provenance_boundary,
    validate_pass189_historical_lineage,
    validate_pass189_hqlh_exact_topology_boundary,
    validate_pass189_no_new_authority,
    validate_pass189_successor_binding,
    validate_pass189_template_registry_boundary,
)


def main() -> None:
    evidence = pass189_membrane_source_evidence()
    assert evidence["frozen_i136"] == "3a76667eb463f8027e2bfaea4a2f76cff470c564"
    assert evidence["pass190_successor"]["successor_preserved"] is True

    manifest = pass189_membrane_manifest()
    assert manifest["pass_number"] == 189
    assert manifest["classification"] == PASS189_CLASSIFICATION == "WIRED"
    assert "CALIBRATION_IN_PROGRESS" in PASS189_CENSUS_CLASSIFICATION
    assert "HARDWARE_EXECUTION_UNAUTHORIZED" in PASS189_CENSUS_CLASSIFICATION

    lineage = validate_pass189_historical_lineage()
    assert lineage["all_historical_layers_preserved"] is True

    registry = validate_pass189_template_registry_boundary()
    assert registry["template_registered"] is True
    assert registry["template_version"] == "1.3.1"
    assert registry["real_driver_execution_pending"] is True

    topology = validate_pass189_hqlh_exact_topology_boundary()
    assert topology["contextual_addresses"] == 51_648_192
    assert topology["lo_shu_41_group"] is True
    assert topology["signed_xnor_ternary"] is True
    assert topology["canonical_float_authority"] is False

    calibration = validate_pass189_calibration_causal_boundary()
    assert calibration["classification"] == "HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS"
    assert calibration["physical_candidates_require_measured_evidence_attestation_and_arm"] is True
    assert calibration["device_driver_dispatch_in_iteration2"] is False

    adapter = validate_pass189_device_adapter_boundary()
    assert adapter["software_adapters"] == ["LOOPBACK", "FILE_SINK"]
    assert adapter["bounded_operator_leases"] is True
    assert adapter["real_hardware_dispatch_authorized"] is False

    provenance = validate_pass189_driver_provenance_boundary()
    assert provenance["promotion_token_validation"] is True
    assert provenance["persistent_promotion_expiry"] is True
    assert provenance["hardware_promotion_class"] == "HARDWARE_CANDIDATE_NONEXECUTABLE"
    assert provenance["hardware_candidate_execution"] is False

    deploy = validate_pass189_deployment_dns_boundary()
    assert deploy["deployment_authority"] == "DIGITALOCEAN_SELF_HOSTED"
    assert deploy["external_digitalocean_mutation_claimed"] is False
    assert deploy["vercel_authority"] is False
    assert deploy["ports"] == [8189, 8190, 8191, 8192]

    successor = validate_pass189_successor_binding()
    assert successor["successor_pass"] == 190
    assert successor["successor_preserved"] is True

    authority = validate_pass189_no_new_authority()
    assert authority["singleton_vm81_authority_remains_inherited"] is True
    for key, value in authority.items():
        if key in {"ok", "singleton_vm81_authority_remains_inherited"}:
            continue
        assert value is False

    preflight = execute_pass189_membrane_preflight()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(manifest["declared_operations"])


if __name__ == "__main__":
    main()
