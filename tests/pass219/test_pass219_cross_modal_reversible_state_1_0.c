#include "hhs_pass219_cross_modal_reversible_state_1_0.h"

#include <assert.h>
#include <string.h>

int main(void) {
    HHSExactPass219CrossModalStateWitnessV1 witness;
    HHSExactPass219CrossModalWorkPlanV1 plan;

    memset(&witness, 0, sizeof(witness));
    witness.version = HHS_PASS219_CROSS_MODAL_VERSION;
    witness.depth = 64u;
    witness.required_modalities = 5u;
    witness.mapped_modalities = 5u;
    witness.constraints_total = 24u;
    witness.constraints_passed = 24u;
    witness.reversible_edges_required = 10u;
    witness.reversible_edges_verified = 10u;
    witness.genesis_lineage_bound = 1u;
    witness.ordered_phase_path_bound = 1u;
    witness.hash216_lineage_bound = 1u;
    witness.global_constraint_root_bound = 1u;
    witness.modality_registry_root_bound = 1u;
    witness.singleton_vm81_authority_required = 1u;
    witness.candidate_mutation_authority = 0u;
    witness.floating_point_authority = 0u;

    assert(hhs_exact_pass219_cross_modal_state_validate(&witness) ==
           HHS_PASS219_CROSS_MODAL_OK);

    witness.mapped_modalities = 4u;
    assert(hhs_exact_pass219_cross_modal_state_validate(&witness) ==
           HHS_PASS219_CROSS_MODAL_MODALITY_COVERAGE_ERROR);
    witness.mapped_modalities = 5u;

    witness.ordered_phase_path_bound = 0u;
    assert(hhs_exact_pass219_cross_modal_state_validate(&witness) ==
           HHS_PASS219_CROSS_MODAL_PHASE_ORDER_ERROR);
    witness.ordered_phase_path_bound = 1u;

    witness.candidate_mutation_authority = 1u;
    assert(hhs_exact_pass219_cross_modal_state_validate(&witness) ==
           HHS_PASS219_CROSS_MODAL_AUTHORITY_ERROR);
    witness.candidate_mutation_authority = 0u;

    assert(hhs_exact_pass219_cross_modal_work_plan(
               64u, 5u, 24u, 56u, 2u, 1u, 1u, &plan) ==
           HHS_PASS219_CROSS_MODAL_OK);
    assert(plan.baseline_constraint_checks == 7680u);
    assert(plan.baseline_translation_checks == 1280u);
    assert(plan.baseline_authority_checks == 64u);
    assert(plan.baseline_total_work == 9024u);
    assert(plan.candidate_constraint_checks == 970u);
    assert(plan.candidate_translation_checks == 90u);
    assert(plan.candidate_authority_checks == 64u);
    assert(plan.candidate_total_work == 1124u);
    assert(plan.optimization_selected == 1u);
    assert(plan.complete_fallback == 0u);
    assert(plan.selected_total_work == 1124u);
    assert(plan.exact_work_saved == 7900u);

    assert(hhs_exact_pass219_cross_modal_work_plan(
               64u, 5u, 24u, 56u, 2u, 0u, 1u, &plan) ==
           HHS_PASS219_CROSS_MODAL_OK);
    assert(plan.optimization_selected == 0u);
    assert(plan.complete_fallback == 1u);
    assert(plan.selected_total_work == plan.baseline_total_work);
    assert(plan.exact_work_saved == 0u);

    assert(HHS_PASS219_CROSS_MODAL_VM81_CELLS *
               HHS_PASS219_CROSS_MODAL_OPERATIONS_PER_CELL ==
           HHS_PASS219_CROSS_MODAL_ADDRESSES);

    return 0;
}
