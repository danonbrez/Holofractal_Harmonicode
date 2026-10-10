#ifndef HHS_PASS220_ORDERED4X4_TYPED_BINDINGS_V1_H
#define HHS_PASS220_ORDERED4X4_TYPED_BINDINGS_V1_H
#include "hhs_pass220_ordered4x4_symbolic_execution_v1.h"
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

#define HHS220_ORDERED4X4_NATIVE_CHARACTERS 5184U
#define HHS220_ORDERED4X4_MAX_UTF8_BYTES (5184U*4U)
#define HHS220_ORDERED4X4_PARENT_GLYPHS 216U

typedef struct HHS220Ordered4x4NativeTensorBindingV1 {
 uint32_t struct_size;
 uint8_t symbol; /* 's' or 'v'; source-locked role, not host scalar */
 uint8_t cell81;
 uint8_t operation64;
 uint8_t reserved;
 const uint8_t *state_utf8;
 size_t state_bytes;
 const uint8_t *predecessor_hash216;
 size_t predecessor_bytes;
} HHS220Ordered4x4NativeTensorBindingV1;

typedef struct HHS220Ordered4x4BoundExecutionV1 {
 uint32_t struct_size;
 uint32_t version;
 uint32_t ordered_opcodes;
 uint32_t maximum_stack_depth;
 uint32_t s_codepoints;
 uint32_t v_codepoints;
 uint32_t s_serialized_bytes;
 uint32_t v_serialized_bytes;
 uint16_t s_vm5184_address;
 uint16_t v_vm5184_address;
 uint8_t source_identity_verified;
 uint8_t ordered_type_graph_executed;
 uint8_t deterministic_bound_graph_replay_verified;
 uint8_t typed_bindings_shape_verified;
 uint8_t native_predecessor_identity_matched;
 uint8_t native_binding_authenticity_verified;
 uint8_t s_value_scalarized;
 uint8_t v_value_scalarized;
 uint8_t matrix_times_value_derived;
 uint8_t matrix_quotient_value_derived;
 uint8_t matrix_power_value_derived;
 uint8_t equation_equality_proved;
 uint8_t vm81_admission_executed;
 uint8_t hash72_commit_authority;
 uint8_t hash216_commit_authority;
 uint8_t canonical_vm81_mutation_authority;
 uint8_t binding_roots_sha256[2][32];
 uint8_t ordered_node_roots[HHS220_ORDERED4X4_OPCODE_COUNT][32];
 uint8_t result_root_sha256[32];
} HHS220Ordered4x4BoundExecutionV1;

/*
 * Shape/provenance-preserving candidate ingress for full 5184-character
 * UTF-8 HARMONICODE tensor state objects. This entry point NEVER authenticates
 * a signed predecessor; thus authenticity_verified stays false. Only a
 * separate inherited VM81 signed admission may establish canonical validity.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_ordered4x4_execute_bound(
 const uint8_t *source, size_t source_size,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 HHS220Ordered4x4BoundExecutionV1 *out_execution
);
#ifdef __cplusplus
}
#endif
#endif
