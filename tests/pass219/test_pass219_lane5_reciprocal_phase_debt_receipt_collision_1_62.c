#include "hhs_runtime_exact_abi.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static void make_event(
    HHSExactPass219Lane5PhaseDebtEventV1 *event,
    uint32_t kind,
    uint8_t class_id,
    uint8_t orientation,
    uint8_t phase,
    int8_t direction,
    int16_t qnum,
    uint8_t operation64,
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
    event->validated_computation_witness = 0U;
    event->lineage_token = lineage;
}

static void reset_receipt(
    HHSExactPass219Lane5PhaseDebtEventReceiptV1 *receipt
) {
    memset(receipt, 0, sizeof(*receipt));
    receipt->struct_size = (uint32_t)sizeof(*receipt);
}

static void reset_commit(
    HHSExactPass219Lane5PhaseDebtCommitReceiptV1 *receipt
) {
    memset(receipt, 0, sizeof(*receipt));
    receipt->struct_size = (uint32_t)sizeof(*receipt);
}

int main(void) {
    HHSExactPass219Lane5PhaseDebtCacheV1 cache_a;
    HHSExactPass219Lane5PhaseDebtCacheV1 cache_b;
    HHSExactPass219Lane5PhaseDebtFrameV1 frames_a[8];
    HHSExactPass219Lane5PhaseDebtFrameV1 frames_b[8];
    HHSExactPass219Lane5PhaseDebtEventV1 event;
    HHSExactPass219Lane5PhaseDebtEventReceiptV1 a;
    HHSExactPass219Lane5PhaseDebtEventReceiptV1 b;
    HHSExactPass219Lane5PhaseDebtCommitReceiptV1 commit_a;
    HHSExactPass219Lane5PhaseDebtCommitReceiptV1 commit_b;
    uint64_t saved_lineage;

    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_init(
              &cache_a, frames_a, 8U) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_init(
              &cache_b, frames_b, 8U) == HHS_EXACT_STATUS_OK);
    CHECK(strlen(cache_a.unresolved_stack_root_hash216) == 216U);
    CHECK(strcmp(
              cache_a.unresolved_stack_root_hash216,
              cache_b.unresolved_stack_root_hash216) == 0);

    /*
     * Construct two different unresolved parent histories with deliberately
     * identical aggregate counters, phase, depth, mask, and lifted phase.
     */
    make_event(&event,
               HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_OPEN,
               1U, 0U, 0U, 1, 9, 7U, UINT64_C(0xA001));
    reset_receipt(&a);
    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
              &cache_a, &event, &a) == HHS_EXACT_STATUS_OK);
    CHECK(a.accepted == 1U);

    make_event(&event,
               HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_OPEN,
               2U, 1U, 0U, 1, 9, 7U, UINT64_C(0xB002));
    reset_receipt(&b);
    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
              &cache_b, &event, &b) == HHS_EXACT_STATUS_OK);
    CHECK(b.accepted == 1U);

    CHECK(cache_a.depth == cache_b.depth);
    CHECK(cache_a.open_event_count == cache_b.open_event_count);
    CHECK(cache_a.close_event_count == cache_b.close_event_count);
    CHECK(cache_a.closed_pair_mask == cache_b.closed_pair_mask);
    CHECK(cache_a.lifted_phase_units == cache_b.lifted_phase_units);
    CHECK(cache_a.current_phase_index == cache_b.current_phase_index);
    CHECK(strcmp(
              cache_a.unresolved_stack_root_hash216,
              cache_b.unresolved_stack_root_hash216) != 0);

    /*
     * Apply the exact same child event to both caches. Before the repair these
     * receipts collided because only the child event plus aggregate fields
     * were hashed. They must now bind different parent and result stack roots.
     */
    make_event(&event,
               HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_OPEN,
               3U, 0U, 16U, -1, 18, 13U, UINT64_C(0xC003));
    reset_receipt(&a);
    reset_receipt(&b);
    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
              &cache_a, &event, &a) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
              &cache_b, &event, &b) == HHS_EXACT_STATUS_OK);
    CHECK(a.accepted == 1U && b.accepted == 1U);

    CHECK(a.kind == b.kind);
    CHECK(a.class_id == b.class_id);
    CHECK(a.orientation == b.orientation);
    CHECK(a.phase_index == b.phase_index);
    CHECK(a.clock_direction == b.clock_direction);
    CHECK(a.quantized_ninth_numerator == b.quantized_ninth_numerator);
    CHECK(a.operation64 == b.operation64);
    CHECK(a.lineage_token == b.lineage_token);
    CHECK(a.depth_before == b.depth_before);
    CHECK(a.depth_after == b.depth_after);
    CHECK(a.closed_pair_mask == b.closed_pair_mask);
    CHECK(a.lifted_phase_units == b.lifted_phase_units);
    CHECK(a.current_phase_index == b.current_phase_index);

    CHECK(strlen(a.parent_stack_root_hash216) == 216U);
    CHECK(strlen(a.unresolved_stack_root_hash216) == 216U);
    CHECK(strcmp(
              a.parent_stack_root_hash216,
              b.parent_stack_root_hash216) != 0);
    CHECK(strcmp(
              a.unresolved_stack_root_hash216,
              b.unresolved_stack_root_hash216) != 0);
    CHECK(strcmp(a.receipt_hash216, b.receipt_hash216) != 0);

    /*
     * The same rejected event under the two different unresolved stacks also
     * must not collide.
     */
    make_event(&event,
               HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_CLOSE,
               4U, 1U, 36U, -1, -18, 13U, UINT64_C(0xC003));
    reset_receipt(&a);
    reset_receipt(&b);
    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
              &cache_a, &event, &a) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
              &cache_b, &event, &b) == HHS_EXACT_STATUS_OK);
    CHECK(a.accepted == 0U && b.accepted == 0U);
    CHECK(a.reason ==
          HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_STACK_CLASS_MISMATCH);
    CHECK(b.reason == a.reason);
    CHECK(a.depth_after == b.depth_after);
    CHECK(a.closed_pair_mask == b.closed_pair_mask);
    CHECK(a.lifted_phase_units == b.lifted_phase_units);
    CHECK(strcmp(a.receipt_hash216, b.receipt_hash216) != 0);

    /*
     * Commit/status receipts bind the current unresolved stack as well.
     */
    reset_commit(&commit_a);
    reset_commit(&commit_b);
    CHECK(hhs_exact_pass219_lane5_phase_debt_commit_status(
              &cache_a, &commit_a) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_lane5_phase_debt_commit_status(
              &cache_b, &commit_b) == HHS_EXACT_STATUS_OK);
    CHECK(commit_a.depth == commit_b.depth);
    CHECK(commit_a.closed_pair_mask == commit_b.closed_pair_mask);
    CHECK(commit_a.lifted_phase_units == commit_b.lifted_phase_units);
    CHECK(strcmp(
              commit_a.unresolved_stack_root_hash216,
              commit_b.unresolved_stack_root_hash216) != 0);
    CHECK(strcmp(commit_a.receipt_hash216, commit_b.receipt_hash216) != 0);

    /*
     * Direct caller mutation of an unresolved frame is detected because the
     * stored root is recomputed before the next receipt/status operation.
     */
    saved_lineage = frames_a[0].lineage_token;
    frames_a[0].lineage_token ^= UINT64_C(1);
    reset_commit(&commit_a);
    CHECK(hhs_exact_pass219_lane5_phase_debt_commit_status(
              &cache_a, &commit_a) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    frames_a[0].lineage_token = saved_lineage;
    reset_commit(&commit_a);
    CHECK(hhs_exact_pass219_lane5_phase_debt_commit_status(
              &cache_a, &commit_a) == HHS_EXACT_STATUS_OK);

    puts("PASS219_LANE5_RECIPROCAL_PHASE_DEBT_RECEIPT_COLLISION_1_62_PASS");
    return 0;
}
