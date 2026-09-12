#include "hhs_pass219_prime_memristive_fifth_lane_1_8.hpp"

#include <cstdio>
#include <cstring>

using namespace hhs::rna;

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed: %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (false)

static bool same_receipt(
    const PrimeLaneMetabolicReceiptV9& a,
    const PrimeLaneMetabolicReceiptV9& b) {
    return a.verdict_signature64 == b.verdict_signature64 &&
           a.neighborhood_binding_signature64 == b.neighborhood_binding_signature64 &&
           a.sequence == b.sequence &&
           a.admission_feedback_trinary == b.admission_feedback_trinary &&
           a.vitality_before == b.vitality_before &&
           a.decay_applied == b.decay_applied &&
           a.reward_applied == b.reward_applied &&
           a.penalty_applied == b.penalty_applied &&
           a.vitality_after == b.vitality_after &&
           a.budget_before == b.budget_before &&
           a.budget_credit == b.budget_credit &&
           a.budget_after == b.budget_after &&
           a.metabolic_ordinal == b.metabolic_ordinal;
}

static PrimeLaneVerifiedOutcomeV9 outcome(
    std::uint64_t verdict,
    std::uint64_t binding,
    std::uint64_t sequence,
    std::int8_t feedback,
    bool verified = true,
    bool speculative = false) {
    PrimeLaneVerifiedOutcomeV9 out{};
    out.verdict_signature64 = verdict;
    out.neighborhood_binding_signature64 = binding;
    out.sequence = sequence;
    out.admission_feedback_trinary = feedback;
    out.vm81_hash216_verified = verified;
    out.speculative_only = speculative;
    return out;
}

int main() {
    CHECK(HHS_EXACT_PASS219_HOLO4_LANE_COUNT == 4U);
    CHECK(hhs_pass219_prime_lane_verified_metabolism_authority_valid(
        PrimeLaneVerifiedMetabolismAuthorityV9{}));
    CHECK(HHS_PASS219_PRIME_LANE_METABOLIC_REWARD == 8U);
    CHECK(HHS_PASS219_PRIME_LANE_METABOLIC_PENALTY == 12U);
    CHECK(HHS_PASS219_PRIME_LANE_METABOLIC_BUDGET_CREDIT == 8U);

    HHSExactPass219Holo4StateV1 holo4_state{};
    CHECK(hhs_exact_pass219_holo4_state_init(&holo4_state) == HHS_EXACT_STATUS_OK);
    const HHSExactPass219Holo4StateV1 frozen_holo4_state = holo4_state;

    constexpr std::uint64_t binding = UINT64_C(0x9100000000000001);
    PrimeLaneBudgetedPredictiveHydratorV8 hydrator{};
    CHECK(hydrator.register_budget(binding, 64U, 32U));
    PrimeLaneVerifiedOutcomeMetabolismV9 metabolism{};
    CHECK(metabolism.register_route(binding, 100U));

    PrimeLaneActivationBudgetStateV8 initial_budget{};
    PrimeLaneMetabolicStateV9 initial_state{};
    CHECK(hydrator.budget_for(binding, initial_budget));
    CHECK(metabolism.state_for(binding, initial_state));
    CHECK(initial_budget.available == 32U);
    CHECK(initial_state.vitality == 100U);

    PrimeLaneMetabolicReceiptV9 rejected{};
    CHECK(!metabolism.apply_verified_outcome(
        outcome(UINT64_C(0x9001), binding, 1U, 1, true, true),
        hydrator, rejected));
    CHECK(!metabolism.apply_verified_outcome(
        outcome(UINT64_C(0x9002), binding, 1U, 1, false, false),
        hydrator, rejected));
    PrimeLaneActivationBudgetStateV8 after_rejected_budget{};
    PrimeLaneMetabolicStateV9 after_rejected_state{};
    CHECK(hydrator.budget_for(binding, after_rejected_budget));
    CHECK(metabolism.state_for(binding, after_rejected_state));
    CHECK(after_rejected_budget.available == initial_budget.available);
    CHECK(after_rejected_state.vitality == initial_state.vitality);
    CHECK(metabolism.consumed_verdict_count() == 0U);

    const PrimeLaneVerifiedOutcomeV9 positive_1 =
        outcome(UINT64_C(0x9101), binding, 1U, 1);
    PrimeLaneMetabolicReceiptV9 receipt_1{};
    CHECK(metabolism.apply_verified_outcome(positive_1, hydrator, receipt_1));
    CHECK(receipt_1.vitality_before == 100U);
    CHECK(receipt_1.decay_applied == 0U);
    CHECK(receipt_1.reward_applied == 8U);
    CHECK(receipt_1.penalty_applied == 0U);
    CHECK(receipt_1.vitality_after == 108U);
    CHECK(receipt_1.budget_before == 32U);
    CHECK(receipt_1.budget_credit == 8U);
    CHECK(receipt_1.budget_after == 40U);
    CHECK(receipt_1.metabolic_ordinal == 1U);
    CHECK(metabolism.verdict_consumed(UINT64_C(0x9101)));

    PrimeLaneMetabolicStateV9 before_duplicate{};
    PrimeLaneActivationBudgetStateV8 before_duplicate_budget{};
    CHECK(metabolism.state_for(binding, before_duplicate));
    CHECK(hydrator.budget_for(binding, before_duplicate_budget));
    CHECK(!metabolism.apply_verified_outcome(positive_1, hydrator, rejected));
    CHECK(!metabolism.apply_verified_outcome(
        outcome(UINT64_C(0x9102), binding, 1U, 1), hydrator, rejected));
    PrimeLaneMetabolicStateV9 after_duplicate{};
    PrimeLaneActivationBudgetStateV8 after_duplicate_budget{};
    CHECK(metabolism.state_for(binding, after_duplicate));
    CHECK(hydrator.budget_for(binding, after_duplicate_budget));
    CHECK(after_duplicate.vitality == before_duplicate.vitality);
    CHECK(after_duplicate.metabolic_ordinal == before_duplicate.metabolic_ordinal);
    CHECK(after_duplicate_budget.available == before_duplicate_budget.available);

    const PrimeLaneVerifiedOutcomeV9 positive_gap =
        outcome(UINT64_C(0x9103), binding, 4U, 1);
    PrimeLaneMetabolicReceiptV9 receipt_2{};
    CHECK(metabolism.apply_verified_outcome(positive_gap, hydrator, receipt_2));
    CHECK(receipt_2.vitality_before == 108U);
    CHECK(receipt_2.decay_applied == 2U);
    CHECK(receipt_2.reward_applied == 8U);
    CHECK(receipt_2.vitality_after == 114U);
    CHECK(receipt_2.budget_before == 40U);
    CHECK(receipt_2.budget_credit == 8U);
    CHECK(receipt_2.budget_after == 48U);

    const PrimeLaneVerifiedOutcomeV9 negative =
        outcome(UINT64_C(0x9104), binding, 5U, -1);
    PrimeLaneMetabolicReceiptV9 receipt_3{};
    CHECK(metabolism.apply_verified_outcome(negative, hydrator, receipt_3));
    CHECK(receipt_3.decay_applied == 0U);
    CHECK(receipt_3.reward_applied == 0U);
    CHECK(receipt_3.penalty_applied == 12U);
    CHECK(receipt_3.vitality_before == 114U);
    CHECK(receipt_3.vitality_after == 102U);
    CHECK(receipt_3.budget_before == 48U);
    CHECK(receipt_3.budget_credit == 0U);
    CHECK(receipt_3.budget_after == 48U);

    const PrimeLaneVerifiedOutcomeV9 negative_gap =
        outcome(UINT64_C(0x9105), binding, 30U, -1);
    PrimeLaneMetabolicReceiptV9 receipt_4{};
    CHECK(metabolism.apply_verified_outcome(negative_gap, hydrator, receipt_4));
    CHECK(receipt_4.decay_applied == 16U);
    CHECK(receipt_4.penalty_applied == 12U);
    CHECK(receipt_4.vitality_before == 102U);
    CHECK(receipt_4.vitality_after == 74U);
    CHECK(receipt_4.budget_credit == 0U);
    CHECK(receipt_4.budget_after == 48U);

    PrimeLaneMetabolicStateV9 final_state{};
    PrimeLaneActivationBudgetStateV8 final_budget{};
    CHECK(metabolism.state_for(binding, final_state));
    CHECK(hydrator.budget_for(binding, final_budget));
    CHECK(final_state.positive_verified == 2U);
    CHECK(final_state.negative_verified == 2U);
    CHECK(final_state.budget_credit_total == 16U);
    CHECK(final_state.decay_total == 18U);
    CHECK(final_state.last_sequence == 30U);
    CHECK(final_state.metabolic_ordinal == 4U);
    CHECK(final_budget.available == 48U);
    CHECK(metabolism.consumed_verdict_count() == 4U);

    PrimeLaneBudgetedPredictiveHydratorV8 replay_hydrator{};
    CHECK(replay_hydrator.register_budget(binding, 64U, 32U));
    PrimeLaneVerifiedOutcomeMetabolismV9 replay_metabolism{};
    CHECK(replay_metabolism.register_route(binding, 100U));
    PrimeLaneMetabolicReceiptV9 replay_1{};
    PrimeLaneMetabolicReceiptV9 replay_2{};
    PrimeLaneMetabolicReceiptV9 replay_3{};
    PrimeLaneMetabolicReceiptV9 replay_4{};
    CHECK(replay_metabolism.apply_verified_outcome(positive_1, replay_hydrator, replay_1));
    CHECK(replay_metabolism.apply_verified_outcome(positive_gap, replay_hydrator, replay_2));
    CHECK(replay_metabolism.apply_verified_outcome(negative, replay_hydrator, replay_3));
    CHECK(replay_metabolism.apply_verified_outcome(negative_gap, replay_hydrator, replay_4));
    CHECK(same_receipt(receipt_1, replay_1));
    CHECK(same_receipt(receipt_2, replay_2));
    CHECK(same_receipt(receipt_3, replay_3));
    CHECK(same_receipt(receipt_4, replay_4));

    constexpr std::uint64_t capped_binding = UINT64_C(0x9100000000000002);
    PrimeLaneBudgetedPredictiveHydratorV8 cap_hydrator{};
    CHECK(cap_hydrator.register_budget(capped_binding, 64U, 64U));
    PrimeLaneVerifiedOutcomeMetabolismV9 cap_metabolism{};
    CHECK(cap_metabolism.register_route(capped_binding, 252U));
    PrimeLaneMetabolicReceiptV9 cap_receipt{};
    CHECK(cap_metabolism.apply_verified_outcome(
        outcome(UINT64_C(0x9201), capped_binding, 1U, 1), cap_hydrator, cap_receipt));
    CHECK(cap_receipt.reward_applied == 4U);
    CHECK(cap_receipt.vitality_after == 256U);
    CHECK(cap_receipt.budget_credit == 0U);
    CHECK(cap_receipt.budget_before == 64U && cap_receipt.budget_after == 64U);

    CHECK(std::memcmp(&holo4_state, &frozen_holo4_state, sizeof(holo4_state)) == 0);

    std::printf(
        "lane5_i9=PASS verified=%zu vitality=%llu budget=%llu positive=%llu negative=%llu "
        "decay=%llu credit=%llu duplicate_rejected=1 speculative_rejected=1 unverified_rejected=1 "
        "replay_receipts=4 capped_vitality=%llu capped_budget=%llu\n",
        metabolism.consumed_verdict_count(),
        static_cast<unsigned long long>(final_state.vitality),
        static_cast<unsigned long long>(final_budget.available),
        static_cast<unsigned long long>(final_state.positive_verified),
        static_cast<unsigned long long>(final_state.negative_verified),
        static_cast<unsigned long long>(final_state.decay_total),
        static_cast<unsigned long long>(final_state.budget_credit_total),
        static_cast<unsigned long long>(cap_receipt.vitality_after),
        static_cast<unsigned long long>(cap_receipt.budget_after));
    return 0;
}
