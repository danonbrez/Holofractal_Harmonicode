#ifndef HHS_PASS219_PQC_MEMBRANE_SPECULATIVE_HYDRATION_I13_H
#define HHS_PASS219_PQC_MEMBRANE_SPECULATIVE_HYDRATION_I13_H

#include "hhs_pass219_vm81_environmental_recovery_1_32.h"
#include "hhs_hash216_bytes.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_PQC_MEMBRANE_I13_VERSION UINT32_C(0x0001000D)
#define HHS_EXACT_PASS219_PQC_SOURCE_HASH_BYTES UINT32_C(64)
#define HHS_EXACT_PASS219_PQC_PROJECTION_LANES UINT32_C(5)
#define HHS_EXACT_PASS219_PQC_CANONICAL_HOLO4_LANES UINT32_C(4)
#define HHS_EXACT_PASS219_PQC_HARMONIC36_MAX UINT64_C(0xFFFFFFFFF)
#define HHS_EXACT_PASS219_PQC_PROOF_SHA256_BYTES UINT32_C(32)

typedef enum HHSExactPass219SourceArchitectureI13 {
    HHS_EXACT_PASS219_SOURCE_ARCH_UNSPECIFIED = 0,
    HHS_EXACT_PASS219_SOURCE_ARCH_LLAMA3 = 1,
    HHS_EXACT_PASS219_SOURCE_ARCH_QWEN2 = 2,
    HHS_EXACT_PASS219_SOURCE_ARCH_MISTRAL = 3,
    HHS_EXACT_PASS219_SOURCE_ARCH_NATIVE = 4,
    HHS_EXACT_PASS219_SOURCE_ARCH_OTHER_FROZEN = 255
} HHSExactPass219SourceArchitectureI13;

typedef enum HHSExactPass219OraclePhaseI13 {
    HHS_EXACT_PASS219_ORACLE_PHASE_INVALID = 0,
    HHS_EXACT_PASS219_ORACLE_DEPENDENCY = 1,
    HHS_EXACT_PASS219_CACHE_HIT_DOMINANCE = 2,
    HHS_EXACT_PASS219_NATIVE_AUTONOMY = 3
} HHSExactPass219OraclePhaseI13;

typedef struct HHSExactPass219FrozenSourceManifestI13 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t source_hash[HHS_EXACT_PASS219_PQC_SOURCE_HASH_BYTES];
    uint32_t architecture_id;
    char projection_root_hash216[HHS_HASH216_BYTES_STRLEN];
    uint8_t immutable_source_archive;
    uint8_t source_archive_outside_pqc;
    uint8_t raw_weight_blob_absent;
    uint8_t provenance_anchor_inside_pqc;
} HHSExactPass219FrozenSourceManifestI13;

typedef struct HHSExactPass219FiveLaneProjectionI13 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t lane_root_sha256[HHS_EXACT_PASS219_PQC_PROJECTION_LANES]
                            [HHS_EXACT_PASS219_PQC_PROOF_SHA256_BYTES];
    uint64_t harmonic36_coordinate;
    uint64_t prime_factor_surface_index;
    uint8_t projection_lane_count;
    uint8_t canonical_holo4_lane_count;
    uint8_t fifth_lane_candidate_only;
    uint8_t five_lane_projection_verified;
} HHSExactPass219FiveLaneProjectionI13;

typedef struct HHSExactPass219ProjectionClosureProofI13 {
    uint32_t struct_size;
    uint32_t version;
    char candidate_frame_hash72[HHS_HASH72_BYTES_STRLEN];
    uint8_t exact_constraint_surface_sha256[HHS_EXACT_PASS219_PQC_PROOF_SHA256_BYTES];
    uint8_t projection_proof_sha256[HHS_EXACT_PASS219_PQC_PROOF_SHA256_BYTES];
    uint8_t exact_rational_only;
    uint8_t delta_e_zero;
    uint8_t psi_zero;
    uint8_t omega_true;
    uint8_t xy_n4_unity_verified;
    uint8_t algebraic_solver_verified;
    uint8_t manifold_closed;
    uint8_t no_probabilistic_payload;
} HHSExactPass219ProjectionClosureProofI13;

typedef struct HHSExactPass219OracleLifecycleI13 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t phase;
    uint64_t verified_route_count;
    uint64_t required_route_count;
    uint64_t frontier_miss_count;
    uint8_t external_oracle_enabled;
    uint8_t oracle_severance_authorized;
    uint8_t canonical_routes_only;
    uint8_t reserved0;
} HHSExactPass219OracleLifecycleI13;

typedef struct HHSExactPass219AdmissibleProjectionI13 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219FrozenSourceManifestI13 provenance;
    HHSExactPass219FiveLaneProjectionI13 lane_mappings;
    HHSExactPass219ProjectionClosureProofI13 closure_proof;
    HHSExactPass219OracleLifecycleI13 lifecycle;
    uint8_t speculative_candidate_only;
    uint8_t probabilistic_payload_present;
    uint8_t requests_direct_model_commit;
    uint8_t requests_non_vm81_canonical_commit;
} HHSExactPass219AdmissibleProjectionI13;

static inline uint8_t hhs_exact_pass219_i13_bytes_nonzero(
    const uint8_t *bytes,
    size_t length
) {
    size_t i;
    uint8_t aggregate = 0U;
    if (bytes == NULL || length == 0U)
        return 0U;
    for (i = 0U; i < length; ++i)
        aggregate = (uint8_t)(aggregate | bytes[i]);
    return aggregate != 0U ? 1U : 0U;
}

static inline uint8_t hhs_exact_pass219_i13_fixed_text_present(
    const char *text,
    size_t payload_length
) {
    size_t i;
    if (text == NULL || text[payload_length] != '\0')
        return 0U;
    for (i = 0U; i < payload_length; ++i) {
        if (text[i] == '\0')
            return 0U;
    }
    return 1U;
}

static inline uint8_t hhs_exact_pass219_i13_source_manifest_valid(
    const HHSExactPass219FrozenSourceManifestI13 *manifest
) {
    if (manifest == NULL ||
        manifest->struct_size != sizeof(*manifest) ||
        manifest->version != HHS_EXACT_PASS219_PQC_MEMBRANE_I13_VERSION ||
        manifest->architecture_id == HHS_EXACT_PASS219_SOURCE_ARCH_UNSPECIFIED ||
        manifest->immutable_source_archive != 1U ||
        manifest->source_archive_outside_pqc != 1U ||
        manifest->raw_weight_blob_absent != 1U ||
        manifest->provenance_anchor_inside_pqc != 1U)
        return 0U;
    if (!hhs_exact_pass219_i13_bytes_nonzero(
            manifest->source_hash, HHS_EXACT_PASS219_PQC_SOURCE_HASH_BYTES))
        return 0U;
    return hhs_exact_pass219_i13_fixed_text_present(
        manifest->projection_root_hash216, HHS_HASH216_BYTES_LEN);
}

static inline uint8_t hhs_exact_pass219_i13_lane_projection_valid(
    const HHSExactPass219FiveLaneProjectionI13 *lanes
) {
    size_t lane;
    if (lanes == NULL ||
        lanes->struct_size != sizeof(*lanes) ||
        lanes->version != HHS_EXACT_PASS219_PQC_MEMBRANE_I13_VERSION ||
        lanes->projection_lane_count != HHS_EXACT_PASS219_PQC_PROJECTION_LANES ||
        lanes->canonical_holo4_lane_count != HHS_EXACT_PASS219_PQC_CANONICAL_HOLO4_LANES ||
        lanes->fifth_lane_candidate_only != 1U ||
        lanes->five_lane_projection_verified != 1U ||
        lanes->harmonic36_coordinate > HHS_EXACT_PASS219_PQC_HARMONIC36_MAX ||
        lanes->prime_factor_surface_index == 0U)
        return 0U;
    for (lane = 0U; lane < HHS_EXACT_PASS219_PQC_PROJECTION_LANES; ++lane) {
        if (!hhs_exact_pass219_i13_bytes_nonzero(
                lanes->lane_root_sha256[lane], HHS_EXACT_PASS219_PQC_PROOF_SHA256_BYTES))
            return 0U;
    }
    return 1U;
}

static inline uint8_t hhs_exact_pass219_i13_closure_proof_valid(
    const HHSExactPass219ProjectionClosureProofI13 *proof
) {
    if (proof == NULL ||
        proof->struct_size != sizeof(*proof) ||
        proof->version != HHS_EXACT_PASS219_PQC_MEMBRANE_I13_VERSION ||
        proof->exact_rational_only != 1U ||
        proof->delta_e_zero != 1U ||
        proof->psi_zero != 1U ||
        proof->omega_true != 1U ||
        proof->xy_n4_unity_verified != 1U ||
        proof->algebraic_solver_verified != 1U ||
        proof->manifold_closed != 1U ||
        proof->no_probabilistic_payload != 1U)
        return 0U;
    if (!hhs_exact_pass219_i13_fixed_text_present(
            proof->candidate_frame_hash72, HHS_HASH72_BYTES_LEN))
        return 0U;
    if (!hhs_exact_pass219_i13_bytes_nonzero(
            proof->exact_constraint_surface_sha256,
            HHS_EXACT_PASS219_PQC_PROOF_SHA256_BYTES))
        return 0U;
    return hhs_exact_pass219_i13_bytes_nonzero(
        proof->projection_proof_sha256,
        HHS_EXACT_PASS219_PQC_PROOF_SHA256_BYTES);
}

static inline uint8_t hhs_exact_pass219_i13_lifecycle_valid(
    const HHSExactPass219OracleLifecycleI13 *lifecycle
) {
    if (lifecycle == NULL ||
        lifecycle->struct_size != sizeof(*lifecycle) ||
        lifecycle->version != HHS_EXACT_PASS219_PQC_MEMBRANE_I13_VERSION ||
        lifecycle->canonical_routes_only != 1U)
        return 0U;

    if (lifecycle->phase == HHS_EXACT_PASS219_ORACLE_DEPENDENCY)
        return lifecycle->external_oracle_enabled == 1U &&
               lifecycle->oracle_severance_authorized == 0U;

    if (lifecycle->phase == HHS_EXACT_PASS219_CACHE_HIT_DOMINANCE)
        return lifecycle->verified_route_count > 0U &&
               lifecycle->oracle_severance_authorized == 0U;

    if (lifecycle->phase == HHS_EXACT_PASS219_NATIVE_AUTONOMY)
        return lifecycle->required_route_count > 0U &&
               lifecycle->verified_route_count >= lifecycle->required_route_count &&
               lifecycle->external_oracle_enabled == 0U &&
               lifecycle->oracle_severance_authorized == 1U;

    return 0U;
}

static inline uint8_t hhs_exact_pass219_pqc_projection_valid_i13(
    const HHSExactPass219AdmissibleProjectionI13 *candidate
) {
    if (candidate == NULL ||
        candidate->struct_size != sizeof(*candidate) ||
        candidate->version != HHS_EXACT_PASS219_PQC_MEMBRANE_I13_VERSION ||
        candidate->speculative_candidate_only != 1U ||
        candidate->probabilistic_payload_present != 0U ||
        candidate->requests_direct_model_commit != 0U ||
        candidate->requests_non_vm81_canonical_commit != 0U)
        return 0U;

    return hhs_exact_pass219_i13_source_manifest_valid(&candidate->provenance) &&
           hhs_exact_pass219_i13_lane_projection_valid(&candidate->lane_mappings) &&
           hhs_exact_pass219_i13_closure_proof_valid(&candidate->closure_proof) &&
           hhs_exact_pass219_i13_lifecycle_valid(&candidate->lifecycle);
}

/*
 * Source-level membrane only: this helper intentionally creates no dynamic
 * mutation symbol.  After I13 verification, the sole state-changing call is
 * the inherited signed VM81 environmental admit function below.
 */
static inline HHSExactStatus hhs_exact_pass219_pqc_membrane_ingest_i13(
    const HHSExactPass219AdmissibleProjectionI13 *candidate,
    uint32_t pass_number,
    uint32_t signature_algorithm,
    const HHSExactUQCELInputV1 *exact_representation,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    int8_t lo_shu_group,
    uint16_t g243,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactVM81Frame *out_committed_frame,
    HHSExactPass219RNAAdmissionV1 *out_admission,
    HHSExactPass219VM81PQCFirewallReceiptV1 *out_firewall_receipt,
    HHSExactPass219VM81PQCSignatureReceiptV1 *out_signature_receipt,
    HHSExactPass219VM81EnvironmentReceiptV1 *out_environment_receipt
) {
    uint8_t frame_bytes[HHS_EXACT_VM81_FRAME_BYTES];
    char frame_hash72[HHS_HASH72_BYTES_STRLEN];
    size_t frame_length = 0U;
    HHSExactStatus status;

    if (candidate == NULL || exact_representation == NULL || candidate_frame == NULL ||
        parent_hash216_reference == NULL || out_committed_frame == NULL ||
        out_admission == NULL || out_firewall_receipt == NULL ||
        out_signature_receipt == NULL || out_environment_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    if (!hhs_exact_pass219_pqc_projection_valid_i13(candidate))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_vm81_frame_export_le(
        candidate_frame, frame_bytes, sizeof(frame_bytes), &frame_length);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (frame_length != HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    hhs_hash72_compute_bytes(frame_bytes, frame_length, frame_hash72);
    if (memcmp(
            frame_hash72,
            candidate->closure_proof.candidate_frame_hash72,
            HHS_HASH72_BYTES_STRLEN) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return hhs_exact_pass219_vm81_environment_admit_signed(
        pass_number,
        signature_algorithm,
        exact_representation,
        candidate_frame,
        parent_hash216_reference,
        lo_shu_group,
        g243,
        feedback_lane,
        feedback_trinary,
        out_committed_frame,
        out_admission,
        out_firewall_receipt,
        out_signature_receipt,
        out_environment_receipt);
}

#ifdef __cplusplus
}
#endif

#endif
