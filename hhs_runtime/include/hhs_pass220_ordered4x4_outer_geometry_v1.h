#ifndef HHS_PASS220_ORDERED4X4_OUTER_GEOMETRY_V1_H
#define HHS_PASS220_ORDERED4X4_OUTER_GEOMETRY_V1_H
#include "hhs_pass220_ordered4x4_parent_preflight_v1.h"
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

#define HHS220_ORDERED4X4_OUTER_BRANCHES 2U
#define HHS220_ORDERED4X4_OUTER_SOURCE_CELLS 16U
#define HHS220_ORDERED4X4_OUTER_INCIDENCES 32U
#define HHS220_ORDERED4X4_DENOMINATOR_BRANCH 0U
#define HHS220_ORDERED4X4_RHS_BRANCH 1U

typedef struct HHS220Ordered4x4OuterIncidenceV1 {
 uint8_t branch_id;
 uint8_t source_matrix_id;
 uint8_t row;
 uint8_t column;
 int8_t source_literal_token;
 uint8_t source_matrix_is_left_operand;
 uint8_t tensor_symbol;
 uint8_t tensor_cell81;
 uint8_t tensor_operation64;
 uint8_t reserved0;
 uint16_t tensor_vm5184_address;
 uint8_t matrix_leaf_root[32];
 uint8_t symbol_binding_root[32];
 uint8_t ordered_incidence_root[32];
} HHS220Ordered4x4OuterIncidenceV1;

typedef struct HHS220Ordered4x4OuterGeometryV1 {
 uint32_t struct_size;
 uint32_t version;
 uint32_t matrix_leaf_count;
 uint32_t ordered_incidence_count;
 uint32_t source_rows;
 uint32_t source_columns;
 uint8_t source_identity_verified;
 uint8_t inherited_hash216_index_preflight_verified;
 uint8_t typed_5184_bindings_verified;
 uint8_t ordered_operand_roles_verified;
 uint8_t complete_source_leaf_coverage_verified;
 uint8_t deterministic_outer_geometry_replay_verified;
 uint8_t s_tensor_action_shape_resolved;
 uint8_t v_tensor_action_shape_resolved;
 uint8_t denominator_value_derived;
 uint8_t rhs_value_derived;
 uint8_t quotient_value_derived;
 uint8_t matrix_power_value_derived;
 uint8_t equation_equality_proved;
 uint8_t parent_signed_authenticity_verified;
 uint8_t vm81_signed_admission_executed;
 uint8_t hash72_commit_authority;
 uint8_t hash216_commit_authority;
 uint8_t canonical_vm81_mutation_authority;
 uint8_t reserved1[1];
 uint8_t source_sha256[32];
 uint8_t parent_reference_sha256[32];
 uint8_t bound_graph_root_sha256[32];
 uint8_t branch_roots_sha256[HHS220_ORDERED4X4_OUTER_BRANCHES][32];
 uint8_t outer_geometry_root_sha256[32];
 HHS220Ordered4x4OuterIncidenceV1
     incidences[HHS220_ORDERED4X4_OUTER_INCIDENCES];
} HHS220Ordered4x4OuterGeometryV1;

/*
 * Build source-locked, ordered branch-incidence geometry for
 *   denominator: MatrixTimes(source 4x4 matrix D, typed object s)
 *   RHS:         MatrixTimes(typed object v, source 4x4 matrix L)
 *
 * s/v are complete address-bearing tensor objects. No vector/matrix rank,
 * broadcast, numeric coefficient, or 4x4 result shape is assumed for them.
 * The 32 output nodes are SOURCE INCIDENCES, NOT evaluated product entries.
 *
 * Parent-reference verification here is structural/index only. Signed
 * authenticity and mutation authority remain solely with inherited VM81.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_ordered4x4_outer_geometry(
 const uint8_t *source, size_t source_bytes,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent_reference,
 HHS220Ordered4x4OuterGeometryV1 *out_geometry
);
#ifdef __cplusplus
}
#endif
#endif
