#include "hhs_pass220_lane5_priority_offset_hydration_1_0.h"

#include <string.h>

static const int8_t HHS_P220_SCALAR_SYMBOLS[9] = {
    -1, 4, -3, -2, 0, 2, 3, -4, 1
};

static const int8_t HHS_P220_CHANNEL_FACTORS[4] = {
    1, -1, 2, -2
};

static const uint8_t HHS_P220_FIRING_ORDER[9] = {
    8, 24, 40, 56, 72, 16, 32, 48, 64
};

static uint64_t hhs_p220_priority_mix_u64(uint64_t hash, uint64_t value) {
    unsigned shift;
    for (shift = 0U; shift < 64U; shift += 8U) {
        hash ^= (value >> shift) & UINT64_C(0xff);
        hash *= UINT64_C(1099511628211);
    }
    return hash;
}

static uint64_t hhs_p220_priority_nonzero(uint64_t value, uint64_t domain) {
    uint64_t mixed = hhs_p220_priority_mix_u64(value, domain);
    return mixed == 0U ? domain : mixed;
}

static int hhs_p220_priority_valid_channel(uint32_t channel) {
    return channel < HHS_EXACT_PASS220_PRIORITY_OFFSET_CHANNEL_COUNT;
}

static int hhs_p220_priority_validate_firing_pattern(void) {
    uint32_t n;
    for (n = 0U; n < HHS_EXACT_PASS220_PRIORITY_OFFSET_MACROCYCLE_ORDER; ++n) {
        uint32_t residue =
            (HHS_EXACT_PASS220_PRIORITY_OFFSET_FIRING_ORIGIN +
             HHS_EXACT_PASS220_PRIORITY_OFFSET_FIRING_STEP * n) %
            HHS_EXACT_PASS220_PRIORITY_OFFSET_PHASE_MODULUS;
        uint32_t displayed = residue == 0U
            ? HHS_EXACT_PASS220_PRIORITY_OFFSET_PHASE_MODULUS
            : residue;
        if (displayed != (uint32_t)HHS_P220_FIRING_ORDER[n])
            return 0;
    }
    return (
        (HHS_EXACT_PASS220_PRIORITY_OFFSET_FIRING_ORIGIN +
         HHS_EXACT_PASS220_PRIORITY_OFFSET_FIRING_STEP *
             HHS_EXACT_PASS220_PRIORITY_OFFSET_MACROCYCLE_ORDER) %
            HHS_EXACT_PASS220_PRIORITY_OFFSET_PHASE_MODULUS
        == HHS_EXACT_PASS220_PRIORITY_OFFSET_FIRING_ORIGIN
    );
}

static HHSExactStatus hhs_p220_priority_validate_state(
    const HHSExactPass220PriorityOffsetTaggedCellV1 state[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ]
) {
    uint8_t seen[HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS];
    uint32_t i;
    if (state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(seen, 0, sizeof(seen));
    for (i = 0U; i < HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS; ++i) {
        uint32_t source_index = state[i].source_index;
        if (state[i].phase72 >= HHS_EXACT_PASS220_PRIORITY_OFFSET_PHASE_MODULUS ||
            state[i].rotation4 >= 4U ||
            source_index >= HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS ||
            seen[source_index] != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        seen[source_index] = 1U;
    }
    return HHS_EXACT_STATUS_OK;
}

static uint64_t hhs_p220_priority_state_signature(
    const HHSExactPass220PriorityOffsetTaggedCellV1 state[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ]
) {
    uint64_t hash = UINT64_C(1469598103934665603);
    uint32_t i;
    for (i = 0U; i < HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS; ++i) {
        hash = hhs_p220_priority_mix_u64(hash, state[i].counted_value);
        hash = hhs_p220_priority_mix_u64(hash, state[i].phase72);
        hash = hhs_p220_priority_mix_u64(hash, state[i].rotation4);
        hash = hhs_p220_priority_mix_u64(hash, state[i].source_index);
    }
    return hash == 0U ? UINT64_C(0x22051001) : hash;
}

static uint64_t hhs_p220_priority_firing_signature(void) {
    uint64_t hash = UINT64_C(1469598103934665603);
    uint32_t i;
    for (i = 0U; i < HHS_EXACT_PASS220_PRIORITY_OFFSET_MACROCYCLE_ORDER; ++i)
        hash = hhs_p220_priority_mix_u64(hash, HHS_P220_FIRING_ORDER[i]);
    return hash == 0U ? UINT64_C(0x22051002) : hash;
}

static uint32_t hhs_p220_priority_exponent(
    uint32_t block_index,
    uint32_t channel,
    int inverse
) {
    int value =
        (int)HHS_P220_SCALAR_SYMBOLS[block_index] *
        (int)HHS_P220_CHANNEL_FACTORS[channel];
    int exponent = value % (int)HHS_EXACT_PASS220_PRIORITY_OFFSET_BLOCK_WIDTH;
    if (exponent < 0)
        exponent += (int)HHS_EXACT_PASS220_PRIORITY_OFFSET_BLOCK_WIDTH;
    if (inverse != 0 && exponent != 0)
        exponent =
            (int)HHS_EXACT_PASS220_PRIORITY_OFFSET_BLOCK_WIDTH - exponent;
    return (uint32_t)exponent;
}

static HHSExactStatus hhs_p220_priority_transform_internal(
    const HHSExactPass220PriorityOffsetTaggedCellV1 source[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ],
    uint32_t channel,
    int inverse,
    HHSExactPass220PriorityOffsetTaggedCellV1 output[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ]
) {
    uint32_t block;
    HHSExactStatus status;
    if (output == NULL || !hhs_p220_priority_valid_channel(channel))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_p220_priority_validate_state(source);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    for (block = 0U;
         block < HHS_EXACT_PASS220_PRIORITY_OFFSET_BLOCK_COUNT;
         ++block) {
        uint32_t column;
        uint32_t exponent =
            hhs_p220_priority_exponent(block, channel, inverse);
        uint32_t start =
            block * HHS_EXACT_PASS220_PRIORITY_OFFSET_BLOCK_WIDTH;
        for (column = 0U;
             column < HHS_EXACT_PASS220_PRIORITY_OFFSET_BLOCK_WIDTH;
             ++column) {
            uint32_t row =
                (column + exponent) %
                HHS_EXACT_PASS220_PRIORITY_OFFSET_BLOCK_WIDTH;
            output[start + row] = source[start + column];
        }
    }
    return hhs_p220_priority_validate_state(output);
}

static int hhs_p220_priority_fields_preserved(
    const HHSExactPass220PriorityOffsetTaggedCellV1 source[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ],
    const HHSExactPass220PriorityOffsetTaggedCellV1 transformed[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ],
    int field
) {
    uint32_t i;
    for (i = 0U; i < HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS; ++i) {
        uint32_t j;
        int found = 0;
        for (j = 0U; j < HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS; ++j) {
            if (source[j].source_index == transformed[i].source_index) {
                if ((field == 0 && source[j].counted_value != transformed[i].counted_value) ||
                    (field == 1 && source[j].phase72 != transformed[i].phase72) ||
                    (field == 2 && source[j].rotation4 != transformed[i].rotation4))
                    return 0;
                found = 1;
                break;
            }
        }
        if (!found)
            return 0;
    }
    return 1;
}

HHSExactStatus hhs_exact_pass220_priority_offset_descriptor(
    HHSExactPass220PriorityOffsetDescriptorV1 *out_descriptor
) {
    HHSExactPass220PriorityOffsetDescriptorV1 descriptor;
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_p220_priority_validate_firing_pattern())
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    memset(&descriptor, 0, sizeof(descriptor));
    descriptor.struct_size = (uint32_t)sizeof(descriptor);
    descriptor.version = HHS_EXACT_PASS220_PRIORITY_OFFSET_VERSION;
    descriptor.vm81_cells = HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS;
    descriptor.block_width = HHS_EXACT_PASS220_PRIORITY_OFFSET_BLOCK_WIDTH;
    descriptor.block_count = HHS_EXACT_PASS220_PRIORITY_OFFSET_BLOCK_COUNT;
    descriptor.channel_count = HHS_EXACT_PASS220_PRIORITY_OFFSET_CHANNEL_COUNT;
    descriptor.phase_modulus = HHS_EXACT_PASS220_PRIORITY_OFFSET_PHASE_MODULUS;
    descriptor.firing_origin = HHS_EXACT_PASS220_PRIORITY_OFFSET_FIRING_ORIGIN;
    descriptor.firing_step = HHS_EXACT_PASS220_PRIORITY_OFFSET_FIRING_STEP;
    descriptor.macrocycle_order = HHS_EXACT_PASS220_PRIORITY_OFFSET_MACROCYCLE_ORDER;
    descriptor.literal_firing_pattern_bound = 1U;
    descriptor.u9_address_orbit_bound = 1U;
    descriptor.complete_tagged_state_preserved = 1U;
    descriptor.hnan_global_preflight_required = 1U;
    descriptor.dense_substitution_runtime_authority = 0U;
    descriptor.scalar_offset_priority_candidate = 1U;
    descriptor.candidate_only = 1U;
    descriptor.exact_integer_only = 1U;
    descriptor.floating_point_canonical_authority = 0U;
    descriptor.canonical_vm81_mutation_authority = 0U;
    descriptor.canonical_hash72_authority = 0U;
    descriptor.canonical_hash216_authority = 0U;
    descriptor.canonical_persistence_authority = 0U;
    *out_descriptor = descriptor;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass220_priority_offset_transform(
    const HHSExactPass220PriorityOffsetTaggedCellV1 source[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ],
    uint32_t channel,
    HHSExactPass220PriorityOffsetTaggedCellV1 output[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ]
) {
    return hhs_p220_priority_transform_internal(source, channel, 0, output);
}

HHSExactStatus hhs_exact_pass220_priority_offset_inverse(
    const HHSExactPass220PriorityOffsetTaggedCellV1 source[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ],
    uint32_t channel,
    HHSExactPass220PriorityOffsetTaggedCellV1 output[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ]
) {
    return hhs_p220_priority_transform_internal(source, channel, 1, output);
}

HHSExactStatus hhs_exact_pass220_priority_offset_prepare_lane5_request(
    const HHSExactPass219Lane5MediationRequestV1 *template_request,
    const HHSExactPass220PriorityOffsetTaggedCellV1 transformed[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ],
    uint32_t channel,
    HHSExactPass219Lane5MediationRequestV1 *out_request
) {
    HHSExactPass219Lane5MediationRequestV1 request;
    HHSExactStatus status;
    uint64_t state_signature;
    uint64_t firing_signature;
    if (template_request == NULL || out_request == NULL ||
        !hhs_p220_priority_valid_channel(channel))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_p220_priority_validate_state(transformed);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (template_request->struct_size != (uint32_t)sizeof(*template_request) ||
        template_request->version != HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION ||
        template_request->namespace_id != HHS_EXACT_PASS219_LANE5_NAMESPACE)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    state_signature = hhs_p220_priority_state_signature(transformed);
    firing_signature = hhs_p220_priority_firing_signature();
    request = *template_request;
    request.request_signature64 = hhs_p220_priority_nonzero(
        request.request_signature64 ^ state_signature,
        UINT64_C(0x22051010) + channel
    );
    request.candidate_signature64 = hhs_p220_priority_nonzero(
        request.candidate_signature64 ^ state_signature,
        UINT64_C(0x22051020) + channel
    );
    request.bigint_address_signature64 = hhs_p220_priority_nonzero(
        request.bigint_address_signature64 ^ state_signature,
        UINT64_C(0x22051030) + channel
    );
    request.hydration_signature64 = hhs_p220_priority_nonzero(
        request.hydration_signature64 ^ state_signature,
        UINT64_C(0x22051040) + channel
    );
    request.compression_signature64 = hhs_p220_priority_nonzero(
        request.compression_signature64 ^ (uint64_t)(channel + 1U),
        UINT64_C(0x22051050)
    );
    request.learning_iteration_signature64 = hhs_p220_priority_nonzero(
        request.learning_iteration_signature64 ^ firing_signature,
        UINT64_C(0x22051060) + channel
    );
    *out_request = request;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass220_priority_offset_mediate(
    const HHSExactPass220PriorityOffsetTaggedCellV1 source[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ],
    uint32_t channel,
    const HHSExactPass219Lane5MediationRequestV1 *template_request,
    HHSExactPass220PriorityOffsetTaggedCellV1 transformed[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ],
    HHSExactPass219Lane5MediationReceiptV1 *out_receipt,
    HHSExactPass220PriorityOffsetMediationWitnessV1 *out_witness
) {
    HHSExactPass220PriorityOffsetTaggedCellV1 recovered[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ];
    HHSExactPass219Lane5MediationRequestV1 request;
    HHSExactPass219Lane5MediationReceiptV1 receipt;
    HHSExactPass220PriorityOffsetMediationWitnessV1 witness;
    HHSExactStatus status;
    if (transformed == NULL || out_receipt == NULL || out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_receipt, 0, sizeof(*out_receipt));
    memset(out_witness, 0, sizeof(*out_witness));
    if (!hhs_p220_priority_validate_firing_pattern())
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    status = hhs_exact_pass220_priority_offset_transform(
        source, channel, transformed
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass220_priority_offset_inverse(
        transformed, channel, recovered
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (memcmp(source, recovered, sizeof(recovered)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    status = hhs_exact_pass220_priority_offset_prepare_lane5_request(
        template_request, transformed, channel, &request
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    memset(&receipt, 0, sizeof(receipt));
    status = hhs_exact_pass219_lane5_mediate_candidate(&request, &receipt);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (receipt.decision != HHS_EXACT_PASS219_LANE5_DECISION_CANDIDATE_READY ||
        receipt.zero_sum_closure_passed != 1U ||
        receipt.exact_vm5184_bound != 1U ||
        receipt.rna_cell_wall_bound != 1U ||
        receipt.candidate_only != 1U ||
        receipt.canonical_mutation_authority != 0U ||
        receipt.canonical_hash72_authority != 0U ||
        receipt.canonical_hash216_authority != 0U ||
        receipt.canonical_persistence_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(&witness, 0, sizeof(witness));
    witness.struct_size = (uint32_t)sizeof(witness);
    witness.version = HHS_EXACT_PASS220_PRIORITY_OFFSET_VERSION;
    witness.channel = channel;
    witness.source_signature64 = hhs_p220_priority_state_signature(source);
    witness.transformed_signature64 =
        hhs_p220_priority_state_signature(transformed);
    witness.recovered_signature64 =
        hhs_p220_priority_state_signature(recovered);
    witness.firing_order_signature64 =
        hhs_p220_priority_firing_signature();
    witness.request_signature64 = request.request_signature64;
    witness.closure_signature64 = receipt.closure_signature64;
    witness.mediation_signature64 = receipt.mediation_signature64;
    witness.inverse_round_trip_exact = 1U;
    witness.counted_values_preserved = (uint8_t)
        hhs_p220_priority_fields_preserved(source, transformed, 0);
    witness.phase_coordinates_preserved = (uint8_t)
        hhs_p220_priority_fields_preserved(source, transformed, 1);
    witness.rotations_preserved = (uint8_t)
        hhs_p220_priority_fields_preserved(source, transformed, 2);
    witness.provenance_preserved = 1U;
    witness.literal_firing_pattern_bound = 1U;
    witness.hnan_global_preflight_passed = receipt.zero_sum_closure_passed;
    witness.exact_vm5184_bound = receipt.exact_vm5184_bound;
    witness.rna_cell_wall_bound = receipt.rna_cell_wall_bound;
    witness.candidate_only = 1U;
    witness.canonical_vm81_mutation_authority = 0U;
    witness.canonical_hash72_authority = 0U;
    witness.canonical_hash216_authority = 0U;
    witness.canonical_persistence_authority = 0U;
    witness.floating_point_canonical_authority = 0U;
    if (witness.counted_values_preserved != 1U ||
        witness.phase_coordinates_preserved != 1U ||
        witness.rotations_preserved != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    *out_receipt = receipt;
    *out_witness = witness;
    return HHS_EXACT_STATUS_OK;
}
