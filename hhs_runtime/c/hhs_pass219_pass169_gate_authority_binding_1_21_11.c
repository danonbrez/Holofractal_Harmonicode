#include "hhs_pass219_pass169_gate_authority_binding_1_21_11.h"

#include <string.h>

#if defined(__GNUC__) || defined(__clang__)
extern HHSExactStatus hhs_pass169_verify_combined_gate_authority_1_21_11(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    HHSExactPass219Pass169AuthorityProofV1 *out_proof
) __attribute__((weak));
#define HHS219_I12111_HAS_WEAK_PROVIDER 1
#else
#define HHS219_I12111_HAS_WEAK_PROVIDER 0
#endif

static const uint8_t HHS219_I12111_SOURCE_SHA256[
    HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES
] = {
    0x33U, 0x15U, 0x64U, 0x1cU, 0x8dU, 0x6aU, 0xa9U, 0xfcU,
    0x4fU, 0x39U, 0x18U, 0xecU, 0xcdU, 0xa8U, 0xe3U, 0xa4U,
    0x0cU, 0x84U, 0x45U, 0xccU, 0x41U, 0x7aU, 0x65U, 0xe5U,
    0xdeU, 0xa6U, 0x83U, 0xf6U, 0x80U, 0x20U, 0xcfU, 0x53U
};

static const uint32_t HHS219_I12111_GATE_OFFSETS[
    HHS_EXACT_PASS219_PASS169_BINDING_GATE_COUNT
] = {96U, 240U, 266U, 274U, 285U};

static uint32_t hhs219_i12111_version_word(void) {
    return (HHS_EXACT_PASS219_PASS169_BINDING_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_PASS169_BINDING_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_PASS169_BINDING_VERSION_PATCH;
}

static uint32_t hhs219_i12110_version_word(void) {
    return (HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_VERSION_PATCH;
}

static int hhs219_i12111_provider_available(void) {
#if HHS219_I12111_HAS_WEAK_PROVIDER
    return hhs_pass169_verify_combined_gate_authority_1_21_11 != NULL;
#else
    return 0;
#endif
}

static int hhs219_i12111_root_nonzero(
    const uint8_t root[HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES]
) {
    size_t i;
    uint8_t aggregate = 0U;
    if (root == NULL)
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES; ++i)
        aggregate = (uint8_t)(aggregate | root[i]);
    return aggregate != 0U;
}

static int hhs219_i12111_hash_string_valid(const char *value, size_t length) {
    size_t i;
    if (value == NULL || value[length] != '\0')
        return 0;
    for (i = 0U; i < length; ++i) {
        if (value[i] == '\0' || strchr(HHS_EXACT_HASH72_ALPHABET, value[i]) == NULL)
            return 0;
    }
    return 1;
}

static int hhs219_i12111_provenance_valid(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance
) {
    size_t i;
    const char *hashes[8];
    if (provenance == NULL || provenance->struct_size < sizeof(*provenance) ||
        provenance->version != hhs219_i12110_version_word())
        return 0;
    if (provenance->source_length != HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SOURCE_BYTES ||
        provenance->gate_count != HHS_EXACT_PASS219_PASS169_BINDING_GATE_COUNT)
        return 0;
    if (memcmp(provenance->combined_source_sha256,
               HHS219_I12111_SOURCE_SHA256,
               sizeof(HHS219_I12111_SOURCE_SHA256)) != 0)
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_PASS169_BINDING_GATE_COUNT; ++i) {
        if (provenance->gate_offsets[i] != HHS219_I12111_GATE_OFFSETS[i])
            return 0;
    }
    if (!provenance->source_identity_exact ||
        !provenance->gate_occurrence_provenance_exact ||
        !provenance->frontend_chain_complete ||
        !provenance->source_root_lineage_exact ||
        !provenance->pass159_whole_expression_provenance_verified ||
        provenance->boolean_gate_results_available ||
        provenance->membrane_input_ready ||
        !provenance->pass169_whole_expression_authority_required ||
        provenance->canonical_monolithic_proof ||
        provenance->floating_point_authority ||
        provenance->vm81_mutation_authority ||
        provenance->hash72_commit_authority ||
        provenance->persistence_mutation_authority ||
        !hhs219_i12111_root_nonzero(provenance->global_symbol_environment_root))
        return 0;

    hashes[0] = provenance->source_hash216;
    hashes[1] = provenance->tokens_hash216;
    hashes[2] = provenance->cst_hash216;
    hashes[3] = provenance->ast_hash216;
    hashes[4] = provenance->type_environment_hash216;
    hashes[5] = provenance->constraint_graph_hash216;
    hashes[6] = provenance->hir_hash216;
    hashes[7] = provenance->vmir_hash216;
    for (i = 0U; i < 8U; ++i) {
        if (!hhs219_i12111_hash_string_valid(
                hashes[i], HHS_EXACT_PASS219_PASS169_BINDING_HASH216_LEN))
            return 0;
    }
    return 1;
}

static int hhs219_i12111_pipeline_matches(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    const HHSExactPass219Pass169AuthorityProofV1 *proof
) {
    const char *provenance_hashes[8];
    const char *proof_hashes[8];
    size_t i;
    provenance_hashes[0] = provenance->source_hash216;
    provenance_hashes[1] = provenance->tokens_hash216;
    provenance_hashes[2] = provenance->cst_hash216;
    provenance_hashes[3] = provenance->ast_hash216;
    provenance_hashes[4] = provenance->type_environment_hash216;
    provenance_hashes[5] = provenance->constraint_graph_hash216;
    provenance_hashes[6] = provenance->hir_hash216;
    provenance_hashes[7] = provenance->vmir_hash216;

    proof_hashes[0] = proof->source_hash216;
    proof_hashes[1] = proof->tokens_hash216;
    proof_hashes[2] = proof->cst_hash216;
    proof_hashes[3] = proof->ast_hash216;
    proof_hashes[4] = proof->type_environment_hash216;
    proof_hashes[5] = proof->constraint_graph_hash216;
    proof_hashes[6] = proof->hir_hash216;
    proof_hashes[7] = proof->vmir_hash216;

    for (i = 0U; i < 8U; ++i) {
        if (!hhs219_i12111_hash_string_valid(
                proof_hashes[i], HHS_EXACT_PASS219_PASS169_BINDING_HASH216_LEN) ||
            memcmp(provenance_hashes[i], proof_hashes[i],
                   HHS_EXACT_PASS219_PASS169_BINDING_HASH216_LEN) != 0)
            return 0;
    }
    return 1;
}

static int hhs219_i12111_gate_bundle_valid(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    const HHSExactPass219Pass169AuthorityProofV1 *proof
) {
    size_t i;
    uint32_t membrane_version = hhs_exact_pass219_global_membrane_version();
    if (proof->gate_count != HHS_EXACT_PASS219_PASS169_BINDING_GATE_COUNT ||
        !hhs219_i12111_root_nonzero(proof->canonical_global_symbol_environment_root))
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_PASS169_BINDING_GATE_COUNT; ++i) {
        const HHSExactPass219GlobalGateWitnessV1 *gate = &proof->gates[i];
        if (gate->struct_size < sizeof(*gate) || gate->version != membrane_version ||
            gate->gate_index != (uint32_t)i ||
            gate->source_offset != provenance->gate_offsets[i] ||
            gate->boolean_result > 1U ||
            memcmp(gate->combined_source_sha256,
                   provenance->combined_source_sha256,
                   HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES) != 0 ||
            memcmp(gate->global_symbol_environment_root,
                   proof->canonical_global_symbol_environment_root,
                   HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES) != 0)
            return 0;
    }
    return 1;
}

static int hhs219_i12111_receipt_identity_valid(
    const HHSExactPass219Pass169AuthorityProofV1 *proof
) {
    if (!hhs219_i12111_hash_string_valid(
            proof->proof_hash216, HHS_EXACT_PASS219_PASS169_BINDING_HASH216_LEN) ||
        !hhs219_i12111_hash_string_valid(
            proof->transition_hash216, HHS_EXACT_PASS219_PASS169_BINDING_HASH216_LEN) ||
        !hhs219_i12111_hash_string_valid(
            proof->receipt_hash72, HHS_EXACT_PASS219_PASS169_BINDING_HASH72_LEN) ||
        !hhs219_i12111_hash_string_valid(
            proof->replay_hash72, HHS_EXACT_PASS219_PASS169_BINDING_HASH72_LEN) ||
        proof->vm81_steps == 0U || proof->replay_vm81_steps == 0U)
        return 0;
    return 1;
}

static int hhs219_i12111_authority_evidence_complete(
    const HHSExactPass219Pass169AuthorityProofV1 *proof
) {
    return proof->whole_expression_constraint_graph_verified == 1U &&
           proof->exact_vm81_admission_verified == 1U &&
           proof->atomic_commit_verified == 1U &&
           proof->hash72_receipt_verified == 1U &&
           proof->hash216_proof_identity_verified == 1U &&
           proof->deterministic_replay_verified == 1U &&
           proof->source_reconstruction_verified == 1U &&
           proof->shared_environment_revalidated == 1U &&
           proof->local_symbol_shadowing_detected == 0U &&
           proof->canonical_monolithic_proof == 1U &&
           proof->floating_point_authority == 0U;
}

uint32_t hhs_exact_pass219_pass169_binding_version(void) {
    return hhs219_i12111_version_word();
}

HHSExactStatus hhs_exact_pass219_pass169_binding_descriptor(
    HHSExactPass219Pass169BindingDescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = hhs219_i12111_version_word();
    memcpy(out_descriptor->combined_source_sha256,
           HHS219_I12111_SOURCE_SHA256,
           sizeof(HHS219_I12111_SOURCE_SHA256));
    out_descriptor->gate_count = HHS_EXACT_PASS219_PASS169_BINDING_GATE_COUNT;
    out_descriptor->pass169_contract_anchor_is_authorization_only = 1U;
    out_descriptor->linked_runtime_provider_required = 1U;
    out_descriptor->linked_runtime_provider_available =
        (uint8_t)hhs219_i12111_provider_available();
    out_descriptor->test_fixture_is_authority = 0U;
    out_descriptor->pass159_can_substitute_for_pass169 = 0U;
    out_descriptor->candidate_vm81_can_substitute_for_pass169 = 0U;
    out_descriptor->canonical_monolithic_proof = 0U;
    out_descriptor->floating_point_authority = 0U;
    out_descriptor->vm81_mutation_authority = 0U;
    out_descriptor->hash72_commit_authority = 0U;
    out_descriptor->persistence_mutation_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_pass169_bind_authority(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    HHSExactPass219Pass169BindingResultV1 *out_result
) {
    HHSExactPass219Pass169AuthorityProofV1 proof;
    HHSExactPass219GlobalMembraneInputV1 input;
    HHSExactStatus status;

    if (provenance == NULL || out_result == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_result, 0, sizeof(*out_result));
    out_result->struct_size = (uint32_t)sizeof(*out_result);
    out_result->version = hhs219_i12111_version_word();
    out_result->decision = HHS_EXACT_PASS219_PASS169_BINDING_UNRESOLVED;
    out_result->runtime_provider_available =
        (uint8_t)hhs219_i12111_provider_available();
    out_result->test_fixture_authority_claimed = 0U;
    out_result->floating_point_authority = 0U;
    out_result->vm81_mutation_authority = 0U;
    out_result->hash72_commit_authority = 0U;
    out_result->persistence_mutation_authority = 0U;

    if (!hhs219_i12111_provenance_valid(provenance)) {
        out_result->reason_mask = HHS_EXACT_PASS219_PASS169_BINDING_REASON_PROVENANCE_INVALID;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_result->pass159_provenance_exact = 1U;

    if (!out_result->runtime_provider_available) {
        out_result->reason_mask = HHS_EXACT_PASS219_PASS169_BINDING_REASON_PROVIDER_UNAVAILABLE;
        return HHS_EXACT_STATUS_OK;
    }

    memset(&proof, 0, sizeof(proof));
    status = hhs_pass169_verify_combined_gate_authority_1_21_11(provenance, &proof);
    if (status == HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN) {
        out_result->decision = HHS_EXACT_PASS219_PASS169_BINDING_UNRESOLVED;
        out_result->reason_mask =
            HHS_EXACT_PASS219_PASS169_BINDING_REASON_FULL_SYMBOLIC_UNRESOLVED;
        return HHS_EXACT_STATUS_OK;
    }
    if (status != HHS_EXACT_STATUS_OK) {
        out_result->decision = HHS_EXACT_PASS219_PASS169_BINDING_REJECT;
        out_result->reason_mask = HHS_EXACT_PASS219_PASS169_BINDING_REASON_PROVIDER_REJECTED;
        return status;
    }

    if (proof.struct_size < sizeof(proof) || proof.version != hhs219_i12111_version_word()) {
        out_result->decision = HHS_EXACT_PASS219_PASS169_BINDING_REJECT;
        out_result->reason_mask = HHS_EXACT_PASS219_PASS169_BINDING_REASON_PROVIDER_REJECTED;
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    }

    if (memcmp(proof.combined_source_sha256,
               provenance->combined_source_sha256,
               HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES) != 0 ||
        memcmp(proof.pass159_provenance_root,
               provenance->global_symbol_environment_root,
               HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES) != 0) {
        out_result->decision = HHS_EXACT_PASS219_PASS169_BINDING_REJECT;
        out_result->reason_mask = HHS_EXACT_PASS219_PASS169_BINDING_REASON_SOURCE_IDENTITY_MISMATCH;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (!hhs219_i12111_pipeline_matches(provenance, &proof)) {
        out_result->decision = HHS_EXACT_PASS219_PASS169_BINDING_REJECT;
        out_result->reason_mask = HHS_EXACT_PASS219_PASS169_BINDING_REASON_PIPELINE_IDENTITY_MISMATCH;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (!hhs219_i12111_gate_bundle_valid(provenance, &proof)) {
        out_result->decision = HHS_EXACT_PASS219_PASS169_BINDING_REJECT;
        out_result->reason_mask = HHS_EXACT_PASS219_PASS169_BINDING_REASON_GATE_PROVENANCE_MISMATCH;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (!hhs219_i12111_receipt_identity_valid(&proof)) {
        out_result->decision = HHS_EXACT_PASS219_PASS169_BINDING_REJECT;
        out_result->reason_mask = HHS_EXACT_PASS219_PASS169_BINDING_REASON_RECEIPT_IDENTITY_INVALID;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (!hhs219_i12111_authority_evidence_complete(&proof)) {
        out_result->decision = HHS_EXACT_PASS219_PASS169_BINDING_REJECT;
        out_result->reason_mask = HHS_EXACT_PASS219_PASS169_BINDING_REASON_AUTHORITY_EVIDENCE_INCOMPLETE;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    memset(&input, 0, sizeof(input));
    input.struct_size = (uint32_t)sizeof(input);
    input.version = hhs_exact_pass219_global_membrane_version();
    memcpy(input.combined_source_sha256,
           proof.combined_source_sha256,
           sizeof(input.combined_source_sha256));
    memcpy(input.global_symbol_environment_root,
           proof.canonical_global_symbol_environment_root,
           sizeof(input.global_symbol_environment_root));
    input.gate_count = proof.gate_count;
    input.global_symbol_environment_complete = 1U;
    input.cross_layer_revalidation_complete = proof.shared_environment_revalidated;
    input.local_symbol_shadowing_detected = proof.local_symbol_shadowing_detected;
    memcpy(input.gates, proof.gates, sizeof(input.gates));

    status = hhs_exact_pass219_global_membrane_evaluate(&input, &out_result->membrane_result);
    if (status != HHS_EXACT_STATUS_OK) {
        out_result->decision = HHS_EXACT_PASS219_PASS169_BINDING_REJECT;
        out_result->reason_mask = HHS_EXACT_PASS219_PASS169_BINDING_REASON_GATE_PROVENANCE_MISMATCH;
        return status;
    }

    out_result->pass169_authority_verified = 1U;
    out_result->boolean_gate_results_available = 1U;
    out_result->membrane_input_ready = 1U;
    out_result->canonical_monolithic_proof = 1U;
    memcpy(out_result->proof_hash216, proof.proof_hash216, sizeof(out_result->proof_hash216));
    memcpy(out_result->transition_hash216, proof.transition_hash216, sizeof(out_result->transition_hash216));
    memcpy(out_result->receipt_hash72, proof.receipt_hash72, sizeof(out_result->receipt_hash72));
    memcpy(out_result->replay_hash72, proof.replay_hash72, sizeof(out_result->replay_hash72));

    if (out_result->membrane_result.decision == HHS_EXACT_PASS219_GLOBAL_MEMBRANE_PROPAGATE) {
        out_result->decision = HHS_EXACT_PASS219_PASS169_BINDING_PROPAGATE;
        out_result->reason_mask = HHS_EXACT_PASS219_PASS169_BINDING_REASON_NONE;
        out_result->whole_equation_propagated = 1U;
    } else {
        out_result->decision = HHS_EXACT_PASS219_PASS169_BINDING_REJECT;
        out_result->reason_mask = HHS_EXACT_PASS219_PASS169_BINDING_REASON_MEMBRANE_REJECTED;
        out_result->whole_equation_propagated = 0U;
    }
    return HHS_EXACT_STATUS_OK;
}
