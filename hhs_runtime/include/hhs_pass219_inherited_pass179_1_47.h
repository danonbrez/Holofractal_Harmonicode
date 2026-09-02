#ifndef HHS_PASS219_INHERITED_PASS179_1_47_H
#define HHS_PASS219_INHERITED_PASS179_1_47_H

#include "hhs_pass219_inherited_pass180_1_46.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS179_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS179_VERSION_MINOR 47U
#define HHS_EXACT_PASS219_INHERITED_PASS179_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS179_NUMBER 179U
#define HHS_EXACT_PASS179_I147_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS179_I147_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS179_I147_REMAINING_TERMINAL_CATEGORY_COUNT 10U

typedef struct HHSExactPass179NativeGraphicsWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t contract_preserved;
    uint32_t native_c11_core_bound;
    uint32_t exact_scene_types_bound;
    uint32_t vm81_scene_admission_bound;
    uint32_t post_vm81_hash72_evidence_bound;
    uint32_t archival_hash216_identity_bound;
    uint32_t software_renderer_bound;
    uint32_t typed_shader_ir_bound;
    uint32_t deterministic_png_capture_bound;
    uint32_t webgpu_projection_bound;
    uint32_t webgl2_projection_bound;
    uint32_t threejs_projection_bound;
    uint32_t lattice_run_nucleus_bound;
    uint32_t motion_5184_nucleus_bound;
    uint32_t served_graphics_studio_bound;
    uint32_t pre_cumulative_validation_green;
    uint32_t pass180_successor_preserved;
    uint32_t terminal_pass179_completion;
    uint32_t repair_forward_required;
    uint32_t remaining_terminal_category_count;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_commit_authority;
    uint32_t hash216_mutation_authority;
    uint32_t gpu_mutation_authority;
    uint32_t browser_mutation_authority;
    uint32_t floating_point_canonical_authority;
    char validated_nucleus_head[HHS_EXACT_PASS179_I147_GIT_SHA_STRLEN];
    char nucleus_receipt_blob[HHS_EXACT_PASS179_I147_GIT_SHA_STRLEN];
    char inherited_i146_head[HHS_EXACT_PASS179_I147_GIT_SHA_STRLEN];
} HHSExactPass179NativeGraphicsWitnessV1;

typedef struct HHSExactPass219InheritedPass179BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t native_runtime_reachable;
    uint32_t native_c11_core_bound;
    uint32_t exact_scene_types_bound;
    uint32_t vm81_scene_admission_bound;
    uint32_t post_vm81_hash72_evidence_bound;
    uint32_t archival_hash216_identity_bound;
    uint32_t software_renderer_bound;
    uint32_t typed_shader_ir_bound;
    uint32_t deterministic_png_capture_bound;
    uint32_t browser_projection_packets_bound;
    uint32_t golden_scene_nuclei_bound;
    uint32_t served_graphics_studio_bound;
    uint32_t no_new_authority_bound;
    uint32_t terminal_completion_claimed;
    uint32_t repair_forward_required;
    uint32_t remaining_terminal_category_count;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_commit_authority;
    uint32_t hash216_mutation_authority;
    uint32_t gpu_mutation_authority;
    uint32_t browser_mutation_authority;
    uint32_t floating_point_canonical_authority;
    char validated_nucleus_head[HHS_EXACT_PASS179_I147_GIT_SHA_STRLEN];
    char nucleus_receipt_blob[HHS_EXACT_PASS179_I147_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass179BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass179_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass179_native_graphics(
    const HHSExactPass179NativeGraphicsWitnessV1 *witness,
    HHSExactPass219InheritedPass179BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif
#endif
