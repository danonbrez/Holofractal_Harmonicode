#include "hhs_pass220_i087_ordered_reconciliation_v1.hpp"
#include <cassert>

static unsigned g_global_ok = 1;
static unsigned g_mode = HHS_EXACT_HNAN_DECISION_VERIFIED;

extern "C" HHSExactStatus hhs_exact_pass219_hnan_global_system_verify(
    HHSExactPass219HNANGlobalReceiptV1* out) {
    *out = {};
    out->decision = g_global_ok ? HHS_EXACT_HNAN_DECISION_VERIFIED
                                : HHS_EXACT_HNAN_DECISION_UNRESOLVED;
    out->verified_rule_mask = g_global_ok ?
        HHS_EXACT_PASS219_HNAN_GLOBAL_ALL_RULES : 0U;
    return HHS_EXACT_STATUS_OK;
}
extern "C" HHSExactStatus hhs_exact_pass219_hnan_resolve(
    const HHSExactPass219HNANClaimV1* claim,
    HHSExactPass219HNANResolutionV1* out) {
    *out = {};
    out->rule_id = claim->rule_id;
    out->decision = g_mode;
    return HHS_EXACT_STATUS_OK;
}
static hhs::pass220::i087::OrderedWitness witness(unsigned addr, unsigned rule) {
    hhs::pass220::i087::OrderedWitness w{};
    w.native_address = addr;
    w.claim.rule_id = rule;
    w.previous_proof_identity = 179971U;
    return w;
}
int main() {
    using hhs::pass220::i087::reconcile_ordered;
    auto ok = reconcile_ordered({witness(10,1), witness(11,2)});
    assert(ok.candidate_preflight_verified && !ok.canonical_admission);
    assert(ok.ordered_steps.size() == 2);
    assert(ok.ordered_steps[1].previous_proof_identity == 179971U);
    auto duplicate = reconcile_ordered({witness(10,1), witness(11,1)});
    assert(!duplicate.candidate_preflight_verified);
    assert(duplicate.ordered_steps.size() == 2);
    assert(!reconcile_ordered({witness(0,1)}).candidate_preflight_verified);
    g_mode = HHS_EXACT_HNAN_DECISION_REJECTED;
    assert(!reconcile_ordered({witness(10,1)}).candidate_preflight_verified);
    g_mode = HHS_EXACT_HNAN_DECISION_UNRESOLVED;
    assert(!reconcile_ordered({witness(10,1)}).candidate_preflight_verified);
    g_mode = HHS_EXACT_HNAN_DECISION_VERIFIED;
    g_global_ok = 0;
    assert(!reconcile_ordered({witness(10,1)}).candidate_preflight_verified);
}
