#include "hhs_pass219_harmonicode_global_constraint_membrane_1_21_9.hpp"

#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>

int main() {
    using Membrane = hhs::harmonicode::GlobalConstraintMembrane;

    Membrane::EnvironmentRoot root{};
    for (std::size_t i = 0; i < root.size(); ++i)
        root[i] = static_cast<std::uint8_t>(i + 1U);

    Membrane::GateTruth all_true{};
    all_true.fill(true);

    const auto descriptor = Membrane::descriptor();
    assert(descriptor.struct_size == sizeof(descriptor));
    assert(descriptor.ordinary_boolean_equality == 1U);
    assert(descriptor.all_nested_boolean_gates_must_be_true == 1U);
    assert(descriptor.whole_equation_propagates_on_true == 1U);
    assert(descriptor.shared_global_symbol_environment_required == 1U);
    assert(descriptor.cross_layer_variable_effect_required == 1U);
    assert(descriptor.local_symbol_shadowing_authorized == 0U);
    assert(descriptor.pass169_whole_expression_authority_required == 1U);

    const auto accepted = Membrane::evaluate(all_true, root, true, true, false);
    assert(accepted.status == HHS_EXACT_STATUS_OK);
    assert(accepted.propagated());
    assert(accepted.result.all_nested_boolean_gates_true == 1U);
    assert(accepted.result.shared_global_symbol_environment_exact == 1U);
    assert(accepted.result.canonical_monolithic_proof == 0U);
    assert(accepted.result.vm81_mutation_authority == 0U);
    assert(accepted.result.hash72_commit_authority == 0U);

    for (std::size_t i = 0; i < Membrane::kGateCount; ++i) {
        auto one_false = all_true;
        one_false[i] = false;
        const auto rejected = Membrane::evaluate(one_false, root, true, true, false);
        assert(rejected.status == HHS_EXACT_STATUS_OK);
        assert(!rejected.propagated());
        assert(rejected.result.first_false_gate == i);
        assert(rejected.result.all_nested_boolean_gates_true == 0U);
    }

    const auto incomplete_environment =
        Membrane::evaluate(all_true, root, false, true, false);
    assert(incomplete_environment.status == HHS_EXACT_STATUS_OK);
    assert(!incomplete_environment.propagated());

    const auto incomplete_revalidation =
        Membrane::evaluate(all_true, root, true, false, false);
    assert(incomplete_revalidation.status == HHS_EXACT_STATUS_OK);
    assert(!incomplete_revalidation.propagated());

    const auto shadowed = Membrane::evaluate(all_true, root, true, true, true);
    assert(shadowed.status == HHS_EXACT_STATUS_OK);
    assert(!shadowed.propagated());
    assert((shadowed.result.reason_mask &
            HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_LOCAL_SHADOWING_DETECTED) != 0U);

    Membrane::EnvironmentRoot zero_root{};
    const auto missing_root = Membrane::evaluate(all_true, zero_root, true, true, false);
    assert(missing_root.status == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(!missing_root.propagated());

    std::cout << "PASS219 I121.9 C++ Harmonicode global constraint membrane: PASS\n";
    return 0;
}