#ifndef HHS_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_1_48_H
#define HHS_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_1_48_H

#include "hhs_pass219_lane5_direct_witness_routing_1_46.h"
#include "hhs_pass219_delta_reciprocal_constructor_1_36.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION UINT32_C(0x00010030)
#define HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_NAMESPACE UINT32_C(0x00021930)
#define HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_DIGEST_BYTES UINT32_C(32)
#define HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES HHS_EXACT_PASS219_FULL_MANIFOLD_MODULUS_BYTES
#define HHS_EXACT_PASS219_LANE5_UNBOUNDED_MIN_EVIDENCE HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_MIN_EVIDENCE
#define HHS_EXACT_PASS219_LANE5_UNBOUNDED_MIN_CONTRADICTION_CHECKS HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_MIN_CONTRADICTION_CHECKS

typedef struct HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t full_manifold_address_bytes;
    uint8_t full_manifold_bigint_addressing;
    uint8_t modulus_is_72_pow_72;
    uint8_t any_byte_serializable_workload;
    uint8_t workload_class_agnostic;
    uint8_t streaming_candidate_ingress;
    uint8_t constant_memory_candidate_reduction;
    uint8_t fixed_candidate_batch_required;
    uint8_t intermediate_materialization_required;
    uint8_t previous_current_goal_bound;
    uint8_t provenance_bound;
    uint8_t contradiction_boundary_bound;
    uint8_t exact_reciprocal_phase_inversion;
    uint8_t balanced_trinary_collapse;
    uint8_t binary_qubit_collapse;
    uint8_t nested_zero_layer;
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
} HHSExactPass219Lane5UnboundedWorkloadAuthorityV1;

typedef struct HHSExactPass219Lane5UnboundedWorkloadRouteV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactBigUIntView previous_address;
    HHSExactBigUIntView current_address;
    HHSExactBigUIntView goal_address;
    HHSExactBigUIntView candidate_address;
    uint8_t workload_sha256[HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_DIGEST_BYTES];
    uint8_t provenance_sha256[HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_DIGEST_BYTES];
    uint8_t forbidden_boundary_sha256[HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_DIGEST_BYTES];
    uint8_t reciprocal_witness_sha256[HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_DIGEST_BYTES];
    uint8_t route_witness_sha256[HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_DIGEST_BYTES];
    uint64_t workload_byte_count;
    uint64_t integer_route_cost;
    uint32_t evidence_count;
    uint32_t contradiction_check_count;
    uint32_t materialized_intermediate_states;
    uint32_t phase_slot;
    uint32_t inverse_phase_slot;
    int8_t trinary_collapse;
    uint8_t binary_collapse;
    uint8_t nested_zero_slot;
    uint8_t workload_serialization_exact;
    uint8_t source_digest_verified;
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
    uint8_t reserved0[2];
} HHSExactPass219Lane5UnboundedWorkloadRouteV1;

typedef struct HHSExactPass219Lane5UnboundedWorkloadReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t candidate_address_length;
    uint8_t candidate_address_be[HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES];
    uint8_t workload_sha256[HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_DIGEST_BYTES];
    uint8_t provenance_sha256[HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_DIGEST_BYTES];
    uint8_t route_witness_sha256[HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_DIGEST_BYTES];
    uint64_t workload_byte_count;
    uint64_t integer_route_cost;
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
    uint8_t full_manifold_coordinate_capable;
    uint8_t workload_class_agnostic;
    uint8_t materialized_intermediate_states;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0[2];
} HHSExactPass219Lane5UnboundedWorkloadReceiptV1;

typedef struct HHSExactPass219Lane5UnboundedWorkloadStreamV1 {
    uint32_t struct_size;
    uint32_t version;
    uint64_t candidates_seen;
    uint64_t admissible_candidates;
    uint64_t rejected_candidates;
    uint64_t workload_binding_signature64;
    uint8_t count_saturated;
    uint8_t has_binding;
    uint8_t has_best;
    uint8_t finalized;
    uint8_t reserved0[4];
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 best_receipt;
} HHSExactPass219Lane5UnboundedWorkloadStreamV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_unbounded_workload_scaling_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_unbounded_workload_scaling_authority(
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_unbounded_workload_route_validate(
    const HHSExactPass219Lane5UnboundedWorkloadRouteV1 *route,
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 *out_receipt
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_unbounded_workload_stream_init(
    HHSExactPass219Lane5UnboundedWorkloadStreamV1 *stream
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_unbounded_workload_stream_consider(
    HHSExactPass219Lane5UnboundedWorkloadStreamV1 *stream,
    const HHSExactPass219Lane5UnboundedWorkloadRouteV1 *route,
    uint8_t *out_candidate_admitted
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_unbounded_workload_stream_finalize(
    HHSExactPass219Lane5UnboundedWorkloadStreamV1 *stream,
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
