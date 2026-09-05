#ifndef HHS_PASS219_I168_PASS169_GENERAL_RUNTIME_BINDING_1_25_H
#define HHS_PASS219_I168_PASS169_GENERAL_RUNTIME_BINDING_1_25_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_I168_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_I168_VERSION_MINOR 25U
#define HHS_EXACT_PASS219_I168_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_I168_SOURCE_BYTES 632U
#define HHS_EXACT_PASS219_I168_HASH216_LEN 216U
#define HHS_EXACT_PASS219_I168_HASH216_STRLEN 217U
#define HHS_EXACT_PASS219_I168_HASH72_LEN 72U
#define HHS_EXACT_PASS219_I168_HASH72_STRLEN 73U

#define HHS_EXACT_PASS219_I168_OP_TOKENS              UINT16_C(0x0001)
#define HHS_EXACT_PASS219_I168_OP_AST                 UINT16_C(0x0002)
#define HHS_EXACT_PASS219_I168_OP_CONSTRAINTS         UINT16_C(0x0004)
#define HHS_EXACT_PASS219_I168_OP_TYPECHECK           UINT16_C(0x0008)
#define HHS_EXACT_PASS219_I168_OP_NORMALIZE           UINT16_C(0x0010)
#define HHS_EXACT_PASS219_I168_OP_PROVE               UINT16_C(0x0020)
#define HHS_EXACT_PASS219_I168_OP_EVALUATE_CANDIDATE  UINT16_C(0x0040)
#define HHS_EXACT_PASS219_I168_OP_ADMIT                UINT16_C(0x0080)
#define HHS_EXACT_PASS219_I168_OP_COMMIT               UINT16_C(0x0100)
#define HHS_EXACT_PASS219_I168_OP_RECEIPT              UINT16_C(0x0200)
#define HHS_EXACT_PASS219_I168_OP_REPLAY               UINT16_C(0x0400)
#define HHS_EXACT_PASS219_I168_OP_REVERSE              UINT16_C(0x0800)
#define HHS_EXACT_PASS219_I168_ALL_OPS                 UINT16_C(0x0FFF)

typedef enum HHSExactPass219I168DecisionV1 {
    HHS_EXACT_PASS219_I168_UNRESOLVED = 0,
    HHS_EXACT_PASS219_I168_VERIFIED = 1,
    HHS_EXACT_PASS219_I168_REJECTED = 2
} HHSExactPass219I168DecisionV1;

typedef enum HHSExactPass219I168ReasonV1 {
    HHS_EXACT_PASS219_I168_REASON_NONE = 0,
    HHS_EXACT_PASS219_I168_REASON_SOURCE_PROVENANCE = 1,
    HHS_EXACT_PASS219_I168_REASON_PASS159_FRONTEND = 2,
    HHS_EXACT_PASS219_I168_REASON_TYPED_PROOF = 3,
    HHS_EXACT_PASS219_I168_REASON_VM81_ADMISSION_COMMIT = 4,
    HHS_EXACT_PASS219_I168_REASON_RECEIPT_REPLAY = 5,
    HHS_EXACT_PASS219_I168_REASON_REVERSE = 6,
    HHS_EXACT_PASS219_I168_REASON_AUTHORITY = 7
} HHSExactPass219I168ReasonV1;

typedef struct HHSExactPass219I168RuntimeBindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason;
    uint16_t operation_verified_mask;
    uint16_t required_operation_mask;

    uint8_t source_identity_exact;
    uint8_t pass159_frontend_chain_complete;
    uint8_t typed_proof_verified;
    uint8_t interpreter_compiler_match;
    uint8_t exact_vm81_admission_verified;
    uint8_t atomic_commit_verified;
    uint8_t hash72_receipts_verified;
    uint8_t hash216_identities_verified;
    uint8_t deterministic_replay_verified;
    uint8_t reverse_restores_prior_state_verified;
    uint8_t live_runtime_abi_verified;
    uint8_t canonical_computation_through_runtime_abi;
    uint8_t single_vm81_commit_authority;
    uint8_t fallback_used;
    uint8_t floating_point_authority;
    uint8_t hash216_persistence_authority;

    uint16_t vm5184_address;
    uint16_t reserved0;
    uint64_t forward_vm81_steps;
    uint64_t replay_vm81_steps;
    uint64_t reverse_vm81_steps;

    char source_hash216[HHS_EXACT_PASS219_I168_HASH216_STRLEN];
    char tokens_hash216[HHS_EXACT_PASS219_I168_HASH216_STRLEN];
    char ast_hash216[HHS_EXACT_PASS219_I168_HASH216_STRLEN];
    char type_environment_hash216[HHS_EXACT_PASS219_I168_HASH216_STRLEN];
    char constraint_graph_hash216[HHS_EXACT_PASS219_I168_HASH216_STRLEN];
    char normalized_ir_hash216[HHS_EXACT_PASS219_I168_HASH216_STRLEN];
    char vmir_hash216[HHS_EXACT_PASS219_I168_HASH216_STRLEN];
    char proof_hash216[HHS_EXACT_PASS219_I168_HASH216_STRLEN];
    char transition_hash216[HHS_EXACT_PASS219_I168_HASH216_STRLEN];
    char reverse_hash216[HHS_EXACT_PASS219_I168_HASH216_STRLEN];
    char receipt_hash72[HHS_EXACT_PASS219_I168_HASH72_STRLEN];
    char replay_hash72[HHS_EXACT_PASS219_I168_HASH72_STRLEN];
    char reverse_hash72[HHS_EXACT_PASS219_I168_HASH72_STRLEN];
} HHSExactPass219I168RuntimeBindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_i168_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_i168_bind_canonical(
    const uint8_t *source_bytes,
    size_t source_length,
    HHSExactPass219I168RuntimeBindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
