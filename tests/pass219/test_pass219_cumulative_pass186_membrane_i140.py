from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i140_pass186 import (
    PASS186_CENSUS_CLASSIFICATION,
    execute_pass186_membrane_preflight,
    pass186_membrane_manifest,
    pass186_membrane_source_evidence,
    validate_pass186_authority_boundary,
    validate_pass186_historical_lineage,
    validate_pass186_native_acceptance,
    validate_pass186_no_new_authority,
    validate_pass186_noncommutative_identity_boundary,
    validate_pass186_successor_binding,
    validate_pass186_x86_64_boundary,
)


def main() -> None:
    evidence = pass186_membrane_source_evidence()
    assert evidence["implementation_commit"] == "fd42056c22071d290945b02efe3a5752aaa3d737"
    assert evidence["frozen_i139"] == "e5ce3529fcdd7c214aeda8b09f3b7b2bff08b8c4"

    manifest = pass186_membrane_manifest()
    assert manifest["pass_number"] == 186
    assert manifest["iteration"] == 140
    assert manifest["classification"] == "WIRED"
    assert manifest["aggregate_order_tail"] == [192, 191, 190, 189, 188, 187, 186]
    assert "MEMBRANE_EXPOSURE_REQUIRED" in PASS186_CENSUS_CLASSIFICATION

    lineage = validate_pass186_historical_lineage()
    assert lineage["implementation_gap"] is False
    assert lineage["historical_sources_byte_identical"] is True

    native = validate_pass186_native_acceptance()
    assert native["q144"] == 144
    assert native["factorial7"] == 5040
    assert native["vm5184"] == 5184
    assert native["g243"] == 243
    assert native["hydrated_states"] == 1_259_712
    assert native["exhaustive_roundtrip_states"] == 1_259_712
    assert native["floating_point_opcode_scan"] == "PASS"

    identity = validate_pass186_noncommutative_identity_boundary()
    assert identity["xy_yx_distinct"] is True
    assert identity["zw_wz_distinct"] is True
    assert identity["ordered_tag_is_identity"] is True
    assert identity["integer_product_witness_is_identity"] is False

    x64 = validate_pass186_x86_64_boundary()
    assert x64["system_v_amd64"] is True
    assert x64["register_probe_required"] is True
    assert x64["register_probe_is_mutation_authority"] is False

    authority = validate_pass186_authority_boundary()
    assert authority["historical_mapping_surface_reused"] is True
    assert authority["projection_is_canonical_mutation_authority"] is False
    assert authority["independent_opcode_authority"] is False
    assert authority["independent_vm81_authority"] is False
    assert authority["independent_hash72_clock"] is False
    assert authority["float_canonical_authority"] is False

    successor = validate_pass186_successor_binding()
    assert successor["successor_pass"] == 187
    assert successor["successor_frozen_commit"] == "e5ce3529fcdd7c214aeda8b09f3b7b2bff08b8c4"
    assert successor["successor_preserved"] is True

    no_new = validate_pass186_no_new_authority()
    assert no_new["singleton_vm81_authority_remains_inherited"] is True
    for key, value in no_new.items():
        if key in {"ok", "singleton_vm81_authority_remains_inherited"}:
            continue
        assert value is False

    preflight = execute_pass186_membrane_preflight()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(manifest["declared_operations"])


if __name__ == "__main__":
    main()
