#ifndef HHS_PASS219_INHERITED_PASS203_1_21_H
#define HHS_PASS219_INHERITED_PASS203_1_21_H

#include "hhs_pass219_inherited_pass204_1_20.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS203_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS203_VERSION_MINOR 21U
#define HHS_EXACT_PASS219_INHERITED_PASS203_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS203_NUMBER 203U
#define HHS_EXACT_PASS203_HISTORICAL_CATALOG_COUNT 2902U
#define HHS_EXACT_PASS203_HISTORICAL_HYDRATED_COUNT 688U
#define HHS_EXACT_PASS203_HISTORICAL_CALLABLE_COUNT 688U
#define HHS_EXACT_PASS203_HISTORICAL_UNBOUND_COUNT 2214U
#define HHS_EXACT_PASS203_GOVERNED_OPERATION_COUNT 42U
#define HHS_EXACT_PASS203_PYTHON_FUNCTION_COUNT 2644U
#define HHS_EXACT_PASS203_NATIVE_ABI_SYMBOL_COUNT 211U
#define HHS_EXACT_PASS203_EXPLICIT_ADAPTER_COUNT 5U
#define HHS_EXACT_PASS203_HISTORICAL_PUBLIC_ROUTE_COUNT 464U
#define HHS_EXACT_PASS203_HISTORICAL_OPENAPI_PATH_COUNT 435U
#define HHS_EXACT_PASS203_RENDER_RECORD_COUNT 415U
#define HHS_EXACT_PASS203_RENDER_STYLE_PARAMETER_COUNT 30U
#define HHS_EXACT_PASS203_RENDER_NATIVE_LAYER_PARAMETER_COUNT 10U
#define HHS_EXACT_PASS203_RENDER_TRANSPORT_PARAMETER_COUNT 21U
#define HHS_EXACT_PASS203_RENDER_COMPILED_CONSTANT_COUNT 346U
#define HHS_EXACT_PASS203_RENDER_QUALITY_PROFILE_COUNT 5U
#define HHS_EXACT_PASS203_RENDER_VALIDATED_WIDTH 1440U
#define HHS_EXACT_PASS203_RENDER_VALIDATED_HEIGHT 2560U
#define HHS_EXACT_PASS203_RENDER_TEXTURE_FLAGS 31U
#define HHS_EXACT_PASS203_RENDER_SPRITE_FLAGS 31U
#define HHS_EXACT_PASS203_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS203_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS203_HASH72_LEN 72U
#define HHS_EXACT_PASS203_HASH72_STRLEN 73U
#define HHS_EXACT_PASS203_SHA256_LEN 64U
#define HHS_EXACT_PASS203_SHA256_STRLEN 65U

typedef struct HHSExactPass203IntegratedMainframeWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t production_verified;
    uint32_t historical_catalog_count;
    uint32_t historical_hydrated_count;
    uint32_t historical_callable_count;
    uint32_t historical_unbound_count;
    uint32_t governed_operation_count;
    uint32_t python_function_count;
    uint32_t native_abi_symbol_count;
    uint32_t explicit_adapter_count;
    uint32_t historical_public_route_count;
    uint32_t historical_openapi_path_count;
    uint32_t all_discovered_functions_indexed;
    uint32_t all_hydrated_functions_callable;
    uint32_t unbound_functions_fail_closed;
    uint32_t arbitrary_host_eval_available;
    uint32_t unrestricted_subprocess_available;
    uint32_t arbitrary_native_symbol_dispatch_available;
    uint32_t assistant_plan_is_execution_authority;
    uint32_t compiler_artifact_is_execution_authority;
    uint32_t renderer_verified;
    uint32_t render_record_count;
    uint32_t render_style_parameter_count;
    uint32_t render_native_layer_parameter_count;
    uint32_t render_transport_parameter_count;
    uint32_t render_compiled_constant_count;
    uint32_t render_quality_profile_count;
    uint32_t render_validated_width;
    uint32_t render_validated_height;
    uint32_t render_texture_flags;
    uint32_t render_sprite_flags;
    uint32_t renderer_frontend_is_authority;
    uint32_t compiled_constants_public_and_read_only;
    uint32_t native_frame_identity_preserved;
    uint32_t logical_frame_is_output_quality_ceiling;
    uint32_t native_layers_publicly_selectable;
    uint32_t pass202_inheritance_verified;
    uint32_t pass204_successor_preserved;
    uint32_t pass204_standalone_replay_verified;
    uint32_t dynamic_catalog_growth_is_compatible;
    uint32_t pass219_new_execution_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint32_t implementation_pull_request;
    uint64_t final_mainframe_workflow_run;
    uint64_t final_mainframe_artifact_id;
    uint64_t final_storybook_workflow_run;
    uint64_t final_storybook_artifact_id;
    char base_commit[HHS_EXACT_PASS203_GIT_SHA_STRLEN];
    char validated_head[HHS_EXACT_PASS203_GIT_SHA_STRLEN];
    char merge_commit[HHS_EXACT_PASS203_GIT_SHA_STRLEN];
    char mainframe_receipt_blob[HHS_EXACT_PASS203_GIT_SHA_STRLEN];
    char renderer_receipt_blob[HHS_EXACT_PASS203_GIT_SHA_STRLEN];
    char pass204_replay_receipt_blob[HHS_EXACT_PASS203_GIT_SHA_STRLEN];
    char mainframe_status_hash72[HHS_EXACT_PASS203_HASH72_STRLEN];
    char renderer_catalog_hash72[HHS_EXACT_PASS203_HASH72_STRLEN];
    char mainframe_catalog_sha256[HHS_EXACT_PASS203_SHA256_STRLEN];
    char renderer_filter_graph_sha256[HHS_EXACT_PASS203_SHA256_STRLEN];
} HHSExactPass203IntegratedMainframeWitnessV1;

typedef struct HHSExactPass219InheritedPass203BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t historical_mainframe_bound;
    uint32_t fail_closed_binding_gaps_bound;
    uint32_t exact_execution_policy_bound;
    uint32_t renderer_subauthority_bound;
    uint32_t renderer_read_only_constants_bound;
    uint32_t native_frame_identity_bound;
    uint32_t pass202_inheritance_bound;
    uint32_t pass204_successor_bound;
    uint32_t pass204_standalone_replay_bound;
    uint32_t dynamic_catalog_growth_compatible_bound;
    uint32_t no_new_execution_authority_bound;
    uint32_t no_new_canonical_mutation_authority_bound;
    uint32_t no_new_persistence_authority_bound;
    uint32_t no_new_hash72_clock_bound;
    uint32_t pass219_new_execution_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char merge_commit[HHS_EXACT_PASS203_GIT_SHA_STRLEN];
    char mainframe_receipt_blob[HHS_EXACT_PASS203_GIT_SHA_STRLEN];
    char renderer_receipt_blob[HHS_EXACT_PASS203_GIT_SHA_STRLEN];
    char mainframe_status_hash72[HHS_EXACT_PASS203_HASH72_STRLEN];
    char renderer_catalog_hash72[HHS_EXACT_PASS203_HASH72_STRLEN];
} HHSExactPass219InheritedPass203BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass203_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass203_integrated_mainframe(
    const HHSExactPass203IntegratedMainframeWitnessV1 *witness,
    HHSExactPass219InheritedPass203BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
