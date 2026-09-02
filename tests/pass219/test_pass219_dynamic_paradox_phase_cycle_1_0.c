#include "hhs_pass219_dynamic_paradox_phase_cycle_1_0.h"

#include <assert.h>
#include <string.h>

static HHSExactPass219ParadoxProblemV1 canonical_problem(void) {
    HHSExactPass219ParadoxProblemV1 problem;
    memset(&problem, 0, sizeof(problem));
    problem.version = HHS_EXACT_PASS219_PARADOX_VERSION;
    problem.option_count = 4U;
    problem.seed_option_index = 1U;
    problem.permit_meta_closure = 1U;
    problem.promote_meta_zero_to_object_correct = 0U;
    problem.declared_visit_bound = 6U;
    problem.options[0].numerator = 1U;
    problem.options[0].denominator = 4U;
    problem.options[1].numerator = 0U;
    problem.options[1].denominator = 1U;
    problem.options[2].numerator = 1U;
    problem.options[2].denominator = 2U;
    problem.options[3].numerator = 1U;
    problem.options[3].denominator = 4U;
    return problem;
}

int main(void) {
    HHSExactPass219ParadoxProblemV1 problem = canonical_problem();
    HHSExactPass219ParadoxWitnessV1 witness;
    HHSExactPass219H36ClosureWitnessV1 h36;

    assert(hhs_exact_pass219_paradox_analyze(&problem, &witness) ==
           HHS_EXACT_PASS219_PARADOX_OK);
    assert(witness.object_has_fixed_point == 0U);
    assert(witness.object_valid_option_count == 0U);
    assert(witness.seed_option_object_correct == 0U);
    assert(witness.cycle_detected == 1U);
    assert(witness.fixed_point_reached == 0U);
    assert(witness.preperiod == 1U);
    assert(witness.period == 2U);
    assert(witness.trajectory_count == 4U);
    assert(witness.finite_visit_bound == 6U);
    assert(witness.meta_empty_valid_set == 1U);
    assert(witness.meta_probability_zero == 1U);
    assert(witness.meta_probability.numerator == 0U);
    assert(witness.meta_probability.denominator == 1U);
    assert(witness.seed_candidate_trinary == -1);
    assert(witness.cycle_motion_trinary == 1);
    assert(witness.meta_closure_trinary == 0);
    assert(witness.typed_level_separation_preserved == 1U);
    assert(witness.bounded_closure == 1U);
    assert(witness.ordered_trajectory_preserved == 1U);
    assert(witness.canonical_mutation_authority == 0U);
    assert(witness.canonical_hash72_authority == 0U);
    assert(witness.canonical_persistence_authority == 0U);
    assert(witness.floating_point_authority == 0U);

    assert(witness.trajectory[0].numerator == 0U);
    assert(witness.trajectory[0].denominator == 1U);
    assert(witness.trajectory[1].numerator == 1U);
    assert(witness.trajectory[1].denominator == 4U);
    assert(witness.trajectory[2].numerator == 1U);
    assert(witness.trajectory[2].denominator == 2U);
    assert(witness.trajectory[3].numerator == 1U);
    assert(witness.trajectory[3].denominator == 4U);

    assert(hhs_exact_pass219_paradox_witness_validate(&problem, &witness) ==
           HHS_EXACT_PASS219_PARADOX_OK);
    witness.trajectory[2].numerator = 3U;
    witness.trajectory[2].denominator = 4U;
    assert(hhs_exact_pass219_paradox_witness_validate(&problem, &witness) ==
           HHS_EXACT_PASS219_PARADOX_WITNESS_ERROR);

    problem = canonical_problem();
    problem.promote_meta_zero_to_object_correct = 1U;
    assert(hhs_exact_pass219_paradox_analyze(&problem, &witness) ==
           HHS_EXACT_PASS219_PARADOX_TYPE_LEVEL_CONFLATION);

    problem = canonical_problem();
    problem.declared_visit_bound = 5U;
    assert(hhs_exact_pass219_paradox_analyze(&problem, &witness) ==
           HHS_EXACT_PASS219_PARADOX_BOUND_ERROR);

    problem = canonical_problem();
    problem.options[2].denominator = 0U;
    assert(hhs_exact_pass219_paradox_analyze(&problem, &witness) ==
           HHS_EXACT_PASS219_PARADOX_DENOMINATOR_ZERO);

    assert(hhs_exact_pass219_h36_closure_identity(&h36) ==
           HHS_EXACT_PASS219_PARADOX_OK);
    assert(h36.a2 == 1U);
    assert(h36.b2 == 2U);
    assert(h36.c2 == 3U);
    assert(h36.b4 == 4U);
    assert(h36.b6 == 8U);
    assert(h36.c4 == 9U);
    assert(h36.denominator == 2U);
    assert(h36.lhs_numerator == 72U);
    assert(h36.lhs_denominator == 2U);
    assert(h36.lhs_value == 36U);
    assert(h36.rhs_value == 36U);
    assert(h36.h36_value == 36U);
    assert(h36.manifold_base == 5184U);
    assert(h36.manifold_power == 4U);
    assert(h36.manifold_cardinality == UINT64_C(722204136308736));
    assert(h36.identity_equal == 1U);
    assert(h36.manifold_cardinality_equal == 1U);
    assert(h36.canonical_mutation_authority == 0U);
    assert(h36.canonical_hash72_authority == 0U);
    assert(h36.canonical_persistence_authority == 0U);
    assert(h36.floating_point_authority == 0U);
    assert(hhs_exact_pass219_h36_closure_identity_validate(&h36) ==
           HHS_EXACT_PASS219_PARADOX_OK);

    h36.h36_value = 35U;
    assert(hhs_exact_pass219_h36_closure_identity_validate(&h36) ==
           HHS_EXACT_PASS219_PARADOX_WITNESS_ERROR);

    return 0;
}
