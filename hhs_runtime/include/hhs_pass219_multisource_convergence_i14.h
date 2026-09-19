#ifndef HHS_PASS219_MULTISOURCE_CONVERGENCE_I14_H
#define HHS_PASS219_MULTISOURCE_CONVERGENCE_I14_H

#include "hhs_pass219_pqc_membrane_speculative_hydration_i13.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_MULTISOURCE_I14_VERSION UINT32_C(0x0001000E)
#define HHS_EXACT_PASS219_MULTISOURCE_I14_MIN_SOURCES UINT32_C(2)
#define HHS_EXACT_PASS219_MULTISOURCE_I14_MAX_SOURCES UINT32_C(8)

typedef enum HHSExactPass219MultiSourceDecisionI14 {
    HHS_EXACT_PASS219_MULTISOURCE_INVALID = 0,
    HHS_EXACT_PASS219_MULTISOURCE_NOT_CONVERGED = 1,
    HHS_EXACT_PASS219_MULTISOURCE_CONVERGED = 2
} HHSExactPass219MultiSourceDecisionI14;

typedef struct HHSExactPass219AdmittedSourceEvidenceI14 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219AdmissibleProjectionI13 projection;
    HHSExactVM81Frame committed_frame;
    HHSExactPass219RNAAdmissionV1 admission;
    HHSExactPass219VM81PQCFirewallReceiptV1 firewall_receipt;
    HHSExactPass219VM81PQCSignatureReceiptV1 signature_receipt;
    HHSExactPass219VM81EnvironmentReceiptV1 environment_receipt;
    uint8_t i13_membrane_passed;
    uint8_t reserved0[7];
} HHSExactPass219AdmittedSourceEvidenceI14;

typedef struct HHSExactPass219MultiSourceConvergenceReceiptI14 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t source_count;
    uint32_t unique_source_count;
    uint32_t reserved0;
    char canonical_child_hash216[HHS_EXACT_UQCEL_HASH216_STRLEN];
    char canonical_frame_hash72[HHS_HASH72_BYTES_STRLEN];
    char source_route_binding_hash216[HHS_EXACT_PASS219_MULTISOURCE_I14_MAX_SOURCES]
                                     [HHS_HASH216_BYTES_STRLEN];
    uint8_t all_i13_evidence_valid;
    uint8_t independent_source_hashes;
    uint8_t source_provenance_preserved;
    uint8_t canonical_identity_equal;
    uint8_t committed_frame_equal;
    uint8_t deduplication_authorized;
    uint8_t canonical_mutation_authority_created;
    uint8_t canonical_hash216_authority_created;
    uint8_t canonical_persistence_authority_created;
    uint8_t reserved1[7];
} HHSExactPass219MultiSourceConvergenceReceiptI14;

static inline size_t hhs_exact_pass219_i14_append(
    uint8_t *out,
    size_t capacity,
    size_t cursor,
    const void *data,
    size_t length
) {
    if (out == NULL || data == NULL || cursor > capacity || length > capacity - cursor)
        return SIZE_MAX;
    if (length != 0U)
        memcpy(out + cursor, data, length);
    return cursor + length;
}

static inline size_t hhs_exact_pass219_i14_append_u32_be(
    uint8_t *out,
    size_t capacity,
    size_t cursor,
    uint32_t value
) {
    const uint8_t bytes[4] = {
        (uint8_t)(value >> 24U),
        (uint8_t)(value >> 16U),
        (uint8_t)(value >> 8U),
        (uint8_t)value
    };
    return hhs_exact_pass219_i14_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static inline size_t hhs_exact_pass219_i14_append_u64_be(
    uint8_t *out,
    size_t capacity,
    size_t cursor,
    uint64_t value
) {
    uint8_t bytes[8];
    size_t i;
    for (i = 0U; i < 8U; ++i)
        bytes[7U - i] = (uint8_t)(value >> (8U * i));
    return hhs_exact_pass219_i14_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static inline uint8_t hhs_exact_pass219_i14_frame_hash72(
    const HHSExactVM81Frame *frame,
    char out_hash72[HHS_HASH72_BYTES_STRLEN]
) {
    uint8_t bytes[HHS_EXACT_VM81_FRAME_BYTES];
    size_t written = 0U;
    HHSExactStatus status;
    if (frame == NULL || out_hash72 == NULL)
        return 0U;
    status = hhs_exact_vm81_frame_export_le(frame, bytes, sizeof(bytes), &written);
    if (status != HHS_EXACT_STATUS_OK || written != sizeof(bytes))
        return 0U;
    hhs_hash72_compute_bytes(bytes, written, out_hash72);
    return 1U;
}

static inline uint8_t hhs_exact_pass219_i14_admitted_evidence_valid(
    const HHSExactPass219AdmittedSourceEvidenceI14 *evidence
) {
    char frame_hash72[HHS_HASH72_BYTES_STRLEN];
    const HHSExactPass219VM81PQCFirewallReceiptV1 *firewall;
    const HHSExactPass219VM81PQCSignatureReceiptV1 *signature;
    const HHSExactPass219VM81EnvironmentReceiptV1 *environment;

    if (evidence == NULL ||
        evidence->struct_size != sizeof(*evidence) ||
        evidence->version != HHS_EXACT_PASS219_MULTISOURCE_I14_VERSION ||
        evidence->i13_membrane_passed != 1U ||
        !hhs_exact_pass219_pqc_projection_valid_i13(&evidence->projection) ||
        evidence->admission.struct_size != sizeof(evidence->admission) ||
        evidence->admission.version != hhs_exact_pass219_rna_version())
        return 0U;

    firewall = &evidence->firewall_receipt;
    signature = &evidence->signature_receipt;
    environment = &evidence->environment_receipt;

    if (firewall->struct_size != sizeof(*firewall) ||
        firewall->version != HHS_EXACT_PASS219_VM81_PQC_VERSION ||
        firewall->decision != HHS_EXACT_PASS219_VM81_PQC_DECISION_COMMITTED ||
        firewall->halted != 0U || firewall->parent_hash216_verified != 1U ||
        firewall->child_hash216_verified != 1U || firewall->rna_cell_wall_routed != 1U ||
        firewall->pqc_authenticated != 1U || firewall->inherited_rna_authority_invoked != 1U ||
        firewall->canonical_receipt_owned_by_inherited_authority != 1U ||
        firewall->firewall_is_canonical_authority != 0U)
        return 0U;

    if (signature->struct_size != sizeof(*signature) ||
        signature->version != HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERSION ||
        signature->decision != HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERIFIED ||
        signature->signature_length == 0U || signature->provider_available != 1U ||
        signature->key_derived_from_kernel_root != 1U ||
        signature->signature_generated_inside_kernel != 1U ||
        signature->signature_verified_before_vm81 != 1U ||
        signature->external_key_authority != 0U ||
        signature->external_signature_authority != 0U ||
        signature->signature_is_canonical_receipt != 0U ||
        !hhs_exact_pass219_i13_bytes_nonzero(signature->public_key_sha256, sizeof(signature->public_key_sha256)) ||
        !hhs_exact_pass219_i13_bytes_nonzero(signature->signed_message_sha256, sizeof(signature->signed_message_sha256)) ||
        !hhs_exact_pass219_i13_bytes_nonzero(signature->signature_sha256, sizeof(signature->signature_sha256)))
        return 0U;

    if (environment->struct_size != sizeof(*environment) ||
        environment->version != HHS_EXACT_PASS219_VM81_ENV_VERSION ||
        environment->state != HHS_EXACT_PASS219_VM81_ENV_STATE_RUNNING ||
        environment->decision != HHS_EXACT_PASS219_VM81_ENV_DECISION_READY ||
        environment->reason != HHS_EXACT_PASS219_VM81_ENV_REASON_NONE ||
        environment->genesis_verified != 1U || environment->witness_verified != 1U ||
        environment->environment_signature_verified != 1U ||
        environment->canonical_mutation_authority != 0U ||
        environment->canonical_receipt_authority != 0U ||
        !hhs_exact_pass219_i13_bytes_nonzero(environment->witness_sha256, sizeof(environment->witness_sha256)))
        return 0U;

    if (hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&evidence->admission.transition) !=
        HHS_EXACT_STATUS_OK)
        return 0U;
    if (memcmp(firewall->child_hash216_identity,
               evidence->admission.transition.transition_identity216,
               HHS_EXACT_UQCEL_HASH216_STRLEN) != 0)
        return 0U;
    if (memcmp(firewall->candidate_hash72,
               evidence->projection.closure_proof.candidate_frame_hash72,
               HHS_HASH72_BYTES_STRLEN) != 0)
        return 0U;
    if (!hhs_exact_pass219_i14_frame_hash72(&evidence->committed_frame, frame_hash72))
        return 0U;
    return memcmp(frame_hash72, firewall->candidate_hash72, HHS_HASH72_BYTES_STRLEN) == 0 ? 1U : 0U;
}

static inline HHSExactStatus hhs_exact_pass219_i14_source_route_binding(
    const HHSExactPass219AdmittedSourceEvidenceI14 *evidence,
    char out_hash216[HHS_HASH216_BYTES_STRLEN]
) {
    uint8_t material[1200];
    size_t cursor = 0U;
    size_t lane;
    static const char domain[] = "HHS-P219-I14-SOURCE-ROUTE-BINDING-V1";

    if (evidence == NULL || out_hash216 == NULL ||
        !hhs_exact_pass219_i14_admitted_evidence_valid(evidence))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    cursor = hhs_exact_pass219_i14_append(material, sizeof(material), cursor,
        domain, sizeof(domain) - 1U);
    cursor = hhs_exact_pass219_i14_append(material, sizeof(material), cursor,
        evidence->projection.provenance.source_hash,
        HHS_EXACT_PASS219_PQC_SOURCE_HASH_BYTES);
    cursor = hhs_exact_pass219_i14_append_u32_be(material, sizeof(material), cursor,
        evidence->projection.provenance.architecture_id);
    cursor = hhs_exact_pass219_i14_append(material, sizeof(material), cursor,
        evidence->projection.provenance.projection_root_hash216, HHS_HASH216_BYTES_LEN);
    for (lane = 0U; lane < HHS_EXACT_PASS219_PQC_PROJECTION_LANES; ++lane) {
        cursor = hhs_exact_pass219_i14_append(material, sizeof(material), cursor,
            evidence->projection.lane_mappings.lane_root_sha256[lane],
            HHS_EXACT_PASS219_PQC_PROOF_SHA256_BYTES);
    }
    cursor = hhs_exact_pass219_i14_append_u64_be(material, sizeof(material), cursor,
        evidence->projection.lane_mappings.harmonic36_coordinate);
    cursor = hhs_exact_pass219_i14_append_u64_be(material, sizeof(material), cursor,
        evidence->projection.lane_mappings.prime_factor_surface_index);
    cursor = hhs_exact_pass219_i14_append(material, sizeof(material), cursor,
        evidence->projection.closure_proof.exact_constraint_surface_sha256,
        HHS_EXACT_PASS219_PQC_PROOF_SHA256_BYTES);
    cursor = hhs_exact_pass219_i14_append(material, sizeof(material), cursor,
        evidence->projection.closure_proof.projection_proof_sha256,
        HHS_EXACT_PASS219_PQC_PROOF_SHA256_BYTES);
    cursor = hhs_exact_pass219_i14_append(material, sizeof(material), cursor,
        evidence->firewall_receipt.candidate_hash72, HHS_EXACT_HASH72_LEN);
    cursor = hhs_exact_pass219_i14_append(material, sizeof(material), cursor,
        evidence->firewall_receipt.child_hash216_identity,
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    cursor = hhs_exact_pass219_i14_append(material, sizeof(material), cursor,
        evidence->signature_receipt.signed_message_sha256,
        sizeof(evidence->signature_receipt.signed_message_sha256));
    cursor = hhs_exact_pass219_i14_append(material, sizeof(material), cursor,
        evidence->environment_receipt.witness_sha256,
        sizeof(evidence->environment_receipt.witness_sha256));
    if (cursor == SIZE_MAX)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    hhs_hash216_compute_bytes(material, cursor, out_hash216);
    return HHS_EXACT_STATUS_OK;
}

static inline HHSExactStatus hhs_exact_pass219_multisource_convergence_i14(
    const HHSExactPass219AdmittedSourceEvidenceI14 *evidence,
    size_t source_count,
    HHSExactPass219MultiSourceConvergenceReceiptI14 *out_receipt
) {
    size_t i;
    size_t j;
    uint8_t identity_equal = 1U;
    uint8_t frame_equal = 1U;

    if (evidence == NULL || out_receipt == NULL ||
        source_count < HHS_EXACT_PASS219_MULTISOURCE_I14_MIN_SOURCES ||
        source_count > HHS_EXACT_PASS219_MULTISOURCE_I14_MAX_SOURCES)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = (uint32_t)sizeof(*out_receipt);
    out_receipt->version = HHS_EXACT_PASS219_MULTISOURCE_I14_VERSION;
    out_receipt->source_count = (uint32_t)source_count;

    for (i = 0U; i < source_count; ++i) {
        if (!hhs_exact_pass219_i14_admitted_evidence_valid(&evidence[i]))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        for (j = 0U; j < i; ++j) {
            if (memcmp(evidence[i].projection.provenance.source_hash,
                       evidence[j].projection.provenance.source_hash,
                       HHS_EXACT_PASS219_PQC_SOURCE_HASH_BYTES) == 0)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        if (hhs_exact_pass219_i14_source_route_binding(
                &evidence[i], out_receipt->source_route_binding_hash216[i]) !=
            HHS_EXACT_STATUS_OK)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_receipt->all_i13_evidence_valid = 1U;
    out_receipt->independent_source_hashes = 1U;
    out_receipt->source_provenance_preserved = 1U;
    out_receipt->unique_source_count = (uint32_t)source_count;
    memcpy(out_receipt->canonical_child_hash216,
           evidence[0].firewall_receipt.child_hash216_identity,
           HHS_EXACT_UQCEL_HASH216_STRLEN);
    memcpy(out_receipt->canonical_frame_hash72,
           evidence[0].firewall_receipt.candidate_hash72,
           HHS_HASH72_BYTES_STRLEN);

    for (i = 1U; i < source_count; ++i) {
        if (memcmp(evidence[0].firewall_receipt.child_hash216_identity,
                   evidence[i].firewall_receipt.child_hash216_identity,
                   HHS_EXACT_UQCEL_HASH216_STRLEN) != 0)
            identity_equal = 0U;
        if (memcmp(evidence[0].firewall_receipt.candidate_hash72,
                   evidence[i].firewall_receipt.candidate_hash72,
                   HHS_HASH72_BYTES_STRLEN) != 0 ||
            memcmp(&evidence[0].committed_frame,
                   &evidence[i].committed_frame,
                   sizeof(HHSExactVM81Frame)) != 0)
            frame_equal = 0U;
    }

    out_receipt->canonical_identity_equal = identity_equal;
    out_receipt->committed_frame_equal = frame_equal;
    if (identity_equal == 1U && frame_equal == 1U) {
        out_receipt->decision = HHS_EXACT_PASS219_MULTISOURCE_CONVERGED;
        out_receipt->deduplication_authorized = 1U;
    } else {
        out_receipt->decision = HHS_EXACT_PASS219_MULTISOURCE_NOT_CONVERGED;
        out_receipt->deduplication_authorized = 0U;
    }
    return HHS_EXACT_STATUS_OK;
}

#ifdef __cplusplus
}
#endif

#endif
