from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i145_pass181 import (
    execute_pass181_membrane_preflight,
    pass181_membrane_manifest,
    validate_pass181_global_default_reachability,
    validate_pass181_historical_lineage,
    validate_pass181_no_new_authority,
    validate_pass181_runtime_reachability,
    validate_pass181_vm81_authority_repair,
)


def main() -> None:
    history = validate_pass181_historical_lineage()
    assert history["historical_green_run"] == 30660886113
    assert validate_pass181_runtime_reachability()["surface_count"] == 8
    repair = validate_pass181_vm81_authority_repair()
    assert repair["freeze_without_vm81_rejected"] is True
    assert repair["inherited_vm81_commit_required"] is True
    defaults = validate_pass181_global_default_reachability()
    assert defaults["wired_floor"] == 181
    assert defaults["binding_count"] == 40
    assert defaults["terminal_completion_claimed"] is False
    assert len(defaults["remaining_terminal_obligations"]) == 3
    no_new = validate_pass181_no_new_authority()
    assert no_new["independent_vm81_authority"] is False
    manifest = pass181_membrane_manifest()
    assert manifest["iteration"] == 145
    assert manifest["aggregate_order_tail"] == [185, 184, 183, 182, 181]
    assert manifest["terminal_completion_claimed"] is False
    assert manifest["repair_forward_required"] is True
    assert execute_pass181_membrane_preflight()["ok"] is True


if __name__ == "__main__":
    main()
