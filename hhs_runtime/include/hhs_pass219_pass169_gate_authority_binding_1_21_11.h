#ifndef HHS_PASS219_PASS169_GATE_AUTHORITY_BINDING_1_21_11_H
#define HHS_PASS219_PASS169_GATE_AUTHORITY_BINDING_1_21_11_H

#include "hhs_pass219_harmonicode_global_constraint_membrane_1_21_9.h"
#include "hhs_pass219_pass159_global_witness_provenance_1_21_10.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_PASS169_BINDING_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_PASS169_BINDING_VERSION_MINOR 21U
#define HHS_EXACT_PASS219_PASS169_BINDING_VERSION_PATCH 11U
#define HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES 32U
#define HHS_EXACT_PASS219_PASS169_BINDING_GATE_COUNT 5U
#define HHS_EXACT_PASS219_PASS169_BINDING_HASH216_LEN 216U
#define HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN 217U
#define HHS_EXACT_PASS219_PASS169_BINDING_HASH72_LEN 72U
#define HHS_EXACT_PASS219_PASS169_BINDING_HASH72_STRLEN 73U

typedef enum HHSExactPass219Pass169BindingDecisionV1 {
    HHS_EXACT_PASS219_PASS169_BINDING_UNRESOLVED = 0,
    HHS_EXACT_PASS219_PASS169_BINDING_REJECT = 1,
    HHS_EXACT_PASS219_PASS169_BINDING_PROPAGATE = 2
} HHSExactPass219Pass169BindingDecisionV1;

typedef enum HHSExactPass219Pass169BindingReasonV1 {
    HHS_EXACT_PASS219_PASS169_BINDING_REASON_NONE = 0U,
    HHS_EXACT_PASS219_PASS169_BINDING_REASON_PROVIDER_UNAVAILABLE = 1U << 0,
    HHS_EXACT_PASS219_PASS169_BINDING_REASON_PROVENANCE_INVALID = 1U << 1,
    HHS_EXACT_PASS219_PASS169_BINDING_REASON_PROVIDER_REJECTED = 1U << 2,
    HHS_EXACT_PASS219_PASS169_BINDING_REASON_SOURCE_IDENTITY_MISMATCH = 1U << 3,
    HHS_EXACT_PASS219_PASS169_BINDING_REASON_PIPELINE_IDENTITY_MISMATCH = 1U << 4,
    HHS_EXACT_PASS219_PASS169_BINDING_REASON_GATE_PROVENANCE_MISMATCH = 1U << 5,
    HHS_EXACT_PASS219_PASS169_BINDING_REASON_RECEIPT_IDENTITY_INVALID = 1U << 6,
    HHS_EXACT_PASS219_PASS169_BINDING_REASON_AUTHORITY_EVIDENCE_INCOMPLETE = 1U << 7,
    HHS_EXACT_PASS219_PASS169_BINDING_REASON_MEMBRANE_REJECTED = 1U << 8
} HHSExactPass219Pass169BindingReasonV1;

typedef struct HHSExactPass219Pass169BindingDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t combined_source_sha256[HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES];
    uint32_t gate_count;
    uint8_t pass169_contract_anchor_is_authorization_only;
    uint8_t linked_runtime_provider_required;
    uint8_t linked_runtime_provider_available;
    uint8_t test_fixture_is_authority;
    uint8_t pass159_can_substitute_for_pass169;
    uint8_t candidate_vm81_can_substitute_for_pass169;
    uint8_t canonical_monolithic_proof;
    uint8_t floating_point_authority;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t persistence_mutation_authority;
    uint8_t reserved0[1];
} HHSExactPass219Pass169BindingDescriptorV1;

typedef struct HHSExactPass219Pass169AuthorityProofV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t combined_source_sha256[HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES];
    uint8_t pass159_provenance_root[HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES];

    char source_hash216[HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN];
    char tokens_hash216[HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN];
    char cst_hash216[HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN];
    char ast_hash216[HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN];
    char type_environment_hash216[HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN];
    char constraint_graph_hash216[HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN];
    char hir_hash216[HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN];
    char vmir_hash216[HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN];

    uint8_t canonical_global_symbol_environment_root[
        HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES
    ];
    uint32_t gate_count;
    HHSExactPass219GlobalGateWitnessV1 gates[HHS_EXACT_PASS219_PASS169_BINDING_GATE_COUNT];

    char proof_hash216[HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN];
    char transition_hash216[HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN];
    char receipt_hash72[HHS_EXACT_PASS219_PASS169_BINDING_HASH72_STRLEN];
    char replay_hash72[HHS_EXACT_PASS219_PASS169_BINDING_HASH72_STRLEN];
    uint64_t vm81_steps;
    uint64_t replay_vm81_steps;

    uint8_t whole_expression_constraint_graph_verified;
    uint8_t exact_vm81_admission_verified;
    uint8_t atomic_commit_verified;
    uint8_t hash72_receipt_verified;
    uint8_t hash216_proof_identity_verified;
    uint8_t deterministic_replay_verified;
    uint8_t source_reconstruction_verified;
    uint8_t shared_environment_revalidated;
    uint8_t local_symbol_shadowing_detected;
    uint8_t canonical_monolithic_proof;
    uint8_t floating_point_authority;
    uint8_t reserved0[5];
} HHSExactPass219Pass169AuthorityProofV1;

typedef struct HHSExactPass219Pass169BindingResultV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason_mask;
    uint8_t runtime_provider_available;
    uint8_t pass159_provenance_exact;
    uint8_t pass169_authority_verified;
    uint8_t boolean_gate_results_available;
    uint8_t membrane_input_ready;
    uint8_t canonical_monolithic_proof;
    uint8_t whole_equation_propagated;
    uint8_t test_fixture_authority_claimed;
    uint8_t floating_point_authority;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t persistence_mutation_authority;
    uint8_t reserved0[4];
    char proof_hash216[HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN];
    char transition_hash216[HHS_EXACT_PASS219_PASS169_BINDING_HASH216_STRLEN];
    char receipt_hash72[HHS_EXACT_PASS219_PASS169_BINDING_HASH72_STRLEN];
    char replay_hash72[HHS_EXACT_PASS219_PASS169_BINDING_HASH72_STRLEN];
    HHSExactPass219GlobalMembraneResultV1 membrane_result;
} HHSExactPass219Pass169BindingResultV1;

/*
 * Optional Pass169 provider ABI expected by I121.11.
 *
 * The canonical repository currently has no production implementation of this
 * symbol. I121.11 probes it weakly. Tests may provide a fixture definition, but
 * a fixture definition is never repository Pass169 authority.
 */
HHSExactStatus hhs_pass169_verify_combined_gate_authority_1_21_11(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    HHSExactPass219Pass169AuthorityProofV1 *out_proof
);

HHS_EXACT_API uint32_t hhs_exact_pass219_pass169_binding_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_pass169_binding_descriptor(
    HHSExactPass219Pass169BindingDescriptorV1 *out_descriptor
);

/*
 * Bind one exact I121.10 provenance record to one linked Pass169 provider.
 *
 * When no provider is linked, this returns OK with UNRESOLVED and leaves
 * membrane_input_ready false. When a provider is linked, every source,
 * pipeline, gate, receipt, replay, and authority invariant is rechecked before
 * I121.9 is called. This function never evaluates algebra, mutates VM81, mints
 * Hash72, or persists canonical state.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_pass169_bind_authority(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    HHSExactPass219Pass169BindingResultV1 *out_result
);

#ifdef __cplusplus
}
#endif

#endif
