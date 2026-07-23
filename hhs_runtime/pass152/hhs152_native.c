#include "hhs152_native.h"

int hhs_p152_closure_satisfied(const hhs_p152_closure_flags *f) {
    if (f == NULL) return 0;
    return f->value && f->constraint && f->phase && f->provenance &&
           f->authority && f->receipt && f->resource;
}

int hhs_p152_commit_gate(const hhs_p152_closure_flags *f, int vm81_admitted, int hash72_present) {
    return hhs_p152_closure_satisfied(f) && vm81_admitted && hash72_present;
}

int hhs_p152_transition_allowed(hhs_p152_candidate_state from, hhs_p152_candidate_state to) {
    if (from == HHS_P152_COMMITTED) return 0;
    if (to == HHS_P152_INVALIDATED) {
        return from == HHS_P152_PARTIAL || from == HHS_P152_READY ||
               from == HHS_P152_EVALUATING || from == HHS_P152_PROVISIONAL ||
               from == HHS_P152_VERIFIED;
    }
    switch (from) {
        case HHS_P152_UNSEEN: return to == HHS_P152_BLOCKED || to == HHS_P152_READY;
        case HHS_P152_BLOCKED: return to == HHS_P152_PARTIAL || to == HHS_P152_READY;
        case HHS_P152_PARTIAL: return to == HHS_P152_READY;
        case HHS_P152_READY: return to == HHS_P152_EVALUATING;
        case HHS_P152_EVALUATING: return to == HHS_P152_PROVISIONAL || to == HHS_P152_CONFLICT || to == HHS_P152_RESOURCE_BOUNDED;
        case HHS_P152_PROVISIONAL: return to == HHS_P152_VERIFIED || to == HHS_P152_CONFLICT;
        case HHS_P152_VERIFIED: return to == HHS_P152_COMMITTED;
        default: return 0;
    }
}

int hhs_p152_provisional_may_advance_hash72(void) {
    return 0;
}

int hhs_p152_recursive_control_gate(const hhs_p152_recursive_control_boundary *b) {
    if (b == NULL) return 0;
    if (!b->policy_only) return 0;
    return !(b->alters_invariant_truth || b->alters_committed_state ||
             b->alters_provenance || b->alters_authority_boundary ||
             b->alters_receipt_history || b->alters_semantic_identity);
}

int hhs_p152_history_append_gate(uint64_t prior_length, uint64_t next_length, int committed_prefix_preserved) {
    if (!committed_prefix_preserved) return 0;
    return next_length > prior_length;
}
