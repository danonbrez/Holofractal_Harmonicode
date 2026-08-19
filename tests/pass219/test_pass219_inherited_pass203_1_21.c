#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <string.h>

static HHSExactPass203IntegratedMainframeWitnessV1 witness(void) {
    HHSExactPass203IntegratedMainframeWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass203_version();
    w.production_verified = 1U;
    w.historical_catalog_count = 2902U;
    w.historical_hydrated_count = 688U;
    w.historical_callable_count = 688U;
    w.historical_unbound_count = 2214U;
    w.governed_operation_count = 42U;
    w.python_function_count = 2644U;
    w.native_abi_symbol_count = 211U;
    w.explicit_adapter_count = 5U;
    w.historical_public_route_count = 464U;
    w.historical_openapi_path_count = 435U;
    w.all_discovered_functions_indexed = 1U;
    w.all_hydrated_functions_callable = 1U;
    w.unbound_functions_fail_closed = 1U;
    w.renderer_verified = 1U;
    w.render_record_count = 415U;
    w.render_style_parameter_count = 30U;
    w.render_native_layer_parameter_count = 10U;
    w.render_transport_parameter_count = 21U;
    w.render_compiled_constant_count = 346U;
    w.render_quality_profile_count = 5U;
    w.render_validated_width = 1440U;
    w.render_validated_height = 2560U;
    w.render_texture_flags = 31U;
    w.render_sprite_flags = 31U;
    w.compiled_constants_public_and_read_only = 1U;
    w.native_frame_identity_preserved = 1U;
    w.native_layers_publicly_selectable = 1U;
    w.pass202_inheritance_verified = 1U;
    w.pass204_successor_preserved = 1U;
    w.pass204_standalone_replay_verified = 1U;
    w.dynamic_catalog_growth_is_compatible = 1U;
    w.implementation_pull_request = 145U;
    w.final_mainframe_workflow_run = 30791006119ULL;
    w.final_mainframe_artifact_id = 8847098572ULL;
    w.final_storybook_workflow_run = 30791006060ULL;
    w.final_storybook_artifact_id = 8847186479ULL;
    strcpy(w.base_commit, "8bd57b5843648efb52092568fae3501eeeefeda0");
    strcpy(w.validated_head, "b1bb5ca1908b6e02a037ea412801286867be74b3");
    strcpy(w.merge_commit, "b5209f0dad3fade8bacede8cf1dd10c3fdc12e34");
    strcpy(w.mainframe_receipt_blob, "96ba032149343cffbde17ee9833e47c79395ac14");
    strcpy(w.renderer_receipt_blob, "100a97fc47477d2f633626c33e89dfd6ccb44d21");
    strcpy(w.pass204_replay_receipt_blob, "69e5e3f8db578fee2dfc07573fcce5423add6376");
    strcpy(w.mainframe_status_hash72, "J*pPaI2yHf3zQj6UDE9v*MNVOsw9/uQ-9ZF6Y!?ZaqjSF-(rMK*0R-wQFRt((-ZNc*CU55Ra");
    strcpy(w.renderer_catalog_hash72, "iN/zFXtXYMQKEf*xUis0(/wqZrCuIh2-5QDiHC8BE<kH!n<xyNubi<0ZPfxA(COAqV9bKmkX");
    strcpy(w.mainframe_catalog_sha256, "aefc0c4997ec6ac798d2c1934242719b3176596296b45921032ba31edbc859fe");
    strcpy(w.renderer_filter_graph_sha256, "d5602d04b1184888cb65ca5ef8384dd251a273374a96011d3d2c60e5dbc69545");
    return w;
}

int main(void) {
    HHSExactPass219InheritedPass203BindingV1 b;
    HHSExactPass203IntegratedMainframeWitnessV1 w = witness();
    assert(hhs_exact_pass219_bind_pass203_integrated_mainframe(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.pass_number == 203U && b.fail_closed_binding_gaps_bound == 1U);
    assert(b.renderer_subauthority_bound == 1U && b.pass204_successor_bound == 1U);
    assert(b.pass219_new_execution_authority == 0U && b.vm81_mutation_authority == 0U);

    w = witness(); w.unbound_functions_fail_closed = 0U;
    assert(hhs_exact_pass219_bind_pass203_integrated_mainframe(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness(); w.arbitrary_host_eval_available = 1U;
    assert(hhs_exact_pass219_bind_pass203_integrated_mainframe(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness(); w.assistant_plan_is_execution_authority = 1U;
    assert(hhs_exact_pass219_bind_pass203_integrated_mainframe(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness(); w.renderer_frontend_is_authority = 1U;
    assert(hhs_exact_pass219_bind_pass203_integrated_mainframe(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness(); w.dynamic_catalog_growth_is_compatible = 0U;
    assert(hhs_exact_pass219_bind_pass203_integrated_mainframe(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness(); w.pass219_new_execution_authority = 1U;
    assert(hhs_exact_pass219_bind_pass203_integrated_mainframe(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness(); w.mainframe_receipt_blob[0] = '0';
    assert(hhs_exact_pass219_bind_pass203_integrated_mainframe(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}
