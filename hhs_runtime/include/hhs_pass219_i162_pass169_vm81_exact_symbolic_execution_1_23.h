#ifndef HHS_PASS219_I162_PASS169_VM81_EXACT_SYMBOLIC_EXECUTION_1_23_H
#define HHS_PASS219_I162_PASS169_VM81_EXACT_SYMBOLIC_EXECUTION_1_23_H

#include "hhs_pass219_pass169_gate_authority_binding_1_21_11.h"
#include "hhs_runtime_uqcel_1_8.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_I162_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_I162_VERSION_MINOR 23U
#define HHS_EXACT_PASS219_I162_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_I162_EDGE_COUNT 10U
#define HHS_EXACT_PASS219_I162_GATE_COUNT 5U
#define HHS_EXACT_PASS219_I162_ALL_EDGE_MASK UINT16_C(0x03FF)
#define HHS_EXACT_PASS219_I162_ALL_GATE_MASK UINT8_C(0x1F)

typedef enum HHSExactPass219I162DecisionV1 {
    HHS_EXACT_PASS219_I162_UNRESOLVED = 0,
    HHS_EXACT_PASS219_I162_VERIFIED = 1,
    HHS_EXACT_PASS219_I162_REJECTED = 2
} HHSExactPass219I162DecisionV1;

typedef enum HHSExactPass219I162ReasonV1 {
    HHS_EXACT_PASS219_I162_REASON_NONE = 0,
    HHS_EXACT_PASS219_I162_REASON_PROVENANCE = 1,
    HHS_EXACT_PASS219_I162_REASON_RATIONAL_CHAIN = 2,
    HHS_EXACT_PASS219_I162_REASON_MODULAR_PIVOT = 3,
    HHS_EXACT_PASS219_I162_REASON_TYPED_JOIN = 4,
    HHS_EXACT_PASS219_I162_REASON_AB_ROOT = 5,
    HHS_EXACT_PASS219_I162_REASON_TYPED_BOUNDARY = 6,
    HHS_EXACT_PASS219_I162_REASON_DELTA_PHASE = 7,
    HHS_EXACT_PASS219_I162_REASON_VM81_ADMISSION = 8,
    HHS_EXACT_PASS219_I162_REASON_REPLAY = 9,
    HHS_EXACT_PASS219_I162_REASON_RECEIPT = 10
} HHSExactPass219I162ReasonV1;

typedef struct HHSExactPass219I162DescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t edge_count;
    uint32_t gate_count;
    uint16_t required_edge_mask;
    uint8_t required_gate_mask;
    uint8_t native_symbolic_verifier;
    uint8_t i161_typed_closure_preserved;
    uint8_t compatibility_ab_transport_only;
    uint8_t source_ab_definitionally_p2;
    uint8_t full_symbolic_uqcel_v1_promoted;
    uint8_t vm81_transport_admission;
    uint8_t hash72_execution_receipt;
    uint8_t hash216_proof_transition_identity;
    uint8_t deterministic_replay;
    uint8_t source_reconstruction_inherited_from_pass159;
    uint8_t floating_point_authority;
    uint8_t hash216_persistence_authority;
    uint8_t reserved0[2];
} HHSExactPass219I162DescriptorV1;

typedef struct HHSExactPass219I162ExecutionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason;
    uint16_t edge_proved_mask;
    uint8_t gate_true_mask;
    uint8_t all_ten_typed_joins_verified;
    uint8_t typed_scalar_zero_verified;
    uint8_t typed_renewed_unit_verified;
    uint8_t ordinary_scalar_boundary_equality_claimed;
    uint8_t compatibility_ab_transport_only;
    uint8_t source_ab_definitionally_p2;
    uint8_t exact_vm81_admission_verified;
    uint8_t atomic_commit_verified;
    uint8_t hash72_receipt_verified;
    uint8_t hash216_proof_identity_verified;
    uint8_t deterministic_replay_verified;
    uint8_t source_reconstruction_verified;
    uint8_t floating_point_authority;
    uint8_t hash216_persistence_authority;
    uint8_t reserved0[2];
    uint32_t P;
    uint32_t p;
    uint32_t q;
    uint32_t delta;
    uint32_t t;
    uint32_t m;
    uint16_t vm5184_address;
    uint16_t reserved1;
    uint64_t vm81_steps;
    uint64_t replay_vm81_steps;
    uint8_t canonical_global_symbol_environment_root[
        HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES
    ];
    char proof_hash216[HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN];
    char transition_hash216[HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN];
    char receipt_hash72[HHS_EXACT_PASS219_PASS169_BINDING_HASH72_STRLEN];
    char replay_hash72[HHS_EXACT_PASS219_PASS169_BINDING_HASH72_STRLEN];
} HHSExactPass219I162ExecutionV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_i162_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_i162_descriptor(
    HHSExactPass219I162DescriptorV1 *out_descriptor
);

/*
 * Verify the sealed I161 source-bound candidate natively, then lower the
 * verified proof state through the inherited VM81 UQCEL admission lane.
 *
 * The UQCEL INTEGER_SYMMETRIC_V1 A/B fields are used strictly as compatibility
 * transport witnesses after source-level A/B closure has been independently
 * established. They never redefine the complete source boundaries as P^2.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_i162_execute(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    HHSExactPass219I162ExecutionV1 *out_execution
);

/*
 * Versioned Pass169 provider preferred by the I121.11 binder when linked.
 */
HHSExactStatus hhs_pass169_verify_combined_gate_authority_i162_1_23(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    HHSExactPass219Pass169AuthorityProofV1 *out_proof
);

#ifdef __cplusplus
}
#endif

#endif
