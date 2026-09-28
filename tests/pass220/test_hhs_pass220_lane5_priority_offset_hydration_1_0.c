#include "hhs_runtime_exact_abi.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed: %s at %s:%d\n", #expr, __FILE__, __LINE__); \
        return 1; \
    } \
} while (0)

static void source_state(
    HHSExactPass220PriorityOffsetTaggedCellV1 state[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ]
) {
    uint32_t i;
    memset(state, 0, sizeof(*state) * HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS);
    for (i = 0U; i < HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS; ++i) {
        state[i].counted_value = (uint64_t)(i % 9U);
        state[i].phase72 = (uint8_t)((i * 8U) % 72U);
        state[i].rotation4 = (uint8_t)(i % 4U);
        state[i].source_index = (uint8_t)i;
    }
}

static HHSExactPass219Lane5MediationRequestV1 template_request(void) {
    HHSExactPass219Lane5MediationRequestV1 r;
    uint32_t i;
    memset(&r, 0, sizeof(r));
    r.struct_size = (uint32_t)sizeof(r);
    r.version = HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION;
    r.namespace_id = HHS_EXACT_PASS219_LANE5_NAMESPACE;
    r.hash216_reference_count = 3U;
    r.capability_reference_count = 4U;
    r.learning_stage = 5U;
    r.request_signature64 = UINT64_C(0x5101);
    r.candidate_signature64 = UINT64_C(0x5102);
    r.parent_hash216_signature64 = UINT64_C(0x5103);
    r.bigint_address_signature64 = UINT64_C(0x5104);
    r.hydration_signature64 = UINT64_C(0x5105);
    r.compression_signature64 = UINT64_C(0x5106);
    r.capability_registry_signature64 = UINT64_C(0x5107);
    r.learning_iteration_signature64 = UINT64_C(0x5108);
    r.rna_prepared_signature64 = UINT64_C(0x5109);
    r.rna_decision_signature64 = UINT64_C(0x5110);
    for (i = 0U; i < r.hash216_reference_count; ++i)
        r.hash216_reference_signature64[i] = UINT64_C(0x5200) + i;
    for (i = 0U; i < r.capability_reference_count; ++i)
        r.capability_reference_signature64[i] = UINT64_C(0x5300) + i;
    return r;
}

int main(void) {
    HHSExactPass220PriorityOffsetDescriptorV1 descriptor;
    HHSExactPass220PriorityOffsetTaggedCellV1 source[81];
    HHSExactPass220PriorityOffsetTaggedCellV1 transformed[81];
    HHSExactPass220PriorityOffsetTaggedCellV1 recovered[81];
    HHSExactPass219Lane5MediationRequestV1 request = template_request();
    HHSExactPass219Lane5MediationReceiptV1 receipt;
    HHSExactPass220PriorityOffsetMediationWitnessV1 witness;
    uint32_t channel;

    memset(&descriptor, 0, sizeof(descriptor));
    CHECK(hhs_exact_pass220_priority_offset_descriptor(&descriptor) == HHS_EXACT_STATUS_OK);
    CHECK(descriptor.vm81_cells == 81U);
    CHECK(descriptor.phase_modulus == 72U);
    CHECK(descriptor.firing_origin == 8U);
    CHECK(descriptor.firing_step == 16U);
    CHECK(descriptor.macrocycle_order == 9U);
    CHECK(descriptor.literal_firing_pattern_bound == 1U);
    CHECK(descriptor.u9_address_orbit_bound == 1U);
    CHECK(descriptor.hnan_global_preflight_required == 1U);
    CHECK(descriptor.scalar_offset_priority_candidate == 1U);
    CHECK(descriptor.dense_substitution_runtime_authority == 0U);
    CHECK(descriptor.candidate_only == 1U);

    source_state(source);
    for (channel = 0U; channel < 4U; ++channel) {
        memset(transformed, 0, sizeof(transformed));
        memset(recovered, 0, sizeof(recovered));
        CHECK(hhs_exact_pass220_priority_offset_transform(
            source, channel, transformed
        ) == HHS_EXACT_STATUS_OK);
        CHECK(hhs_exact_pass220_priority_offset_inverse(
            transformed, channel, recovered
        ) == HHS_EXACT_STATUS_OK);
        CHECK(memcmp(source, recovered, sizeof(source)) == 0);

        memset(&receipt, 0, sizeof(receipt));
        memset(&witness, 0, sizeof(witness));
        CHECK(hhs_exact_pass220_priority_offset_mediate(
            source,
            channel,
            &request,
            transformed,
            &receipt,
            &witness
        ) == HHS_EXACT_STATUS_OK);
        CHECK(receipt.decision == HHS_EXACT_PASS219_LANE5_DECISION_CANDIDATE_READY);
        CHECK(receipt.zero_sum_closure_passed == 1U);
        CHECK(witness.inverse_round_trip_exact == 1U);
        CHECK(witness.counted_values_preserved == 1U);
        CHECK(witness.phase_coordinates_preserved == 1U);
        CHECK(witness.rotations_preserved == 1U);
        CHECK(witness.provenance_preserved == 1U);
        CHECK(witness.literal_firing_pattern_bound == 1U);
        CHECK(witness.hnan_global_preflight_passed == 1U);
        CHECK(witness.exact_vm5184_bound == 1U);
        CHECK(witness.rna_cell_wall_bound == 1U);
        CHECK(witness.candidate_only == 1U);
        CHECK(witness.canonical_vm81_mutation_authority == 0U);
        CHECK(witness.canonical_hash72_authority == 0U);
        CHECK(witness.canonical_hash216_authority == 0U);
        CHECK(witness.canonical_persistence_authority == 0U);
        CHECK(witness.floating_point_canonical_authority == 0U);
    }

    source[0].phase72 = 72U;
    CHECK(hhs_exact_pass220_priority_offset_transform(
        source,
        HHS_EXACT_PASS220_PRIORITY_OFFSET_CHANNEL_XY,
        transformed
    ) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    source_state(source);
    CHECK(hhs_exact_pass220_priority_offset_transform(
        source,
        4U,
        transformed
    ) == HHS_EXACT_STATUS_INVALID_ARGUMENT);

    puts("PASS220_LANE5_PRIORITY_OFFSET_HYDRATION_1_0_PASS");
    return 0;
}
