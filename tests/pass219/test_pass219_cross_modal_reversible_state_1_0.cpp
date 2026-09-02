#include "hhs_pass219_cross_modal_reversible_state_1_0.hpp"

#include <cassert>

int main() {
    HHSExactPass219CrossModalStateWitnessV1 witness{};
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

    assert(hhs::pass219::CrossModalStateWitness::validate(witness));

    HHSExactPass219CrossModalWorkPlanV1 plan{};
    const auto status = hhs::pass219::CrossModalWorkPlan::make(
        64u, 5u, 24u, 56u, 2u, true, true, plan);
    assert(status == HHS_PASS219_CROSS_MODAL_OK);
    assert(plan.optimization_selected == 1u);
    assert(plan.baseline_total_work == 9024u);
    assert(plan.selected_total_work == 1124u);
    assert(plan.exact_work_saved == 7900u);

    HHSExactPass219CrossModalWorkPlanV1 fallback{};
    assert(hhs::pass219::CrossModalWorkPlan::make(
               64u, 5u, 24u, 56u, 2u, true, false, fallback) ==
           HHS_PASS219_CROSS_MODAL_OK);
    assert(fallback.complete_fallback == 1u);
    assert(fallback.selected_total_work == fallback.baseline_total_work);

    return 0;
}
