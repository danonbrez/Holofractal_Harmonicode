#ifndef HHS_PASS220_I087_ORDERED_RECONCILIATION_V1_HPP
#define HHS_PASS220_I087_ORDERED_RECONCILIATION_V1_HPP

// Candidate proof bridge into the existing C cell wall. No VM81 mutation,
// Hash72 receipt, or Hash216 minting authority is granted here.
#include "hhs_pass219_lane5_hnan_global_constraint_1_63.h"
#include <cstddef>
#include <cstdint>
#include <vector>

namespace hhs::pass220::i087 {

struct OrderedWitness {
    std::uint32_t native_address;
    HHSExactPass219HNANClaimV1 claim;
    std::uint64_t previous_proof_identity;
};

struct Step {
    std::uint32_t native_address;
    std::uint32_t registered_rule;
    std::uint32_t decision;
    std::uint32_t reason;
    std::uint64_t previous_proof_identity;
};

struct CandidateTrace {
    std::vector<Step> ordered_steps;
    HHSExactPass219HNANGlobalReceiptV1 inherited_global{};
    bool candidate_preflight_verified = false;
    bool canonical_admission = false;
};

inline CandidateTrace reconcile_ordered(const std::vector<OrderedWitness>& witnesses) {
    CandidateTrace result;
    result.ordered_steps.reserve(witnesses.size());
    // Validate the inherited global graph first, not only the local conflict.
    if (hhs_exact_pass219_hnan_global_system_verify(&result.inherited_global)
            != HHS_EXACT_STATUS_OK ||
        result.inherited_global.decision != HHS_EXACT_HNAN_DECISION_VERIFIED ||
        result.inherited_global.verified_rule_mask !=
            HHS_EXACT_PASS219_HNAN_GLOBAL_ALL_RULES ||
        result.inherited_global.jordan_depth2_verified != 1U ||
        result.inherited_global.minimal_polynomial_degree4_verified != 1U ||
        result.inherited_global.ordered_zero_closure_preserved != 1U ||
        result.inherited_global.global_delta_denominator_preserved != 1U ||
        result.inherited_global.delta_cancellation_forbidden != 1U ||
        result.inherited_global.unbounded_carrier_symbolic != 1U ||
        result.inherited_global.u72_to_u0_closure_preserved != 1U ||
        result.inherited_global.xy_yx_distinct != 1U ||
        result.inherited_global.zw_wz_distinct != 1U ||
        result.inherited_global.canonical_vm81_mutation_authority != 0U ||
        result.inherited_global.canonical_hash72_authority != 0U ||
        result.inherited_global.canonical_hash216_authority != 0U ||
        result.inherited_global.floating_point_canonical_authority != 0U)
        return result;

    std::uint32_t last_rule = 0U;
    for (const auto& witness : witnesses) {
        Step step{witness.native_address, witness.claim.rule_id,
                  HHS_EXACT_HNAN_DECISION_INVALID,
                  HHS_EXACT_HNAN_REASON_INVALID_ARGUMENT,
                  witness.previous_proof_identity};
        // One authoritative ordering, no fallback to rule search or scalarization.
        if (witness.native_address == 0U ||
            witness.claim.rule_id <= last_rule ||
            witness.claim.rule_id > HHS_EXACT_PASS219_HNAN_GLOBAL_RULE_COUNT) {
            result.ordered_steps.push_back(step);
            return result;
        }
        last_rule = witness.claim.rule_id;
        HHSExactPass219HNANResolutionV1 resolution{};
        if (hhs_exact_pass219_hnan_resolve(&witness.claim, &resolution)
                != HHS_EXACT_STATUS_OK)
        {
            result.ordered_steps.push_back(step);
            return result;
        }
        step.decision = resolution.decision;
        step.reason = resolution.reason;
        result.ordered_steps.push_back(step);
        if (resolution.decision != HHS_EXACT_HNAN_DECISION_VERIFIED)
            return result;
    }
    result.candidate_preflight_verified = !witnesses.empty();
    // Full P -> P+1 proof and native VM81 admission are separate required gates.
    return result;
}

}  // namespace hhs::pass220::i087

#endif
