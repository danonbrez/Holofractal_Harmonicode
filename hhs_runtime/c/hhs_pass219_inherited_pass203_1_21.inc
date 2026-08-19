#include "../include/hhs_pass219_inherited_pass203_1_21.h"

#include <stddef.h>
#include <string.h>

static const char P203_BASE_COMMIT[] = "8bd57b5843648efb52092568fae3501eeeefeda0";
static const char P203_VALIDATED_HEAD[] = "b1bb5ca1908b6e02a037ea412801286867be74b3";
static const char P203_MERGE_COMMIT[] = "b5209f0dad3fade8bacede8cf1dd10c3fdc12e34";
static const char P203_MAINFRAME_RECEIPT_BLOB[] = "96ba032149343cffbde17ee9833e47c79395ac14";
static const char P203_RENDERER_RECEIPT_BLOB[] = "100a97fc47477d2f633626c33e89dfd6ccb44d21";
static const char P203_PASS204_REPLAY_RECEIPT_BLOB[] = "69e5e3f8db578fee2dfc07573fcce5423add6376";
static const char P203_MAINFRAME_STATUS_HASH72[] = "J*pPaI2yHf3zQj6UDE9v*MNVOsw9/uQ-9ZF6Y!?ZaqjSF-(rMK*0R-wQFRt((-ZNc*CU55Ra";
static const char P203_RENDERER_CATALOG_HASH72[] = "iN/zFXtXYMQKEf*xUis0(/wqZrCuIh2-5QDiHC8BE<kH!n<xyNubi<0ZPfxA(COAqV9bKmkX";
static const char P203_MAINFRAME_CATALOG_SHA256[] = "aefc0c4997ec6ac798d2c1934242719b3176596296b45921032ba31edbc859fe";
static const char P203_RENDERER_FILTER_GRAPH_SHA256[] = "d5602d04b1184888cb65ca5ef8384dd251a273374a96011d3d2c60e5dbc69545";

static uint32_t p203_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS203_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS203_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS203_VERSION_PATCH;
}

static int p203_text(const char *value, size_t size, const char *expected, size_t expected_len) {
    return value != NULL && expected != NULL && size == expected_len + 1U &&
           value[expected_len] == '\0' && memcmp(value, expected, expected_len) == 0;
}

static int p203_git(const char value[HHS_EXACT_PASS203_GIT_SHA_STRLEN], const char *expected) {
    return p203_text(value, HHS_EXACT_PASS203_GIT_SHA_STRLEN, expected, HHS_EXACT_PASS203_GIT_SHA_LEN);
}

static int p203_hash72(const char value[HHS_EXACT_PASS203_HASH72_STRLEN], const char *expected) {
    return p203_text(value, HHS_EXACT_PASS203_HASH72_STRLEN, expected, HHS_EXACT_PASS203_HASH72_LEN);
}

static int p203_sha256(const char value[HHS_EXACT_PASS203_SHA256_STRLEN], const char *expected) {
    return p203_text(value, HHS_EXACT_PASS203_SHA256_STRLEN, expected, HHS_EXACT_PASS203_SHA256_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass203_version(void) { return p203_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass203_integrated_mainframe(
    const HHSExactPass203IntegratedMainframeWitnessV1 *witness,
    HHSExactPass219InheritedPass203BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p203_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->production_verified != 1U ||
        witness->historical_catalog_count != HHS_EXACT_PASS203_HISTORICAL_CATALOG_COUNT ||
        witness->historical_hydrated_count != HHS_EXACT_PASS203_HISTORICAL_HYDRATED_COUNT ||
        witness->historical_callable_count != HHS_EXACT_PASS203_HISTORICAL_CALLABLE_COUNT ||
        witness->historical_unbound_count != HHS_EXACT_PASS203_HISTORICAL_UNBOUND_COUNT ||
        witness->governed_operation_count != HHS_EXACT_PASS203_GOVERNED_OPERATION_COUNT ||
        witness->python_function_count != HHS_EXACT_PASS203_PYTHON_FUNCTION_COUNT ||
        witness->native_abi_symbol_count != HHS_EXACT_PASS203_NATIVE_ABI_SYMBOL_COUNT ||
        witness->explicit_adapter_count != HHS_EXACT_PASS203_EXPLICIT_ADAPTER_COUNT ||
        witness->historical_public_route_count != HHS_EXACT_PASS203_HISTORICAL_PUBLIC_ROUTE_COUNT ||
        witness->historical_openapi_path_count != HHS_EXACT_PASS203_HISTORICAL_OPENAPI_PATH_COUNT ||
        witness->all_discovered_functions_indexed != 1U ||
        witness->all_hydrated_functions_callable != 1U ||
        witness->unbound_functions_fail_closed != 1U ||
        witness->arbitrary_host_eval_available != 0U ||
        witness->unrestricted_subprocess_available != 0U ||
        witness->arbitrary_native_symbol_dispatch_available != 0U ||
        witness->assistant_plan_is_execution_authority != 0U ||
        witness->compiler_artifact_is_execution_authority != 0U ||
        witness->renderer_verified != 1U ||
        witness->render_record_count != HHS_EXACT_PASS203_RENDER_RECORD_COUNT ||
        witness->render_style_parameter_count != HHS_EXACT_PASS203_RENDER_STYLE_PARAMETER_COUNT ||
        witness->render_native_layer_parameter_count != HHS_EXACT_PASS203_RENDER_NATIVE_LAYER_PARAMETER_COUNT ||
        witness->render_transport_parameter_count != HHS_EXACT_PASS203_RENDER_TRANSPORT_PARAMETER_COUNT ||
        witness->render_compiled_constant_count != HHS_EXACT_PASS203_RENDER_COMPILED_CONSTANT_COUNT ||
        witness->render_quality_profile_count != HHS_EXACT_PASS203_RENDER_QUALITY_PROFILE_COUNT ||
        witness->render_validated_width != HHS_EXACT_PASS203_RENDER_VALIDATED_WIDTH ||
        witness->render_validated_height != HHS_EXACT_PASS203_RENDER_VALIDATED_HEIGHT ||
        witness->render_texture_flags != HHS_EXACT_PASS203_RENDER_TEXTURE_FLAGS ||
        witness->render_sprite_flags != HHS_EXACT_PASS203_RENDER_SPRITE_FLAGS ||
        witness->renderer_frontend_is_authority != 0U ||
        witness->compiled_constants_public_and_read_only != 1U ||
        witness->native_frame_identity_preserved != 1U ||
        witness->logical_frame_is_output_quality_ceiling != 0U ||
        witness->native_layers_publicly_selectable != 1U ||
        witness->pass202_inheritance_verified != 1U ||
        witness->pass204_successor_preserved != 1U ||
        witness->pass204_standalone_replay_verified != 1U ||
        witness->dynamic_catalog_growth_is_compatible != 1U ||
        witness->pass219_new_execution_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U ||
        witness->implementation_pull_request != 145U ||
        witness->final_mainframe_workflow_run != 30791006119ULL ||
        witness->final_mainframe_artifact_id != 8847098572ULL ||
        witness->final_storybook_workflow_run != 30791006060ULL ||
        witness->final_storybook_artifact_id != 8847186479ULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p203_git(witness->base_commit, P203_BASE_COMMIT) ||
        !p203_git(witness->validated_head, P203_VALIDATED_HEAD) ||
        !p203_git(witness->merge_commit, P203_MERGE_COMMIT) ||
        !p203_git(witness->mainframe_receipt_blob, P203_MAINFRAME_RECEIPT_BLOB) ||
        !p203_git(witness->renderer_receipt_blob, P203_RENDERER_RECEIPT_BLOB) ||
        !p203_git(witness->pass204_replay_receipt_blob, P203_PASS204_REPLAY_RECEIPT_BLOB) ||
        !p203_hash72(witness->mainframe_status_hash72, P203_MAINFRAME_STATUS_HASH72) ||
        !p203_hash72(witness->renderer_catalog_hash72, P203_RENDERER_CATALOG_HASH72) ||
        !p203_sha256(witness->mainframe_catalog_sha256, P203_MAINFRAME_CATALOG_SHA256) ||
        !p203_sha256(witness->renderer_filter_graph_sha256, P203_RENDERER_FILTER_GRAPH_SHA256))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p203_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS203_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->historical_mainframe_bound = 1U;
    out_binding->fail_closed_binding_gaps_bound = 1U;
    out_binding->exact_execution_policy_bound = 1U;
    out_binding->renderer_subauthority_bound = 1U;
    out_binding->renderer_read_only_constants_bound = 1U;
    out_binding->native_frame_identity_bound = 1U;
    out_binding->pass202_inheritance_bound = 1U;
    out_binding->pass204_successor_bound = 1U;
    out_binding->pass204_standalone_replay_bound = 1U;
    out_binding->dynamic_catalog_growth_compatible_bound = 1U;
    out_binding->no_new_execution_authority_bound = 1U;
    out_binding->no_new_canonical_mutation_authority_bound = 1U;
    out_binding->no_new_persistence_authority_bound = 1U;
    out_binding->no_new_hash72_clock_bound = 1U;
    out_binding->pass219_new_execution_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->merge_commit, witness->merge_commit, HHS_EXACT_PASS203_GIT_SHA_STRLEN);
    memcpy(out_binding->mainframe_receipt_blob, witness->mainframe_receipt_blob, HHS_EXACT_PASS203_GIT_SHA_STRLEN);
    memcpy(out_binding->renderer_receipt_blob, witness->renderer_receipt_blob, HHS_EXACT_PASS203_GIT_SHA_STRLEN);
    memcpy(out_binding->mainframe_status_hash72, witness->mainframe_status_hash72, HHS_EXACT_PASS203_HASH72_STRLEN);
    memcpy(out_binding->renderer_catalog_hash72, witness->renderer_catalog_hash72, HHS_EXACT_PASS203_HASH72_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
