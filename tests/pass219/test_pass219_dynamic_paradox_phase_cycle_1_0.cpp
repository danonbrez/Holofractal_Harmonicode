#include "hhs_pass219_dynamic_paradox_phase_cycle_1_0.hpp"

#include <cassert>

int main() {
    HHSExactPass219ParadoxProblemV1 problem{};
    problem.version = HHS_EXACT_PASS219_PARADOX_VERSION;
    problem.option_count = 4U;
    problem.seed_option_index = 1U;
    problem.permit_meta_closure = 1U;
    problem.declared_visit_bound = 6U;
    problem.options[0] = {1U, 4U};
    problem.options[1] = {0U, 1U};
    problem.options[2] = {1U, 2U};
    problem.options[3] = {1U, 4U};

    HHSExactPass219ParadoxWitnessV1 witness{};
    assert(
        hhs::pass219::DynamicParadoxPhaseCycle::analyze(problem, witness) ==
        HHS_EXACT_PASS219_PARADOX_OK
    );
    assert(witness.object_has_fixed_point == 0U);
    assert(witness.preperiod == 1U);
    assert(witness.period == 2U);
    assert(witness.meta_empty_valid_set == 1U);
    assert(hhs::pass219::DynamicParadoxPhaseCycle::validate(problem, witness));

    HHSExactPass219H36ClosureWitnessV1 h36{};
    assert(hhs::pass219::DynamicParadoxPhaseCycle::h36(h36));
    assert(h36.h36_value == 36U);
    assert(h36.lhs_value == h36.rhs_value);
    assert(h36.manifold_cardinality == UINT64_C(722204136308736));
    return 0;
}
