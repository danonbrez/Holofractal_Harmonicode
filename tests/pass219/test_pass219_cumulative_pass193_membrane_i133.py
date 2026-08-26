from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i133_pass193 import (
    PASS193_CENSUS_CLASSIFICATION,
    REQUIRED_OPERATIONS,
    execute_pass193_membrane_preflight,
    invoke,
    pass193_membrane_manifest,
)


def main() -> None:
    manifest = pass193_membrane_manifest()
    assert manifest["classification"] == "WIRED"
    assert PASS193_CENSUS_CLASSIFICATION == "MISSING_IMPLEMENTATION_AND_MEMBRANE_EXPOSURE"
    assert manifest["contract_authorization_commit"] == "eebc47a52de143df4a9acf807735f576ad0ce844"
    assert manifest["frozen_predecessor"] == "d311cd243845456851518ce1fef026a7d3cac45e"
    assert tuple(manifest["declared_operations"]) == REQUIRED_OPERATIONS

    preflight = execute_pass193_membrane_preflight()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(REQUIRED_OPERATIONS)

    lineage = invoke("validate_pass193_contract_and_lineage")
    assert lineage["ok"] is True
    assert lineage["historical_contract_preserved"] is True

    geometry = invoke("validate_pass193_exact_geometry_boundary")
    assert geometry["regular_3d_families"] == 5
    assert geometry["regular_4d_families"] == 6
    assert geometry["canonical_coordinates"] == "EXACT_OR_SYMBOLIC"
    assert geometry["float_canonical_authority"] is False
    assert geometry["hash216_canonical_identity"] is True

    phase = invoke("validate_pass193_phase_nesting_boundary")
    assert phase["ordered_rational_phase_history"] is True
    assert phase["phase_plane_count_rule"] == "N(N-1)/2"
    assert phase["noncommutative_order_preserved"] is True
    assert phase["pass192_fibonacci_witness_reused"] is True
    assert phase["projection_is_canonical_authority"] is False

    native = invoke("validate_pass193_native_egress_boundary")
    assert native["native_artifact_bytes_persisted"] is True
    assert native["compiler_linker_environment_provenance"] is True
    assert native["required_ci_targets"] == ["linux-x86_64-elf", "linux-arm64-elf"]
    assert native["native_target_evidence_is_vm81_authority"] is False

    package = invoke("validate_pass193_package_nft_boundary")
    assert package["portable_zip_is_real"] is True
    assert package["path_traversal_rejected"] is True
    assert package["automatic_execution"] is False
    assert package["explicit_user_action_install"] is True
    assert package["nft_identity_is_execution_authority"] is False

    api = invoke("validate_pass193_api_transport_boundary")
    assert api["api_prefix"] == "/api/runtime/hypersolids"
    assert api["hash216_identity_unchanged"] is True
    assert api["path_reference_transport"] == "REVERSIBLE_BASE64URL"
    assert api["canonical_mutations_require_authority_execution"] is True

    production = invoke("validate_pass193_production_registration_boundary")
    assert production["production_router_registered"] is True
    assert production["registration_precedes_public_federation"] is True
    assert production["public_api_federation_preserved"] is True
    assert production["system_status_api_exposed"] is True
    assert production["canonical_server_remains_runtime_authority"] is True

    successor = invoke("validate_pass193_successor_binding")
    assert successor["successor_pass"] == 194
    assert successor["successor_contract_authorization"] == "714f3f3c5c77eab9714be421811ce4fd650a8e99"
    assert successor["successor_preserved"] is True

    authority = invoke("validate_pass193_no_new_authority")
    assert authority["i133_new_candidate_authority"] is False
    assert authority["i133_new_canonical_mutation_authority"] is False
    assert authority["i133_new_persistence_authority"] is False
    assert authority["i133_new_hash72_clock"] is False
    assert authority["cxx_mutation_authority"] is False
    assert authority["vm81_mutation_authority"] is False
    assert authority["float_canonical_authority"] is False
    assert authority["projection_authority"] is False
    assert authority["package_autoexec_authority"] is False
    assert authority["nft_identity_execution_authority"] is False
    assert authority["public_api_federation_is_vm81_authority"] is False
    assert authority["singleton_vm81_authority_remains_inherited"] is True


if __name__ == "__main__":
    main()
