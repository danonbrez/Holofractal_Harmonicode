#ifndef HHS_PASS152_NATIVE_H
#define HHS_PASS152_NATIVE_H
#include <stddef.h>
#include <stdint.h>

typedef enum {
    HHS_P152_UNSEEN = 0,
    HHS_P152_BLOCKED,
    HHS_P152_PARTIAL,
    HHS_P152_READY,
    HHS_P152_EVALUATING,
    HHS_P152_PROVISIONAL,
    HHS_P152_VERIFIED,
    HHS_P152_INVALIDATED,
    HHS_P152_CONFLICT,
    HHS_P152_RESOURCE_BOUNDED,
    HHS_P152_COMMITTED
} hhs_p152_candidate_state;

typedef struct {
    uint8_t value;
    uint8_t constraint;
    uint8_t phase;
    uint8_t provenance;
    uint8_t authority;
    uint8_t receipt;
    uint8_t resource;
} hhs_p152_closure_flags;

typedef struct {
    uint8_t alters_invariant_truth;
    uint8_t alters_committed_state;
    uint8_t alters_provenance;
    uint8_t alters_authority_boundary;
    uint8_t alters_receipt_history;
    uint8_t alters_semantic_identity;
    uint8_t policy_only;
} hhs_p152_recursive_control_boundary;

int hhs_p152_closure_satisfied(const hhs_p152_closure_flags *flags);
int hhs_p152_commit_gate(const hhs_p152_closure_flags *flags, int vm81_admitted, int hash72_present);
int hhs_p152_transition_allowed(hhs_p152_candidate_state from, hhs_p152_candidate_state to);
int hhs_p152_provisional_may_advance_hash72(void);
int hhs_p152_recursive_control_gate(const hhs_p152_recursive_control_boundary *boundary);
int hhs_p152_history_append_gate(uint64_t prior_length, uint64_t next_length, int committed_prefix_preserved);

#endif
