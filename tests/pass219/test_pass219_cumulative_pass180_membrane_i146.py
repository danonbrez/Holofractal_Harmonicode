from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i146_pass180 import (
    execute_pass180_membrane_preflight,
    pass180_membrane_manifest,
    validate_pass180_global_default_reachability,
    validate_pass180_historical_lineage,
    validate_pass180_no_new_authority,
    validate_pass180_runtime_reachability,
    validate_pass180_terminal_contract,
    validate_pass180_vm81_authority_repair,
)


def main() -> None:
    history = validate_pass180_historical_lineage()
    assert history["historical_green_run"] == 30633469008
    runtime = validate_pass180_runtime_reachability()
    assert runtime["module_count"] == 14
    assert runtime["workflow_count"] == 7
    repair = validate_pass180_vm81_authority_repair()
    assert repair["create_upsert_lifecycle_vm81_admitted"] is True
    terminal = validate_pass180_terminal_contract()
    assert terminal["terminal_pass180_completion"] is True
    assert terminal["remaining_terminal_obligation_count"] == 0
    defaults = validate_pass180_global_default_reachability()
    assert defaults["wired_floor"] == 180
    assert defaults["binding_count"] == 41
    no_new = validate_pass180_no_new_authority()
    assert no_new["independent_vm81_authority"] is False
    manifest = pass180_membrane_manifest()
    assert manifest["aggregate_order_tail"] == [184, 183, 182, 181, 180]
    assert manifest["terminal_completion_claimed"] is True
    assert manifest["repair_forward_required"] is False
    assert execute_pass180_membrane_preflight()["ok"] is True


if __name__ == "__main__":
    main()
