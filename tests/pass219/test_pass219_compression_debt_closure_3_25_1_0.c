#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static HHSExactStatus resolver(
    const char transition_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    uint8_t lane_role,
    uint8_t lane_position72,
    uint16_t absolute_position216,
    uint8_t glyph,
    uint8_t out_sha256[HHS_EXACT_PASS219_HASH216_SHA256_BYTES],
    void *context
) {
    uint32_t i;
    (void)context;
    if (transition_identity216 == NULL || out_sha256 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_SHA256_BYTES; ++i) {
        out_sha256[i] = (uint8_t)(
            glyph ^ lane_role ^ lane_position72 ^
            (uint8_t)absolute_position216 ^
            (uint8_t)transition_identity216[
                i % HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] ^
            (uint8_t)(i + 1U));
    }
    return HHS_EXACT_STATUS_OK;
}

static void fill_hash72(
    char out[HHS_EXACT_HASH72_STRLEN],
    uint8_t offset
) {
    uint32_t i;
    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_HASH72_LEN] = '\0';
}

static void fill_identity216(
    char out[HHS_EXACT_UQCEL_HASH216_STRLEN],
    uint8_t offset
) {
    uint32_t i;
    for (i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i * 5U + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
}

static void build_transition(
    HHSExactPass219Hash216TransitionViewV1 *out,
    uint8_t offset
) {
    char previous[HHS_EXACT_HASH72_STRLEN];
    char change[HHS_EXACT_HASH72_STRLEN];
    char receipt[HHS_EXACT_HASH72_STRLEN];
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN];

    fill_hash72(previous, offset);
    fill_hash72(change, (uint8_t)(offset + 1U));
    fill_hash72(receipt, (uint8_t)(offset + 2U));
    fill_identity216(identity, (uint8_t)(offset + 3U));

    assert(hhs_exact_pass219_hash216_transition_init(
        previous, change, receipt, identity, out) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_hash216_resolve_indexes(
        out, resolver, NULL) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_hash216_indexes_complete(out) == HHS_EXACT_STATUS_OK);
}

static HHSExactPass219CompressionDebtLayerResultV1 close_layer(
    uint32_t layer_id,
    uint64_t inbound,
    uint64_t issued,
    uint64_t executed,
    uint64_t retained,
    uint64_t transferred,
    uint32_t active_count
) {
    HHSExactPass219CompressionDebtLayerInputV1 input;
    HHSExactPass219CompressionDebtLayerResultV1 result;
    uint32_t i;

    memset(&input, 0, sizeof(input));
    input.struct_size = (uint32_t)sizeof(input);
    input.version = hhs_exact_pass219_compression_debt_version();
    input.layer_id = layer_id;
    input.inbound_debt = inbound;
    input.issued_debt = issued;
    input.executed_settled = executed;
    input.retained_compressed = retained;
    input.transferred_out = transferred;
    for (i = 0U; i < active_count; ++i)
        input.active_cell_mask[(i * 11U) % 81U] = 1U;

    assert(hhs_exact_pass219_compression_debt_layer_close(
        &input, &result) == HHS_EXACT_STATUS_OK);
    return result;
}

static void init_transfer_entry(
    HHSExactPass219CompressionDebtTransferEntryV1 *entry,
    uint32_t role,
    uint32_t source_layer,
    uint32_t target_layer,
    uint64_t amount,
    uint16_t source_slot,
    uint16_t target_slot,
    const HHSExactPass219Hash216TransitionViewV1 *source,
    const HHSExactPass219Hash216TransitionViewV1 *target,
    uint8_t witness_seed
) {
    uint32_t i;
    memset(entry, 0, sizeof(*entry));
    entry->struct_size = (uint32_t)sizeof(*entry);
    entry->version = hhs_exact_pass219_compression_debt_version();
    entry->role = role;
    entry->source_layer_id = source_layer;
    entry->target_layer_id = target_layer;
    entry->modality_id = 17U;
    entry->amount = amount;
    entry->source_slot5184 = source_slot;
    entry->target_slot5184 = target_slot;
    entry->phase_left8 = HHS_EXACT_PHASE_X;
    entry->phase_right8 = HHS_EXACT_PHASE_Y;
    entry->witness_present = 1U;
    memcpy(entry->source_transition_word216,
           source->transition_word216,
           HHS_EXACT_UQCEL_HASH216_STRLEN);
    memcpy(entry->target_transition_word216,
           target->transition_word216,
           HHS_EXACT_UQCEL_HASH216_STRLEN);
    for (i = 0U; i < HHS_EXACT_PASS219_DEBT_SHA256_BYTES; ++i)
        entry->closure_witness_sha256[i] =
            (uint8_t)(witness_seed ^ (uint8_t)(i + 1U));
}

static HHSExactPass219CompressionDebtTransferPairV1 make_pair(
    uint32_t source_layer,
    uint32_t target_layer,
    uint64_t amount,
    uint16_t source_slot,
    uint16_t target_slot,
    const HHSExactPass219Hash216TransitionViewV1 *source,
    const HHSExactPass219Hash216TransitionViewV1 *target,
    uint8_t witness_seed
) {
    HHSExactPass219CompressionDebtTransferPairV1 pair;
    memset(&pair, 0, sizeof(pair));
    pair.struct_size = (uint32_t)sizeof(pair);
    pair.version = hhs_exact_pass219_compression_debt_version();

    init_transfer_entry(
        &pair.source_debit,
        HHS_EXACT_PASS219_DEBT_TRANSFER_ROLE_SOURCE_DEBIT,
        source_layer, target_layer, amount, source_slot, target_slot,
        source, target, witness_seed);
    init_transfer_entry(
        &pair.target_credit,
        HHS_EXACT_PASS219_DEBT_TRANSFER_ROLE_TARGET_CREDIT,
        source_layer, target_layer, amount, source_slot, target_slot,
        source, target, witness_seed);

    assert(hhs_exact_pass219_compression_debt_transfer_pair_verify(&pair) ==
           HHS_EXACT_STATUS_OK);
    return pair;
}

int main(void) {
    HHSExactPass219CompressionDebtPolicyV1 policy;
    HHSExactPass219CompressionDebtExchangeV1 exchange;
    HHSExactPass219CompressionDebtLayerResultV1 layers[3];
    HHSExactPass219CompressionDebtTransferPairV1 pairs[2];
    HHSExactPass219CompressionDebtGlobalResultV1 global;
    HHSExactPass219CompressionDebtScheduleResultV1 schedule;
    HHSExactPass219NativeClosureBoundaryResultV1 boundary;
    HHSExactPass219Hash216TransitionViewV1 source_transition;
    HHSExactPass219Hash216TransitionViewV1 targets[2];
    HHSExactPass219NativePhaseWitnessV1 phase;
    HHSExactVM81Frame frame;
    uint32_t i;

    assert(hhs_exact_pass219_compression_debt_version() ==
           ((1U << 16U) | 0U));
    assert(hhs_exact_pass219_compression_debt_policy(&policy) ==
           HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_compression_debt_policy_validate() ==
           HHS_EXACT_STATUS_OK);

    assert(policy.boundary_bits == 5184U);
    assert(policy.boundary_bytes == 648U);
    assert(policy.vm81_cells == 81U);
    assert(policy.x86_word_bits == 64U);
    assert(policy.hash72_lanes == 3U);
    assert(policy.hash216_occurrences == 216U);
    assert(policy.debt_exchange_numerator == 3U);
    assert(policy.debt_exchange_denominator == 25U);
    assert(policy.capacity_exchange_numerator == 25U);
    assert(policy.capacity_exchange_denominator == 3U);
    assert(policy.active_surface_cells == 7U);
    assert(policy.active_surface_total_cells == 81U);
    assert(policy.active_surface_reduction_x1000 == 11571U);
    assert(policy.physical_time_monotonic == 1U);
    assert(policy.compression_debt_is_conserved_quantity == 1U);
    assert(policy.anonymous_debt_cross_boundary_allowed == 0U);

    assert(hhs_exact_pass219_compression_debt_exchange(9U, &exchange) ==
           HHS_EXACT_STATUS_OK);
    assert(exchange.compression_numerator == 27U);
    assert(exchange.compression_denominator == 25U);
    assert(exchange.execution_capacity_numerator == 225U);
    assert(exchange.execution_capacity_denominator == 3U);
    assert(exchange.reciprocal_exact == 1U);

    build_transition(&source_transition, 0U);
    build_transition(&targets[0], 9U);
    build_transition(&targets[1], 18U);

    layers[0] = close_layer(1U, 0U, 9U, 3U, 0U, 6U, 7U);
    layers[1] = close_layer(2U, 4U, 0U, 0U, 4U, 0U, 1U);
    layers[2] = close_layer(3U, 2U, 0U, 0U, 2U, 0U, 1U);

    assert(layers[0].total_obligation == 9U);
    assert(layers[0].accounted_obligation == 9U);
    assert(layers[0].outstanding_debt == 6U);
    assert(layers[0].active_cell_count == 7U);

    pairs[0] = make_pair(
        1U, 2U, 4U, 0U, 64U,
        &source_transition, &targets[0], 0x51U);
    pairs[1] = make_pair(
        1U, 3U, 2U, 1U, 128U,
        &source_transition, &targets[1], 0xA3U);

    assert(hhs_exact_pass219_compression_debt_transfer_pair_verify_bound(
        &pairs[0], &source_transition, &targets[0]) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_compression_debt_transfer_pair_verify_bound(
        &pairs[1], &source_transition, &targets[1]) == HHS_EXACT_STATUS_OK);

    assert(hhs_exact_pass219_compression_debt_global_close(
        layers, 3U, pairs, 2U, &global) == HHS_EXACT_STATUS_OK);
    assert(global.created_total == 9U);
    assert(global.settled_total == 3U);
    assert(global.retained_total == 6U);
    assert(global.internal_transfer_debit_total == 6U);
    assert(global.internal_transfer_credit_total == 6U);
    assert(global.global_outstanding_debt == 6U);
    assert(global.global_zero_sum_closed == 1U);

    assert(hhs_exact_pass219_compression_debt_schedule_evaluate(
        UINT64_C(8000000), &layers[0], &schedule) == HHS_EXACT_STATUS_OK);
    assert(schedule.within_25_over_3_ms == 1U);
    assert(schedule.decision ==
           HHS_EXACT_PASS219_DEBT_SCHEDULE_LOCAL_WITHIN_25_3);
    assert(schedule.physical_time_monotonic == 1U);
    assert(schedule.timing_is_noncanonical == 1U);

    assert(hhs_exact_pass219_compression_debt_schedule_evaluate(
        UINT64_C(9000000), &layers[0], &schedule) == HHS_EXACT_STATUS_OK);
    assert(schedule.within_25_over_3_ms == 0U);
    assert(schedule.decision ==
           HHS_EXACT_PASS219_DEBT_SCHEDULE_TRANSFER_OR_RECOMPRESS);

    assert(hhs_exact_pass219_native_phase_witness(
        HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y, &phase) ==
        HHS_EXACT_STATUS_OK);

    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        frame.words[i] =
            UINT64_C(0x9E3779B97F4A7C15) ^
            ((uint64_t)i * UINT64_C(0x0102030405060708));

    assert(hhs_exact_pass219_native_5184_closure_boundary_verify(
        &frame,
        &source_transition,
        &phase,
        &layers[0],
        pairs,
        2U,
        targets,
        2U,
        &boundary) == HHS_EXACT_STATUS_OK);
    assert(boundary.boundary_bits == 5184U);
    assert(boundary.boundary_bytes == 648U);
    assert(boundary.transferred_debt_verified == 6U);
    assert(boundary.vm81_frame_roundtrip_exact == 1U);
    assert(boundary.genesis_sudoku_zero_sum_valid == 1U);
    assert(boundary.ordered_phase_witness_valid == 1U);
    assert(boundary.hash216_lane_order_valid == 1U);
    assert(boundary.hash216_sha256_indexes_complete == 1U);
    assert(boundary.hash216_native_5184_binding_valid == 1U);
    assert(boundary.debt_local_zero_sum_closed == 1U);
    assert(boundary.transferred_debt_fully_typed == 1U);
    assert(boundary.active_surface_within_7_of_81 == 1U);
    assert(boundary.latency_policy_bound == 1U);
    assert(boundary.native_boundary_valid == 1U);
    assert(boundary.canonical_authority == 0U);

    {
        HHSExactPass219CompressionDebtLayerInputV1 too_wide;
        HHSExactPass219CompressionDebtLayerResultV1 rejected;
        memset(&too_wide, 0, sizeof(too_wide));
        too_wide.struct_size = (uint32_t)sizeof(too_wide);
        too_wide.version = hhs_exact_pass219_compression_debt_version();
        too_wide.layer_id = 7U;
        too_wide.issued_debt = 8U;
        too_wide.executed_settled = 8U;
        for (i = 0U; i < 8U; ++i)
            too_wide.active_cell_mask[i] = 1U;
        assert(hhs_exact_pass219_compression_debt_layer_close(
            &too_wide, &rejected) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    }

    {
        HHSExactPass219CompressionDebtTransferPairV1 mismatch = pairs[0];
        mismatch.target_credit.amount = 5U;
        assert(hhs_exact_pass219_compression_debt_transfer_pair_verify(
            &mismatch) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
        assert(mismatch.pair_verified == 0U);
    }

    {
        HHSExactPass219CompressionDebtTransferPairV1 orphan[1] = {pairs[0]};
        assert(hhs_exact_pass219_compression_debt_global_close(
            layers, 3U, orphan, 1U, &global) ==
            HHS_EXACT_STATUS_INVARIANT_FAILURE);
    }

    {
        HHSExactPass219Hash216TransitionViewV1 incomplete = targets[0];
        incomplete.occurrences[0].sha256_index_present = 0U;
        incomplete.resolved_index_count -= 1U;
        assert(hhs_exact_pass219_compression_debt_transfer_pair_verify_bound(
            &pairs[0], &source_transition, &incomplete) ==
            HHS_EXACT_STATUS_INVARIANT_FAILURE);
    }

    puts("PASS219 compression-debt native 5184 closure: PASS");
    return 0;
}
