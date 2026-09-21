#include "../include/hhs_pass219_lane5_reciprocal_phase_debt_cache_1_62.h"

#include <limits.h>
#include <stdio.h>
#include <string.h>

#define HHS_P219_LANE5_PHASE_DEBT_ALL40_MASK ((UINT64_C(1) << 40U) - UINT64_C(1))

static const uint8_t hhs_p219_lane5_phase_debt_sudoku81[9][9] = {
    {7U,3U,5U,2U,4U,9U,6U,8U,1U},
    {6U,8U,1U,7U,3U,5U,2U,4U,9U},
    {2U,4U,9U,6U,8U,1U,7U,3U,5U},
    {3U,5U,7U,4U,9U,2U,8U,1U,6U},
    {8U,1U,6U,3U,5U,7U,4U,9U,2U},
    {4U,9U,2U,8U,1U,6U,3U,5U,7U},
    {5U,7U,3U,9U,2U,4U,1U,6U,8U},
    {1U,6U,8U,5U,7U,3U,9U,2U,4U},
    {9U,2U,4U,1U,6U,8U,5U,7U,3U}
};

static const uint8_t hhs_p219_lane5_phase_debt_lo_shu[9] = {
    4U,9U,2U,3U,5U,7U,8U,1U,6U
};

static int hhs_p219_lane5_phase_debt_valid_flag(uint8_t value) {
    return value == 0U || value == 1U;
}

static void hhs_p219_lane5_phase_debt_position_anchor(
    uint8_t position,
    uint8_t *out_row,
    uint8_t *out_column
) {
    uint8_t zero = (uint8_t)(position - 1U);
    *out_row = (uint8_t)(zero / 9U);
    *out_column = (uint8_t)(zero % 9U);
}

static void hhs_p219_lane5_phase_debt_fingerprint_for_position(
    uint8_t position,
    uint8_t out[9]
) {
    uint8_t row;
    uint8_t column;
    int dr;
    int dc;
    size_t index = 0U;
    hhs_p219_lane5_phase_debt_position_anchor(position, &row, &column);
    for (dr = -1; dr <= 1; ++dr) {
        for (dc = -1; dc <= 1; ++dc) {
            int rr = ((int)row + dr + 9) % 9;
            int cc = ((int)column + dc + 9) % 9;
            out[index++] = hhs_p219_lane5_phase_debt_sudoku81[rr][cc];
        }
    }
}

static void hhs_p219_lane5_phase_debt_reciprocal_fingerprint(
    const uint8_t in[9],
    uint8_t out[9]
) {
    size_t i;
    for (i = 0U; i < 9U; ++i)
        out[i] = (uint8_t)(10U - in[8U - i]);
}

static int hhs_p219_lane5_phase_debt_fp_cmp(
    const uint8_t left[9],
    const uint8_t right[9]
) {
    return memcmp(left, right, 9U);
}

static void hhs_p219_lane5_phase_debt_canonical_key(
    const uint8_t direct[9],
    const uint8_t reciprocal[9],
    uint8_t out[9]
) {
    if (hhs_p219_lane5_phase_debt_fp_cmp(direct, reciprocal) <= 0)
        memcpy(out, direct, 9U);
    else
        memcpy(out, reciprocal, 9U);
}

static int16_t hhs_p219_lane5_phase_debt_sum9(const uint8_t values[9]) {
    size_t i;
    int16_t total = 0;
    for (i = 0U; i < 9U; ++i)
        total = (int16_t)(total + (int16_t)values[i]);
    return total;
}

static uint8_t hhs_p219_lane5_phase_debt_reciprocal_phase(uint8_t phase) {
    return (uint8_t)(((uint32_t)phase +
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_HALF_CYCLE) %
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_PHASE_MODULUS);
}

static void hhs_p219_lane5_phase_debt_hash_text(
    const char *text,
    char out[HHS_HASH216_BYTES_STRLEN]
) {
    hhs_hash216_compute_bytes(text, strlen(text), out);
}

static int hhs_p219_lane5_phase_debt_pair_boundary_valid(
    const HHSExactPass219Lane5PhaseDebtPairV1 *pair
) {
    return pair != NULL &&
        pair->pair_sum == HHS_EXACT_PASS219_LANE5_PHASE_DEBT_PAIR_SUM &&
        pair->pair_mean == HHS_EXACT_PASS219_LANE5_PHASE_DEBT_LO_SHU_SUM &&
        pair->normalization_offset ==
            HHS_EXACT_PASS219_LANE5_PHASE_DEBT_CLOSURE_OFFSET &&
        pair->normalized_mean == 0;
}

static void hhs_p219_lane5_phase_debt_event_receipt_hash(
    const HHSExactPass219Lane5PhaseDebtEventReceiptV1 *receipt,
    char out[HHS_HASH216_BYTES_STRLEN]
) {
    char material[768];
    int written = snprintf(
        material,
        sizeof(material),
        "HHS|P219|LANE5|PHASE-DEBT|1.62|kind=%u|accepted=%u|reason=%u|"
        "class=%u|orientation=%u|reciprocal=%u|phase=%u|expected=%u|"
        "direction=%d|qnum=%d|op64=%u|witness=%u|lineage=%llu|"
        "depth_before=%llu|depth_after=%llu|mask=%llu|lifted=%lld|"
        "clock=%u|covered=%u|zero=%u|ready=%u",
        (unsigned)receipt->kind,
        (unsigned)receipt->accepted,
        (unsigned)receipt->reason,
        (unsigned)receipt->class_id,
        (unsigned)receipt->orientation,
        (unsigned)receipt->reciprocal_orientation,
        (unsigned)receipt->phase_index,
        (unsigned)receipt->expected_reciprocal_phase,
        (int)receipt->clock_direction,
        (int)receipt->quantized_ninth_numerator,
        (unsigned)receipt->operation64,
        (unsigned)receipt->validated_computation_witness,
        (unsigned long long)receipt->lineage_token,
        (unsigned long long)receipt->depth_before,
        (unsigned long long)receipt->depth_after,
        (unsigned long long)receipt->closed_pair_mask,
        (long long)receipt->lifted_phase_units,
        (unsigned)receipt->current_phase_index,
        (unsigned)receipt->all_40_pairs_covered,
        (unsigned)receipt->zero_open_debt,
        (unsigned)receipt->commit_ready
    );
    if (written < 0 || (size_t)written >= sizeof(material))
        hhs_p219_lane5_phase_debt_hash_text("HHS|P219|LANE5|PHASE-DEBT|1.62|HASH-ERROR", out);
    else
        hhs_p219_lane5_phase_debt_hash_text(material, out);
}

static void hhs_p219_lane5_phase_debt_fill_event_state(
    const HHSExactPass219Lane5PhaseDebtCacheV1 *cache,
    HHSExactPass219Lane5PhaseDebtEventReceiptV1 *receipt
) {
    receipt->depth_after = (uint64_t)cache->depth;
    receipt->closed_pair_mask = cache->closed_pair_mask;
    receipt->lifted_phase_units = cache->lifted_phase_units;
    receipt->current_phase_index = cache->current_phase_index;
    receipt->all_40_pairs_covered =
        cache->closed_pair_mask == HHS_P219_LANE5_PHASE_DEBT_ALL40_MASK ? 1U : 0U;
    receipt->zero_open_debt = cache->depth == 0U ? 1U : 0U;
    receipt->commit_ready =
        receipt->all_40_pairs_covered != 0U &&
        receipt->zero_open_debt != 0U &&
        cache->nucleus_verified != 0U &&
        cache->topology_verified != 0U ? 1U : 0U;
    receipt->candidate_only = 1U;
    receipt->canonical_mutation_authority = 0U;
    receipt->canonical_hash72_authority = 0U;
    receipt->canonical_hash216_commit_authority = 0U;
}

static HHSExactStatus hhs_p219_lane5_phase_debt_reject(
    HHSExactPass219Lane5PhaseDebtCacheV1 *cache,
    HHSExactPass219Lane5PhaseDebtEventReceiptV1 *receipt,
    uint32_t reason
) {
    receipt->reason = reason;
    receipt->accepted = 0U;
    ++cache->rejected_event_count;
    hhs_p219_lane5_phase_debt_fill_event_state(cache, receipt);
    hhs_p219_lane5_phase_debt_event_receipt_hash(receipt, receipt->receipt_hash216);
    return HHS_EXACT_STATUS_OK;
}

uint32_t hhs_exact_pass219_lane5_phase_debt_version(void) {
    return HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_phase_debt_authority(
    HHSExactPass219Lane5PhaseDebtAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5PhaseDebtAuthorityV1 authority;
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&authority, 0, sizeof(authority));
    authority.struct_size = (uint32_t)sizeof(authority);
    authority.version = HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VERSION;
    authority.namespace_id = HHS_EXACT_PASS219_LANE5_PHASE_DEBT_NAMESPACE;
    authority.vm81_cells = HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VM81_CELLS;
    authority.reciprocal_classes =
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_RECIPROCAL_CLASSES;
    authority.outer_pair_count =
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_OUTER_PAIRS;
    authority.fingerprint_cells =
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_FINGERPRINT_CELLS;
    authority.operation64_states =
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_OPERATION64_STATES;
    authority.serialization_characters =
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_SERIALIZATION_CHARS;
    authority.phase_modulus =
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_PHASE_MODULUS;
    authority.half_cycle =
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_HALF_CYCLE;
    authority.orbit_step =
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_ORBIT_STEP;
    authority.lo_shu_sum =
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_LO_SHU_SUM;
    authority.pair_sum =
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_PAIR_SUM;
    authority.closure_offset =
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_CLOSURE_OFFSET;
    authority.quantization_denominator =
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_QUANT_DENOMINATOR;
    authority.quantization_numerator_abs_max =
        HHS_EXACT_PASS219_LANE5_PHASE_DEBT_QUANT_NUMERATOR_ABS_MAX;

    authority.one_fixed_nucleus_plus_40_pairs = 1U;
    authority.center_self_reciprocal = 1U;
    authority.reciprocal_position_sum_82 = 1U;
    authority.shared_canonical_fingerprint_required = 1U;
    authority.reciprocal_fingerprint_10_minus_rotate180 = 1U;
    authority.pair_mean_normalizes_to_45 = 1U;
    authority.closure_offset_minus45_to_zero = 1U;
    authority.exact_one_ninth_quantization = 1U;
    authority.half_cycle_phase36 = 1U;
    authority.bidirectional_orbit_step16 = 1U;
    authority.operation64_is_ordered_8x8 = 1U;
    authority.recursive_debt_is_separate_from_lane5_skip = 1U;
    authority.validated_witness_may_skip_compute = 1U;
    authority.validated_witness_may_skip_closure = 0U;
    authority.caller_workspace_controls_nesting_capacity = 1U;
    authority.commit_requires_all_40_pairs_covered = 1U;
    authority.commit_requires_zero_open_debt = 1U;
    authority.exact_integer_only = 1U;
    authority.candidate_only = 1U;
    authority.canonical_vm81_mutation_authority = 0U;
    authority.canonical_hash72_authority = 0U;
    authority.canonical_hash216_commit_authority = 0U;
    authority.canonical_persistence_authority = 0U;
    authority.floating_point_canonical_authority = 0U;
    *out_authority = authority;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_phase_debt_pair(
    uint8_t class_id,
    HHSExactPass219Lane5PhaseDebtPairV1 *out_pair
) {
    HHSExactPass219Lane5PhaseDebtPairV1 pair;
    uint8_t reciprocal_of_direct[9];
    uint8_t direct_position;
    uint8_t reciprocal_position;

    if (out_pair == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (class_id == 0U ||
        class_id > HHS_EXACT_PASS219_LANE5_PHASE_DEBT_RECIPROCAL_CLASSES)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    direct_position = class_id;
    reciprocal_position =
        class_id == HHS_EXACT_PASS219_LANE5_PHASE_DEBT_CENTER_POSITION
        ? class_id : (uint8_t)(82U - class_id);

    memset(&pair, 0, sizeof(pair));
    pair.struct_size = (uint32_t)sizeof(pair);
    pair.version = HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VERSION;
    pair.class_id = class_id;
    pair.direct_position = direct_position;
    pair.reciprocal_position = reciprocal_position;
    pair.fixed_center =
        class_id == HHS_EXACT_PASS219_LANE5_PHASE_DEBT_CENTER_POSITION ? 1U : 0U;

    hhs_p219_lane5_phase_debt_fingerprint_for_position(
        direct_position, pair.direct_fingerprint);
    hhs_p219_lane5_phase_debt_fingerprint_for_position(
        reciprocal_position, pair.reciprocal_fingerprint);
    hhs_p219_lane5_phase_debt_reciprocal_fingerprint(
        pair.direct_fingerprint, reciprocal_of_direct);
    if (memcmp(reciprocal_of_direct, pair.reciprocal_fingerprint, 9U) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    hhs_p219_lane5_phase_debt_canonical_key(
        pair.direct_fingerprint,
        pair.reciprocal_fingerprint,
        pair.canonical_fingerprint);

    pair.direct_sum = hhs_p219_lane5_phase_debt_sum9(pair.direct_fingerprint);
    pair.reciprocal_sum =
        hhs_p219_lane5_phase_debt_sum9(pair.reciprocal_fingerprint);
    pair.pair_sum = (int16_t)(pair.direct_sum + pair.reciprocal_sum);
    if ((pair.pair_sum & 1) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    pair.pair_mean = (int16_t)(pair.pair_sum / 2);
    pair.normalization_offset =
        (int16_t)HHS_EXACT_PASS219_LANE5_PHASE_DEBT_CLOSURE_OFFSET;
    pair.normalized_mean =
        (int16_t)(pair.pair_mean + pair.normalization_offset);
    pair.reciprocal_phase_delta =
        (uint8_t)HHS_EXACT_PASS219_LANE5_PHASE_DEBT_HALF_CYCLE;
    pair.quantization_denominator =
        (uint8_t)HHS_EXACT_PASS219_LANE5_PHASE_DEBT_QUANT_DENOMINATOR;
    pair.operation64_states =
        (uint8_t)HHS_EXACT_PASS219_LANE5_PHASE_DEBT_OPERATION64_STATES;

    if (!hhs_p219_lane5_phase_debt_pair_boundary_valid(&pair))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    *out_pair = pair;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_phase_debt_operation64_encode(
    uint8_t left_basis8,
    uint8_t right_basis8,
    uint8_t *out_operation64
) {
    if (out_operation64 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (left_basis8 >= 8U || right_basis8 >= 8U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    *out_operation64 = (uint8_t)(8U * left_basis8 + right_basis8);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_phase_debt_operation64_decode(
    uint8_t operation64,
    uint8_t *out_left_basis8,
    uint8_t *out_right_basis8
) {
    if (out_left_basis8 == NULL || out_right_basis8 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (operation64 >= 64U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    *out_left_basis8 = (uint8_t)(operation64 / 8U);
    *out_right_basis8 = (uint8_t)(operation64 % 8U);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_phase_debt_topology_verify(
    HHSExactPass219Lane5PhaseDebtTopologyReceiptV1 *out_receipt
) {
    uint8_t oriented[81][9];
    uint8_t keys[41][9];
    uint8_t seen64[64];
    uint8_t reciprocal_once[9];
    uint8_t reciprocal_twice[9];
    uint32_t position;
    uint8_t class_id;
    uint32_t i;
    uint32_t j;
    uint32_t op_count = 0U;
    int unique_oriented = 1;
    int unique_keys = 1;
    int all_pairs_size_two = 1;
    int reciprocal_all = 1;
    int all_means = 1;
    int all_normalized = 1;
    int center_is_lo_shu = 0;
    int center_self = 0;
    char material[512];
    int written;

    if (out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = (uint32_t)sizeof(*out_receipt);
    out_receipt->version = HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VERSION;

    for (position = 1U; position <= 81U; ++position) {
        hhs_p219_lane5_phase_debt_fingerprint_for_position(
            (uint8_t)position, oriented[position - 1U]);
        hhs_p219_lane5_phase_debt_reciprocal_fingerprint(
            oriented[position - 1U], reciprocal_once);
        hhs_p219_lane5_phase_debt_reciprocal_fingerprint(
            reciprocal_once, reciprocal_twice);
        if (memcmp(reciprocal_twice, oriented[position - 1U], 9U) != 0)
            reciprocal_all = 0;
    }

    for (i = 0U; i < 81U; ++i)
        for (j = i + 1U; j < 81U; ++j)
            if (memcmp(oriented[i], oriented[j], 9U) == 0)
                unique_oriented = 0;

    for (class_id = 1U; class_id <= 41U; ++class_id) {
        HHSExactPass219Lane5PhaseDebtPairV1 pair;
        if (hhs_exact_pass219_lane5_phase_debt_pair(class_id, &pair) !=
            HHS_EXACT_STATUS_OK)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        memcpy(keys[class_id - 1U], pair.canonical_fingerprint, 9U);
        if (class_id <= 40U) {
            if (pair.direct_position == pair.reciprocal_position)
                all_pairs_size_two = 0;
            if (pair.pair_mean != 45)
                all_means = 0;
            if (pair.normalized_mean != 0)
                all_normalized = 0;
        } else {
            center_is_lo_shu =
                memcmp(pair.direct_fingerprint,
                       hhs_p219_lane5_phase_debt_lo_shu, 9U) == 0;
            center_self =
                pair.fixed_center != 0U &&
                memcmp(pair.direct_fingerprint,
                       pair.reciprocal_fingerprint, 9U) == 0;
        }
    }

    for (i = 0U; i < 41U; ++i)
        for (j = i + 1U; j < 41U; ++j)
            if (memcmp(keys[i], keys[j], 9U) == 0)
                unique_keys = 0;

    memset(seen64, 0, sizeof(seen64));
    for (i = 0U; i < 8U; ++i) {
        for (j = 0U; j < 8U; ++j) {
            uint8_t op;
            uint8_t left;
            uint8_t right;
            if (hhs_exact_pass219_lane5_phase_debt_operation64_encode(
                    (uint8_t)i, (uint8_t)j, &op) != HHS_EXACT_STATUS_OK ||
                hhs_exact_pass219_lane5_phase_debt_operation64_decode(
                    op, &left, &right) != HHS_EXACT_STATUS_OK ||
                left != i || right != j || seen64[op] != 0U)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            seen64[op] = 1U;
            ++op_count;
        }
    }

    out_receipt->oriented_fingerprint_count = 81U;
    out_receipt->reciprocal_class_count = 41U;
    out_receipt->outer_pair_count = 40U;
    out_receipt->operation64_count = op_count;
    out_receipt->vm5184_coordinate_count = 81U * 64U;
    out_receipt->all_81_oriented_fingerprints_unique =
        unique_oriented ? 1U : 0U;
    out_receipt->all_41_canonical_keys_unique = unique_keys ? 1U : 0U;
    out_receipt->all_40_outer_classes_size_two =
        all_pairs_size_two ? 1U : 0U;
    out_receipt->center_is_single_fixed_class = center_self ? 1U : 0U;
    out_receipt->center_is_lo_shu = center_is_lo_shu ? 1U : 0U;
    out_receipt->center_self_reciprocal = center_self ? 1U : 0U;
    out_receipt->reciprocal_involution_all_81 = reciprocal_all ? 1U : 0U;
    out_receipt->all_outer_pair_means_45 = all_means ? 1U : 0U;
    out_receipt->all_outer_normalized_means_zero =
        all_normalized ? 1U : 0U;
    out_receipt->operation64_bijection = op_count == 64U ? 1U : 0U;
    out_receipt->vm81_x_operation64_is_5184 =
        out_receipt->vm5184_coordinate_count == 5184U ? 1U : 0U;
    out_receipt->exact_integer_only = 1U;
    out_receipt->candidate_only = 1U;
    out_receipt->topology_valid = (
        out_receipt->all_81_oriented_fingerprints_unique &&
        out_receipt->all_41_canonical_keys_unique &&
        out_receipt->all_40_outer_classes_size_two &&
        out_receipt->center_is_single_fixed_class &&
        out_receipt->center_is_lo_shu &&
        out_receipt->center_self_reciprocal &&
        out_receipt->reciprocal_involution_all_81 &&
        out_receipt->all_outer_pair_means_45 &&
        out_receipt->all_outer_normalized_means_zero &&
        out_receipt->operation64_bijection &&
        out_receipt->vm81_x_operation64_is_5184
    ) ? 1U : 0U;

    written = snprintf(
        material,
        sizeof(material),
        "HHS|P219|LANE5|PHASE-DEBT|TOPOLOGY|1.62|oriented=%u|classes=%u|"
        "pairs=%u|op64=%u|vm=%u|unique81=%u|unique41=%u|center=%u|"
        "involution=%u|mean45=%u|norm0=%u|valid=%u",
        (unsigned)out_receipt->oriented_fingerprint_count,
        (unsigned)out_receipt->reciprocal_class_count,
        (unsigned)out_receipt->outer_pair_count,
        (unsigned)out_receipt->operation64_count,
        (unsigned)out_receipt->vm5184_coordinate_count,
        (unsigned)out_receipt->all_81_oriented_fingerprints_unique,
        (unsigned)out_receipt->all_41_canonical_keys_unique,
        (unsigned)out_receipt->center_is_lo_shu,
        (unsigned)out_receipt->reciprocal_involution_all_81,
        (unsigned)out_receipt->all_outer_pair_means_45,
        (unsigned)out_receipt->all_outer_normalized_means_zero,
        (unsigned)out_receipt->topology_valid
    );
    if (written < 0 || (size_t)written >= sizeof(material))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    hhs_p219_lane5_phase_debt_hash_text(
        material, out_receipt->receipt_hash216);

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_phase_debt_cache_init(
    HHSExactPass219Lane5PhaseDebtCacheV1 *cache,
    HHSExactPass219Lane5PhaseDebtFrameV1 *frames,
    size_t frame_capacity
) {
    HHSExactPass219Lane5PhaseDebtTopologyReceiptV1 topology;
    if (cache == NULL || frames == NULL || frame_capacity == 0U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (hhs_exact_pass219_lane5_phase_debt_topology_verify(&topology) !=
            HHS_EXACT_STATUS_OK ||
        topology.topology_valid == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(cache, 0, sizeof(*cache));
    memset(frames, 0, frame_capacity * sizeof(*frames));
    cache->struct_size = (uint32_t)sizeof(*cache);
    cache->version = HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VERSION;
    cache->frames = frames;
    cache->frame_capacity = frame_capacity;
    cache->current_phase_index = 0U;
    cache->nucleus_verified =
        topology.center_is_lo_shu && topology.center_self_reciprocal ? 1U : 0U;
    cache->topology_verified = topology.topology_valid;
    cache->exact_integer_only = 1U;
    cache->candidate_only = 1U;
    cache->canonical_mutation_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_phase_debt_cache_apply(
    HHSExactPass219Lane5PhaseDebtCacheV1 *cache,
    const HHSExactPass219Lane5PhaseDebtEventV1 *event,
    HHSExactPass219Lane5PhaseDebtEventReceiptV1 *out_receipt
) {
    HHSExactPass219Lane5PhaseDebtPairV1 pair;
    uint32_t receipt_size;
    uint8_t expected_reciprocal_phase;

    if (cache == NULL || event == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    receipt_size = out_receipt->struct_size;
    if (cache->struct_size != sizeof(*cache) ||
        cache->version != HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VERSION ||
        cache->frames == NULL || cache->frame_capacity == 0U ||
        event->struct_size != sizeof(*event) ||
        event->version != HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VERSION ||
        receipt_size != sizeof(*out_receipt))
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = (uint32_t)sizeof(*out_receipt);
    out_receipt->version = HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VERSION;
    out_receipt->kind = event->kind;
    out_receipt->class_id = event->class_id;
    out_receipt->orientation = event->orientation;
    out_receipt->reciprocal_orientation = (uint8_t)(event->orientation ^ 1U);
    out_receipt->phase_index = event->phase_index;
    out_receipt->expected_reciprocal_phase =
        hhs_p219_lane5_phase_debt_reciprocal_phase(event->phase_index);
    out_receipt->operation64 = event->operation64;
    out_receipt->validated_computation_witness =
        event->validated_computation_witness;
    out_receipt->clock_direction = event->clock_direction;
    out_receipt->quantized_ninth_numerator =
        event->quantized_ninth_numerator;
    out_receipt->lineage_token = event->lineage_token;
    out_receipt->depth_before = (uint64_t)cache->depth;

    if (event->class_id == 0U || event->class_id > 41U)
        return hhs_p219_lane5_phase_debt_reject(
            cache, out_receipt,
            HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_CLASS_RANGE);
    if (event->class_id == 41U)
        return hhs_p219_lane5_phase_debt_reject(
            cache, out_receipt,
            HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_CENTER_NOT_PAIR);
    if (event->orientation > 1U)
        return hhs_p219_lane5_phase_debt_reject(
            cache, out_receipt,
            HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_ORIENTATION);
    if (event->quantized_ninth_numerator < -81 ||
        event->quantized_ninth_numerator > 81)
        return hhs_p219_lane5_phase_debt_reject(
            cache, out_receipt,
            HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_QUANTIZATION_RANGE);
    if (event->phase_index >= 72U)
        return hhs_p219_lane5_phase_debt_reject(
            cache, out_receipt,
            HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_PHASE_RANGE);
    if (event->clock_direction != -1 && event->clock_direction != 1)
        return hhs_p219_lane5_phase_debt_reject(
            cache, out_receipt,
            HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_DIRECTION);
    if (!hhs_p219_lane5_phase_debt_valid_flag(
            event->validated_computation_witness))
        return hhs_p219_lane5_phase_debt_reject(
            cache, out_receipt,
            HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_WITNESS_FLAG);
    if (event->operation64 >= 64U)
        return hhs_p219_lane5_phase_debt_reject(
            cache, out_receipt,
            HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_OPERATION64_RANGE);
    if (event->lineage_token == 0U)
        return hhs_p219_lane5_phase_debt_reject(
            cache, out_receipt,
            HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_LINEAGE_MISMATCH);

    if (hhs_exact_pass219_lane5_phase_debt_pair(event->class_id, &pair) !=
        HHS_EXACT_STATUS_OK ||
        !hhs_p219_lane5_phase_debt_pair_boundary_valid(&pair))
        return hhs_p219_lane5_phase_debt_reject(
            cache, out_receipt,
            HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_BOUNDARY_MISMATCH);

    out_receipt->normalized_pair_mean = pair.normalized_mean;

    if (event->kind == HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_OPEN) {
        HHSExactPass219Lane5PhaseDebtFrameV1 *frame;
        int next_phase;

        if (cache->depth >= cache->frame_capacity)
            return hhs_p219_lane5_phase_debt_reject(
                cache, out_receipt,
                HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_STACK_OVERFLOW);
        if (event->phase_index != cache->current_phase_index)
            return hhs_p219_lane5_phase_debt_reject(
                cache, out_receipt,
                HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_PHASE_RANGE);
        if ((event->clock_direction > 0 &&
             cache->lifted_phase_units > INT64_MAX - 16) ||
            (event->clock_direction < 0 &&
             cache->lifted_phase_units < INT64_MIN + 16))
            return hhs_p219_lane5_phase_debt_reject(
                cache, out_receipt,
                HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_PHASE_ACCUMULATOR_OVERFLOW);

        frame = &cache->frames[cache->depth];
        memset(frame, 0, sizeof(*frame));
        frame->class_id = event->class_id;
        frame->opening_orientation = event->orientation;
        frame->opening_phase_index = event->phase_index;
        frame->clock_direction = event->clock_direction;
        frame->quantized_ninth_numerator = event->quantized_ninth_numerator;
        frame->operation64 = event->operation64;
        frame->validated_computation_witness =
            event->validated_computation_witness;
        frame->lineage_token = event->lineage_token;
        memcpy(frame->canonical_fingerprint, pair.canonical_fingerprint, 9U);

        ++cache->depth;
        ++cache->open_event_count;
        if (event->validated_computation_witness != 0U)
            ++cache->validated_witness_replay_count;
        if (event->clock_direction > 0) {
            ++cache->forward_clock_steps;
            cache->lifted_phase_units += 16;
        } else {
            ++cache->reverse_clock_steps;
            cache->lifted_phase_units -= 16;
        }
        next_phase = (int)cache->current_phase_index +
            (int)event->clock_direction * 16;
        next_phase %= 72;
        if (next_phase < 0)
            next_phase += 72;
        cache->current_phase_index = (uint8_t)next_phase;

        out_receipt->accepted = 1U;
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_NONE;
    } else if (event->kind == HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_CLOSE) {
        HHSExactPass219Lane5PhaseDebtFrameV1 *frame;
        if (cache->depth == 0U)
            return hhs_p219_lane5_phase_debt_reject(
                cache, out_receipt,
                HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_STACK_UNDERFLOW);

        frame = &cache->frames[cache->depth - 1U];
        expected_reciprocal_phase =
            hhs_p219_lane5_phase_debt_reciprocal_phase(
                frame->opening_phase_index);
        out_receipt->expected_reciprocal_phase = expected_reciprocal_phase;

        if (event->class_id != frame->class_id)
            return hhs_p219_lane5_phase_debt_reject(
                cache, out_receipt,
                HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_STACK_CLASS_MISMATCH);
        if (event->orientation != (uint8_t)(frame->opening_orientation ^ 1U))
            return hhs_p219_lane5_phase_debt_reject(
                cache, out_receipt,
                HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_RECIPROCAL_ORIENTATION_MISMATCH);
        if (event->quantized_ninth_numerator !=
            (int16_t)(-frame->quantized_ninth_numerator))
            return hhs_p219_lane5_phase_debt_reject(
                cache, out_receipt,
                HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_QUANTIZATION_RECIPROCAL_MISMATCH);
        if (event->phase_index != expected_reciprocal_phase)
            return hhs_p219_lane5_phase_debt_reject(
                cache, out_receipt,
                HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_PHASE_RECIPROCAL_MISMATCH);
        if (event->lineage_token != frame->lineage_token)
            return hhs_p219_lane5_phase_debt_reject(
                cache, out_receipt,
                HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_LINEAGE_MISMATCH);
        if (event->operation64 != frame->operation64)
            return hhs_p219_lane5_phase_debt_reject(
                cache, out_receipt,
                HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_OPERATION64_IDENTITY_MISMATCH);
        if (event->clock_direction != frame->clock_direction)
            return hhs_p219_lane5_phase_debt_reject(
                cache, out_receipt,
                HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_DIRECTION);
        if (memcmp(frame->canonical_fingerprint,
                   pair.canonical_fingerprint, 9U) != 0)
            return hhs_p219_lane5_phase_debt_reject(
                cache, out_receipt,
                HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_BOUNDARY_MISMATCH);

        memset(frame, 0, sizeof(*frame));
        --cache->depth;
        ++cache->close_event_count;
        if (event->validated_computation_witness != 0U)
            ++cache->validated_witness_replay_count;
        cache->closed_pair_mask |=
            UINT64_C(1) << (uint64_t)(event->class_id - 1U);

        out_receipt->accepted = 1U;
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_NONE;
    } else {
        return hhs_p219_lane5_phase_debt_reject(
            cache, out_receipt,
            HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_CLASS_RANGE);
    }

    hhs_p219_lane5_phase_debt_fill_event_state(cache, out_receipt);
    hhs_p219_lane5_phase_debt_event_receipt_hash(
        out_receipt, out_receipt->receipt_hash216);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_phase_debt_commit_status(
    const HHSExactPass219Lane5PhaseDebtCacheV1 *cache,
    HHSExactPass219Lane5PhaseDebtCommitReceiptV1 *out_receipt
) {
    uint32_t receipt_size;
    char material[512];
    int written;
    if (cache == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    receipt_size = out_receipt->struct_size;
    if (cache->struct_size != sizeof(*cache) ||
        cache->version != HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VERSION ||
        cache->frames == NULL || cache->frame_capacity == 0U ||
        receipt_size != sizeof(*out_receipt))
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = (uint32_t)sizeof(*out_receipt);
    out_receipt->version = HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VERSION;
    out_receipt->closed_pair_mask = cache->closed_pair_mask;
    out_receipt->open_event_count = cache->open_event_count;
    out_receipt->close_event_count = cache->close_event_count;
    out_receipt->rejected_event_count = cache->rejected_event_count;
    out_receipt->validated_witness_replay_count =
        cache->validated_witness_replay_count;
    out_receipt->lifted_phase_units = cache->lifted_phase_units;
    out_receipt->depth = (uint64_t)cache->depth;
    out_receipt->current_phase_index = cache->current_phase_index;
    out_receipt->all_40_pairs_covered =
        cache->closed_pair_mask == HHS_P219_LANE5_PHASE_DEBT_ALL40_MASK ? 1U : 0U;
    out_receipt->zero_open_debt = cache->depth == 0U ? 1U : 0U;
    out_receipt->nucleus_verified = cache->nucleus_verified;
    out_receipt->topology_verified = cache->topology_verified;
    out_receipt->phase_at_genesis =
        cache->current_phase_index == 0U ? 1U : 0U;
    out_receipt->commit_ready =
        out_receipt->all_40_pairs_covered != 0U &&
        out_receipt->zero_open_debt != 0U &&
        out_receipt->nucleus_verified != 0U &&
        out_receipt->topology_verified != 0U ? 1U : 0U;
    out_receipt->candidate_only = 1U;
    out_receipt->canonical_mutation_authority = 0U;

    written = snprintf(
        material,
        sizeof(material),
        "HHS|P219|LANE5|PHASE-DEBT|COMMIT|1.62|mask=%llu|open=%llu|"
        "close=%llu|reject=%llu|witness=%llu|lifted=%lld|depth=%llu|"
        "clock=%u|covered=%u|zero=%u|nucleus=%u|topology=%u|genesis=%u|ready=%u",
        (unsigned long long)out_receipt->closed_pair_mask,
        (unsigned long long)out_receipt->open_event_count,
        (unsigned long long)out_receipt->close_event_count,
        (unsigned long long)out_receipt->rejected_event_count,
        (unsigned long long)out_receipt->validated_witness_replay_count,
        (long long)out_receipt->lifted_phase_units,
        (unsigned long long)out_receipt->depth,
        (unsigned)out_receipt->current_phase_index,
        (unsigned)out_receipt->all_40_pairs_covered,
        (unsigned)out_receipt->zero_open_debt,
        (unsigned)out_receipt->nucleus_verified,
        (unsigned)out_receipt->topology_verified,
        (unsigned)out_receipt->phase_at_genesis,
        (unsigned)out_receipt->commit_ready
    );
    if (written < 0 || (size_t)written >= sizeof(material))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    hhs_p219_lane5_phase_debt_hash_text(
        material, out_receipt->receipt_hash216);
    return HHS_EXACT_STATUS_OK;
}
