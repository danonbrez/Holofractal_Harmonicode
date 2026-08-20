#ifndef HHS_PASS219_MONOLITHIC_CONSTRAINT_ABI_1_20_H
#define HHS_PASS219_MONOLITHIC_CONSTRAINT_ABI_1_20_H

#include "hhs_runtime_uqcel_1_8.h"
#include "hhs_pass219_octonion_runtime_1_19.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_MONOLITHIC_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_MONOLITHIC_VERSION_MINOR 20U
#define HHS_EXACT_PASS219_MONOLITHIC_VERSION_PATCH 0U

#define HHS_EXACT_PASS219_MONOLITHIC_SOURCE_LENGTH 354U
#define HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH 348U
#define HHS_EXACT_PASS219_MONOLITHIC_EDGE_COUNT 10U
#define HHS_EXACT_PASS219_MONOLITHIC_BINDING_EDGE_COUNT 5U
#define HHS_EXACT_PASS219_MONOLITHIC_CONSTRAINT_EDGE_COUNT 5U
#define HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT 8U
#define HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES 32U
#define HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN 216U
#define HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN 217U

#define HHS_EXACT_PASS219_MONOLITHIC_ALL_EDGE_MASK UINT64_C(0x03FF)

#define HHS_EXACT_PASS219_STAGE_SOURCE_OPEN       UINT32_C(0x0001)
#define HHS_EXACT_PASS219_STAGE_LEX               UINT32_C(0x0002)
#define HHS_EXACT_PASS219_STAGE_CST               UINT32_C(0x0004)
#define HHS_EXACT_PASS219_STAGE_AST               UINT32_C(0x0008)
#define HHS_EXACT_PASS219_STAGE_TYPECHECK         UINT32_C(0x0010)
#define HHS_EXACT_PASS219_STAGE_CONSTRAINT_GRAPH  UINT32_C(0x0020)
#define HHS_EXACT_PASS219_STAGE_HIR               UINT32_C(0x0040)
#define HHS_EXACT_PASS219_STAGE_VMIR              UINT32_C(0x0080)
#define HHS_EXACT_PASS219_STAGE_INTERPRET         UINT32_C(0x0100)
#define HHS_EXACT_PASS219_STAGE_REPLAY            UINT32_C(0x0200)
#define HHS_EXACT_PASS219_STAGE_VM81_PROOF        UINT32_C(0x0400)
#define HHS_EXACT_PASS219_STAGE_REQUIRED          UINT32_C(0x07FF)

#define HHS_EXACT_PASS219_FAMILY_HARMONIC             UINT32_C(0x01)
#define HHS_EXACT_PASS219_FAMILY_MATRIX               UINT32_C(0x02)
#define HHS_EXACT_PASS219_FAMILY_ORDERED_PHASE        UINT32_C(0x04)
#define HHS_EXACT_PASS219_FAMILY_TENSOR_SUBSTITUTION  UINT32_C(0x08)
#define HHS_EXACT_PASS219_FAMILY_MODULAR              UINT32_C(0x10)
#define HHS_EXACT_PASS219_FAMILY_AB_ROOT              UINT32_C(0x20)
#define HHS_EXACT_PASS219_FAMILY_TERMINAL              UINT32_C(0x40)
#define HHS_EXACT_PASS219_FAMILY_DELTA_ROOT            UINT32_C(0x80)
#define HHS_EXACT_PASS219_FAMILY_REQUIRED              UINT32_C(0xFF)

typedef enum HHSExactPass219MonolithicEdgeKind {
    HHS_EXACT_PASS219_MONOLITHIC_EDGE_BINDING = 1,
    HHS_EXACT_PASS219_MONOLITHIC_EDGE_CONSTRAINT = 2
} HHSExactPass219MonolithicEdgeKind;

typedef enum HHSExactPass219MonolithicDecision {
    HHS_EXACT_PASS219_MONOLITHIC_UNRESOLVED = 0,
    HHS_EXACT_PASS219_MONOLITHIC_PROVEN = 1,
    HHS_EXACT_PASS219_MONOLITHIC_REJECTED = 2
} HHSExactPass219MonolithicDecision;

typedef enum HHSExactPass219MonolithicFamily {
    HHS_EXACT_PASS219_MONOLITHIC_FAMILY_HARMONIC = 0,
    HHS_EXACT_PASS219_MONOLITHIC_FAMILY_MATRIX = 1,
    HHS_EXACT_PASS219_MONOLITHIC_FAMILY_ORDERED_PHASE = 2,
    HHS_EXACT_PASS219_MONOLITHIC_FAMILY_TENSOR_SUBSTITUTION = 3,
    HHS_EXACT_PASS219_MONOLITHIC_FAMILY_MODULAR = 4,
    HHS_EXACT_PASS219_MONOLITHIC_FAMILY_AB_ROOT = 5,
    HHS_EXACT_PASS219_MONOLITHIC_FAMILY_TERMINAL = 6,
    HHS_EXACT_PASS219_MONOLITHIC_FAMILY_DELTA_ROOT = 7
} HHSExactPass219MonolithicFamily;

typedef struct HHSExactPass219MonolithicDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t source_length;
    uint32_t native_source_length;
    uint32_t equality_edge_count;
    uint32_t binding_edge_count;
    uint32_t constraint_edge_count;
    uint32_t semantic_family_count;
    uint32_t required_stage_mask;
    uint32_t required_family_mask;
    uint32_t monolithic_admission_only;
    uint32_t source_structure_preserved;
    uint32_t pass159_constraint_graph_required;
    uint32_t vm81_proof_required;
    uint32_t raw_packet_can_prove;
    uint32_t floating_point_authority;
    uint32_t vm81_mutation_authority;
    uint32_t hash72_commit_authority;
    uint8_t native_source_sha256[HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES];
    uint8_t machine_source_sha256[HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES];
    uint8_t frozen_tex_sha256[HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES];
} HHSExactPass219MonolithicDescriptorV1;

typedef struct HHSExactPass219MonolithicEdgeV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t ordinal;
    uint32_t byte_offset;
    uint16_t paren_depth;
    uint16_t brace_depth;
    uint16_t bracket_depth;
    uint8_t kind;
    uint8_t token_length;
} HHSExactPass219MonolithicEdgeV1;

typedef struct HHSExactPass219MonolithicFamilySpanV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t family;
    uint32_t byte_begin;
    uint32_t byte_end;
    uint32_t required_mask_bit;
} HHSExactPass219MonolithicFamilySpanV1;

typedef struct HHSExactPass219MonolithicProofV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t completed_stage_mask;
    uint32_t resolved_family_mask;
    uint64_t edge_satisfied_mask;
    uint64_t edge_failed_mask;
    uint64_t edge_unresolved_mask;
    uint8_t source_sha256[HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES];
    uint8_t all_values_exact;
    uint8_t one_candidate_state;
    uint8_t lhs_rhs_equal;
    uint8_t reserved0;
    HHSExactPass219OctonionStateV1 octonion_state;
    char source_hash216[HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN];
    char ast_hash216[HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN];
    char constraint_graph_hash216[HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN];
    char vmir_hash216[HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN];
    char candidate_state_hash216[HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN];
    char proof_hash216[HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN];
    char family_witness_hash216[HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT][HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN];
    char receipt_hash72[HHS_EXACT_HASH72_STRLEN];
} HHSExactPass219MonolithicProofV1;

typedef struct HHSExactPass219MonolithicVerificationV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t completed_stage_mask;
    uint32_t resolved_family_mask;
    uint32_t missing_stage_mask;
    uint32_t missing_family_mask;
    uint64_t edge_satisfied_mask;
    uint64_t edge_failed_mask;
    uint64_t edge_unresolved_mask;
    uint8_t source_identity_valid;
    uint8_t ordered_xy_bound;
    uint8_t proof_identity_valid;
    uint8_t proof_packet_complete;
    uint8_t requires_vm81_authority;
    uint8_t monolithic_chain_ok;
    uint16_t reserved0;
    uint32_t floating_point_authority;
    uint32_t vm81_mutation_authority;
    uint32_t hash72_commit_authority;
} HHSExactPass219MonolithicVerificationV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_monolithic_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_monolithic_descriptor(
    HHSExactPass219MonolithicDescriptorV1 *out_descriptor
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_monolithic_native_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_monolithic_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_monolithic_native_edge(
    uint32_t ordinal,
    HHSExactPass219MonolithicEdgeV1 *out_edge
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_monolithic_edge(
    uint32_t ordinal,
    HHSExactPass219MonolithicEdgeV1 *out_edge
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_monolithic_family_span(
    uint32_t family,
    HHSExactPass219MonolithicFamilySpanV1 *out_span
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_monolithic_verify_proof(
    const HHSExactPass219MonolithicProofV1 *proof,
    HHSExactPass219MonolithicVerificationV1 *out_verification
);

#ifdef __cplusplus
}
#endif

#endif
