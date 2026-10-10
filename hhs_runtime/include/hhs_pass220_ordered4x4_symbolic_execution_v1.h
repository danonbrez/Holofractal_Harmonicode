#ifndef HHS_PASS220_ORDERED4X4_SYMBOLIC_EXECUTION_V1_H
#define HHS_PASS220_ORDERED4X4_SYMBOLIC_EXECUTION_V1_H
#include "hhs_pass220_ordered4x4_neg4_1_0.h"
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

#define HHS220_ORDERED4X4_OPCODE_COUNT 15U
#define HHS220_ORDERED4X4_SYMBOLIC_ROOT_BYTES 32U

typedef enum HHS220Ordered4x4OpcodeV1 {
 HHS220_4X4_PUSH_SOURCE_MATRIX = 1,
 HHS220_4X4_ORDERED_NEGATE = 2,
 HHS220_4X4_MATRIX_TIMES = 3,
 HHS220_4X4_PUSH_SOURCE_SYMBOL = 4,
 HHS220_4X4_TYPED_QUOTIENT = 5,
 HHS220_4X4_PUSH_NEGATIVE_FOUR = 6,
 HHS220_4X4_NCALC_MATRIX_POWER = 7,
 HHS220_4X4_ORDERED_EQUALITY = 8
} HHS220Ordered4x4OpcodeV1;

typedef struct HHS220Ordered4x4SymbolicExecutionV1 {
 uint32_t struct_size;
 uint32_t version;
 uint32_t steps;
 uint32_t maximum_stack_depth;
 uint32_t matrices_bound;
 uint32_t symbols_bound;
 uint8_t source_identity_verified;
 uint8_t operator_types_verified;
 uint8_t ordered_program_verified;
 uint8_t exact_symbolic_program_executed;
 uint8_t deterministic_symbolic_replay_verified;
 uint8_t expression_equality_proved;
 uint8_t matrix_power_value_derived;
 uint8_t matrix_times_numeric_evaluated;
 uint8_t quotient_value_derived;
 uint8_t typed_s_substituted;
 uint8_t typed_v_substituted;
 uint8_t vm81_admission_executed;
 uint8_t canonical_vm81_mutation_authority;
 uint8_t hash72_commit_authority;
 uint8_t hash216_commit_authority;
 uint8_t reserved[1];
 uint8_t source_sha256[32];
 uint8_t program_sha256[32];
 uint8_t result_node_sha256[32];
 uint8_t ordered_node_roots[HHS220_ORDERED4X4_OPCODE_COUNT][32];
} HHS220Ordered4x4SymbolicExecutionV1;

/* Program is a typed, source-bound constructor graph. This is NOT a new
 * VM81 admission path. It never computes matrix entries or mints receipts.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_ordered4x4_program(
 uint8_t *out_program, size_t capacity, size_t *out_length);
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_ordered4x4_execute_symbolic(
 const uint8_t *source, size_t source_size,
 const uint8_t *program, size_t program_size,
 HHS220Ordered4x4SymbolicExecutionV1 *out_execution);
#ifdef __cplusplus
}
#endif
#endif
