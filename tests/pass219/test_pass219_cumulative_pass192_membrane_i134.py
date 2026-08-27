from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i134_pass192 import (
    PASS192_CENSUS_CLASSIFICATION,
    REQUIRED_OPERATIONS,
    execute_pass192_membrane_preflight,
    invoke,
    pass192_membrane_manifest,
)


def main() -> None:
    manifest = pass192_membrane_manifest()
    assert manifest["classification"] == "WIRED"
    assert PASS192_CENSUS_CLASSIFICATION == "PARTIAL_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE"
    assert manifest["contract_authorization_commit"] == "c3da7e2b7125754b65f08fb8922a151bf01df2b8"
    assert manifest["frozen_predecessor"] == "8380d2dbc9cf1b0245f006eaa440b47a921d4901"
    assert tuple(manifest["declared_operations"]) == REQUIRED_OPERATIONS

    preflight = execute_pass192_membrane_preflight()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(REQUIRED_OPERATIONS)

    lineage = invoke("validate_pass192_contract_and_lineage")
    assert lineage["historical_contract_preserved"] is True

    tensor = invoke("validate_pass192_exact_tensor_boundary")
    assert tensor["lo_shu_cells"] == 9
    assert tensor["lo_shu_magic_sum"] == 15
    assert tensor["magnitude_rows"] == [1, 2, 3, 5, 8]
    assert tensor["exact_arithmetic"] == "INTEGER_AND_RATIONAL"
    assert tensor["float_canonical_authority"] is False

    materialization = invoke("validate_pass192_materialization_replay_boundary")
    assert materialization["declarative_depth"] == "UNBOUNDED"
    assert materialization["execution_materialization"] == "FINITE_PREFIX_ONLY"
    assert materialization["outer_modulus_applied_locally"] is False
    assert materialization["safe_filesystem_locator"] == "SHA256_HEX_PROJECTION"
    assert materialization["filesystem_locator_is_canonical_authority"] is False
    assert materialization["hash72_replay_chain_verified"] is True

    interface = invoke("validate_pass192_interface_parity_boundary")
    assert interface["python_sdk"] == "hhs_runtime.pass192"
    assert interface["cli_grammar"] == "hhs tensor fibonacci"
    assert interface["openapi_prefix"] == "/v1/tensors/fibonacci"
    assert interface["path_reference_transport"] == "REVERSIBLE_BASE64URL"

    compression = invoke("validate_pass192_inherited_compression_boundary")
    assert compression["pass219_1_9_compression_preserved"] is True
    assert compression["lossless_exact_descriptor"] is True

    production = invoke("validate_pass192_production_registration_boundary")
    assert production["production_router_registered"] is True
    assert production["registration_precedes_public_federation"] is True
    assert production["canonical_server_remains_runtime_authority"] is True

    successor = invoke("validate_pass192_successor_binding")
    assert successor["successor_pass"] == 193
    assert successor["successor_frozen_commit"] == "8380d2dbc9cf1b0245f006eaa440b47a921d4901"
    assert successor["successor_preserved"] is True

    authority = invoke("validate_pass192_no_new_authority")
    assert authority["i134_new_candidate_authority"] is False
    assert authority["i134_new_canonical_mutation_authority"] is False
    assert authority["i134_new_persistence_authority"] is False
    assert authority["i134_new_hash72_clock"] is False
    assert authority["cxx_mutation_authority"] is False
    assert authority["vm81_mutation_authority"] is False
    assert authority["float_canonical_authority"] is False
    assert authority["filesystem_locator_canonical_authority"] is False
    assert authority["singleton_vm81_authority_remains_inherited"] is True


if __name__ == "__main__":
    main()
