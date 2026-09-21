#include "hhs_runtime_exact_abi.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CHECK(expr) do {     if (!(expr)) {         fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr);         return 1;     } } while (0)

static void reset_event(
    HHSExactPass219Lane5PhaseDebtEventV1 *event,
    uint32_t kind,
    uint8_t class_id,
    uint8_t orientation,
    uint8_t phase,
    int8_t direction,
    int16_t qnum,
    uint8_t operation64,
    uint8_t witness,
    uint64_t lineage
) {
    memset(event, 0, sizeof(*event));
    event->struct_size = (uint32_t)sizeof(*event);
    event->version = HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VERSION;
    event->kind = kind;
    event->class_id = class_id;
    event->orientation = orientation;
    event->phase_index = phase;
    event->clock_direction = direction;
    event->quantized_ninth_numerator = qnum;
    event->operation64 = operation64;
    event->validated_computation_witness = witness;
    event->lineage_token = lineage;
}

static void reset_event_receipt(
    HHSExactPass219Lane5PhaseDebtEventReceiptV1 *receipt
) {
    memset(receipt, 0, sizeof(*receipt));
    receipt->struct_size = (uint32_t)sizeof(*receipt);
}

static void reset_commit_receipt(
    HHSExactPass219Lane5PhaseDebtCommitReceiptV1 *receipt
) {
    memset(receipt, 0, sizeof(*receipt));
    receipt->struct_size = (uint32_t)sizeof(*receipt);
}

static uint8_t reciprocal_phase(uint8_t phase) {
    return (uint8_t)(((uint32_t)phase + 36U) % 72U);
}

int main(void) {
    HHSExactPass219Lane5PhaseDebtAuthorityV1 authority;
    HHSExactPass219Lane5PhaseDebtTopologyReceiptV1 topology;
    HHSExactPass219Lane5PhaseDebtPairV1 pair;
    HHSExactPass219Lane5PhaseDebtCacheV1 cache;
    HHSExactPass219Lane5PhaseDebtFrameV1 frames[128];
    HHSExactPass219Lane5PhaseDebtEventV1 event;
    HHSExactPass219Lane5PhaseDebtEventReceiptV1 receipt;
    HHSExactPass219Lane5PhaseDebtCommitReceiptV1 commit;
    uint8_t left;
    uint8_t right;
    uint8_t op;
    uint32_t i;
    uint32_t j;

    memset(&authority, 0, sizeof(authority));
    authority.struct_size = (uint32_t)sizeof(authority);
    CHECK(hhs_exact_pass219_lane5_phase_debt_version() ==
          HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VERSION);
    CHECK(hhs_exact_pass219_lane5_phase_debt_authority(&authority) ==
          HHS_EXACT_STATUS_OK);
    CHECK(authority.vm81_cells == 81U);
    CHECK(authority.reciprocal_classes == 41U);
    CHECK(authority.outer_pair_count == 40U);
    CHECK(authority.fingerprint_cells == 9U);
    CHECK(authority.operation64_states == 64U);
    CHECK(authority.serialization_characters == 5184U);
    CHECK(authority.phase_modulus == 72U);
    CHECK(authority.half_cycle == 36U);
    CHECK(authority.orbit_step == 16U);
    CHECK(authority.lo_shu_sum == 45);
    CHECK(authority.pair_sum == 90);
    CHECK(authority.closure_offset == -45);
    CHECK(authority.quantization_denominator == 9);
    CHECK(authority.quantization_numerator_abs_max == 81);
    CHECK(authority.one_fixed_nucleus_plus_40_pairs == 1U);
    CHECK(authority.center_self_reciprocal == 1U);
    CHECK(authority.reciprocal_position_sum_82 == 1U);
    CHECK(authority.shared_canonical_fingerprint_required == 1U);
    CHECK(authority.reciprocal_fingerprint_10_minus_rotate180 == 1U);
    CHECK(authority.pair_mean_normalizes_to_45 == 1U);
    CHECK(authority.closure_offset_minus45_to_zero == 1U);
    CHECK(authority.exact_one_ninth_quantization == 1U);
    CHECK(authority.half_cycle_phase36 == 1U);
    CHECK(authority.bidirectional_orbit_step16 == 1U);
    CHECK(authority.operation64_is_ordered_8x8 == 1U);
    CHECK(authority.recursive_debt_is_separate_from_lane5_skip == 1U);
    CHECK(authority.validated_witness_may_skip_compute == 1U);
    CHECK(authority.validated_witness_may_skip_closure == 0U);
    CHECK(authority.caller_workspace_controls_nesting_capacity == 1U);
    CHECK(authority.commit_requires_all_40_pairs_covered == 1U);
    CHECK(authority.commit_requires_zero_open_debt == 1U);
    CHECK(authority.exact_integer_only == 1U);
    CHECK(authority.candidate_only == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_commit_authority == 0U);
    CHECK(authority.canonical_persistence_authority == 0U);
    CHECK(authority.floating_point_canonical_authority == 0U);

    memset(&topology, 0, sizeof(topology));
    topology.struct_size = (uint32_t)sizeof(topology);
    CHECK(hhs_exact_pass219_lane5_phase_debt_topology_verify(&topology) ==
          HHS_EXACT_STATUS_OK);
    CHECK(topology.oriented_fingerprint_count == 81U);
    CHECK(topology.reciprocal_class_count == 41U);
    CHECK(topology.outer_pair_count == 40U);
    CHECK(topology.operation64_count == 64U);
    CHECK(topology.vm5184_coordinate_count == 5184U);
    CHECK(topology.all_81_oriented_fingerprints_unique == 1U);
    CHECK(topology.all_41_canonical_keys_unique == 1U);
    CHECK(topology.all_40_outer_classes_size_two == 1U);
    CHECK(topology.center_is_single_fixed_class == 1U);
    CHECK(topology.center_is_lo_shu == 1U);
    CHECK(topology.center_self_reciprocal == 1U);
    CHECK(topology.reciprocal_involution_all_81 == 1U);
    CHECK(topology.all_outer_pair_means_45 == 1U);
    CHECK(topology.all_outer_normalized_means_zero == 1U);
    CHECK(topology.operation64_bijection == 1U);
    CHECK(topology.vm81_x_operation64_is_5184 == 1U);
    CHECK(topology.topology_valid == 1U);
    CHECK(strlen(topology.receipt_hash216) == 216U);

    memset(&pair, 0, sizeof(pair));
    CHECK(hhs_exact_pass219_lane5_phase_debt_pair(1U, &pair) ==
          HHS_EXACT_STATUS_OK);
    CHECK(pair.class_id == 1U);
    CHECK(pair.direct_position == 1U);
    CHECK(pair.reciprocal_position == 81U);
    CHECK(pair.fixed_center == 0U);
    CHECK(pair.direct_sum + pair.reciprocal_sum == 90);
    CHECK(pair.pair_mean == 45);
    CHECK(pair.normalization_offset == -45);
    CHECK(pair.normalized_mean == 0);
    CHECK(pair.reciprocal_phase_delta == 36U);
    CHECK(pair.quantization_denominator == 9U);
    CHECK(pair.operation64_states == 64U);

    memset(&pair, 0, sizeof(pair));
    CHECK(hhs_exact_pass219_lane5_phase_debt_pair(41U, &pair) ==
          HHS_EXACT_STATUS_OK);
    CHECK(pair.fixed_center == 1U);
    CHECK(pair.direct_position == 41U);
    CHECK(pair.reciprocal_position == 41U);
    {
        static const uint8_t lo_shu[9] = {4U,9U,2U,3U,5U,7U,8U,1U,6U};
        CHECK(memcmp(pair.direct_fingerprint, lo_shu, sizeof(lo_shu)) == 0);
        CHECK(memcmp(pair.reciprocal_fingerprint, lo_shu, sizeof(lo_shu)) == 0);
    }

    for (i = 0U; i < 8U; ++i) {
        for (j = 0U; j < 8U; ++j) {
            CHECK(hhs_exact_pass219_lane5_phase_debt_operation64_encode(
                      (uint8_t)i, (uint8_t)j, &op) == HHS_EXACT_STATUS_OK);
            CHECK(op == (uint8_t)(8U * i + j));
            CHECK(hhs_exact_pass219_lane5_phase_debt_operation64_decode(
                      op, &left, &right) == HHS_EXACT_STATUS_OK);
            CHECK(left == (uint8_t)i);
            CHECK(right == (uint8_t)j);
        }
    }

    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_init(
              &cache, frames, 128U) == HHS_EXACT_STATUS_OK);

    /* Recursive debt: class 1 contains class 2. */
    reset_event(&event, HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_OPEN,
                1U, 0U, 0U, 1, 9, 7U, 0U, UINT64_C(0x1001));
    reset_event_receipt(&receipt);
    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
              &cache, &event, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.accepted == 1U);
    CHECK(cache.depth == 1U);
    CHECK(cache.current_phase_index == 16U);

    reset_event(&event, HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_OPEN,
                2U, 1U, 16U, -1, -18, 13U, 1U, UINT64_C(0x1002));
    reset_event_receipt(&receipt);
    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
              &cache, &event, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.accepted == 1U);
    CHECK(cache.depth == 2U);
    CHECK(cache.current_phase_index == 0U);
    CHECK(cache.validated_witness_replay_count == 1U);

    /* Parent cannot close while child debt remains. */
    reset_event(&event, HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_CLOSE,
                1U, 1U, 36U, 1, -9, 7U, 0U, UINT64_C(0x1001));
    reset_event_receipt(&receipt);
    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
              &cache, &event, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.accepted == 0U);
    CHECK(receipt.reason ==
          HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_STACK_CLASS_MISMATCH);
    CHECK(cache.depth == 2U);

    /* A validated compute witness does not skip reciprocal closure. */
    reset_event(&event, HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_CLOSE,
                2U, 0U, reciprocal_phase(16U), -1, 18, 13U, 1U,
                UINT64_C(0x1002));
    reset_event_receipt(&receipt);
    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
              &cache, &event, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.accepted == 1U);
    CHECK(cache.depth == 1U);
    CHECK(cache.validated_witness_replay_count == 2U);

    reset_event(&event, HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_CLOSE,
                1U, 1U, reciprocal_phase(0U), 1, -9, 7U, 0U,
                UINT64_C(0x1001));
    reset_event_receipt(&receipt);
    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
              &cache, &event, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.accepted == 1U);
    CHECK(cache.depth == 0U);
    CHECK((cache.closed_pair_mask & UINT64_C(3)) == UINT64_C(3));

    /* The nucleus is singular and cannot be opened as an outer pair. */
    reset_event(&event, HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_OPEN,
                41U, 0U, cache.current_phase_index, 1, 0, 0U, 0U,
                UINT64_C(0x1041));
    reset_event_receipt(&receipt);
    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
              &cache, &event, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.accepted == 0U);
    CHECK(receipt.reason ==
          HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_CENTER_NOT_PAIR);

    /* Fresh cache: every one of the 40 classes must close before commit. */
    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_init(
              &cache, frames, 128U) == HHS_EXACT_STATUS_OK);
    for (i = 1U; i <= 40U; ++i) {
        uint8_t opening_phase = cache.current_phase_index;
        uint8_t orientation = (uint8_t)(i & 1U);
        int8_t direction = (i & 1U) ? 1 : -1;
        int16_t qnum = (int16_t)((int)i - 20);
        uint8_t operation64 = (uint8_t)((i * 7U) % 64U);
        uint64_t lineage = UINT64_C(0x2000) + (uint64_t)i;

        reset_event(&event, HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_OPEN,
                    (uint8_t)i, orientation, opening_phase, direction,
                    qnum, operation64, (uint8_t)((i % 5U) == 0U), lineage);
        reset_event_receipt(&receipt);
        CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
                  &cache, &event, &receipt) == HHS_EXACT_STATUS_OK);
        CHECK(receipt.accepted == 1U);

        reset_event(&event, HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_CLOSE,
                    (uint8_t)i, (uint8_t)(orientation ^ 1U),
                    reciprocal_phase(opening_phase), direction,
                    (int16_t)(-qnum), operation64,
                    (uint8_t)((i % 5U) == 0U), lineage);
        reset_event_receipt(&receipt);
        CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
                  &cache, &event, &receipt) == HHS_EXACT_STATUS_OK);
        CHECK(receipt.accepted == 1U);
    }

    reset_commit_receipt(&commit);
    CHECK(hhs_exact_pass219_lane5_phase_debt_commit_status(
              &cache, &commit) == HHS_EXACT_STATUS_OK);
    CHECK(commit.all_40_pairs_covered == 1U);
    CHECK(commit.zero_open_debt == 1U);
    CHECK(commit.nucleus_verified == 1U);
    CHECK(commit.topology_verified == 1U);
    CHECK(commit.phase_at_genesis == 1U);
    CHECK(commit.current_phase_index == 0U);
    CHECK(commit.lifted_phase_units == 0);
    CHECK(commit.commit_ready == 1U);
    CHECK(commit.open_event_count == 40U);
    CHECK(commit.close_event_count == 40U);
    CHECK(commit.candidate_only == 1U);
    CHECK(commit.canonical_mutation_authority == 0U);
    CHECK(strlen(commit.receipt_hash216) == 216U);

    puts("PASS219_LANE5_RECIPROCAL_PHASE_DEBT_CACHE_1_62_PASS");
    return 0;
}
