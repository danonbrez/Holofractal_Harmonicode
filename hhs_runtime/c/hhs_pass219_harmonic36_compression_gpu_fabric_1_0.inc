#include "../include/hhs_pass219_harmonic36_compression_gpu_fabric_1_0.h"

#include <string.h>

static uint32_t h36_cgpu_version_word(void) {
    return (HHS_EXACT_PASS219_H36_CGPU_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_H36_CGPU_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_H36_CGPU_VERSION_PATCH;
}

static HHSExactStatus h36_validate_pass210(
    const HHSExactPass219InheritedPass210BindingV1 *p
) {
    if (p == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (p->struct_size < sizeof(*p) ||
        p->version != hhs_exact_pass219_inherited_pass210_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (p->pass_number != HHS_EXACT_PASS219_INHERITED_PASS210_NUMBER ||
        p->classification != HHS_EXACT_PASS219_INHERITED_PASS_WIRED ||
        p->exact_frame_authority_bound != 1U ||
        p->double_witness_coverage_bound != 1U ||
        p->single_snapshot_recovery_bound != 1U ||
        p->multimodal_agreement_bound != 1U ||
        p->strict_compression_domain_bound != 1U ||
        p->digest_decode_boundary_bound != 1U ||
        p->pass219_new_canonical_mutation_authority != 0U ||
        p->cxx_mutation_authority != 0U ||
        p->vm81_mutation_authority != 0U ||
        p->register_len != HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES ||
        p->snapshot_count != HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT ||
        p->snapshot_width != HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_WIDTH ||
        p->snapshot_stride != HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_STRIDE)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_validate_gpu_bindings(
    const HHSExactPass219InheritedPass207BindingV1 *p207,
    const HHSExactPass219InheritedPass208BindingV1 *p208
) {
    if (p207 == NULL || p208 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (p207->struct_size < sizeof(*p207) ||
        p207->version != hhs_exact_pass219_inherited_pass207_version() ||
        p208->struct_size < sizeof(*p208) ||
        p208->version != hhs_exact_pass219_inherited_pass208_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (p207->pass_number != HHS_EXACT_PASS219_INHERITED_PASS207_NUMBER ||
        p207->classification != HHS_EXACT_PASS219_INHERITED_PASS_WIRED ||
        p207->stable_vm5184_lane_dispatch_bound != 1U ||
        p207->lane_phase_bijection_bound != 1U ||
        p207->exact_cpu_oracle_verification_bound != 1U ||
        p207->candidate_only_bound != 1U ||
        p207->gpu_hash72_commit_forbidden != 1U ||
        p207->gpu_canonical_mutation_forbidden != 1U ||
        p207->gpu_vm81_bypass_forbidden != 1U ||
        p207->pass205_singleton_vm81_admission_bound != 1U ||
        p207->logical_lanes_per_batch != HHS_EXACT_PASS219_H36_FRAME_BITS ||
        p207->pass219_new_canonical_mutation_authority != 0U ||
        p207->direct_gpu_vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (p208->pass_number != HHS_EXACT_PASS219_INHERITED_PASS208_NUMBER ||
        p208->classification != HHS_EXACT_PASS219_INHERITED_PASS_WIRED ||
        p208->gpu_candidate_expansion_bound != 1U ||
        p208->exact_cpu_oracle_verification_bound != 1U ||
        p208->stable_integer_ranking_bound != 1U ||
        p208->pass205_singleton_vm81_commit_path_bound != 1U ||
        p208->gpu_hash72_commit_forbidden != 1U ||
        p208->gpu_canonical_persistence_forbidden != 1U ||
        p208->gpu_vm81_bypass_forbidden != 1U ||
        p208->logical_lanes_per_branch != HHS_EXACT_PASS219_H36_FRAME_BITS ||
        p208->pass219_new_canonical_mutation_authority != 0U ||
        p208->direct_gpu_vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

uint32_t hhs_exact_pass219_h36_compression_gpu_version(void) {
    return h36_cgpu_version_word();
}

HHSExactStatus hhs_exact_pass219_h36_boolean_expand(
    const HHSExactVM81Frame *frame,
    uint8_t out_register[HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES]
) {
    uint32_t linear;
    if (frame == NULL || out_register == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    for (linear = 0U; linear < HHS_EXACT_PASS219_H36_FRAME_BITS; ++linear) {
        uint32_t word = linear / 64U;
        uint32_t bit = linear % 64U;
        out_register[linear] =
            (uint8_t)((frame->words[word] >> bit) & UINT64_C(1));
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_boolean_contract(
    const uint8_t register_bytes[HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES],
    HHSExactVM81Frame *out_frame
) {
    uint32_t linear;
    if (register_bytes == NULL || out_frame == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_frame, 0, sizeof(*out_frame));
    for (linear = 0U; linear < HHS_EXACT_PASS219_H36_FRAME_BITS; ++linear) {
        uint32_t word = linear / 64U;
        uint32_t bit = linear % 64U;
        if (register_bytes[linear] > 1U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        out_frame->words[word] |=
            ((uint64_t)register_bytes[linear]) << bit;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_hfc_snapshot_encode(
    const uint8_t register_bytes[HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES],
    uint8_t *out_snapshots,
    size_t capacity
) {
    uint32_t snapshot;
    uint32_t offset;
    if (register_bytes == NULL || out_snapshots == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (capacity < HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_BYTES)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;

    for (snapshot = 0U;
         snapshot < HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT;
         ++snapshot) {
        uint32_t start =
            snapshot * HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_STRIDE;
        for (offset = 0U;
             offset < HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_WIDTH;
             ++offset) {
            uint32_t linear =
                (start + offset) % HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES;
            uint8_t value = register_bytes[linear];
            if (value > 1U)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            out_snapshots[
                snapshot * HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_WIDTH + offset
            ] = value;
        }
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_hfc_snapshot_reconstruct(
    const uint8_t *snapshots,
    size_t snapshot_bytes,
    const uint8_t available[HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT],
    uint8_t out_register[HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES]
) {
    uint8_t seen[HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES];
    uint32_t snapshot;
    uint32_t offset;
    if (snapshots == NULL || available == NULL || out_register == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (snapshot_bytes < HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_BYTES)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;

    memset(seen, 0, sizeof(seen));
    memset(out_register, 0, HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES);

    for (snapshot = 0U;
         snapshot < HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT;
         ++snapshot) {
        uint32_t start;
        if (available[snapshot] > 1U)
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        if (available[snapshot] == 0U)
            continue;
        start = snapshot * HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_STRIDE;
        for (offset = 0U;
             offset < HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_WIDTH;
             ++offset) {
            uint32_t linear =
                (start + offset) % HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES;
            uint8_t value = snapshots[
                snapshot * HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_WIDTH + offset
            ];
            if (value > 1U)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            if (seen[linear] == 0U) {
                out_register[linear] = value;
                seen[linear] = 1U;
            } else if (out_register[linear] != value) {
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            }
        }
    }

    for (offset = 0U;
         offset < HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES;
         ++offset) {
        if (seen[offset] == 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_hfc_snapshot_reconstruct_blocks(
    const uint8_t *snapshots,
    size_t snapshot_bytes,
    const uint8_t available[HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT],
    uint8_t out_register[HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES]
) {
    uint32_t block;
    if (snapshots == NULL || available == NULL || out_register == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (snapshot_bytes < HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_BYTES)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;

    for (block = 0U;
         block < HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT;
         ++block) {
        uint32_t source_snapshot;
        uint32_t source_offset;
        uint32_t byte_offset;

        if (available[block] > 1U)
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;

        if (available[block] != 0U) {
            source_snapshot = block;
            source_offset = 0U;
        } else {
            uint32_t previous =
                (block + HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT - 1U) %
                HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT;
            if (available[previous] > 1U)
                return HHS_EXACT_STATUS_INVALID_ARGUMENT;
            if (available[previous] == 0U)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            source_snapshot = previous;
            source_offset = HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_STRIDE;
        }

        for (byte_offset = 0U;
             byte_offset < HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_STRIDE;
             ++byte_offset) {
            uint8_t value = snapshots[
                source_snapshot * HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_WIDTH +
                source_offset + byte_offset
            ];
            if (value > 1U)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            out_register[
                block * HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_STRIDE +
                byte_offset
            ] = value;
        }
    }

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_compression_verify(
    const HHSExactVM81Frame *frame,
    const HHSExactPass219InheritedPass210BindingV1 *pass210,
    HHSExactPass219H36CompressionWitnessV1 *out_witness
) {
    uint8_t register_bytes[HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES];
    uint8_t reconstructed_register[HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES];
    uint8_t snapshots[HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_BYTES];
    uint8_t available[HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT];
    uint8_t fib_descriptor[HHS_EXACT_PASS192_FIB_MAX_DESCRIPTOR_BYTES];
    size_t fib_length = 0U;
    HHSExactPass192FibonacciCompressionV1 fib;
    HHSExactVM81Frame contracted;
    HHSExactPass219H36HydrationWitnessV1 h36;
    uint32_t erasure;
    HHSExactStatus status;

    if (frame == NULL || out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = h36_validate_pass210(pass210);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219_h36_boolean_expand(frame, register_bytes);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_exact_pass219_h36_boolean_contract(register_bytes, &contracted);
    if (status != HHS_EXACT_STATUS_OK ||
        memcmp(frame, &contracted, sizeof(*frame)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_h36_hfc_snapshot_encode(
        register_bytes, snapshots, sizeof(snapshots));
    if (status != HHS_EXACT_STATUS_OK) return status;

    for (erasure = 0U;
         erasure < HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT;
         ++erasure) {
        memset(available, 1, sizeof(available));
        available[erasure] = 0U;
        status = hhs_exact_pass219_h36_hfc_snapshot_reconstruct_blocks(
            snapshots, sizeof(snapshots), available, reconstructed_register);
        if (status != HHS_EXACT_STATUS_OK ||
            memcmp(register_bytes, reconstructed_register,
                   sizeof(register_bytes)) != 0)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    status = hhs_exact_pass192_fibonacci_compress(
        HHS_EXACT_PASS219_UCE_FIBONACCI_DEPTH,
        fib_descriptor, sizeof(fib_descriptor), &fib_length, &fib);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass192_fibonacci_validate_descriptor(
        HHS_EXACT_PASS219_UCE_FIBONACCI_DEPTH,
        fib_descriptor, fib_length);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219_h36_hydration_roundtrip(frame, &h36);
    if (status != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_hydration_witness_validate(&h36) !=
            HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_witness, 0, sizeof(*out_witness));
    out_witness->struct_size = (uint32_t)sizeof(*out_witness);
    out_witness->version = h36_cgpu_version_word();
    out_witness->register_bytes = HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES;
    out_witness->snapshot_count = HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT;
    out_witness->snapshot_width = HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_WIDTH;
    out_witness->snapshot_stride = HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_STRIDE;
    out_witness->single_snapshot_erasure_drills =
        HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT;
    out_witness->fibonacci_depth = HHS_EXACT_PASS219_UCE_FIBONACCI_DEPTH;
    out_witness->fibonacci_descriptor_length = (uint32_t)fib_length;
    out_witness->vm81_boolean_expand_equal = 1U;
    out_witness->hfc_double_coverage_equal = 1U;
    out_witness->hfc_all_single_erasure_recoveries_equal = 1U;
    out_witness->fibonacci_descriptor_equal = 1U;
    out_witness->h36_roundtrip_equal = 1U;
    out_witness->exact_reconstruction_equal = 1U;
    out_witness->pass210_binding_preserved = 1U;
    out_witness->compression_path_mandatory = 1U;
    out_witness->canonical_mutation_authority = 0U;
    out_witness->canonical_hash72_authority = 0U;
    out_witness->canonical_persistence_authority = 0U;
    out_witness->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_gpu_locality_plan(
    const HHSExactPass219InheritedPass207BindingV1 *pass207,
    const HHSExactPass219InheritedPass208BindingV1 *pass208,
    uint16_t first_word144,
    uint16_t word_count,
    uint16_t first_bit36,
    uint16_t bit_count,
    HHSExactPass219H36GPULocalityPlanV1 *out_plan
) {
    HHSExactPass219BPhaseLocalityDimensionV1 dims[2];
    HHSExactStatus status;
    uint32_t selected;

    if (out_plan == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = h36_validate_gpu_bindings(pass207, pass208);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (word_count == 0U || bit_count == 0U ||
        first_word144 >= HHS_EXACT_PASS219_H36_WORD_COUNT ||
        first_bit36 >= HHS_EXACT_PASS219_H36_WORD_BITS ||
        (uint32_t)first_word144 + word_count >
            HHS_EXACT_PASS219_H36_WORD_COUNT ||
        (uint32_t)first_bit36 + bit_count >
            HHS_EXACT_PASS219_H36_WORD_BITS)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    selected = (uint32_t)word_count * (uint32_t)bit_count;
    dims[0].potential_q = HHS_EXACT_PASS219_H36_WORD_COUNT;
    dims[0].selected_s = word_count;
    dims[1].potential_q = HHS_EXACT_PASS219_H36_WORD_BITS;
    dims[1].selected_s = bit_count;

    memset(out_plan, 0, sizeof(*out_plan));
    out_plan->struct_size = (uint32_t)sizeof(*out_plan);
    out_plan->version = h36_cgpu_version_word();
    out_plan->first_word144 = first_word144;
    out_plan->word_count = word_count;
    out_plan->first_bit36 = first_bit36;
    out_plan->bit_count = bit_count;
    out_plan->selected_lane_count = selected;
    out_plan->full_lane_count = HHS_EXACT_PASS219_H36_FRAME_BITS;
    out_plan->avoided_lane_count =
        HHS_EXACT_PASS219_H36_FRAME_BITS - selected;

    status = hhs_exact_pass219b_phase_locality_plan(
        dims, 2U, 1U, 0U, 1U, &out_plan->locality);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (out_plan->locality.required_realized_units != selected)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_plan->pass207_bound = 1U;
    out_plan->pass208_bound = 1U;
    out_plan->candidate_only = 1U;
    out_plan->exact_cpu_vm81_equality_required = 1U;
    out_plan->stable_lane_identity_required = 1U;
    out_plan->hash216_lineage_required = 1U;
    out_plan->physical_completion_order_noncanonical = 1U;
    out_plan->singleton_vm81_admission_required = 1U;
    out_plan->canonical_mutation_authority = 0U;
    out_plan->canonical_hash72_authority = 0U;
    out_plan->canonical_persistence_authority = 0U;
    out_plan->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_gpu_locality_lane(
    const HHSExactPass219H36GPULocalityPlanV1 *plan,
    uint32_t ordinal,
    HHSExactPass219H36FactorizationCircuitV1 *out_circuit
) {
    uint32_t word_offset;
    uint32_t bit_offset;
    uint32_t word;
    uint32_t bit;
    uint16_t linear;
    if (plan == NULL || out_circuit == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (plan->struct_size != sizeof(*plan) ||
        plan->version != h36_cgpu_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (ordinal >= plan->selected_lane_count || plan->bit_count == 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    word_offset = ordinal / plan->bit_count;
    bit_offset = ordinal % plan->bit_count;
    word = plan->first_word144 + word_offset;
    bit = plan->first_bit36 + bit_offset;
    linear = (uint16_t)(word * HHS_EXACT_PASS219_H36_WORD_BITS + bit);
    return hhs_exact_pass219_h36_factorization_circuit(
        linear, out_circuit);
}

HHSExactStatus hhs_exact_pass219_h36_gpu_candidate_verify(
    const HHSExactPass219H36GPULocalityPlanV1 *plan,
    uint32_t realized_lane_count,
    const HHSExactVM81Frame *gpu_candidate,
    const HHSExactVM81Frame *cpu_vm81_oracle,
    HHSExactPass219H36GPUEqualityWitnessV1 *out_witness
) {
    HHSExactPass219H36HydrationWitnessV1 gpu_h36;
    HHSExactPass219H36HydrationWitnessV1 cpu_h36;
    HHSExactStatus status;

    if (plan == NULL || gpu_candidate == NULL ||
        cpu_vm81_oracle == NULL || out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (plan->struct_size != sizeof(*plan) ||
        plan->version != h36_cgpu_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (plan->candidate_only != 1U ||
        plan->exact_cpu_vm81_equality_required != 1U ||
        plan->singleton_vm81_admission_required != 1U ||
        plan->canonical_mutation_authority != 0U ||
        plan->canonical_hash72_authority != 0U ||
        plan->canonical_persistence_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219b_phase_locality_verify_realization(
        &plan->locality,
        realized_lane_count,
        1U,
        1U,
        0U);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (memcmp(gpu_candidate, cpu_vm81_oracle,
               sizeof(*gpu_candidate)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_h36_hydration_roundtrip(
        gpu_candidate, &gpu_h36);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_exact_pass219_h36_hydration_roundtrip(
        cpu_vm81_oracle, &cpu_h36);
    if (status != HHS_EXACT_STATUS_OK) return status;

    memset(out_witness, 0, sizeof(*out_witness));
    out_witness->struct_size = (uint32_t)sizeof(*out_witness);
    out_witness->version = h36_cgpu_version_word();
    out_witness->realized_lane_count = realized_lane_count;
    out_witness->gpu_cpu_frame_equal = 1U;
    out_witness->h36_gpu_roundtrip_equal = 1U;
    out_witness->h36_cpu_roundtrip_equal = 1U;
    out_witness->locality_realization_equal = 1U;
    out_witness->candidate_only_preserved = 1U;
    out_witness->singleton_vm81_admission_preserved = 1U;
    out_witness->canonical_mutation_authority = 0U;
    out_witness->canonical_hash72_authority = 0U;
    out_witness->canonical_persistence_authority = 0U;
    out_witness->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}
