#ifndef HHS_PASS220_ORDERED4X4_FULL_GRAPH_V1_H
#define HHS_PASS220_ORDERED4X4_FULL_GRAPH_V1_H
#include "hhs_pass220_ordered4x4_numerator_terms_v1.h"
#include "hhs_pass220_ordered4x4_phase_address_v1.h"
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

typedef struct HHS220Ordered4x4FullGraphV1 {
 uint32_t struct_size;
 uint32_t version;
 uint32_t numerator_ordered_product_terms;
 uint32_t numerator_ordered_sum_nodes;
 uint32_t denominator_source_incidences;
 uint32_t rhs_source_incidences;
 uint8_t source_verified;
 uint8_t full_216_index_parent_reference_verified;
 uint8_t typed_s_v_identity_verified;
 uint8_t native_phase_address_verified;
 uint8_t numerator_64_term_graph_executed;
 uint8_t denominator_direction_verified;
 uint8_t rhs_direction_verified;
 uint8_t quotient_order_verified;
 uint8_t negative_fourth_power_order_verified;
 uint8_t equality_gate_source_order_verified;
 uint8_t deterministic_full_graph_replay_verified;
 uint8_t tensor_action_rank_proved;
 uint8_t native_matrix_values_derived;
 uint8_t native_quotient_value_derived;
 uint8_t native_matrix_power_value_derived;
 uint8_t equality_mathematically_proved;
 uint8_t predecessor_pqc_signature_authenticated;
 uint8_t signed_vm81_admission_executed;
 uint8_t hash72_commit_authority;
 uint8_t hash216_commit_authority;
 uint8_t canonical_vm81_mutation_authority;
 uint8_t reserved[3];
 uint8_t source_sha256[32];
 uint8_t parent_reference_sha256[32];
 uint8_t numerator_root_sha256[32];
 uint8_t denominator_root_sha256[32];
 uint8_t rhs_root_sha256[32];
 uint8_t phase_root_sha256[32];
 uint8_t quotient_root_sha256[32];
 uint8_t negative_fourth_power_root_sha256[32];
 uint8_t equality_gate_root_sha256[32];
 uint8_t inherited_bound_symbolic_root_sha256[32];
 uint8_t full_graph_root_sha256[32];
} HHS220Ordered4x4FullGraphV1;

/*
 * Source-locked read-only proof dependency graph; no arithmetic shortcut:
 *
 *    ordered_num  = MatrixTimes(-M1,-M2)        64 terms / 16 sums
 *    ordered_den  = MatrixTimes(D,s)            D left, opaque s right
 *    quotient     = OrderedDivide(num,den)     no scalar inverse
 *    neg4         = NcalcMatrixPower(quotient,(-4))  exact source token
 *    ordered_rhs  = MatrixTimes(v,L)            opaque v left, L right
 *    equality     = OrderedGate(neg4,rhs)
 *
 * Input tensor rank and action semantics are not inferred. All hashes are
 * non-authoritative diagnostic identities, NEVER canonical Hash72/216.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_ordered4x4_full_graph(
 const uint8_t *source, size_t source_size,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,
 HHS220Ordered4x4FullGraphV1 *out_graph
);
#ifdef __cplusplus
}
#endif
#endif
