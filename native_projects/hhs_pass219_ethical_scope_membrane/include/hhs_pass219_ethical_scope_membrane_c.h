#ifndef HHS_PASS219_ETHICAL_SCOPE_MEMBRANE_C_H
#define HHS_PASS219_ETHICAL_SCOPE_MEMBRANE_C_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_P219_ETHICAL_INVARIANT_COUNT 18u
#define HHS_P219_SCOPE_WORD_COUNT 4u

/* Exact trinary invariant states. */
enum hhs_p219_invariant_state_v1 {
    HHS_P219_INVARIANT_PASS = 1,
    HHS_P219_INVARIANT_FAIL = 2,
    HHS_P219_INVARIANT_UNRESOLVED = 3
};

enum hhs_p219_evaluation_phase_v1 {
    HHS_P219_PHASE_PROSPECTIVE = 0,
    HHS_P219_PHASE_POST_ACTION = 1
};

enum hhs_p219_ethical_decision_v1 {
    HHS_P219_EXECUTE_LOCAL_PROVISIONAL = 1,
    HHS_P219_NARROW_AND_RESIMULATE = 2,
    HHS_P219_SIMULATE_ONLY = 3,
    HHS_P219_HOLD = 4,
    HHS_P219_DENY = 5,
    HHS_P219_REQUIRE_ADDITIONAL_AUTHORITY = 6,
    HHS_P219_CLOSE_GOOD = 7,
    HHS_P219_REPAIR_OR_ROLLBACK = 8
};

typedef struct hhs_p219_scope_mask_v1 {
    uint64_t words[HHS_P219_SCOPE_WORD_COUNT];
} hhs_p219_scope_mask_v1;

typedef struct hhs_p219_ethical_eval_input_v1 {
    uint8_t phase;
    uint8_t invariant_states[HHS_P219_ETHICAL_INVARIANT_COUNT];
    hhs_p219_scope_mask_v1 requested_scope;
    hhs_p219_scope_mask_v1 minimum_necessary_scope;
    hhs_p219_scope_mask_v1 granted_scope;
    hhs_p219_scope_mask_v1 revoked_or_expired_scope;
} hhs_p219_ethical_eval_input_v1;

typedef struct hhs_p219_ethical_eval_output_v1 {
    uint8_t decision;
    uint8_t prospective_alignment;
    uint8_t good_closed;
    uint8_t reserved0;
    hhs_p219_scope_mask_v1 active_authority_scope;
    hhs_p219_scope_mask_v1 effective_scope;
    hhs_p219_scope_mask_v1 missing_requested_scope;
    hhs_p219_scope_mask_v1 missing_authority_scope;
    hhs_p219_scope_mask_v1 extra_requested_scope;
    uint32_t failed_invariant_count;
    uint32_t unresolved_invariant_count;
} hhs_p219_ethical_eval_output_v1;

/*
 * Pure constraint evaluation only.
 * This function does not mutate VM81, mint Hash72/Hash216 authority,
 * perform I/O, grant consent, or create external capability.
 */
int hhs_p219_ethical_evaluate_v1(
    const hhs_p219_ethical_eval_input_v1* input,
    hhs_p219_ethical_eval_output_v1* output
);

#ifdef __cplusplus
}
#endif

#endif
