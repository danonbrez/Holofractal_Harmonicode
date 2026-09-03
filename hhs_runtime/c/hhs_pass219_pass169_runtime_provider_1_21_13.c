#include "hhs_pass219_pass169_runtime_provider_1_21_13.h"
#include "hhs_runtime_uqcel_1_8.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

static uint32_t hhs219_i155_provider_version_word(void) {
    return (HHS_EXACT_PASS219_PASS169_PROVIDER_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_PASS169_PROVIDER_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_PASS169_PROVIDER_VERSION_PATCH;
}

static uint32_t hhs219_i155_binding_version_word(void) {
    return (HHS_EXACT_PASS219_PASS169_BINDING_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_PASS169_BINDING_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_PASS169_BINDING_VERSION_PATCH;
}

static void hhs219_i155_copy_stage_hashes(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    HHSExactPass219Pass169AuthorityProofV1 *proof
) {
#define COPY_STAGE(field) memcpy(proof->field, provenance->field, sizeof(proof->field))
    COPY_STAGE(source_hash216);
    COPY_STAGE(tokens_hash216);
    COPY_STAGE(cst_hash216);
    COPY_STAGE(ast_hash216);
    COPY_STAGE(type_environment_hash216);
    COPY_STAGE(constraint_graph_hash216);
    COPY_STAGE(hir_hash216);
    COPY_STAGE(vmir_hash216);
#undef COPY_STAGE
}

static void hhs219_i155_fill_hash72(
    char out[HHS_EXACT_HASH72_STRLEN],
    char symbol
) {
    memset(out, (unsigned char)symbol, HHS_EXACT_HASH72_LEN);
    out[HHS_EXACT_HASH72_LEN] = '\0';
}

static HHSExactStatus hhs219_i155_probe_full_symbolic_uqcel(
    HHSExactUQCELAdmissionV1 *out_admission
) {
    static const uint8_t one[] = {1U};
    static const uint8_t zero[] = {0U};
    HHSExactUQCELInputV1 input;
    uint8_t source_sha256[HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES];
    HHSExactStatus status;

    if (out_admission == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(&input, 0, sizeof(input));
    memset(out_admission, 0, sizeof(*out_admission));

    status = hhs_exact_uqcel_source_sha256(source_sha256);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    input.struct_size = (uint32_t)sizeof(input);
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1;

#define SET_VIEW(field, bytes) do { \
    input.field.struct_size = (uint32_t)sizeof(input.field); \
    input.field.byte_length = (uint32_t)sizeof(bytes); \
    input.field.bytes_be = (bytes); \
} while (0)
    SET_VIEW(P, one);
    SET_VIEW(p, one);
    SET_VIEW(q, one);
    SET_VIEW(delta, zero);
    SET_VIEW(A, one);
    SET_VIEW(B, one);
#undef SET_VIEW

    input.cell81 = 0U;
    input.left_basis8 = HHS_EXACT_PHASE_X;
    input.right_basis8 = HHS_EXACT_PHASE_Y;
    memcpy(input.source_envelope_sha256, source_sha256, sizeof(source_sha256));
    hhs219_i155_fill_hash72(input.previous_hash72, HHS_EXACT_HASH72_ALPHABET[0]);

    return hhs_exact_uqcel_validate(&input, out_admission);
}

uint32_t hhs_exact_pass219_pass169_runtime_provider_version(void) {
    return hhs219_i155_provider_version_word();
}

HHSExactStatus hhs_exact_pass219_pass169_runtime_provider_descriptor(
    HHSExactPass219Pass169RuntimeProviderDescriptorV1 *out_descriptor
) {
    HHSExactUQCELAdmissionV1 admission;
    HHSExactStatus probe_status;

    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = hhs219_i155_provider_version_word();
    out_descriptor->production_provider_implementation_present = 1U;
    out_descriptor->non_test_provider = 1U;
    out_descriptor->pass159_provenance_required = 1U;
    out_descriptor->full_symbolic_uqcel_probe_required = 1U;
    out_descriptor->test_fixture_authority = 0U;
    out_descriptor->floating_point_authority = 0U;
    out_descriptor->vm81_mutation_authority = 0U;
    out_descriptor->hash72_mint_authority = 0U;
    out_descriptor->hash216_persistence_authority = 0U;

    probe_status = hhs219_i155_probe_full_symbolic_uqcel(&admission);
    if (probe_status == HHS_EXACT_STATUS_OK &&
        admission.decision == HHS_EXACT_UQCEL_DECISION_ADMIT &&
        admission.residual_mask == 0U) {
        out_descriptor->full_symbolic_uqcel_supported = 1U;
    }

    /*
     * I155 closes provider presence and exact residual probing only.
     * Local P/Hash216 binding and canonical five-gate export remain disabled
     * until the monolithic residual evaluator can authoritatively produce them.
     */
    out_descriptor->local_p_snapshot_binding_supported = 0U;
    out_descriptor->canonical_gate_vector_export_supported = 0U;
    out_descriptor->canonical_authority_available = 0U;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_pass169_verify_combined_gate_authority_1_21_11(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    HHSExactPass219Pass169AuthorityProofV1 *out_proof
) {
    HHSExactUQCELAdmissionV1 admission;
    HHSExactStatus status;

    if (provenance == NULL || out_proof == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_proof, 0, sizeof(*out_proof));
    out_proof->struct_size = (uint32_t)sizeof(*out_proof);
    out_proof->version = hhs219_i155_binding_version_word();

    memcpy(out_proof->combined_source_sha256,
           provenance->combined_source_sha256,
           sizeof(out_proof->combined_source_sha256));
    memcpy(out_proof->pass159_provenance_root,
           provenance->global_symbol_environment_root,
           sizeof(out_proof->pass159_provenance_root));
    hhs219_i155_copy_stage_hashes(provenance, out_proof);

    /*
     * Preserve provenance identity before probing the native full-symbolic
     * domain.  No Boolean gate, canonical environment root, Hash72 receipt,
     * Hash216 proof identity, or VM81 authority is manufactured here.
     */
    status = hhs219_i155_probe_full_symbolic_uqcel(&admission);

    if (status == HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN &&
        admission.decision == HHS_EXACT_UQCEL_DECISION_UNSUPPORTED_DOMAIN &&
        admission.reject_reason == HHS_EXACT_UQCEL_REASON_FULL_SYMBOLIC_RESIDUAL &&
        (admission.residual_mask & HHS_UQCEL_RESIDUAL_MONOLITHIC_EQUALITY_CHAIN) != 0U) {
        return HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN;
    }

    /*
     * If the underlying full-symbolic profile changes, fail closed until this
     * provider is explicitly upgraded to bind local P, the canonical five-gate
     * environment, VM81 commit evidence, receipts, and deterministic replay.
     */
    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
}
