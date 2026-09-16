#ifndef HHS_PASS219_LANE5_DIRECT_WITNESS_ROUTING_1_46_H
#define HHS_PASS219_LANE5_DIRECT_WITNESS_ROUTING_1_46_H

#include "hhs_pass219_hash216_fractal_qudit_admission_1_45.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_ROUTING_VERSION UINT32_C(0x0001002E)
#define HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_ROUTING_NAMESPACE UINT32_C(0x0002192E)
#define HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_PHASE_CYCLE UINT32_C(72)
#define HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_PHASE_HALF UINT32_C(36)
#define HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_PHASE_QUARTER UINT32_C(18)
#define HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_MIN_EVIDENCE UINT32_C(5)
#define HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_MIN_CONTRADICTION_CHECKS UINT32_C(1)

typedef struct HHSExactPass219Lane5DirectWitnessAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t phase_cycle;
    uint32_t phase_quarter;
    uint8_t bigint_serialization_addressed;
    uint8_t direct_composition_jump;
    uint8_t intermediate_materialization_required;
    uint8_t previous_current_witness_bound;
    uint8_t goal_bound;
    uint8_t contradiction_boundary_bound;
    uint8_t exact_reciprocal_phase_inversion;
    uint8_t balanced_trinary_collapse;
    uint8_t binary_qubit_collapse;
    uint8_t nested_zero_layer;
    uint8_t integer_only_route_cost;
    uint8_t deterministic_tie_break;
    uint8_t candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t floating_point_canonical_authority;
    uint8_t reserved0[3];
} HHSExactPass219Lane5DirectWitnessAuthorityV1;

typedef struct HHSExactPass219Lane5DirectWitnessRouteV1 {
    uint32_t struct_size;
    uint32_t version;
    uint64_t previous_signature64;
    uint64_t current_signature64;
    uint64_t provenance_signature64;
    uint64_t goal_signature64;
    uint64_t forbidden_boundary_signature64;
    uint64_t reciprocal_inverse_signature64;
    uint64_t candidate_signature64;
    uint64_t route_signature64;
    uint64_t represented_span;
    uint64_t integer_route_cost;
    uint32_t evidence_count;
    uint32_t contradiction_check_count;
    uint32_t materialized_intermediate_states;
    uint32_t phase_slot;
    uint32_t inverse_phase_slot;
    int8_t trinary_collapse;
    uint8_t binary_collapse;
    uint8_t nested_zero_slot;
    uint8_t replay_witness_verified;
    uint8_t exact_goal_reached;
    uint8_t contradiction_free;
    uint8_t goal_forbidden_conflict;
    uint8_t reciprocal_phase_verified;
    uint8_t bigint_serialization_addressed;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0[3];
} HHSExactPass219Lane5DirectWitnessRouteV1;

typedef struct HHSExactPass219Lane5DirectWitnessReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t selected_candidate_index;
    uint64_t represented_span;
    uint64_t integer_route_cost;
    uint64_t avoided_intermediate_states;
    uint64_t descriptor_signature64;
    uint64_t route_receipt_signature64;
    uint32_t phase_slot;
    uint32_t inverse_phase_slot;
    int8_t trinary_collapse;
    uint8_t binary_collapse;
    uint8_t nested_zero_slot;
    uint8_t accepted;
    uint8_t optimizer_selected;
    uint8_t replay_witness_verified;
    uint8_t exact_goal_reached;
    uint8_t contradiction_free;
    uint8_t reciprocal_phase_verified;
    uint8_t bigint_serialization_addressed;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0[3];
} HHSExactPass219Lane5DirectWitnessReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_direct_witness_routing_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_direct_witness_routing_authority(
    HHSExactPass219Lane5DirectWitnessAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_direct_witness_route_validate(
    const HHSExactPass219Lane5DirectWitnessRouteV1 *route,
    HHSExactPass219Lane5DirectWitnessReceiptV1 *out_receipt
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_direct_witness_route_optimize(
    const HHSExactPass219Lane5DirectWitnessRouteV1 *routes,
    uint32_t route_count,
    HHSExactPass219Lane5DirectWitnessReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
