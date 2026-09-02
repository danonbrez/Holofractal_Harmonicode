#include <assert.h>
#include <string.h>
#include "hhs_runtime_exact_abi.h"

static void fill(char out[HHS_EXACT_PASS181_I145_GIT_SHA_STRLEN], const char *value) {
    memcpy(out, value, HHS_EXACT_PASS181_I145_GIT_SHA_LEN);
    out[HHS_EXACT_PASS181_I145_GIT_SHA_LEN] = '\0';
}

static HHSExactPass181GraphicsHydrationWitnessV1 witness(void) {
    HHSExactPass181GraphicsHydrationWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass181_version();
    w.historical_contract_preserved = 1U;
    w.historical_implementation_preserved = 1U;
    w.historical_ci_green = 1U;
    w.read_only_reference_ingestion_bound = 1U;
    w.canonical_mp4_timeline_bound = 1U;
    w.native_recipe_residual_bound = 1U;
    w.bounded_optimization_bound = 1U;
    w.vector_hydration_bound = 1U;
    w.governed_constraint_registry_bound = 1U;
    w.vm81_admission_repair_bound = 1U;
    w.legacy_direct_promotion_disabled = 1U;
    w.cold_restart_constraint_registry_replay_bound = 1U;
    w.singleton_vm81_bound = 1U;
    w.hash72_evidence_bound = 1U;
    w.hash216_archival_only_bound = 1U;
    w.pass182_successor_preserved = 1U;
    w.terminal_pass181_completion = 0U;
    w.remaining_terminal_obligation_count = 3U;
    fill(w.historical_green_head, "3ae56827b27500c2c8187126d5825a901d4feb40");
    fill(w.frozen_i144_checkpoint, "132694cee0af4a43113ddc4c50f867c084a22bae");
    return w;
}

int main(void) {
    HHSExactPass181GraphicsHydrationWitnessV1 w = witness();
    HHSExactPass219InheritedPass181BindingV1 b;
    assert(hhs_exact_pass219_bind_pass181_graphics_hydration(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.pass_number == 181U);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.vm81_admission_repair_bound == 1U);
    assert(b.legacy_direct_promotion_disabled == 1U);
    assert(b.singleton_vm81_bound == 1U);
    assert(b.no_new_authority_bound == 1U);
    assert(b.terminal_completion_claimed == 0U);
    assert(b.repair_forward_required == 1U);
    assert(b.remaining_terminal_obligation_count == 3U);
    assert(b.independent_vm81_authority == 0U);
    assert(b.independent_hash72_authority == 0U);
    assert(b.hash216_mutation_authority == 0U);
    assert(b.floating_point_canonical_authority == 0U);
    assert(b.threejs_final_frame_authority == 0U);

    w.terminal_pass181_completion = 1U;
    assert(hhs_exact_pass219_bind_pass181_graphics_hydration(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.vm81_admission_repair_bound = 0U;
    assert(hhs_exact_pass219_bind_pass181_graphics_hydration(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}
