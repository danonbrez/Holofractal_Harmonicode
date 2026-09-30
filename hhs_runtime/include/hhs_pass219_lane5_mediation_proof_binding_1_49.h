#ifndef HHS_PASS219_LANE5_MEDIATION_PROOF_BINDING_1_49_H
#define HHS_PASS219_LANE5_MEDIATION_PROOF_BINDING_1_49_H

#include "hhs_pass219_lane5_unbounded_workload_scaling_1_48.h"
#include "hhs_pass219_rna_vm5184_abi_1_33.h"
#include "hhs_pass219_lane5_executable_capability_self_model_1_43.h"
#include "hhs_pass219_harmonicode_global_constraint_membrane_1_21_9.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_VERSION UINT32_C(0x00010031)
#define HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_NAMESPACE UINT32_C(0x00021931)
#define HHS_EXACT_PASS219_LANE5_ZERO_SUM_RESIDUAL_COUNT UINT32_C(8)
#define HHS_EXACT_PASS219_LANE5_MEDIATION_ENVIRONMENT_ROOT_BYTES UINT32_C(32)

typedef struct HHSExactPass219Lane5MediationProofBindingAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint8_t legacy_1_34_proof_flags_authoritative;
    uint8_t legacy_mediation_recomputed;
    uint8_t exact_vm5184_recomputed;
    uint8_t rna_cpp_cell_wall_replayed;
    uint8_t hash216_sha256_positions_verified;
    uint8_t capability_registry_recomputed;
    uint8_t direct_witness_route_recomputed;
    uint8_t global_constraint_membrane_recomputed;
    uint8_t global_environment_request_bound;
    uint8_t exact_zero_sum_residual_vector_derived;
    uint8_t deterministic_proof_binding;
    uint8_t candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0[4];
} HHSExactPass219Lane5MediationProofBindingAuthorityV1;

typedef struct HHSExactPass219Lane5ZeroSumClosureWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    int64_t state_change_residual;
    int64_t dependency_change_residual;
    int64_t phase_change_residual;
    int64_t resource_work_residual;
    int64_t lineage_residual;
    int64_t inverse_recovery_residual;
    int64_t local_constraint_residual;
    int64_t global_constraint_residual;
    uint64_t request_signature64;
    uint64_t candidate_signature64;
    uint64_t parent_hash216_signature64;
    uint64_t rna_prepared_signature64;
    uint64_t rna_decision_signature64;
    uint64_t capability_registry_signature64;
    uint64_t direct_witness_receipt_signature64;
    uint64_t global_membrane_signature64;
    uint64_t witness_signature64;
} HHSExactPass219Lane5ZeroSumClosureWitnessV1;

typedef struct HHSExactPass219Lane5MediationProofBundleV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t hash216_reference_count;
    uint8_t feedback_lane;
    int8_t feedback_trinary;
    uint8_t reserved0[2];
    const HHSExactUQCELInputV1 *input;
    const HHSExactVM81Frame *candidate_frame;
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference;
    const HHSExactPass219Holo4PreparedV1 *rna_prepared;
    const HHSExactPass219Holo4DecisionV1 *rna_decision;
    const HHSExactPass219Hash216TransitionViewV1 *hash216_references;
    const HHSExactPass219Lane5CapabilitySelfModelDescriptorV1 *capability_descriptor;
    const HHSExactPass219Lane5CapabilitySelfModelReceiptV1 *capability_receipt;
    const HHSExactPass219Lane5DirectWitnessRouteV1 *direct_witness_route;
    const HHSExactPass219Lane5DirectWitnessReceiptV1 *direct_witness_receipt;
    const HHSExactPass219GlobalMembraneInputV1 *global_membrane_input;
    const HHSExactPass219GlobalMembraneResultV1 *global_membrane_result;
} HHSExactPass219Lane5MediationProofBundleV1;

typedef struct HHSExactPass219Lane5ProvenMediationReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t hash216_reference_count;
    uint32_t capability_reference_count;
    HHSExactPass219Lane5MediationReceiptV1 base_receipt;
    HHSExactPass219Lane5ZeroSumClosureWitnessV1 zero_sum_witness;
    uint64_t candidate_frame_signature64;
    uint64_t parent_hash216_signature64;
    uint64_t hash216_reference_set_signature64;
    uint64_t capability_receipt_signature64;
    uint64_t direct_witness_receipt_signature64;
    uint64_t global_membrane_signature64;
    uint64_t proof_binding_signature64;
    uint8_t legacy_mediation_recomputed;
    uint8_t exact_vm5184_bound;
    uint8_t rna_cell_wall_bound;
    uint8_t hash216_references_validated;
    uint8_t capability_registry_validated;
    uint8_t direct_witness_route_validated;
    uint8_t global_constraint_membrane_validated;
    uint8_t zero_sum_closure_passed;
    uint8_t all_proofs_bound;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t requires_environmental_admission;
    uint8_t reserved0;
} HHSExactPass219Lane5ProvenMediationReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_mediation_proof_binding_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_mediation_proof_binding_authority(
    HHSExactPass219Lane5MediationProofBindingAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_mediation_frame_signature(
    const HHSExactVM81Frame *frame,
    uint64_t *out_signature64
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_mediation_hash216_reference_signature(
    const HHSExactPass219Hash216TransitionViewV1 *reference,
    uint64_t *out_signature64
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_mediation_environment_root(
    const HHSExactPass219Lane5MediationRequestV1 *request,
    const HHSExactPass219Lane5DirectWitnessReceiptV1 *direct_witness_receipt,
    uint8_t out_root[HHS_EXACT_PASS219_LANE5_MEDIATION_ENVIRONMENT_ROOT_BYTES]
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_mediation_proof_bind(
    const HHSExactPass219Lane5MediationRequestV1 *request,
    const HHSExactPass219Lane5MediationProofBundleV1 *proof,
    HHSExactPass219Lane5ProvenMediationReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
