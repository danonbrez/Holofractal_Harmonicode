#include "hhs_pass219_lane5_global_holographic_nucleus_1_34.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "RNA_LANE5_CHECK_FAILED:%s:%d:%s\\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static int is_zero(const void *record, size_t size) {
    const uint8_t *b = (const uint8_t *)record;
    size_t i;
    for (i = 0U; i < size; ++i)
        if (b[i] != 0U)
            return 0;
    return 1;
}

/* All inherited witnesses except RNA signatures are TEST-ONLY references.
 * The two RNA signatures are obtained from real native C++ execution below.
 * This test does not certify independent provenance of the remaining fields.
 */
static HHSExactPass219Lane5MediationRequestV1 request_with_rna(
    const HHSExactPass219Holo4PreparedV1 *prepared,
    const HHSExactPass219Holo4DecisionV1 *decision
) {
    HHSExactPass219Lane5MediationRequestV1 r;
    memset(&r, 0, sizeof(r));
    r.struct_size = (uint32_t)sizeof(r);
    r.version = HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION;
    r.namespace_id = HHS_EXACT_PASS219_LANE5_NAMESPACE;
    r.hash216_reference_count = 3U;
    r.capability_reference_count = 4U;
    r.learning_stage = 4U;
    r.request_signature64 = UINT64_C(0x1101);
    r.candidate_signature64 = UINT64_C(0x1102);
    r.parent_hash216_signature64 = UINT64_C(0x1103);
    r.bigint_address_signature64 = UINT64_C(0x1104);
    r.hydration_signature64 = UINT64_C(0x1105);
    r.compression_signature64 = UINT64_C(0x1106);
    r.capability_registry_signature64 = UINT64_C(0x1107);
    r.learning_iteration_signature64 = UINT64_C(0x1108);
    r.rna_prepared_signature64 = prepared->tensor_signature64;
    r.rna_decision_signature64 = decision->decision_signature64;
    r.hash216_reference_signature64[0] = UINT64_C(0x2101);
    r.hash216_reference_signature64[1] = UINT64_C(0x2102);
    r.hash216_reference_signature64[2] = UINT64_C(0x2103);
    r.capability_reference_signature64[0] = UINT64_C(0x3101);
    r.capability_reference_signature64[1] = UINT64_C(0x3102);
    r.capability_reference_signature64[2] = UINT64_C(0x3103);
    r.capability_reference_signature64[3] = UINT64_C(0x3104);
    return r;
}

int main(void) {
    HHSExactPass219Hash216TransitionViewV1 transition;
    HHSExactPass219Hash216TransitionViewV1 bad_transition;
    HHSExactUQCELInputV1 input;
    HHSExactVM81Frame frame;
    HHSExactPass219Holo4PreparedV1 reference_prepared, emitted_prepared;
    HHSExactPass219Holo4DecisionV1 reference_decision, emitted_decision;
    HHSExactPass219Lane5MediationRequestV1 request, corrupted;
    HHSExactPass219Lane5MediationReceiptV1 first, replay;
    uint8_t one = 1U;
    size_t i;

    memset(&transition, 0, sizeof(transition));
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&transition) ==
          HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&transition) ==
          HHS_EXACT_STATUS_OK);

    memset(&input, 0, sizeof(input));
    input.struct_size = (uint32_t)sizeof(input);
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.delta.struct_size = (uint32_t)sizeof(input.delta);
    input.delta.byte_length = 1U;
    input.delta.bytes_be = &one;
    memset(&frame, 0, sizeof(frame));
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        frame.words[i] = UINT64_C(0x9E3779B97F4A7C15) ^
                         ((uint64_t)i * UINT64_C(0x100000001B3));

    /* Baseline is the actual C++ RNA cell wall, not a fake signature maker. */
    memset(&reference_prepared, 0, sizeof(reference_prepared));
    memset(&reference_decision, 0, sizeof(reference_decision));
    CHECK(hhs_exact_pass219_rna_vm5184_route(
          &input, &frame, &transition, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
          0, &reference_prepared, &reference_decision) == HHS_EXACT_STATUS_OK);
    CHECK(reference_prepared.tensor_signature64 != 0U);
    CHECK(reference_decision.decision_signature64 != 0U);
    request = request_with_rna(&reference_prepared, &reference_decision);

    memset(&emitted_prepared, 0, sizeof(emitted_prepared));
    memset(&emitted_decision, 0, sizeof(emitted_decision));
    memset(&first, 0, sizeof(first));
    CHECK(hhs_exact_pass219_lane5_mediate_rna_vm5184(
          &input, &frame, &transition, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
          0, &request, &emitted_prepared, &emitted_decision,
          &first) == HHS_EXACT_STATUS_OK);
    CHECK(memcmp(&emitted_prepared, &reference_prepared, sizeof(emitted_prepared)) == 0);
    CHECK(memcmp(&emitted_decision, &reference_decision, sizeof(emitted_decision)) == 0);
    CHECK(first.decision == HHS_EXACT_PASS219_LANE5_DECISION_CANDIDATE_READY);
    CHECK(first.rna_prepared_signature64 == reference_prepared.tensor_signature64);
    CHECK(first.rna_decision_signature64 == reference_decision.decision_signature64);
    CHECK(first.candidate_only == 1U);
    CHECK(first.exact_vm5184_bound == 1U);
    CHECK(first.rna_cell_wall_bound == 1U);
    CHECK(first.requires_environmental_admission == 1U);
    CHECK(first.canonical_mutation_authority == 0U);
    CHECK(first.canonical_hash72_authority == 0U);
    CHECK(first.canonical_hash216_authority == 0U);

    memset(&replay, 0, sizeof(replay));
    CHECK(hhs_exact_pass219_lane5_mediate_rna_vm5184(
          &input, &frame, &transition, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
          0, &request, &emitted_prepared, &emitted_decision,
          &replay) == HHS_EXACT_STATUS_OK);
    CHECK(memcmp(&replay, &first, sizeof(replay)) == 0);

    corrupted = request;
    corrupted.rna_prepared_signature64 ^= UINT64_C(1);
    memset(&first, 0xA5, sizeof(first));
    memset(&emitted_prepared, 0xA5, sizeof(emitted_prepared));
    memset(&emitted_decision, 0xA5, sizeof(emitted_decision));
    CHECK(hhs_exact_pass219_lane5_mediate_rna_vm5184(
          &input, &frame, &transition, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
          0, &corrupted, &emitted_prepared, &emitted_decision,
          &first) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(is_zero(&first, sizeof(first)));
    CHECK(is_zero(&emitted_prepared, sizeof(emitted_prepared)));
    CHECK(is_zero(&emitted_decision, sizeof(emitted_decision)));

    corrupted = request;
    corrupted.rna_decision_signature64 ^= UINT64_C(1);
    CHECK(hhs_exact_pass219_lane5_mediate_rna_vm5184(
          &input, &frame, &transition, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
          0, &corrupted, &emitted_prepared, &emitted_decision,
          &first) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    corrupted = request;
    corrupted.hash216_reference_signature64[0] = 0U;
    CHECK(hhs_exact_pass219_lane5_mediate_rna_vm5184(
          &input, &frame, &transition, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
          0, &corrupted, &emitted_prepared, &emitted_decision,
          &first) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    memcpy(&bad_transition, &transition, sizeof(bad_transition));
    bad_transition.transition_identity216[0] ^= 1;
    CHECK(hhs_exact_pass219_lane5_mediate_rna_vm5184(
          &input, &frame, &bad_transition, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
          0, &request, &emitted_prepared, &emitted_decision,
          &first) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    CHECK(hhs_exact_pass219_lane5_mediate_rna_vm5184(
          &input, &frame, &transition, 5U,
          0, &request, &emitted_prepared, &emitted_decision,
          &first) == HHS_EXACT_STATUS_RANGE_ERROR);

    puts("PASS219_LANE5_RNA_VM5184_COUPLED_MEDIATION_PASS");
    return 0;
}
