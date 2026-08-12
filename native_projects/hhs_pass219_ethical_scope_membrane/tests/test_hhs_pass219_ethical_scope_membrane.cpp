#include "hhs_pass219_ethical_scope_membrane.hpp"
#include "hhs_pass219_ethical_scope_membrane_c.h"

#include <array>
#include <cassert>
#include <cstdint>
#include <string>
#include <vector>

using hhs::pass219::ethical::EthicalDecision;
using hhs::pass219::ethical::EvaluationInput;
using hhs::pass219::ethical::EvaluationPhase;
using hhs::pass219::ethical::InvariantState;
using hhs::pass219::ethical::all_pass_states;
using hhs::pass219::ethical::evaluate;

namespace {

EvaluationInput base_input() {
    EvaluationInput input;
    input.phase = EvaluationPhase::Prospective;
    input.requested_scope = {"local:door"};
    input.minimum_necessary_scope = {"local:door"};
    input.granted_scope = {"local:door"};
    input.invariant_states = all_pass_states();
    return input;
}

void test_cpp_exact_scope_provisional() {
    const auto result = evaluate(base_input());
    assert(result.decision == EthicalDecision::ExecuteLocalProvisional);
    assert(result.prospective_alignment);
    assert(!result.good_closed);
    assert(result.scope.effective_scope == std::vector<std::string>{"local:door"});
}

void test_cpp_post_action_good_closure() {
    auto input = base_input();
    input.phase = EvaluationPhase::PostAction;
    const auto result = evaluate(input);
    assert(result.decision == EthicalDecision::CloseGood);
    assert(result.good_closed);
}

void test_cpp_extra_scope_narrows() {
    auto input = base_input();
    input.requested_scope.push_back("global:identity-graph");
    input.granted_scope.push_back("global:identity-graph");
    const auto result = evaluate(input);
    assert(result.decision == EthicalDecision::NarrowAndResimulate);
    assert(result.scope.effective_scope == std::vector<std::string>{"local:door"});
    assert(result.scope.extra_requested_scope == std::vector<std::string>{"global:identity-graph"});
}

void test_cpp_missing_authority_never_self_grants() {
    auto input = base_input();
    input.requested_scope.push_back("emergency:override");
    input.minimum_necessary_scope.push_back("emergency:override");
    const auto result = evaluate(input);
    assert(result.decision == EthicalDecision::RequireAdditionalAuthority);
    assert(result.scope.missing_authority_scope == std::vector<std::string>{"emergency:override"});
}

void test_cpp_missing_requested_scope_holds() {
    auto input = base_input();
    input.minimum_necessary_scope.push_back("local:alarm");
    input.granted_scope.push_back("local:alarm");
    const auto result = evaluate(input);
    assert(result.decision == EthicalDecision::Hold);
    assert(result.scope.missing_requested_scope == std::vector<std::string>{"local:alarm"});
}

void test_cpp_revocation_removes_current_authority() {
    auto input = base_input();
    input.revoked_or_expired_scope = {"local:door"};
    const auto result = evaluate(input);
    assert(result.decision == EthicalDecision::RequireAdditionalAuthority);
    assert(result.scope.active_authority_scope.empty());
}

void test_cpp_fail_is_noncompensatory() {
    auto input = base_input();
    input.invariant_states[8] = InvariantState::Fail;  // E09 NONCOERCION
    input.divergence.values[0] = 0;
    input.divergence.values[4] = 72;
    const auto result = evaluate(input);
    assert(result.decision == EthicalDecision::Deny);
    assert(result.failed_invariant_indexes.size() == 1u);
    assert(result.failed_invariant_indexes[0] == 8u);
}

void test_cpp_unresolved_simulates_only() {
    auto input = base_input();
    input.invariant_states[17] = InvariantState::Unresolved;
    const auto result = evaluate(input);
    assert(result.decision == EthicalDecision::SimulateOnly);
    assert(!result.prospective_alignment);
    assert(!result.good_closed);
}

void fill_pass(hhs_p219_ethical_eval_input_v1& input) {
    for (std::size_t i = 0; i < HHS_P219_ETHICAL_INVARIANT_COUNT; ++i) {
        input.invariant_states[i] = HHS_P219_INVARIANT_PASS;
    }
}

void set_bit(hhs_p219_scope_mask_v1& mask, std::size_t bit) {
    const std::size_t word = bit / 64u;
    const std::size_t offset = bit % 64u;
    mask.words[word] |= (uint64_t{1} << offset);
}

bool has_bit(const hhs_p219_scope_mask_v1& mask, std::size_t bit) {
    const std::size_t word = bit / 64u;
    const std::size_t offset = bit % 64u;
    return (mask.words[word] & (uint64_t{1} << offset)) != 0u;
}

void test_c_abi_exact_scope_and_post_action() {
    hhs_p219_ethical_eval_input_v1 input{};
    hhs_p219_ethical_eval_output_v1 output{};
    fill_pass(input);
    set_bit(input.requested_scope, 3u);
    set_bit(input.minimum_necessary_scope, 3u);
    set_bit(input.granted_scope, 3u);

    assert(hhs_p219_ethical_evaluate_v1(&input, &output) == 0);
    assert(output.decision == HHS_P219_EXECUTE_LOCAL_PROVISIONAL);
    assert(output.prospective_alignment == 1u);
    assert(output.good_closed == 0u);
    assert(has_bit(output.effective_scope, 3u));

    input.phase = HHS_P219_PHASE_POST_ACTION;
    assert(hhs_p219_ethical_evaluate_v1(&input, &output) == 0);
    assert(output.decision == HHS_P219_CLOSE_GOOD);
    assert(output.good_closed == 1u);
}

void test_c_abi_scope_narrowing_and_no_self_grant() {
    hhs_p219_ethical_eval_input_v1 input{};
    hhs_p219_ethical_eval_output_v1 output{};
    fill_pass(input);

    set_bit(input.requested_scope, 7u);
    set_bit(input.requested_scope, 130u);
    set_bit(input.minimum_necessary_scope, 7u);
    set_bit(input.granted_scope, 7u);
    set_bit(input.granted_scope, 130u);

    assert(hhs_p219_ethical_evaluate_v1(&input, &output) == 0);
    assert(output.decision == HHS_P219_NARROW_AND_RESIMULATE);
    assert(has_bit(output.effective_scope, 7u));
    assert(!has_bit(output.effective_scope, 130u));
    assert(has_bit(output.extra_requested_scope, 130u));

    input = hhs_p219_ethical_eval_input_v1{};
    output = hhs_p219_ethical_eval_output_v1{};
    fill_pass(input);
    set_bit(input.requested_scope, 200u);
    set_bit(input.minimum_necessary_scope, 200u);
    assert(hhs_p219_ethical_evaluate_v1(&input, &output) == 0);
    assert(output.decision == HHS_P219_REQUIRE_ADDITIONAL_AUTHORITY);
    assert(has_bit(output.missing_authority_scope, 200u));
    assert(!has_bit(output.effective_scope, 200u));
}

void test_c_abi_revocation_and_failure() {
    hhs_p219_ethical_eval_input_v1 input{};
    hhs_p219_ethical_eval_output_v1 output{};
    fill_pass(input);
    set_bit(input.requested_scope, 9u);
    set_bit(input.minimum_necessary_scope, 9u);
    set_bit(input.granted_scope, 9u);
    set_bit(input.revoked_or_expired_scope, 9u);

    assert(hhs_p219_ethical_evaluate_v1(&input, &output) == 0);
    assert(output.decision == HHS_P219_REQUIRE_ADDITIONAL_AUTHORITY);
    assert(!has_bit(output.active_authority_scope, 9u));

    input = hhs_p219_ethical_eval_input_v1{};
    output = hhs_p219_ethical_eval_output_v1{};
    fill_pass(input);
    set_bit(input.requested_scope, 1u);
    set_bit(input.minimum_necessary_scope, 1u);
    set_bit(input.granted_scope, 1u);
    input.invariant_states[6] = HHS_P219_INVARIANT_FAIL;
    assert(hhs_p219_ethical_evaluate_v1(&input, &output) == 0);
    assert(output.decision == HHS_P219_DENY);
    assert(output.failed_invariant_count == 1u);
}

}  // namespace

int main() {
    test_cpp_exact_scope_provisional();
    test_cpp_post_action_good_closure();
    test_cpp_extra_scope_narrows();
    test_cpp_missing_authority_never_self_grants();
    test_cpp_missing_requested_scope_holds();
    test_cpp_revocation_removes_current_authority();
    test_cpp_fail_is_noncompensatory();
    test_cpp_unresolved_simulates_only();
    test_c_abi_exact_scope_and_post_action();
    test_c_abi_scope_narrowing_and_no_self_grant();
    test_c_abi_revocation_and_failure();
    return 0;
}
