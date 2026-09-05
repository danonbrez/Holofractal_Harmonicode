from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i143_pass183 import (
    execute_pass183_membrane_preflight,
    pass183_membrane_manifest,
    validate_pass183_global_default_reachability,
    validate_pass183_historical_green_evidence,
    validate_pass183_historical_lineage,
    validate_pass183_native_compatibility_quarantine,
    validate_pass183_no_new_authority,
    validate_pass183_receipt_authority_order,
    validate_pass183_runtime_os_projection,
)

def main() -> None:
    assert validate_pass183_historical_lineage()["historical_sources_preserved_at_implementation_commit"] is True
    assert validate_pass183_historical_green_evidence()["historical_workflow_conclusion"] == "success"
    order = validate_pass183_receipt_authority_order()
    assert order["hash216_precommit_authority"] is False
    assert order["hash216_archival_only"] is True
    native = validate_pass183_native_compatibility_quarantine()
    assert native["historical_native_hash_strings_canonical"] is False
    assert native["native_hash72_authority"] is False
    assert validate_pass183_runtime_os_projection()["runtime_os_gui"] is True
    defaults = validate_pass183_global_default_reachability()
    assert defaults["wired_floor"] == 183
    assert defaults["binding_count"] == 38
    no_new = validate_pass183_no_new_authority()
    assert no_new["singleton_vm81_authority_remains_inherited"] is True
    assert no_new["hash216_precommit_authority"] is False
    manifest = pass183_membrane_manifest()
    assert manifest["iteration"] == 143
    assert manifest["aggregate_order_tail"] == [187, 186, 185, 184, 183]
    assert execute_pass183_membrane_preflight()["ok"] is True

if __name__ == "__main__":
    main()
