#include <assert.h>
#include <string.h>
#include "hhs_runtime_exact_abi.h"

static void fill(char out[HHS_EXACT_PASS179_I147_GIT_SHA_STRLEN], const char *value) {
    memcpy(out, value, HHS_EXACT_PASS179_I147_GIT_SHA_LEN);
    out[HHS_EXACT_PASS179_I147_GIT_SHA_LEN] = '\0';
}

static HHSExactPass179NativeGraphicsWitnessV1 witness(void) {
    HHSExactPass179NativeGraphicsWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass179_version();
    w.contract_preserved = 1U;
    w.native_c11_core_bound = 1U;
    w.exact_scene_types_bound = 1U;
    w.vm81_scene_admission_bound = 1U;
    w.post_vm81_hash72_evidence_bound = 1U;
    w.archival_hash216_identity_bound = 1U;
    w.software_renderer_bound = 1U;
    w.typed_shader_ir_bound = 1U;
    w.deterministic_png_capture_bound = 1U;
    w.webgpu_projection_bound = 1U;
    w.webgl2_projection_bound = 1U;
    w.threejs_projection_bound = 1U;
    w.lattice_run_nucleus_bound = 1U;
    w.motion_5184_nucleus_bound = 1U;
    w.served_graphics_studio_bound = 1U;
    w.pre_cumulative_validation_green = 1U;
    w.pass180_successor_preserved = 1U;
    w.terminal_pass179_completion = 0U;
    w.repair_forward_required = 1U;
    w.remaining_terminal_category_count =
        HHS_EXACT_PASS179_I147_REMAINING_TERMINAL_CATEGORY_COUNT;
    fill(w.validated_nucleus_head, "ff149faeadf3e31764138a2316052a013b28599c");
    fill(w.nucleus_receipt_blob, "b6c7c9b42d3892de6ddaff354514ceafaa695b8e");
    fill(w.inherited_i146_head, "f03491cd6744e56e2e81a689416b94a6fb0ae9a4");
    return w;
}

int main(void) {
    HHSExactPass179NativeGraphicsWitnessV1 w = witness();
    HHSExactPass219InheritedPass179BindingV1 b;
    assert(hhs_exact_pass219_bind_pass179_native_graphics(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.pass_number == 179U);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.native_runtime_reachable == 1U);
    assert(b.vm81_scene_admission_bound == 1U);
    assert(b.post_vm81_hash72_evidence_bound == 1U);
    assert(b.archival_hash216_identity_bound == 1U);
    assert(b.software_renderer_bound == 1U);
    assert(b.typed_shader_ir_bound == 1U);
    assert(b.browser_projection_packets_bound == 1U);
    assert(b.golden_scene_nuclei_bound == 1U);
    assert(b.no_new_authority_bound == 1U);
    assert(b.terminal_completion_claimed == 0U);
    assert(b.repair_forward_required == 1U);
    assert(b.remaining_terminal_category_count == 10U);
    assert(b.independent_vm81_authority == 0U);
    assert(b.independent_hash72_commit_authority == 0U);
    assert(b.hash216_mutation_authority == 0U);
    assert(b.gpu_mutation_authority == 0U);
    assert(b.browser_mutation_authority == 0U);
    assert(b.floating_point_canonical_authority == 0U);

    w.terminal_pass179_completion = 1U;
    assert(hhs_exact_pass219_bind_pass179_native_graphics(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.independent_hash72_commit_authority = 1U;
    assert(hhs_exact_pass219_bind_pass179_native_graphics(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}
