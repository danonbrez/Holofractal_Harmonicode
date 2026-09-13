#include "hhs_pass219_lane5_global_holographic_nucleus_1_34.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed: %s at %s:%d\n", #expr, __FILE__, __LINE__); \
        return 1; \
    } \
} while (0)

static HHSExactPass219Lane5MediationRequestV1 valid_request(void) {
    HHSExactPass219Lane5MediationRequestV1 r;
    uint32_t i;
    memset(&r, 0, sizeof(r));
    r.struct_size = (uint32_t)sizeof(r);
    r.version = HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION;
    r.namespace_id = HHS_EXACT_PASS219_LANE5_NAMESPACE;
    r.hash216_reference_count = 3U;
    r.capability_reference_count = 4U;
    r.learning_stage = 4U;
    r.request_signature64 = UINT64_C(0x1001);
    r.candidate_signature64 = UINT64_C(0x1002);
    r.parent_hash216_signature64 = UINT64_C(0x1003);
    r.bigint_address_signature64 = UINT64_C(0x1004);
    r.hydration_signature64 = UINT64_C(0x1005);
    r.compression_signature64 = UINT64_C(0x1006);
    r.capability_registry_signature64 = UINT64_C(0x1007);
    r.learning_iteration_signature64 = UINT64_C(0x1008);
    r.rna_prepared_signature64 = UINT64_C(0x1009);
    r.rna_decision_signature64 = UINT64_C(0x1010);
    for (i = 0U; i < r.hash216_reference_count; ++i)
        r.hash216_reference_signature64[i] = UINT64_C(0x2000) + i;
    for (i = 0U; i < r.capability_reference_count; ++i)
        r.capability_reference_signature64[i] = UINT64_C(0x3000) + i;
    return r;
}

int main(void) {
    HHSExactPass219Lane5NucleusAuthorityV1 authority;
    HHSExactPass219Lane5MediationRequestV1 request;
    HHSExactPass219Lane5MediationRequestV1 tampered;
    HHSExactPass219Lane5MediationReceiptV1 receipt_a;
    HHSExactPass219Lane5MediationReceiptV1 receipt_b;

    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_nucleus_version() == HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION);
    CHECK(hhs_exact_pass219_lane5_nucleus_authority(&authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.struct_size == sizeof(authority));
    CHECK(authority.namespace_id == HHS_EXACT_PASS219_LANE5_NAMESPACE);
    CHECK(authority.global_root_orchestration == 1U);
    CHECK(authority.global_traffic_mediation == 1U);
    CHECK(authority.validated_hash216_read_only == 1U);
    CHECK(authority.hash216_sha256_array_addressing == 1U);
    CHECK(authority.four_lane_hydration_composition == 1U);
    CHECK(authority.pass133_bigint_serialization == 1U);
    CHECK(authority.pass211_hfc_frame_compatible == 1U);
    CHECK(authority.nested_modular_fibonacci_reuse == 1U);
    CHECK(authority.graphics_vector_hydration == 1U);
    CHECK(authority.api_registry_visible == 1U);
    CHECK(authority.learning_iteration_cycle == 1U);
    CHECK(authority.rna_cpp_cell_wall_bound == 1U);
    CHECK(authority.exact_vm5184_carrier == 1U);
    CHECK(authority.exact_integer_only == 1U);
    CHECK(authority.candidate_only == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.canonical_persistence_authority == 0U);
    CHECK(authority.pqc_key_authority == 0U);
    CHECK(authority.receipt_clock_authority == 0U);
    CHECK(authority.floating_point_canonical_authority == 0U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);

    request = valid_request();
    memset(&receipt_a, 0, sizeof(receipt_a));
    memset(&receipt_b, 0, sizeof(receipt_b));
    CHECK(hhs_exact_pass219_lane5_mediate_candidate(&request, &receipt_a) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_lane5_mediate_candidate(&request, &receipt_b) == HHS_EXACT_STATUS_OK);
    CHECK(memcmp(&receipt_a, &receipt_b, sizeof(receipt_a)) == 0);
    CHECK(receipt_a.decision == HHS_EXACT_PASS219_LANE5_DECISION_CANDIDATE_READY);
    CHECK(receipt_a.closure_signature64 != 0U);
    CHECK(receipt_a.mediation_signature64 != 0U);
    CHECK(receipt_a.hash216_references_validated == 1U);
    CHECK(receipt_a.capability_registry_validated == 1U);
    CHECK(receipt_a.exact_vm5184_bound == 1U);
    CHECK(receipt_a.rna_cell_wall_bound == 1U);
    CHECK(receipt_a.zero_sum_closure_passed == 1U);
    CHECK(receipt_a.candidate_only == 1U);
    CHECK(receipt_a.canonical_mutation_authority == 0U);
    CHECK(receipt_a.canonical_hash72_authority == 0U);
    CHECK(receipt_a.canonical_hash216_authority == 0U);
    CHECK(receipt_a.canonical_persistence_authority == 0U);
    CHECK(receipt_a.requires_environmental_admission == 1U);

    tampered = request;
    tampered.namespace_id ^= 1U;
    CHECK(hhs_exact_pass219_lane5_mediate_candidate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVALID_ARGUMENT);

    tampered = request;
    tampered.hash216_reference_signature64[1] = 0U;
    CHECK(hhs_exact_pass219_lane5_mediate_candidate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = request;
    tampered.capability_reference_signature64[2] = 0U;
    CHECK(hhs_exact_pass219_lane5_mediate_candidate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = request;
    tampered.rna_prepared_signature64 = 0U;
    CHECK(hhs_exact_pass219_lane5_mediate_candidate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVALID_ARGUMENT);

    tampered = request;
    tampered.hash216_reference_count = HHS_EXACT_PASS219_LANE5_MAX_HASH216_REFS + 1U;
    CHECK(hhs_exact_pass219_lane5_mediate_candidate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVALID_ARGUMENT);

    printf(
        "PASS219_LANE5_GLOBAL_HOLOGRAPHIC_NUCLEUS_PASS closure=%llu mediation=%llu hash216_refs=%u capabilities=%u\n",
        (unsigned long long)receipt_a.closure_signature64,
        (unsigned long long)receipt_a.mediation_signature64,
        receipt_a.hash216_reference_count,
        receipt_a.capability_reference_count);
    return 0;
}
