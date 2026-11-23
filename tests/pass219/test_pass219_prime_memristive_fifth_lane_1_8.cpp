#include "hhs_pass219_prime_memristive_fifth_lane_1_8.hpp"

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

using namespace hhs::rna;

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed: %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (false)

struct I9UQCELOwners final {
    std::uint8_t P{4U};
    std::uint8_t p{3U};
    std::uint8_t q{5U};
    std::uint8_t delta{1U};
    std::uint8_t A{16U};
    std::uint8_t B{16U};
};

static HHSExactBigUIntView i9_view_of(const std::uint8_t* value) noexcept {
    HHSExactBigUIntView view{};
    view.struct_size = static_cast<std::uint32_t>(sizeof(view));
    view.byte_length = 1U;
    view.bytes_be = value;
    return view;
}

static bool i9_install_root_key() {
    std::string hex;
    hex.reserve(HHS_EXACT_PASS219_VM81_PQC_KEY_HEX_CHARS);
    static constexpr char digits[] = "0123456789abcdef";
    for (std::size_t i = 0U; i < HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES; ++i) {
        const std::uint8_t value = static_cast<std::uint8_t>(i + 1U);
        hex.push_back(digits[(value >> 4U) & 0x0FU]);
        hex.push_back(digits[value & 0x0FU]);
    }
    return setenv(HHS_EXACT_PASS219_VM81_PQC_KEY_ENV, hex.c_str(), 1) == 0;
}

static HHSExactVM81Frame i9_candidate() noexcept {
    HHSExactVM81Frame frame{};
    for (std::size_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        frame.words[i] = UINT64_C(0x0102030405060708) ^ static_cast<std::uint64_t>(i);
    return frame;
}

static HHSExactStatus i9_build_input(
    I9UQCELOwners& owners,
    const HHSExactPass219Hash216TransitionViewV1& parent,
    HHSExactUQCELInputV1& input) noexcept {
    input = HHSExactUQCELInputV1{};
    input.struct_size = static_cast<std::uint32_t>(sizeof(input));
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.P = i9_view_of(&owners.P);
    input.p = i9_view_of(&owners.p);
    input.q = i9_view_of(&owners.q);
    input.delta = i9_view_of(&owners.delta);
    input.A = i9_view_of(&owners.A);
    input.B = i9_view_of(&owners.B);
    input.cell81 = 41U;
    input.left_basis8 = HHS_EXACT_PHASE_X;
    input.right_basis8 = HHS_EXACT_PHASE_Y;
    HHSExactStatus status = hhs_exact_uqcel_source_sha256(input.source_envelope_sha256);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    std::memcpy(input.previous_hash72, parent.receipt_hash72, HHS_EXACT_HASH72_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

static bool same_receipt(
    const PrimeLaneMetabolicReceiptV9& a,
    const PrimeLaneMetabolicReceiptV9& b) noexcept {
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

int main() {
    CHECK(HHS_EXACT_PASS219_HOLO4_LANE_COUNT == 4U);
    CHECK(hhs_pass219_prime_lane_verified_metabolism_authority_valid(
        PrimeLaneVerifiedMetabolismAuthorityV9{}));
    CHECK(i9_install_root_key());

    HHSExactPass219Hash216TransitionViewV1 parent{};
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&parent) == HHS_EXACT_STATUS_OK);
    I9UQCELOwners owners{};
    HHSExactUQCELInputV1 input{};
    CHECK(i9_build_input(owners, parent, input) == HHS_EXACT_STATUS_OK);
    const HHSExactVM81Frame candidate = i9_candidate();

    constexpr std::uint64_t binding = UINT64_C(0x9100000000000001);
    PrimeLaneBudgetedPredictiveHydratorV8 hydrator{};
    CHECK(hydrator.register_budget(binding, 64U, 32U));
    PrimeLaneVerifiedOutcomeMetabolismV9 metabolism{};
    CHECK(metabolism.register_route(binding, 100U));
    PrimeLaneVerifiedOutcomeIssuerV9 issuer{};

    const std::uint32_t algorithm = HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65;
    const bool provider_available =
        hhs_exact_pass219_vm81_pqc_signature_provider_available(algorithm) == 1U;

    HHSExactVM81Frame committed{};
    PrimeLaneVerifiedOutcomeV9 positive{};
    const bool issued_positive = issuer.admit_and_issue(
        220U, algorithm, input, candidate, parent,
        0, 0U, 0U, binding, 1U, 1, committed, positive);

    if (!provider_available) {
        CHECK(!issued_positive);
        PrimeLaneVerifiedOutcomeV9 forged{};
        forged.verdict_signature64 = UINT64_C(0x9101);
        forged.neighborhood_binding_signature64 = binding;
        forged.sequence = 1U;
        forged.admission_feedback_trinary = 1;
        PrimeLaneMetabolicReceiptV9 rejected{};
        CHECK(!issuer.issued(forged));
        CHECK(!metabolism.apply_verified_outcome(issuer, forged, hydrator, rejected));
        CHECK(metabolism.consumed_verdict_count() == 0U);
        std::printf("lane5_i9=PASS provider=unavailable inherited_admission_fail_closed=1\n");
        return 0;
    }

    CHECK(issued_positive);
    CHECK(issuer.issued(positive));
    CHECK(positive.verdict_signature64 == positive.firewall.decision_signature64);
    CHECK(hhs_pass219_prime_lane_verified_outcome_evidence_valid(positive));
    CHECK(std::memcmp(&committed, &candidate, sizeof(committed)) == 0);

    PrimeLaneMetabolicReceiptV9 receipt_1{};
    CHECK(metabolism.apply_verified_outcome(issuer, positive, hydrator, receipt_1));
    CHECK(receipt_1.vitality_before == 100U);
    CHECK(receipt_1.reward_applied == 8U);
    CHECK(receipt_1.vitality_after == 108U);
    CHECK(receipt_1.budget_before == 32U);
    CHECK(receipt_1.budget_credit == 8U);
    CHECK(receipt_1.budget_after == 40U);

    PrimeLaneVerifiedOutcomeV9 forged = positive;
    forged.firewall.pqc_authenticated = 0U;
    PrimeLaneMetabolicReceiptV9 rejected{};
    CHECK(!issuer.issued(forged));
    CHECK(!metabolism.apply_verified_outcome(issuer, forged, hydrator, rejected));
    PrimeLaneVerifiedOutcomeV9 speculative = positive;
    speculative.speculative_only = true;
    CHECK(!issuer.issued(speculative));
    CHECK(!metabolism.apply_verified_outcome(issuer, speculative, hydrator, rejected));
    CHECK(!metabolism.apply_verified_outcome(issuer, positive, hydrator, rejected));

    HHSExactVM81Frame committed_negative{};
    PrimeLaneVerifiedOutcomeV9 negative{};
    CHECK(issuer.admit_and_issue(
        220U, algorithm, input, candidate, parent,
        0, 0U, 0U, binding, 4U, -1, committed_negative, negative));
    CHECK(issuer.issued(negative));
    CHECK(negative.verdict_signature64 != positive.verdict_signature64);

    PrimeLaneMetabolicReceiptV9 receipt_2{};
    CHECK(metabolism.apply_verified_outcome(issuer, negative, hydrator, receipt_2));
    CHECK(receipt_2.vitality_before == 108U);
    CHECK(receipt_2.decay_applied == 2U);
    CHECK(receipt_2.penalty_applied == 12U);
    CHECK(receipt_2.vitality_after == 94U);
    CHECK(receipt_2.budget_after == 40U);

    PrimeLaneMetabolicStateV9 final_state{};
    PrimeLaneActivationBudgetStateV8 final_budget{};
    CHECK(metabolism.state_for(binding, final_state));
    CHECK(hydrator.budget_for(binding, final_budget));
    CHECK(final_state.positive_verified == 1U);
    CHECK(final_state.negative_verified == 1U);
    CHECK(final_state.last_sequence == 4U);
    CHECK(final_state.metabolic_ordinal == 2U);
    CHECK(final_budget.available == 40U);
    CHECK(metabolism.consumed_verdict_count() == 2U);
    CHECK(issuer.issued_count() == 2U);

    PrimeLaneBudgetedPredictiveHydratorV8 replay_hydrator{};
    CHECK(replay_hydrator.register_budget(binding, 64U, 32U));
    PrimeLaneVerifiedOutcomeMetabolismV9 replay_metabolism{};
    CHECK(replay_metabolism.register_route(binding, 100U));
    PrimeLaneMetabolicReceiptV9 replay_1{};
    PrimeLaneMetabolicReceiptV9 replay_2{};
    CHECK(replay_metabolism.apply_verified_outcome(issuer, positive, replay_hydrator, replay_1));
    CHECK(replay_metabolism.apply_verified_outcome(issuer, negative, replay_hydrator, replay_2));
    CHECK(same_receipt(receipt_1, replay_1));
    CHECK(same_receipt(receipt_2, replay_2));

    std::printf(
        "lane5_i9=PASS provider=available issued=%zu verified=%zu vitality=%llu budget=%llu "
        "forged_rejected=1 speculative_rejected=1 duplicate_rejected=1\n",
        issuer.issued_count(), metabolism.consumed_verdict_count(),
        static_cast<unsigned long long>(final_state.vitality),
        static_cast<unsigned long long>(final_budget.available));
    return 0;
}
