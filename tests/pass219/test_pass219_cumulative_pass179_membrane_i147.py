from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i147_pass179 import (
    execute_pass179_membrane_preflight,
    pass179_membrane_manifest,
    validate_pass179_exact_binding_surface,
    validate_pass179_frozen_nucleus,
    validate_pass179_global_census,
    validate_pass179_runtime_projection,
    validate_pass179_shader_and_golden_nuclei,
)


def main() -> None:
    frozen = validate_pass179_frozen_nucleus()
    assert frozen["pre_cumulative_green_run"] == 33621928309
    runtime = validate_pass179_runtime_projection()
    assert runtime["software_renderer_projection_only"] is True
    golden = validate_pass179_shader_and_golden_nuclei()
    assert golden["motion_5184_node_count"] == 5184
    census = validate_pass179_global_census()
    assert census["wired_floor"] == 179
    assert census["binding_count"] == 42
    assert census["terminal_completion_claimed"] is False
    assert census["remaining_terminal_category_count"] == 10
    exact = validate_pass179_exact_binding_surface()
    assert exact["terminal_completion_claimed"] is False
    manifest = pass179_membrane_manifest()
    assert manifest["aggregate_order_tail"] == [183, 182, 181, 180, 179]
    assert manifest["repair_forward_required"] is True
    assert len(manifest["remaining_terminal_categories"]) == 10
    assert execute_pass179_membrane_preflight()["ok"] is True


if __name__ == "__main__":
    main()
