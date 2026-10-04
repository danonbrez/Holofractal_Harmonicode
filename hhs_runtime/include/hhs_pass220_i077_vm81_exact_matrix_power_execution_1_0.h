#ifndef HHS_PASS220_I077_VM81_EXACT_MATRIX_POWER_EXECUTION_1_0_H
#define HHS_PASS220_I077_VM81_EXACT_MATRIX_POWER_EXECUTION_1_0_H

#include "hhs_runtime_uqcel_1_8.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS220_I077_VERSION_MAJOR 1U
#define HHS_EXACT_PASS220_I077_VERSION_MINOR 0U
#define HHS_EXACT_PASS220_I077_VERSION_PATCH 0U

#define HHS_EXACT_PASS220_I077_NODE_COUNT 2U
#define HHS_EXACT_PASS220_I077_ROWS 4U
#define HHS_EXACT_PASS220_I077_COLUMNS 2U
#define HHS_EXACT_PASS220_I077_CELL_OCCURRENCES 8U
#define HHS_EXACT_PASS220_I077_UNIQUE_CELL_ROOTS 6U
#define HHS_EXACT_PASS220_I077_HASH216_LEN 216U
#define HHS_EXACT_PASS220_I077_HASH216_STRLEN 217U
#define HHS_EXACT_PASS220_I077_HASH72_LEN 72U
#define HHS_EXACT_PASS220_I077_HASH72_STRLEN 73U
#define HHS_EXACT_PASS220_I077_SHA256_BYTES 32U
#define HHS_EXACT_PASS220_I077_SHA256_HEX_STRLEN 65U

typedef enum HHSExactPass220I077NodeIdV1 {
    HHS_EXACT_PASS220_I077_NODE_M_WZ_X2 = 0,
    HHS_EXACT_PASS220_I077_NODE_M_XY_X4 = 1
} HHSExactPass220I077NodeIdV1;

typedef enum HHSExactPass220I077CellTokenV1 {
    HHS_EXACT_PASS220_I077_CELL_NEG_WZ = 0,
    HHS_EXACT_PASS220_I077_CELL_Z_MINUS_W = 1,
    HHS_EXACT_PASS220_I077_CELL_WZ = 2,
    HHS_EXACT_PASS220_I077_CELL_Y_PLUS_X = 3,
    HHS_EXACT_PASS220_I077_CELL_NEG_XY = 4,
    HHS_EXACT_PASS220_I077_CELL_XY = 5
} HHSExactPass220I077CellTokenV1;

typedef enum HHSExactPass220I077DecisionV1 {
    HHS_EXACT_PASS220_I077_UNRESOLVED = 0,
    HHS_EXACT_PASS220_I077_VERIFIED = 1,
    HHS_EXACT_PASS220_I077_REJECTED = 2
} HHSExactPass220I077DecisionV1;

typedef enum HHSExactPass220I077ReasonV1 {
    HHS_EXACT_PASS220_I077_REASON_NONE = 0,
    HHS_EXACT_PASS220_I077_REASON_NODE_ID = 1,
    HHS_EXACT_PASS220_I077_REASON_SOURCE_IDENTITY = 2,
    HHS_EXACT_PASS220_I077_REASON_ORDERED_TOPOLOGY = 3,
    HHS_EXACT_PASS220_I077_REASON_VM81_ADMISSION = 4,
    HHS_EXACT_PASS220_I077_REASON_REPLAY = 5,
    HHS_EXACT_PASS220_I077_REASON_AUTHORITY = 6
} HHSExactPass220I077ReasonV1;

typedef struct HHSExactPass220I077DescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t node_count;
    uint32_t rows;
    uint32_t columns;
    uint32_t cell_occurrences_per_node;
    uint32_t unique_cell_roots;
    uint8_t exact_matrix_power_hir_required;
    uint8_t native_symbolic_executor;
    uint8_t rectangular_4x2_supported;
    uint8_t source_identity_required;
    uint8_t ordered_topology_required;
    uint8_t vm81_transport_admission;
    uint8_t hash72_execution_receipt;
    uint8_t hash216_transition_identity;
    uint8_t deterministic_replay;
    uint8_t matrix_power_value_derivation;
    uint8_t host_matrixpower_authority;
    uint8_t host_square_matrix_requirement_authority;
    uint8_t numeric_exponent_evaluation_authority;
    uint8_t floating_point_authority;
    uint8_t canonical_state_persistence_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_commit_authority;
    uint8_t canonical_hash216_commit_authority;
    uint8_t external_egress_authority;
    uint8_t reserved0[2];
} HHSExactPass220I077DescriptorV1;

typedef struct HHSExactPass220I077ExecutionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason;
    uint32_t node_id;
    uint32_t rows;
    uint32_t columns;
    uint32_t exponent_token_degree;
    uint32_t cell_occurrence_count;
    uint32_t unique_cell_root_count;
    uint8_t cell_tokens[HHS_EXACT_PASS220_I077_CELL_OCCURRENCES];
    uint8_t source_identity_exact;
    uint8_t ordered_topology_verified;
    uint8_t exact_symbolic_node_executed;
    uint8_t host_matrixpower_used;
    uint8_t square_matrix_requirement_imported;
    uint8_t numeric_exponent_evaluated;
    uint8_t matrix_power_value_derived;
    uint8_t exact_vm81_admission_verified;
    uint8_t atomic_frame_commit_verified;
    uint8_t hash72_receipt_verified;
    uint8_t hash216_transition_identity_verified;
    uint8_t deterministic_replay_verified;
    uint8_t canonical_state_persisted;
    uint8_t floating_point_authority;
    uint8_t reserved0;
    uint16_t vm5184_address;
    uint16_t reserved1;
    uint64_t vm81_steps;
    uint64_t replay_vm81_steps;
    char source_node[64];
    char exponent_token[8];
    char source_node_sha256[HHS_EXACT_PASS220_I077_SHA256_HEX_STRLEN];
    char ordered_cells_sha256[HHS_EXACT_PASS220_I077_SHA256_HEX_STRLEN];
    char change_hash72[HHS_EXACT_PASS220_I077_HASH72_STRLEN];
    char receipt_hash72[HHS_EXACT_PASS220_I077_HASH72_STRLEN];
    char replay_hash72[HHS_EXACT_PASS220_I077_HASH72_STRLEN];
    char proof_hash216[HHS_EXACT_PASS220_I077_HASH216_STRLEN];
    char transition_hash216[HHS_EXACT_PASS220_I077_HASH216_STRLEN];
} HHSExactPass220I077ExecutionV1;

HHS_EXACT_API uint32_t hhs_exact_pass220_i077_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_i077_descriptor(
    HHSExactPass220I077DescriptorV1 *out_descriptor
);

/*
 * Execute one of the two source-bound Pass 220 I076 ExactMatrixPower HIR nodes
 * through the native VM81 admission lane.
 *
 * This call verifies and executes the exact symbolic node identity and ordered
 * 4x2 topology. It intentionally does not derive a conventional matrix-power
 * value and does not import square-matrix or floating-point semantics.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_i077_execute(
    uint32_t node_id,
    HHSExactPass220I077ExecutionV1 *out_execution
);

#ifdef __cplusplus
}
#endif

#endif
