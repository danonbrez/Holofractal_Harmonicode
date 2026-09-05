#ifndef HHS_PASS219_I163_PASS169_REVERSE_CROSSARCH_1_24_H
#define HHS_PASS219_I163_PASS169_REVERSE_CROSSARCH_1_24_H

#include "hhs_pass219_pass159_global_witness_provenance_1_21_10.h"
#include "hhs_runtime_exact_abi_v1_1_base.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_I163_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_I163_VERSION_MINOR 24U
#define HHS_EXACT_PASS219_I163_VERSION_PATCH 1U
#define HHS_EXACT_PASS219_I163_HASH216_LEN 216U
#define HHS_EXACT_PASS219_I163_HASH216_STRLEN 217U
#define HHS_EXACT_PASS219_I163_HASH72_LEN 72U
#define HHS_EXACT_PASS219_I163_HASH72_STRLEN 73U

typedef enum HHSExactPass219I163DecisionV1 {
    HHS_EXACT_PASS219_I163_UNRESOLVED = 0,
    HHS_EXACT_PASS219_I163_VERIFIED = 1,
    HHS_EXACT_PASS219_I163_REJECTED = 2
} HHSExactPass219I163DecisionV1;

typedef enum HHSExactPass219I163ReasonV1 {
    HHS_EXACT_PASS219_I163_REASON_NONE = 0,
    HHS_EXACT_PASS219_I163_REASON_SOURCE_PROVENANCE = 1,
    HHS_EXACT_PASS219_I163_REASON_FORWARD_COMMIT = 2,
    HHS_EXACT_PASS219_I163_REASON_REVERSE_RUNTIME = 3,
    HHS_EXACT_PASS219_I163_REASON_VM81_PRIOR_STATE_RESTORE = 4,
    HHS_EXACT_PASS219_I163_REASON_INTERPRETER_COMPILER = 5,
    HHS_EXACT_PASS219_I163_REASON_RING_REVERSE = 6,
    HHS_EXACT_PASS219_I163_REASON_RECEIPT_IDENTITY = 7
} HHSExactPass219I163ReasonV1;

typedef struct HHSExactPass219I163DescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t pass169_reverse_runtime_required;
    uint8_t pass159_reverse_api_used;
    uint8_t pass159_reverse_is_transition_receipt;
    uint8_t hash72_reverse_state_api_used;
    uint8_t vm81_transaction_snapshot_restore_required;
    uint8_t interpreter_compiler_equality_required;
    uint8_t prior_committed_state_restoration_required;
    uint8_t cross_architecture_receipt_identity_required;
    uint8_t python_native_parity_required;
    uint8_t i162_parent_immutable;
    uint8_t floating_point_authority;
    uint8_t canonical_mutation_authority;
    uint8_t hash216_persistence_authority;
    uint8_t pass169_terminal_contract_claimed;
    uint8_t reserved0[2];
} HHSExactPass219I163DescriptorV1;

typedef struct HHSExactPass219I163ReverseExecutionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason;
    uint8_t source_provenance_exact;
    uint8_t forward_commit_verified;
    uint8_t forward_receipt_hash72_valid;
    uint8_t forward_receipt_hash216_valid;
    uint8_t reverse_runtime_verified;
    uint8_t reverse_transition_receipt_verified;
    uint8_t reverse_transition_deterministic;
    uint8_t reverse_receipt_hash72_valid;
    uint8_t reverse_receipt_hash216_valid;
    uint8_t vm81_snapshot_reverse_verified;
    uint8_t prior_committed_state_restored;
    uint8_t interpreter_compiler_match;
    uint8_t hash72_ring_reverse_verified;
    uint8_t hash72_ring_restored_prior_state;
    uint8_t deterministic_repeat_verified;
    uint8_t floating_point_authority;
    uint8_t canonical_mutation_authority;
    uint8_t hash216_persistence_authority;
    uint8_t pass169_terminal_contract_claimed;
    uint8_t reserved0;
    uint16_t vm5184_address;
    uint64_t forward_vm81_steps;
    uint64_t reverse_vm81_steps;
    char source_hash216[HHS_EXACT_PASS219_I163_HASH216_STRLEN];
    char forward_semantic_root_hash216[HHS_EXACT_PASS219_I163_HASH216_STRLEN];
    char reverse_semantic_root_hash216[HHS_EXACT_PASS219_I163_HASH216_STRLEN];
    char forward_receipt_hash72[HHS_EXACT_PASS219_I163_HASH72_STRLEN];
    char reverse_receipt_hash72[HHS_EXACT_PASS219_I163_HASH72_STRLEN];
    char forward_receipt_hash216[HHS_EXACT_PASS219_I163_HASH216_STRLEN];
    char reverse_receipt_hash216[HHS_EXACT_PASS219_I163_HASH216_STRLEN];
    char vm81_receipt_hash72[HHS_EXACT_PASS219_I163_HASH72_STRLEN];
    char vm81_hash216_identity[HHS_EXACT_PASS219_I163_HASH216_STRLEN];
} HHSExactPass219I163ReverseExecutionV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_i163_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_i163_descriptor(
    HHSExactPass219I163DescriptorV1 *out_descriptor
);

/*
 * Execute the exact submitted source through the inherited Pass159 Runtime ABI,
 * require a committed forward receipt, and invoke hhs159_reverse.  Frozen
 * Pass159 defines hhs159_reverse as a deterministic reverse-transition receipt,
 * not as an in-place state restore.  I163 therefore verifies that receipt as
 * lineage evidence and separately proves the required prior-state restoration
 * with an exact VM81 transactional snapshot plus hhs_hash72_reverse_state.
 * The snapshot is local proof state only: no persistent/canonical mutation is
 * authorized.  Internal Pass159 receipt fields are diagnostic views only;
 * authoritative execution still enters through public Runtime ABI calls.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_i163_verify_reverse(
    const uint8_t *source_bytes,
    size_t source_length,
    HHSExactPass219I163ReverseExecutionV1 *out_execution
);

#ifdef __cplusplus
}
#endif

#endif
