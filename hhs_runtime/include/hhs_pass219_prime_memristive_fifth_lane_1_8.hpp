#ifndef HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_8_HPP
#define HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_8_HPP

#include "hhs_pass219_prime_memristive_fifth_lane_1_7.hpp"
#include "hhs_pass219_vm81_environmental_recovery_1_32.h"

#include <algorithm>
#include <cstdint>
#include <cstring>
#include <limits>
#include <map>
#include <set>

namespace hhs::rna {

inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_VERIFIED_METABOLISM_VERSION = UINT32_C(0x00010008);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_METABOLIC_VITALITY_CAP = UINT64_C(256);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_METABOLIC_REWARD = UINT64_C(8);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_METABOLIC_PENALTY = UINT64_C(12);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_METABOLIC_BUDGET_CREDIT = UINT64_C(8);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_METABOLIC_DECAY_QUANTUM = UINT64_C(1);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_METABOLIC_DECAY_STEP_LIMIT = UINT64_C(16);
inline constexpr std::size_t HHS_PASS219_PRIME_LANE_VERIFIED_OUTCOME_ISSUANCE_LIMIT = 1024U;

struct PrimeLaneVerifiedMetabolismAuthorityV9 final {
    bool candidate_only{true};
    bool exact_integer_only{true};
    bool verified_outcome_only{true};
    bool speculative_reinforcement{false};
    bool local_metabolic_state_only{true};
    bool budget_replenishment_only{true};
    bool bounded_decay_only{true};
    bool duplicate_verdict_replay{false};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
    bool requires_inherited_vm81_hash216_admission{true};
};

constexpr bool hhs_pass219_prime_lane_verified_metabolism_authority_valid(
    const PrimeLaneVerifiedMetabolismAuthorityV9& authority) noexcept {
    return authority.candidate_only && authority.exact_integer_only &&
           authority.verified_outcome_only && !authority.speculative_reinforcement &&
           authority.local_metabolic_state_only && authority.budget_replenishment_only &&
           authority.bounded_decay_only && !authority.duplicate_verdict_replay &&
           !authority.canonical_mutation_authority &&
           !authority.canonical_hash72_authority &&
           !authority.canonical_hash216_authority &&
           !authority.canonical_persistence_authority &&
           !authority.floating_point_authority &&
           authority.requires_inherited_vm81_hash216_admission;
}

struct PrimeLaneVerifiedOutcomeV9 final {
    std::uint64_t verdict_signature64{};
    std::uint64_t neighborhood_binding_signature64{};
    std::uint64_t sequence{};
    std::int8_t admission_feedback_trinary{};
    HHSExactPass219RNAAdmissionV1 admission{};
    HHSExactPass219VM81PQCFirewallReceiptV1 firewall{};
    HHSExactPass219VM81PQCSignatureReceiptV1 pqc_signature{};
    HHSExactPass219VM81EnvironmentReceiptV1 environment{};
    bool speculative_only{};
};

inline bool hhs_pass219_prime_lane_verified_outcome_evidence_valid(
    const PrimeLaneVerifiedOutcomeV9& event) noexcept {
    const auto& firewall = event.firewall;
    const auto& signature = event.pqc_signature;
    const auto& environment = event.environment;
    const auto& transition = event.admission.transition;

    if (event.verdict_signature64 == 0U ||
        event.neighborhood_binding_signature64 == 0U ||
        event.sequence == 0U ||
        (event.admission_feedback_trinary != 1 && event.admission_feedback_trinary != -1) ||
        event.speculative_only)
        return false;

    if (firewall.struct_size != sizeof(firewall) ||
        firewall.version != HHS_EXACT_PASS219_VM81_PQC_VERSION ||
        firewall.pass_number < HHS_EXACT_PASS219_VM81_PQC_MIN_PASS ||
        firewall.decision != HHS_EXACT_PASS219_VM81_PQC_DECISION_COMMITTED ||
        firewall.halt_reason != HHS_EXACT_PASS219_VM81_PQC_HALT_NONE ||
        firewall.halted != 0U || firewall.pqc_authenticated != 1U ||
        firewall.parent_hash216_verified != 1U || firewall.child_hash216_verified != 1U ||
        firewall.rna_cell_wall_routed != 1U ||
        firewall.inherited_rna_authority_invoked != 1U ||
        firewall.canonical_receipt_owned_by_inherited_authority != 1U ||
        firewall.firewall_is_canonical_authority != 0U ||
        firewall.decision_signature64 == 0U ||
        event.verdict_signature64 != firewall.decision_signature64)
        return false;

    auto bytes_nonzero = [](const std::uint8_t* bytes, std::size_t length) noexcept {
        if (bytes == nullptr || length == 0U)
            return false;
        std::uint8_t aggregate = 0U;
        for (std::size_t i = 0U; i < length; ++i)
            aggregate = static_cast<std::uint8_t>(aggregate | bytes[i]);
        return aggregate != 0U;
    };

    if (signature.struct_size != sizeof(signature) ||
        signature.version != HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERSION ||
        (signature.algorithm != HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65 &&
         signature.algorithm != HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_SLH_DSA_SHA2_192S) ||
        signature.decision != HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERIFIED ||
        signature.signature_length == 0U || signature.provider_available != 1U ||
        signature.key_derived_from_kernel_root != 1U ||
        signature.signature_generated_inside_kernel != 1U ||
        signature.signature_verified_before_vm81 != 1U ||
        signature.external_key_authority != 0U ||
        signature.external_signature_authority != 0U ||
        signature.signature_is_canonical_receipt != 0U ||
        !bytes_nonzero(signature.signed_message_sha256, sizeof(signature.signed_message_sha256)) ||
        !bytes_nonzero(signature.signature_sha256, sizeof(signature.signature_sha256)))
        return false;

    if (environment.struct_size != sizeof(environment) ||
        environment.version != HHS_EXACT_PASS219_VM81_ENV_VERSION ||
        environment.state != HHS_EXACT_PASS219_VM81_ENV_STATE_RUNNING ||
        environment.decision != HHS_EXACT_PASS219_VM81_ENV_DECISION_READY ||
        environment.reason != HHS_EXACT_PASS219_VM81_ENV_REASON_NONE ||
        environment.signature_algorithm != signature.algorithm ||
        environment.security_epoch != HHS_EXACT_PASS219_VM81_ENV_SECURITY_EPOCH ||
        environment.witness_sequence == 0U ||
        environment.genesis_verified != 1U || environment.witness_verified != 1U ||
        environment.environment_signature_verified != 1U ||
        environment.recovery_candidate_only != 1U ||
        environment.canonical_mutation_authority != 0U ||
        environment.canonical_receipt_authority != 0U ||
        !bytes_nonzero(environment.witness_sha256, sizeof(environment.witness_sha256)) ||
        !bytes_nonzero(environment.environment_signature_sha256,
                       sizeof(environment.environment_signature_sha256)))
        return false;

    if (transition.struct_size != sizeof(transition) ||
        hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&transition) != HHS_EXACT_STATUS_OK ||
        std::memcmp(firewall.child_hash216_identity,
                    transition.transition_identity216,
                    HHS_EXACT_UQCEL_HASH216_STRLEN) != 0)
        return false;

    return true;
}

class PrimeLaneVerifiedOutcomeIssuerV9 final {
public:
    bool admit_and_issue(
        std::uint32_t pass_number,
        std::uint32_t signature_algorithm,
        const HHSExactUQCELInputV1& input,
        const HHSExactVM81Frame& candidate_frame,
        const HHSExactPass219Hash216TransitionViewV1& parent_hash216_reference,
        std::int8_t lo_shu_group,
        std::uint16_t g243,
        std::uint8_t feedback_lane,
        std::uint64_t neighborhood_binding_signature64,
        std::uint64_t metabolic_sequence,
        std::int8_t admission_feedback_trinary,
        HHSExactVM81Frame& out_committed_frame,
        PrimeLaneVerifiedOutcomeV9& out) {
        out = PrimeLaneVerifiedOutcomeV9{};
        out_committed_frame = HHSExactVM81Frame{};
        if (neighborhood_binding_signature64 == 0U || metabolic_sequence == 0U ||
            (admission_feedback_trinary != 1 && admission_feedback_trinary != -1) ||
            issued_.size() >= HHS_PASS219_PRIME_LANE_VERIFIED_OUTCOME_ISSUANCE_LIMIT)
            return false;

        HHSExactPass219RNAAdmissionV1 admission{};
        HHSExactPass219VM81PQCFirewallReceiptV1 firewall{};
        HHSExactPass219VM81PQCSignatureReceiptV1 signature{};
        HHSExactPass219VM81EnvironmentReceiptV1 environment{};
        const HHSExactStatus status = hhs_exact_pass219_vm81_environment_admit_signed(
            pass_number,
            signature_algorithm,
            &input,
            &candidate_frame,
            &parent_hash216_reference,
            lo_shu_group,
            g243,
            feedback_lane,
            admission_feedback_trinary,
            &out_committed_frame,
            &admission,
            &firewall,
            &signature,
            &environment);
        if (status != HHS_EXACT_STATUS_OK)
            return false;

        out.verdict_signature64 = firewall.decision_signature64;
        out.neighborhood_binding_signature64 = neighborhood_binding_signature64;
        out.sequence = metabolic_sequence;
        out.admission_feedback_trinary = admission_feedback_trinary;
        out.admission = admission;
        out.firewall = firewall;
        out.pqc_signature = signature;
        out.environment = environment;
        out.speculative_only = false;
        if (!hhs_pass219_prime_lane_verified_outcome_evidence_valid(out))
            return false;

        const auto [it, inserted] = issued_.emplace(out.verdict_signature64, out);
        if (!inserted && !same_outcome(it->second, out))
            return false;
        return true;
    }

    bool issued(const PrimeLaneVerifiedOutcomeV9& event) const noexcept {
        if (!hhs_pass219_prime_lane_verified_outcome_evidence_valid(event))
            return false;
        const auto it = issued_.find(event.verdict_signature64);
        return it != issued_.end() && same_outcome(it->second, event);
    }

    std::size_t issued_count() const noexcept { return issued_.size(); }

private:
    static bool same_outcome(
        const PrimeLaneVerifiedOutcomeV9& a,
        const PrimeLaneVerifiedOutcomeV9& b) noexcept {
        return a.verdict_signature64 == b.verdict_signature64 &&
               a.neighborhood_binding_signature64 == b.neighborhood_binding_signature64 &&
               a.sequence == b.sequence &&
               a.admission_feedback_trinary == b.admission_feedback_trinary &&
               a.speculative_only == b.speculative_only &&
               std::memcmp(&a.admission, &b.admission, sizeof(a.admission)) == 0 &&
               std::memcmp(&a.firewall, &b.firewall, sizeof(a.firewall)) == 0 &&
               std::memcmp(&a.pqc_signature, &b.pqc_signature, sizeof(a.pqc_signature)) == 0 &&
               std::memcmp(&a.environment, &b.environment, sizeof(a.environment)) == 0;
    }

    std::map<std::uint64_t, PrimeLaneVerifiedOutcomeV9> issued_{};
};

struct PrimeLaneMetabolicStateV9 final {
    std::uint64_t neighborhood_binding_signature64{};
    std::uint64_t vitality_capacity{HHS_PASS219_PRIME_LANE_METABOLIC_VITALITY_CAP};
    std::uint64_t vitality{};
    std::uint64_t positive_verified{};
    std::uint64_t negative_verified{};
    std::uint64_t budget_credit_total{};
    std::uint64_t decay_total{};
    std::uint64_t last_sequence{};
    std::uint64_t metabolic_ordinal{};
    PrimeLaneVerifiedMetabolismAuthorityV9 authority{};
};

struct PrimeLaneMetabolicReceiptV9 final {
    std::uint64_t verdict_signature64{};
    std::uint64_t neighborhood_binding_signature64{};
    std::uint64_t sequence{};
    std::int8_t admission_feedback_trinary{};
    std::uint64_t vitality_before{};
    std::uint64_t decay_applied{};
    std::uint64_t reward_applied{};
    std::uint64_t penalty_applied{};
    std::uint64_t vitality_after{};
    std::uint64_t budget_before{};
    std::uint64_t budget_credit{};
    std::uint64_t budget_after{};
    std::uint64_t metabolic_ordinal{};
    PrimeLaneVerifiedMetabolismAuthorityV9 authority{};
};

class PrimeLaneVerifiedOutcomeMetabolismV9 final {
public:
    bool register_route(
        std::uint64_t neighborhood_binding_signature64,
        std::uint64_t initial_vitality) {
        if (neighborhood_binding_signature64 == 0U ||
            initial_vitality > HHS_PASS219_PRIME_LANE_METABOLIC_VITALITY_CAP ||
            states_.find(neighborhood_binding_signature64) != states_.end())
            return false;
        PrimeLaneMetabolicStateV9 state{};
        state.neighborhood_binding_signature64 = neighborhood_binding_signature64;
        state.vitality = initial_vitality;
        states_.emplace(neighborhood_binding_signature64, state);
        return hhs_pass219_prime_lane_verified_metabolism_authority_valid(state.authority);
    }

    bool state_for(
        std::uint64_t neighborhood_binding_signature64,
        PrimeLaneMetabolicStateV9& out) const {
        out = PrimeLaneMetabolicStateV9{};
        const auto it = states_.find(neighborhood_binding_signature64);
        if (it == states_.end())
            return false;
        out = it->second;
        return true;
    }

    bool apply_verified_outcome(
        const PrimeLaneVerifiedOutcomeIssuerV9& issuer,
        const PrimeLaneVerifiedOutcomeV9& event,
        PrimeLaneBudgetedPredictiveHydratorV8& hydrator,
        PrimeLaneMetabolicReceiptV9& out) {
        out = PrimeLaneMetabolicReceiptV9{};
        if (!issuer.issued(event) ||
            consumed_verdicts_.find(event.verdict_signature64) != consumed_verdicts_.end())
            return false;

        auto state_it = states_.find(event.neighborhood_binding_signature64);
        if (state_it == states_.end())
            return false;
        const auto& prior = state_it->second;
        if (event.sequence <= prior.last_sequence)
            return false;

        PrimeLaneActivationBudgetStateV8 budget{};
        if (!hydrator.budget_for(event.neighborhood_binding_signature64, budget))
            return false;
        if (!hhs_pass219_prime_lane_budgeted_hydration_authority_valid(budget.authority))
            return false;

        PrimeLaneMetabolicStateV9 next = prior;
        out.verdict_signature64 = event.verdict_signature64;
        out.neighborhood_binding_signature64 = event.neighborhood_binding_signature64;
        out.sequence = event.sequence;
        out.admission_feedback_trinary = event.admission_feedback_trinary;
        out.vitality_before = prior.vitality;
        out.budget_before = budget.available;

        const std::uint64_t gap_steps = decay_steps(prior.last_sequence, event.sequence);
        const std::uint64_t requested_decay = gap_steps * HHS_PASS219_PRIME_LANE_METABOLIC_DECAY_QUANTUM;
        out.decay_applied = std::min(next.vitality, requested_decay);
        next.vitality -= out.decay_applied;
        if (out.decay_applied > std::numeric_limits<std::uint64_t>::max() - next.decay_total)
            return false;
        next.decay_total += out.decay_applied;

        if (event.admission_feedback_trinary == 1) {
            const std::uint64_t room = next.vitality_capacity - next.vitality;
            out.reward_applied = std::min(room, HHS_PASS219_PRIME_LANE_METABOLIC_REWARD);
            next.vitality += out.reward_applied;
            if (next.positive_verified == std::numeric_limits<std::uint64_t>::max())
                return false;
            ++next.positive_verified;

            const std::uint64_t budget_room = budget.capacity - budget.available;
            out.budget_credit = std::min(budget_room, HHS_PASS219_PRIME_LANE_METABOLIC_BUDGET_CREDIT);
            if (out.budget_credit != 0U) {
                if (out.budget_credit > std::numeric_limits<std::uint64_t>::max() - next.budget_credit_total)
                    return false;
                if (!hydrator.replenish_budget(event.neighborhood_binding_signature64, out.budget_credit))
                    return false;
                next.budget_credit_total += out.budget_credit;
            }
        } else {
            out.penalty_applied = std::min(next.vitality, HHS_PASS219_PRIME_LANE_METABOLIC_PENALTY);
            next.vitality -= out.penalty_applied;
            if (next.negative_verified == std::numeric_limits<std::uint64_t>::max())
                return false;
            ++next.negative_verified;
        }

        if (next.metabolic_ordinal == std::numeric_limits<std::uint64_t>::max())
            return false;
        ++next.metabolic_ordinal;
        next.last_sequence = event.sequence;
        out.vitality_after = next.vitality;
        out.metabolic_ordinal = next.metabolic_ordinal;

        PrimeLaneActivationBudgetStateV8 budget_after{};
        if (!hydrator.budget_for(event.neighborhood_binding_signature64, budget_after))
            return false;
        out.budget_after = budget_after.available;
        if (out.budget_after - out.budget_before != out.budget_credit)
            return false;

        state_it->second = next;
        consumed_verdicts_.insert(event.verdict_signature64);
        return hhs_pass219_prime_lane_verified_metabolism_authority_valid(out.authority);
    }

    bool verdict_consumed(std::uint64_t verdict_signature64) const noexcept {
        return verdict_signature64 != 0U && consumed_verdicts_.find(verdict_signature64) != consumed_verdicts_.end();
    }

    std::size_t route_count() const noexcept { return states_.size(); }
    std::size_t consumed_verdict_count() const noexcept { return consumed_verdicts_.size(); }

private:
    static std::uint64_t decay_steps(
        std::uint64_t last_sequence,
        std::uint64_t sequence) noexcept {
        if (last_sequence == 0U || sequence <= last_sequence + 1U)
            return 0U;
        const std::uint64_t gap = sequence - last_sequence - 1U;
        return std::min(gap, HHS_PASS219_PRIME_LANE_METABOLIC_DECAY_STEP_LIMIT);
    }

    std::map<std::uint64_t, PrimeLaneMetabolicStateV9> states_{};
    std::set<std::uint64_t> consumed_verdicts_{};
};

} // namespace hhs::rna

#endif
