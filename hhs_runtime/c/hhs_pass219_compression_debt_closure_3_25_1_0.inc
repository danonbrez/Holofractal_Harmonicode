#include "../include/hhs_pass219_compression_debt_closure_3_25_1_0.h"

#include <limits.h>
#include <string.h>

_Static_assert(HHS_EXACT_PASS219_DEBT_VM81_CELLS *
                   HHS_EXACT_PASS219_DEBT_X86_WORD_BITS ==
               HHS_EXACT_PASS219_DEBT_BOUNDARY_BITS,
               "Pass219 compression-debt VM81 boundary drift");
_Static_assert(HHS_EXACT_HASH72_LEN * HHS_EXACT_HASH72_LEN ==
               HHS_EXACT_PASS219_DEBT_BOUNDARY_BITS,
               "Pass219 compression-debt Hash72 72x72 boundary drift");
_Static_assert(HHS_EXACT_PASS219_DEBT_HASH72_LANES *
                   HHS_EXACT_PASS219_DEBT_HASH72_GLYPHS_PER_LANE ==
               HHS_EXACT_PASS219_DEBT_HASH216_OCCURRENCES,
               "Pass219 compression-debt Hash216 lane drift");
_Static_assert(sizeof(HHSExactVM81Frame) ==
               HHS_EXACT_PASS219_DEBT_BOUNDARY_BYTES,
               "Pass219 compression-debt VM81 frame must be exactly 648 bytes");
_Static_assert(HHS_EXACT_PASS219_ACTIVE_SURFACE_TOTAL_CELLS ==
               HHS_EXACT_PASS219_DEBT_VM81_CELLS,
               "Pass219 active-surface VM81 census drift");

static uint32_t hhs219_debt_version_word(void) {
    return (HHS_EXACT_PASS219_COMPRESSION_DEBT_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_COMPRESSION_DEBT_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_COMPRESSION_DEBT_VERSION_PATCH;
}

static int hhs219_debt_bool(uint8_t value) {
    return value <= 1U;
}

static int hhs219_debt_add_u64(uint64_t a, uint64_t b, uint64_t *out) {
    if (out == NULL || UINT64_MAX - a < b)
        return 0;
    *out = a + b;
    return 1;
}

static int hhs219_debt_mul_u64_u32(uint64_t a, uint32_t b, uint64_t *out) {
    if (out == NULL)
        return 0;
    if (b != 0U && a > UINT64_MAX / (uint64_t)b)
        return 0;
    *out = a * (uint64_t)b;
    return 1;
}

static int hhs219_hash72_glyph_valid(char glyph) {
    size_t i;
    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i) {
        if (HHS_EXACT_HASH72_ALPHABET[i] == glyph)
            return 1;
    }
    return 0;
}

static int hhs219_transition_word216_valid(
    const char value[HHS_EXACT_UQCEL_HASH216_STRLEN]
) {
    size_t i;
    if (value == NULL ||
        value[HHS_EXACT_PASS219_DEBT_HASH216_OCCURRENCES] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_DEBT_HASH216_OCCURRENCES; ++i) {
        if (!hhs219_hash72_glyph_valid(value[i]))
            return 0;
    }
    return 1;
}

static int hhs219_sha256_witness_nonzero(
    const uint8_t witness[HHS_EXACT_PASS219_DEBT_SHA256_BYTES]
) {
    size_t i;
    if (witness == NULL)
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_DEBT_SHA256_BYTES; ++i) {
        if (witness[i] != 0U)
            return 1;
    }
    return 0;
}

static int hhs219_transition_lane_order_valid(
    const HHSExactPass219Hash216TransitionViewV1 *transition
) {
    if (transition == NULL ||
        transition->struct_size < sizeof(*transition) ||
        transition->version != hhs_exact_pass219_rna_version())
        return 0;

    if (memcmp(
            transition->transition_word216,
            transition->previous_hash72,
            HHS_EXACT_HASH72_LEN) != 0)
        return 0;
    if (memcmp(
            transition->transition_word216 + HHS_EXACT_HASH72_LEN,
            transition->change_hash72,
            HHS_EXACT_HASH72_LEN) != 0)
        return 0;
    if (memcmp(
            transition->transition_word216 + 2U * HHS_EXACT_HASH72_LEN,
            transition->receipt_hash72,
            HHS_EXACT_HASH72_LEN) != 0)
        return 0;
    return transition->transition_word216[
               HHS_EXACT_PASS219_DEBT_HASH216_OCCURRENCES] == '\0';
}

static int hhs219_transfer_entry_valid(
    const HHSExactPass219CompressionDebtTransferEntryV1 *entry,
    uint32_t required_role
) {
    if (entry == NULL ||
        entry->struct_size != sizeof(*entry) ||
        entry->version != hhs219_debt_version_word() ||
        entry->role != required_role ||
        entry->source_layer_id == entry->target_layer_id ||
        entry->amount == 0U ||
        entry->source_slot5184 >= HHS_EXACT_PASS219_DEBT_BOUNDARY_BITS ||
        entry->target_slot5184 >= HHS_EXACT_PASS219_DEBT_BOUNDARY_BITS ||
        entry->phase_left8 >= HHS_EXACT_PHASE_BASIS_COUNT ||
        entry->phase_right8 >= HHS_EXACT_PHASE_BASIS_COUNT ||
        !hhs219_debt_bool(entry->witness_present) ||
        !hhs219_debt_bool(entry->canonical_authority_requested) ||
        entry->witness_present != 1U ||
        entry->canonical_authority_requested != 0U ||
        !hhs219_transition_word216_valid(entry->source_transition_word216) ||
        !hhs219_transition_word216_valid(entry->target_transition_word216) ||
        !hhs219_sha256_witness_nonzero(entry->closure_witness_sha256))
        return 0;

    return 1;
}

static int hhs219_layer_result_valid(
    const HHSExactPass219CompressionDebtLayerResultV1 *layer
) {
    uint64_t total;
    uint64_t accounted;
    uint64_t outstanding;

    if (layer == NULL ||
        layer->struct_size != sizeof(*layer) ||
        layer->version != hhs219_debt_version_word() ||
        layer->active_cell_count > HHS_EXACT_PASS219_ACTIVE_SURFACE_CELLS ||
        layer->local_zero_sum_closed != 1U ||
        layer->active_surface_within_7_of_81 != 1U ||
        layer->full_vm81_frame_preserved != 1U ||
        layer->canonical_authority != 0U ||
        layer->floating_point_authority != 0U)
        return 0;

    if (!hhs219_debt_add_u64(layer->inbound_debt, layer->issued_debt, &total) ||
        !hhs219_debt_add_u64(
            layer->executed_settled, layer->retained_compressed, &accounted) ||
        !hhs219_debt_add_u64(accounted, layer->transferred_out, &accounted) ||
        !hhs219_debt_add_u64(
            layer->retained_compressed, layer->transferred_out, &outstanding))
        return 0;

    return total == layer->total_obligation &&
           accounted == layer->accounted_obligation &&
           outstanding == layer->outstanding_debt &&
           total == accounted;
}

uint32_t hhs_exact_pass219_compression_debt_version(void) {
    return hhs219_debt_version_word();
}

HHSExactStatus hhs_exact_pass219_compression_debt_policy(
    HHSExactPass219CompressionDebtPolicyV1 *out_policy
) {
    if (out_policy == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_policy, 0, sizeof(*out_policy));
    out_policy->struct_size = (uint32_t)sizeof(*out_policy);
    out_policy->version = hhs219_debt_version_word();

    out_policy->boundary_bits = HHS_EXACT_PASS219_DEBT_BOUNDARY_BITS;
    out_policy->boundary_bytes = HHS_EXACT_PASS219_DEBT_BOUNDARY_BYTES;
    out_policy->vm81_cells = HHS_EXACT_PASS219_DEBT_VM81_CELLS;
    out_policy->x86_word_bits = HHS_EXACT_PASS219_DEBT_X86_WORD_BITS;

    out_policy->hash72_lanes = HHS_EXACT_PASS219_DEBT_HASH72_LANES;
    out_policy->hash72_glyphs_per_lane =
        HHS_EXACT_PASS219_DEBT_HASH72_GLYPHS_PER_LANE;
    out_policy->hash216_occurrences =
        HHS_EXACT_PASS219_DEBT_HASH216_OCCURRENCES;
    out_policy->sha256_bytes = HHS_EXACT_PASS219_DEBT_SHA256_BYTES;

    out_policy->debt_exchange_numerator =
        HHS_EXACT_PASS219_DEBT_EXCHANGE_NUMERATOR;
    out_policy->debt_exchange_denominator =
        HHS_EXACT_PASS219_DEBT_EXCHANGE_DENOMINATOR;
    out_policy->capacity_exchange_numerator =
        HHS_EXACT_PASS219_CAPACITY_EXCHANGE_NUMERATOR;
    out_policy->capacity_exchange_denominator =
        HHS_EXACT_PASS219_CAPACITY_EXCHANGE_DENOMINATOR;

    out_policy->active_surface_cells =
        HHS_EXACT_PASS219_ACTIVE_SURFACE_CELLS;
    out_policy->active_surface_total_cells =
        HHS_EXACT_PASS219_ACTIVE_SURFACE_TOTAL_CELLS;
    out_policy->active_surface_reduction_numerator =
        HHS_EXACT_PASS219_ACTIVE_SURFACE_REDUCTION_NUMERATOR;
    out_policy->active_surface_reduction_denominator =
        HHS_EXACT_PASS219_ACTIVE_SURFACE_REDUCTION_DENOMINATOR;
    out_policy->active_surface_reduction_x1000 =
        HHS_EXACT_PASS219_ACTIVE_SURFACE_REDUCTION_X1000;

    out_policy->physical_time_monotonic = 1U;
    out_policy->timing_is_noncanonical = 1U;
    out_policy->compression_debt_is_conserved_quantity = 1U;
    out_policy->anonymous_debt_cross_boundary_allowed = 0U;
    out_policy->reciprocal_transfer_required = 1U;
    out_policy->full_vm81_frame_preserved = 1U;
    out_policy->hash216_indexes_required_for_transfer = 1U;
    out_policy->singleton_vm81_authority_preserved = 1U;
    out_policy->hash72_hash216_authority_preserved = 1U;
    out_policy->floating_point_authority = 0U;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_compression_debt_policy_validate(void) {
    HHSExactPass219CompressionDebtPolicyV1 p;
    uint64_t left;
    uint64_t right;

    if (hhs_exact_pass219_compression_debt_policy(&p) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (p.struct_size != sizeof(p) ||
        p.version != hhs219_debt_version_word() ||
        p.boundary_bits != HHS_EXACT_VM81_FRAME_BITS ||
        p.boundary_bytes != HHS_EXACT_VM81_FRAME_BYTES ||
        p.vm81_cells != HHS_EXACT_VM81_CELLS ||
        p.x86_word_bits != HHS_EXACT_VM81_WORD_BITS ||
        p.hash72_lanes != 3U ||
        p.hash72_glyphs_per_lane != 72U ||
        p.hash216_occurrences != HHS_EXACT_PASS219_HASH216_OCCURRENCES ||
        p.sha256_bytes != HHS_EXACT_PASS219_HASH216_SHA256_BYTES ||
        p.debt_exchange_numerator != 3U ||
        p.debt_exchange_denominator != 25U ||
        p.capacity_exchange_numerator != 25U ||
        p.capacity_exchange_denominator != 3U ||
        p.active_surface_cells != 7U ||
        p.active_surface_total_cells != 81U ||
        p.active_surface_reduction_numerator != 81U ||
        p.active_surface_reduction_denominator != 7U ||
        p.active_surface_reduction_x1000 != 11571U ||
        p.physical_time_monotonic != 1U ||
        p.timing_is_noncanonical != 1U ||
        p.compression_debt_is_conserved_quantity != 1U ||
        p.anonymous_debt_cross_boundary_allowed != 0U ||
        p.reciprocal_transfer_required != 1U ||
        p.full_vm81_frame_preserved != 1U ||
        p.hash216_indexes_required_for_transfer != 1U ||
        p.singleton_vm81_authority_preserved != 1U ||
        p.hash72_hash216_authority_preserved != 1U ||
        p.floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    left = (uint64_t)p.debt_exchange_numerator *
           (uint64_t)p.capacity_exchange_numerator;
    right = (uint64_t)p.debt_exchange_denominator *
            (uint64_t)p.capacity_exchange_denominator;
    if (left != right)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if ((uint64_t)p.active_surface_reduction_numerator * 1000U /
            p.active_surface_reduction_denominator !=
        p.active_surface_reduction_x1000)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (hhs_exact_pass219_global_latency_policy_validate() !=
        HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_compression_debt_exchange(
    uint64_t debt_units,
    HHSExactPass219CompressionDebtExchangeV1 *out_exchange
) {
    uint64_t compression_numerator;
    uint64_t capacity_numerator;

    if (out_exchange == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs219_debt_mul_u64_u32(
            debt_units,
            HHS_EXACT_PASS219_DEBT_EXCHANGE_NUMERATOR,
            &compression_numerator) ||
        !hhs219_debt_mul_u64_u32(
            debt_units,
            HHS_EXACT_PASS219_CAPACITY_EXCHANGE_NUMERATOR,
            &capacity_numerator))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_exchange, 0, sizeof(*out_exchange));
    out_exchange->struct_size = (uint32_t)sizeof(*out_exchange);
    out_exchange->version = hhs219_debt_version_word();
    out_exchange->debt_units = debt_units;
    out_exchange->compression_numerator = compression_numerator;
    out_exchange->compression_denominator =
        HHS_EXACT_PASS219_DEBT_EXCHANGE_DENOMINATOR;
    out_exchange->execution_capacity_numerator = capacity_numerator;
    out_exchange->execution_capacity_denominator =
        HHS_EXACT_PASS219_CAPACITY_EXCHANGE_DENOMINATOR;
    out_exchange->reciprocal_exact = 1U;
    out_exchange->floating_point_authority = 0U;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_compression_debt_layer_close(
    const HHSExactPass219CompressionDebtLayerInputV1 *input,
    HHSExactPass219CompressionDebtLayerResultV1 *out_result
) {
    uint64_t total;
    uint64_t accounted;
    uint64_t outstanding;
    uint32_t active_count = 0U;
    uint32_t i;

    if (input == NULL || out_result == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (input->struct_size != sizeof(*input) ||
        input->version != hhs219_debt_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (!hhs219_debt_bool(input->canonical_authority_requested) ||
        input->canonical_authority_requested != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (i = 0U; i < HHS_EXACT_PASS219_DEBT_VM81_CELLS; ++i) {
        if (!hhs219_debt_bool(input->active_cell_mask[i]))
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        if (input->active_cell_mask[i] != 0U)
            ++active_count;
    }
    if (active_count > HHS_EXACT_PASS219_ACTIVE_SURFACE_CELLS)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!hhs219_debt_add_u64(input->inbound_debt, input->issued_debt, &total) ||
        !hhs219_debt_add_u64(
            input->executed_settled, input->retained_compressed, &accounted) ||
        !hhs219_debt_add_u64(accounted, input->transferred_out, &accounted) ||
        !hhs219_debt_add_u64(
            input->retained_compressed, input->transferred_out, &outstanding))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_result, 0, sizeof(*out_result));
    out_result->struct_size = (uint32_t)sizeof(*out_result);
    out_result->version = hhs219_debt_version_word();
    out_result->layer_id = input->layer_id;
    out_result->active_cell_count = active_count;
    out_result->inbound_debt = input->inbound_debt;
    out_result->issued_debt = input->issued_debt;
    out_result->executed_settled = input->executed_settled;
    out_result->retained_compressed = input->retained_compressed;
    out_result->transferred_out = input->transferred_out;
    out_result->total_obligation = total;
    out_result->accounted_obligation = accounted;
    out_result->outstanding_debt = outstanding;
    out_result->local_zero_sum_closed = (uint8_t)(total == accounted ? 1U : 0U);
    out_result->active_surface_within_7_of_81 = 1U;
    out_result->full_vm81_frame_preserved = 1U;
    out_result->canonical_authority = 0U;
    out_result->floating_point_authority = 0U;

    return total == accounted
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_compression_debt_transfer_pair_verify(
    HHSExactPass219CompressionDebtTransferPairV1 *pair
) {
    HHSExactPass219CompressionDebtTransferEntryV1 *debit;
    HHSExactPass219CompressionDebtTransferEntryV1 *credit;

    if (pair == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (pair->struct_size != sizeof(*pair) ||
        pair->version != hhs219_debt_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    debit = &pair->source_debit;
    credit = &pair->target_credit;

    pair->reciprocal_amount_equal = 0U;
    pair->reciprocal_identity_equal = 0U;
    pair->reciprocal_address_equal = 0U;
    pair->reciprocal_phase_equal = 0U;
    pair->reciprocal_witness_equal = 0U;
    pair->canonical_authority = 0U;
    pair->floating_point_authority = 0U;
    pair->pair_verified = 0U;

    if (!hhs219_transfer_entry_valid(
            debit, HHS_EXACT_PASS219_DEBT_TRANSFER_ROLE_SOURCE_DEBIT) ||
        !hhs219_transfer_entry_valid(
            credit, HHS_EXACT_PASS219_DEBT_TRANSFER_ROLE_TARGET_CREDIT))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    pair->reciprocal_amount_equal =
        (uint8_t)(debit->amount == credit->amount ? 1U : 0U);
    pair->reciprocal_identity_equal =
        (uint8_t)(debit->source_layer_id == credit->source_layer_id &&
                  debit->target_layer_id == credit->target_layer_id &&
                  debit->modality_id == credit->modality_id &&
                  memcmp(debit->source_transition_word216,
                         credit->source_transition_word216,
                         HHS_EXACT_UQCEL_HASH216_STRLEN) == 0 &&
                  memcmp(debit->target_transition_word216,
                         credit->target_transition_word216,
                         HHS_EXACT_UQCEL_HASH216_STRLEN) == 0 ? 1U : 0U);
    pair->reciprocal_address_equal =
        (uint8_t)(debit->source_slot5184 == credit->source_slot5184 &&
                  debit->target_slot5184 == credit->target_slot5184 ? 1U : 0U);
    pair->reciprocal_phase_equal =
        (uint8_t)(debit->phase_left8 == credit->phase_left8 &&
                  debit->phase_right8 == credit->phase_right8 ? 1U : 0U);
    pair->reciprocal_witness_equal =
        (uint8_t)(memcmp(debit->closure_witness_sha256,
                         credit->closure_witness_sha256,
                         HHS_EXACT_PASS219_DEBT_SHA256_BYTES) == 0 ? 1U : 0U);

    pair->pair_verified =
        (uint8_t)(pair->reciprocal_amount_equal != 0U &&
                  pair->reciprocal_identity_equal != 0U &&
                  pair->reciprocal_address_equal != 0U &&
                  pair->reciprocal_phase_equal != 0U &&
                  pair->reciprocal_witness_equal != 0U ? 1U : 0U);

    return pair->pair_verified != 0U
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_compression_debt_transfer_pair_verify_bound(
    HHSExactPass219CompressionDebtTransferPairV1 *pair,
    const HHSExactPass219Hash216TransitionViewV1 *source_transition,
    const HHSExactPass219Hash216TransitionViewV1 *target_transition
) {
    HHSExactStatus status;

    if (pair == NULL || source_transition == NULL || target_transition == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_pass219_compression_debt_transfer_pair_verify(pair);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (!hhs219_transition_lane_order_valid(source_transition) ||
        !hhs219_transition_lane_order_valid(target_transition) ||
        hhs_exact_pass219_hash216_indexes_complete(source_transition) !=
            HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_hash216_indexes_complete(target_transition) !=
            HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (memcmp(pair->source_debit.source_transition_word216,
               source_transition->transition_word216,
               HHS_EXACT_UQCEL_HASH216_STRLEN) != 0 ||
        memcmp(pair->source_debit.target_transition_word216,
               target_transition->transition_word216,
               HHS_EXACT_UQCEL_HASH216_STRLEN) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_compression_debt_global_close(
    const HHSExactPass219CompressionDebtLayerResultV1 *layers,
    size_t layer_count,
    HHSExactPass219CompressionDebtTransferPairV1 *pairs,
    size_t pair_count,
    HHSExactPass219CompressionDebtGlobalResultV1 *out_result
) {
    uint64_t created = 0U;
    uint64_t settled = 0U;
    uint64_t retained = 0U;
    uint64_t debit_total = 0U;
    uint64_t credit_total = 0U;
    uint64_t inbound_by_layer[HHS_EXACT_PASS219_DEBT_MAX_LAYERS] = {0U};
    uint64_t outbound_by_layer[HHS_EXACT_PASS219_DEBT_MAX_LAYERS] = {0U};
    size_t i;
    size_t j;

    if (layers == NULL || out_result == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (layer_count == 0U || layer_count > HHS_EXACT_PASS219_DEBT_MAX_LAYERS ||
        pair_count > HHS_EXACT_PASS219_DEBT_MAX_TRANSFER_PAIRS ||
        (pair_count != 0U && pairs == NULL))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    for (i = 0U; i < layer_count; ++i) {
        if (!hhs219_layer_result_valid(&layers[i]))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        for (j = i + 1U; j < layer_count; ++j) {
            if (layers[i].layer_id == layers[j].layer_id)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        if (!hhs219_debt_add_u64(created, layers[i].issued_debt, &created) ||
            !hhs219_debt_add_u64(settled, layers[i].executed_settled, &settled) ||
            !hhs219_debt_add_u64(retained, layers[i].retained_compressed, &retained))
            return HHS_EXACT_STATUS_RANGE_ERROR;
    }

    for (i = 0U; i < pair_count; ++i) {
        size_t source_index = SIZE_MAX;
        size_t target_index = SIZE_MAX;
        HHSExactStatus status =
            hhs_exact_pass219_compression_debt_transfer_pair_verify(&pairs[i]);
        if (status != HHS_EXACT_STATUS_OK)
            return status;

        for (j = 0U; j < layer_count; ++j) {
            if (layers[j].layer_id == pairs[i].source_debit.source_layer_id)
                source_index = j;
            if (layers[j].layer_id == pairs[i].source_debit.target_layer_id)
                target_index = j;
        }
        if (source_index == SIZE_MAX || target_index == SIZE_MAX)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        if (!hhs219_debt_add_u64(
                outbound_by_layer[source_index],
                pairs[i].source_debit.amount,
                &outbound_by_layer[source_index]) ||
            !hhs219_debt_add_u64(
                inbound_by_layer[target_index],
                pairs[i].target_credit.amount,
                &inbound_by_layer[target_index]) ||
            !hhs219_debt_add_u64(
                debit_total, pairs[i].source_debit.amount, &debit_total) ||
            !hhs219_debt_add_u64(
                credit_total, pairs[i].target_credit.amount, &credit_total))
            return HHS_EXACT_STATUS_RANGE_ERROR;
    }

    for (i = 0U; i < layer_count; ++i) {
        if (outbound_by_layer[i] != layers[i].transferred_out ||
            inbound_by_layer[i] != layers[i].inbound_debt)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    memset(out_result, 0, sizeof(*out_result));
    out_result->struct_size = (uint32_t)sizeof(*out_result);
    out_result->version = hhs219_debt_version_word();
    out_result->layer_count = (uint32_t)layer_count;
    out_result->transfer_pair_count = (uint32_t)pair_count;
    out_result->created_total = created;
    out_result->settled_total = settled;
    out_result->retained_total = retained;
    out_result->internal_transfer_debit_total = debit_total;
    out_result->internal_transfer_credit_total = credit_total;
    out_result->global_outstanding_debt = retained;
    out_result->all_layers_closed = 1U;
    out_result->internal_transfers_cancel =
        (uint8_t)(debit_total == credit_total ? 1U : 0U);
    out_result->issued_equals_settled_plus_outstanding =
        (uint8_t)(created <= UINT64_MAX - retained &&
                  created == settled + retained ? 1U : 0U);
    out_result->global_zero_sum_closed =
        (uint8_t)(out_result->all_layers_closed != 0U &&
                  out_result->internal_transfers_cancel != 0U &&
                  out_result->issued_equals_settled_plus_outstanding != 0U ? 1U : 0U);
    out_result->canonical_authority = 0U;
    out_result->floating_point_authority = 0U;

    return out_result->global_zero_sum_closed != 0U
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_compression_debt_schedule_evaluate(
    uint64_t observed_ns,
    const HHSExactPass219CompressionDebtLayerResultV1 *layer,
    HHSExactPass219CompressionDebtScheduleResultV1 *out_result
) {
    uint32_t tier;

    if (layer == NULL || out_result == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs219_layer_result_valid(layer))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (hhs_exact_pass219_global_latency_classify_ns(
            observed_ns, &tier) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_result, 0, sizeof(*out_result));
    out_result->struct_size = (uint32_t)sizeof(*out_result);
    out_result->version = hhs219_debt_version_word();
    out_result->latency_tier = tier;
    out_result->observed_ns = observed_ns;
    out_result->outstanding_debt = layer->outstanding_debt;
    out_result->within_25_over_3_ms =
        (uint8_t)(tier == HHS_EXACT_PASS219_LATENCY_TIER1_120FPS ? 1U : 0U);
    out_result->local_ledger_closed = 1U;
    out_result->active_surface_within_7_of_81 = 1U;
    out_result->timing_is_noncanonical = 1U;
    out_result->physical_time_monotonic = 1U;
    out_result->canonical_authority = 0U;
    out_result->decision =
        out_result->within_25_over_3_ms != 0U
            ? HHS_EXACT_PASS219_DEBT_SCHEDULE_LOCAL_WITHIN_25_3
            : HHS_EXACT_PASS219_DEBT_SCHEDULE_TRANSFER_OR_RECOMPRESS;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_native_5184_closure_boundary_verify(
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *source_transition,
    const HHSExactPass219NativePhaseWitnessV1 *phase_witness,
    const HHSExactPass219CompressionDebtLayerResultV1 *layer,
    HHSExactPass219CompressionDebtTransferPairV1 *pairs,
    size_t pair_count,
    const HHSExactPass219Hash216TransitionViewV1 *target_transitions,
    size_t target_transition_count,
    HHSExactPass219NativeClosureBoundaryResultV1 *out_result
) {
    HHSExactPass219GenesisDescriptorV1 genesis;
    HHSExactPass219NativePhaseWitnessV1 expected_phase;
    HHSExactPass219H36Hash216TransitionBindingV1 source_binding;
    HHSExactVM81Frame roundtrip;
    uint8_t bytes[HHS_EXACT_VM81_FRAME_BYTES];
    size_t bytes_written = 0U;
    uint64_t transfer_total = 0U;
    size_t i;

    if (frame == NULL || source_transition == NULL ||
        phase_witness == NULL || layer == NULL || out_result == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (pair_count > HHS_EXACT_PASS219_DEBT_MAX_TRANSFER_PAIRS ||
        pair_count != target_transition_count ||
        (pair_count != 0U && (pairs == NULL || target_transitions == NULL)))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (!hhs219_layer_result_valid(layer))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_result, 0, sizeof(*out_result));
    out_result->struct_size = (uint32_t)sizeof(*out_result);
    out_result->version = hhs219_debt_version_word();
    out_result->boundary_bits = HHS_EXACT_PASS219_DEBT_BOUNDARY_BITS;
    out_result->boundary_bytes = HHS_EXACT_PASS219_DEBT_BOUNDARY_BYTES;
    out_result->active_cell_count = layer->active_cell_count;
    out_result->transfer_pair_count = (uint32_t)pair_count;
    out_result->outstanding_debt = layer->outstanding_debt;

    if (hhs_exact_vm81_frame_export_le(
            frame, bytes, sizeof(bytes), &bytes_written) == HHS_EXACT_STATUS_OK &&
        bytes_written == HHS_EXACT_PASS219_DEBT_BOUNDARY_BYTES &&
        hhs_exact_vm81_frame_import_le(
            bytes, bytes_written, &roundtrip) == HHS_EXACT_STATUS_OK &&
        memcmp(frame, &roundtrip, sizeof(roundtrip)) == 0)
        out_result->vm81_frame_roundtrip_exact = 1U;

    if (hhs_exact_pass219_genesis_descriptor(&genesis) == HHS_EXACT_STATUS_OK &&
        hhs_exact_pass219_genesis_validate(&genesis) == HHS_EXACT_STATUS_OK &&
        genesis.trinary_zero_sum_rows == 1U &&
        genesis.trinary_zero_sum_columns == 1U &&
        genesis.trinary_zero_sum_blocks == 1U &&
        genesis.trinary_zero_sum_diagonals == 1U &&
        genesis.lo_shu_binding_valid == 1U &&
        genesis.phase_channel_binding_valid == 1U)
        out_result->genesis_sudoku_zero_sum_valid = 1U;

    if (phase_witness->struct_size == sizeof(*phase_witness) &&
        phase_witness->version == hhs_exact_pass219_rna_version() &&
        phase_witness->left_basis < HHS_EXACT_PHASE_BASIS_COUNT &&
        phase_witness->right_basis < HHS_EXACT_PHASE_BASIS_COUNT &&
        hhs_exact_pass219_native_phase_witness(
            phase_witness->left_basis,
            phase_witness->right_basis,
            &expected_phase) == HHS_EXACT_STATUS_OK &&
        memcmp(phase_witness, &expected_phase, sizeof(expected_phase)) == 0 &&
        phase_witness->ordered_source_preserved == 1U)
        out_result->ordered_phase_witness_valid = 1U;

    if (hhs219_transition_lane_order_valid(source_transition))
        out_result->hash216_lane_order_valid = 1U;

    if (hhs_exact_pass219_hash216_indexes_complete(source_transition) ==
        HHS_EXACT_STATUS_OK)
        out_result->hash216_sha256_indexes_complete = 1U;

    if (hhs_exact_pass219_h36_hash216_transition_bind(
            source_transition, &source_binding) == HHS_EXACT_STATUS_OK &&
        source_binding.vector_indexes_complete == 1U &&
        source_binding.all_occurrences_factorized == 1U &&
        source_binding.directional_lane_order_preserved == 1U &&
        hhs_exact_pass219_h36_hash216_transition_binding_validate(
            source_transition, &source_binding) == HHS_EXACT_STATUS_OK)
        out_result->hash216_native_5184_binding_valid = 1U;

    out_result->debt_local_zero_sum_closed = layer->local_zero_sum_closed;
    out_result->active_surface_within_7_of_81 =
        layer->active_surface_within_7_of_81;

    for (i = 0U; i < pair_count; ++i) {
        HHSExactPass219H36Hash216TransitionBindingV1 target_binding;
        HHSExactStatus status;

        if (pairs[i].source_debit.source_layer_id != layer->layer_id)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        status = hhs_exact_pass219_compression_debt_transfer_pair_verify_bound(
            &pairs[i], source_transition, &target_transitions[i]);
        if (status != HHS_EXACT_STATUS_OK)
            return status;

        if (hhs_exact_pass219_h36_hash216_transition_bind(
                &target_transitions[i], &target_binding) != HHS_EXACT_STATUS_OK ||
            target_binding.vector_indexes_complete != 1U ||
            target_binding.all_occurrences_factorized != 1U ||
            hhs_exact_pass219_h36_hash216_transition_binding_validate(
                &target_transitions[i], &target_binding) != HHS_EXACT_STATUS_OK)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        if (!hhs219_debt_add_u64(
                transfer_total, pairs[i].source_debit.amount, &transfer_total))
            return HHS_EXACT_STATUS_RANGE_ERROR;
    }

    out_result->transferred_debt_verified = transfer_total;
    out_result->transferred_debt_fully_typed =
        (uint8_t)(transfer_total == layer->transferred_out ? 1U : 0U);

    if (hhs_exact_pass219_global_latency_policy_validate() ==
        HHS_EXACT_STATUS_OK)
        out_result->latency_policy_bound = 1U;

    out_result->singleton_vm81_authority_preserved = 1U;
    out_result->hash72_hash216_authority_preserved = 1U;
    out_result->canonical_authority = 0U;
    out_result->floating_point_authority = 0U;

    out_result->native_boundary_valid =
        (uint8_t)(out_result->vm81_frame_roundtrip_exact != 0U &&
                  out_result->genesis_sudoku_zero_sum_valid != 0U &&
                  out_result->ordered_phase_witness_valid != 0U &&
                  out_result->hash216_lane_order_valid != 0U &&
                  out_result->hash216_sha256_indexes_complete != 0U &&
                  out_result->hash216_native_5184_binding_valid != 0U &&
                  out_result->debt_local_zero_sum_closed != 0U &&
                  out_result->transferred_debt_fully_typed != 0U &&
                  out_result->active_surface_within_7_of_81 != 0U &&
                  out_result->latency_policy_bound != 0U &&
                  out_result->singleton_vm81_authority_preserved != 0U &&
                  out_result->hash72_hash216_authority_preserved != 0U ? 1U : 0U);

    return out_result->native_boundary_valid != 0U
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}
