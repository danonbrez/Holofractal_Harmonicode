#ifndef HHS_PASS219_EXACT_VM81_CANDIDATE_ADAPTER_1_21_3_H
#define HHS_PASS219_EXACT_VM81_CANDIDATE_ADAPTER_1_21_3_H

#include "hhs_pass219_monolithic_constraint_abi_1_20.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_VM81_ADAPTER_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_VM81_ADAPTER_VERSION_MINOR 21U
#define HHS_EXACT_PASS219_VM81_ADAPTER_VERSION_PATCH 3U

#define HHS_EXACT_PASS219_VM81_PROGRAM_THREADS 64U
#define HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS 49U
#define HHS_EXACT_PASS219_VM81_DERIVED_THREADS 15U
#define HHS_EXACT_PASS219_VM81_NEXT_EDGES 4U
#define HHS_EXACT_PASS219_VM81_SYMBOL_COUNT 24U
#define HHS_EXACT_PASS219_VM81_MAX_EXECUTION_STEPS 4096U

typedef enum HHSExactPass219VM81SymbolV1 {
    HHS_EXACT_PASS219_VM81_SYMBOL_P_UPPER = 0,
    HHS_EXACT_PASS219_VM81_SYMBOL_T,
    HHS_EXACT_PASS219_VM81_SYMBOL_P_LOWER,
    HHS_EXACT_PASS219_VM81_SYMBOL_Q,
    HHS_EXACT_PASS219_VM81_SYMBOL_DELTA,
    HHS_EXACT_PASS219_VM81_SYMBOL_M,
    HHS_EXACT_PASS219_VM81_SYMBOL_B_LOWER,
    HHS_EXACT_PASS219_VM81_SYMBOL_C,
    HHS_EXACT_PASS219_VM81_SYMBOL_U,
    HHS_EXACT_PASS219_VM81_SYMBOL_S,
    HHS_EXACT_PASS219_VM81_SYMBOL_X,
    HHS_EXACT_PASS219_VM81_SYMBOL_Y,
    HHS_EXACT_PASS219_VM81_SYMBOL_Z,
    HHS_EXACT_PASS219_VM81_SYMBOL_W,
    HHS_EXACT_PASS219_VM81_SYMBOL_XY,
    HHS_EXACT_PASS219_VM81_SYMBOL_YX,
    HHS_EXACT_PASS219_VM81_SYMBOL_ZW,
    HHS_EXACT_PASS219_VM81_SYMBOL_WZ,
    HHS_EXACT_PASS219_VM81_SYMBOL_AT,
    HHS_EXACT_PASS219_VM81_SYMBOL_F,
    HHS_EXACT_PASS219_VM81_SYMBOL_BT,
    HHS_EXACT_PASS219_VM81_SYMBOL_A,
    HHS_EXACT_PASS219_VM81_SYMBOL_B_UPPER,
    HHS_EXACT_PASS219_VM81_SYMBOL_A2,
    HHS_EXACT_PASS219_VM81_SYMBOL_COUNT
} HHSExactPass219VM81SymbolV1;

typedef enum HHSExactPass219VM81OpcodeV1 {
    HHS_EXACT_PASS219_VM81_OP_NOP = 0,
    HHS_EXACT_PASS219_VM81_OP_ADD,
    HHS_EXACT_PASS219_VM81_OP_SUB,
    HHS_EXACT_PASS219_VM81_OP_ROT,
    HHS_EXACT_PASS219_VM81_OP_XOR,
    HHS_EXACT_PASS219_VM81_OP_AND,
    HHS_EXACT_PASS219_VM81_OP_OR,
    HHS_EXACT_PASS219_VM81_OP_LOAD,
    HHS_EXACT_PASS219_VM81_OP_STORE,
    HHS_EXACT_PASS219_VM81_OP_BRANCH,
    HHS_EXACT_PASS219_VM81_OP_BZ,
    HHS_EXACT_PASS219_VM81_OP_BNZ,
    HHS_EXACT_PASS219_VM81_OP_MULXY,
    HHS_EXACT_PASS219_VM81_OP_MULYX,
    HHS_EXACT_PASS219_VM81_OP_QGU,
    HHS_EXACT_PASS219_VM81_OP_GATE_APB,
    HHS_EXACT_PASS219_VM81_OP_GATE_CLOSURE,
    HHS_EXACT_PASS219_VM81_OP_GATE_IDENTITY,
    HHS_EXACT_PASS219_VM81_OP_QBRANCH,
    HHS_EXACT_PASS219_VM81_OP_CONSTRAIN,
    HHS_EXACT_PASS219_VM81_OP_RELAX,
    HHS_EXACT_PASS219_VM81_OP_SWEEP81,
    HHS_EXACT_PASS219_VM81_OP_CLOSE81,
    HHS_EXACT_PASS219_VM81_OP_HALT,
    HHS_EXACT_PASS219_VM81_OP_COUNT
} HHSExactPass219VM81OpcodeV1;

typedef struct HHSExactPass219VM81InstructionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t opcode;
    uint8_t a;
    uint8_t b;
    uint8_t c;
    uint8_t constraint_group;
    uint8_t phase;
    uint8_t next_enabled[HHS_EXACT_PASS219_VM81_NEXT_EDGES];
    uint8_t next_target[HHS_EXACT_PASS219_VM81_NEXT_EDGES];
} HHSExactPass219VM81InstructionV1;

typedef struct HHSExactPass219VM81ProgramV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t instruction_count;
    uint32_t source_structure_thread_count;
    uint32_t derived_thread_count;
    uint32_t semantic_family_coverage_mask;
    uint64_t equality_edge_coverage_mask;
    uint8_t source_sha256[HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES];
    uint8_t symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_COUNT];
    uint8_t x_cell81;
    uint8_t y_cell81;
    uint8_t z_cell81;
    uint8_t w_cell81;
    uint8_t source_structure_complete;
    uint8_t effectful_lowering_complete;
    uint8_t source_semantics_complete;
    uint8_t full_symbolic_identity_required;
    HHSExactPass219VM81InstructionV1
        instructions[HHS_EXACT_PASS219_VM81_PROGRAM_THREADS];
} HHSExactPass219VM81ProgramV1;

typedef struct HHSExactPass219VM81ExecutionV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactVM81Frame before_frame;
    HHSExactVM81Frame after_frame;
    uint8_t source_sha256[HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES];
    char previous_hash72[HHS_EXACT_HASH72_STRLEN];
    char state_hash72[HHS_EXACT_HASH72_STRLEN];
    char receipt_hash72[HHS_EXACT_HASH72_STRLEN];
    uint64_t steps_executed;
    uint64_t last_receipt_step;
    uint64_t identity_exact_witness;
    uint64_t orbit_period;
    uint32_t witness_flags;
    uint32_t semantic_family_coverage_mask;
    uint64_t equality_edge_coverage_mask;
    uint8_t x_phase;
    uint8_t y_phase;
    uint8_t z_phase;
    uint8_t w_phase;
    uint8_t xy_phase;
    uint8_t yx_phase;
    uint8_t zw_phase;
    uint8_t wz_phase;
    uint8_t halted;
    uint8_t converged;
    uint8_t ledger_advanced;
    uint8_t identity_has_data;
    uint8_t source_identity_valid;
    uint8_t candidate_frame_bound;
    uint8_t exact_kernel_execution_observed;
    uint8_t source_structure_complete;
    uint8_t effectful_lowering_complete;
    uint8_t source_semantics_complete;
    uint8_t full_symbolic_identity_required;
    uint8_t full_symbolic_identity_gate_supported;
    uint8_t canonical_monolithic_proof;
    uint8_t floating_point_authority;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t reserved1[3];
} HHSExactPass219VM81ExecutionV1;

typedef struct HHSExactPass219VM81ReplayV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219VM81ExecutionV1 replay;
    uint8_t frame_equal;
    uint8_t previous_hash72_equal;
    uint8_t state_hash72_equal;
    uint8_t receipt_hash72_equal;
    uint8_t witness_equal;
    uint8_t steps_equal;
    uint8_t phase_surface_equal;
    uint8_t source_identity_equal;
    uint8_t coverage_equal;
    uint8_t authority_boundary_equal;
    uint8_t replay_verified;
    uint8_t reserved0[5];
} HHSExactPass219VM81ReplayV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_vm81_adapter_version(void);

/*
 * Lower the frozen 1.20 native source topology into one effectful 64-thread
 * VM81 program. The lowerer preserves all 34 parenthesis shells and all 15
 * literal equality half-gates, then fills the inherited 15 derived slots with
 * semantic-family constraint registration, ordered-phase witness operations,
 * closure operations, an exact identity-gate probe, and HALT.
 *
 * This is deliberately classified as effectful but semantically incomplete:
 * the current exact kernel identity gate cannot prove the entire symbolic
 * radical/modular equality chain, so source_semantics_complete remains zero.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_lower_monolithic_structure(
    HHSExactPass219VM81ProgramV1 *out_program
);

/*
 * Execute one source-bound 64-thread candidate program against one exact
 * 81x64-bit input frame in the canonical HARMONICODE VM81 kernel. Execution
 * occurs on an isolated local copy and exposes no canonical mutation or Hash72
 * commit authority.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_execute_candidate(
    const HHSExactPass219VM81ProgramV1 *program,
    const HHSExactVM81Frame *candidate_frame,
    HHSExactPass219VM81ExecutionV1 *out_execution
);

/*
 * Re-execute from the same exact candidate frame and program and require exact
 * equality of the resulting frame, receipt chain tip, witness state, steps,
 * source identity, topology coverage, and ordered phase surface.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_replay_candidate(
    const HHSExactPass219VM81ProgramV1 *program,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactPass219VM81ExecutionV1 *expected,
    HHSExactPass219VM81ReplayV1 *out_replay
);

#ifdef __cplusplus
}
#endif

#endif
