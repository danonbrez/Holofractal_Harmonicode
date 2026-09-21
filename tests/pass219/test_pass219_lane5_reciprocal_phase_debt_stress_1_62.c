#include "hhs_runtime_exact_abi.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define EPOCHS 100U
#define PAIRS 40U
#define DEEP 128U
#define FRAME_CAPACITY 256U

#define CHECK(expr) do {     if (!(expr)) {         fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr);         return 1;     } } while (0)

typedef struct OpenRecord {
    uint8_t class_id;
    uint8_t orientation;
    uint8_t phase;
    int8_t direction;
    int16_t qnum;
    uint8_t operation64;
    uint8_t witness;
    uint64_t lineage;
} OpenRecord;

static void make_event(
    HHSExactPass219Lane5PhaseDebtEventV1 *event,
    uint32_t kind,
    const OpenRecord *record,
    int reciprocal
) {
    memset(event, 0, sizeof(*event));
    event->struct_size = (uint32_t)sizeof(*event);
    event->version = HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VERSION;
    event->kind = kind;
    event->class_id = record->class_id;
    event->orientation = reciprocal
        ? (uint8_t)(record->orientation ^ 1U)
        : record->orientation;
    event->phase_index = reciprocal
        ? (uint8_t)(((uint32_t)record->phase + 36U) % 72U)
        : record->phase;
    event->clock_direction = record->direction;
    event->quantized_ninth_numerator = reciprocal
        ? (int16_t)(-record->qnum)
        : record->qnum;
    event->operation64 = record->operation64;
    event->validated_computation_witness = record->witness;
    event->lineage_token = record->lineage;
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
    HHSExactPass219Lane5PhaseDebtCacheV1 cache;
    HHSExactPass219Lane5PhaseDebtFrameV1 frames[FRAME_CAPACITY];
    HHSExactPass219Lane5PhaseDebtEventV1 event;
    HHSExactPass219Lane5PhaseDebtEventReceiptV1 receipt;
    HHSExactPass219Lane5PhaseDebtCommitReceiptV1 commit;
    OpenRecord records[PAIRS];
    OpenRecord deep[DEEP];
    uint32_t epoch;
    uint32_t i;
    uint64_t accepted = 0U;
    uint64_t rejected = 0U;
    size_t max_depth = 0U;

    CHECK(hhs_exact_pass219_lane5_phase_debt_cache_init(
              &cache, frames, FRAME_CAPACITY) == HHS_EXACT_STATUS_OK);

    for (epoch = 0U; epoch < EPOCHS; ++epoch) {
        for (i = 0U; i < PAIRS; ++i) {
            OpenRecord *r = &records[i];
            uint32_t class_number = i + 1U;
            r->class_id = (uint8_t)class_number;
            r->orientation = (uint8_t)((class_number + epoch) & 1U);
            r->phase = cache.current_phase_index;
            r->direction = ((class_number + epoch) & 1U) ? 1 : -1;
            r->qnum = (int16_t)(((int)((class_number * 17U + epoch) % 163U)) - 81);
            r->operation64 = (uint8_t)((class_number * 11U + epoch) % 64U);
            r->witness = (uint8_t)((class_number % 7U) == 0U);
            r->lineage = UINT64_C(0x10000000) +
                (uint64_t)epoch * UINT64_C(0x100) + (uint64_t)class_number;

            make_event(&event,
                       HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_OPEN,
                       r, 0);
            reset_receipt(&receipt);
            CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
                      &cache, &event, &receipt) == HHS_EXACT_STATUS_OK);
            CHECK(receipt.accepted == 1U);
            ++accepted;
            if (cache.depth > max_depth)
                max_depth = cache.depth;
        }

        CHECK(cache.depth == PAIRS);

        /* Wrong class cannot discharge the current top debt. */
        make_event(&event,
                   HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_CLOSE,
                   &records[PAIRS - 2U], 1);
        reset_receipt(&receipt);
        CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
                  &cache, &event, &receipt) == HHS_EXACT_STATUS_OK);
        CHECK(receipt.accepted == 0U);
        CHECK(receipt.reason ==
              HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_STACK_CLASS_MISMATCH);
        CHECK(cache.depth == PAIRS);
        ++rejected;

        /* Right class with wrong reciprocal quantization also cannot close. */
        make_event(&event,
                   HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_CLOSE,
                   &records[PAIRS - 1U], 1);
        event.quantized_ninth_numerator =
            (int16_t)(event.quantized_ninth_numerator == 81
                ? 80 : event.quantized_ninth_numerator + 1);
        reset_receipt(&receipt);
        CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
                  &cache, &event, &receipt) == HHS_EXACT_STATUS_OK);
        CHECK(receipt.accepted == 0U);
        CHECK(receipt.reason ==
              HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_QUANTIZATION_RECIPROCAL_MISMATCH);
        CHECK(cache.depth == PAIRS);
        ++rejected;

        for (i = PAIRS; i > 0U; --i) {
            make_event(&event,
                       HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_CLOSE,
                       &records[i - 1U], 1);
            reset_receipt(&receipt);
            CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
                      &cache, &event, &receipt) == HHS_EXACT_STATUS_OK);
            CHECK(receipt.accepted == 1U);
            ++accepted;
        }

        CHECK(cache.depth == 0U);
        CHECK(cache.current_phase_index == 0U);
        CHECK(cache.lifted_phase_units == 0);
    }

    reset_commit(&commit);
    CHECK(hhs_exact_pass219_lane5_phase_debt_commit_status(
              &cache, &commit) == HHS_EXACT_STATUS_OK);
    CHECK(commit.commit_ready == 1U);
    CHECK(commit.all_40_pairs_covered == 1U);
    CHECK(commit.zero_open_debt == 1U);
    CHECK(commit.phase_at_genesis == 1U);

    /*
     * Caller workspace, rather than the library, bounds recursion. Prove a
     * depth well beyond the 40 reciprocal classes by nesting one class 128
     * times with distinct lineage and operation identities.
     */
    for (i = 0U; i < DEEP; ++i) {
        OpenRecord *r = &deep[i];
        r->class_id = 7U;
        r->orientation = (uint8_t)(i & 1U);
        r->phase = cache.current_phase_index;
        r->direction = (i & 1U) ? 1 : -1;
        r->qnum = (int16_t)(((int)((i * 29U) % 163U)) - 81);
        r->operation64 = (uint8_t)(i % 64U);
        r->witness = (uint8_t)((i % 11U) == 0U);
        r->lineage = UINT64_C(0x80000000) + (uint64_t)i + 1U;

        make_event(&event,
                   HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_OPEN,
                   r, 0);
        reset_receipt(&receipt);
        CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
                  &cache, &event, &receipt) == HHS_EXACT_STATUS_OK);
        CHECK(receipt.accepted == 1U);
        ++accepted;
        if (cache.depth > max_depth)
            max_depth = cache.depth;
    }
    CHECK(cache.depth == DEEP);
    CHECK(cache.current_phase_index == 0U);
    CHECK(cache.lifted_phase_units == 0);

    for (i = DEEP; i > 0U; --i) {
        make_event(&event,
                   HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_CLOSE,
                   &deep[i - 1U], 1);
        reset_receipt(&receipt);
        CHECK(hhs_exact_pass219_lane5_phase_debt_cache_apply(
                  &cache, &event, &receipt) == HHS_EXACT_STATUS_OK);
        CHECK(receipt.accepted == 1U);
        ++accepted;
    }

    reset_commit(&commit);
    CHECK(hhs_exact_pass219_lane5_phase_debt_commit_status(
              &cache, &commit) == HHS_EXACT_STATUS_OK);
    CHECK(commit.commit_ready == 1U);
    CHECK(commit.zero_open_debt == 1U);
    CHECK(commit.phase_at_genesis == 1U);
    CHECK(max_depth == DEEP);
    CHECK(accepted == UINT64_C(8256));
    CHECK(rejected == UINT64_C(200));
    CHECK(cache.rejected_event_count == rejected);
    CHECK(cache.open_event_count == UINT64_C(4128));
    CHECK(cache.close_event_count == UINT64_C(4128));
    CHECK(cache.validated_witness_replay_count > 0U);

    printf(
        "PASS219_LANE5_RECIPROCAL_PHASE_DEBT_STRESS_1_62_PASS "
        "accepted=%llu rejected=%llu epochs=%u max_depth=%zu witness_replays=%llu\n",
        (unsigned long long)accepted,
        (unsigned long long)rejected,
        (unsigned)EPOCHS,
        max_depth,
        (unsigned long long)cache.validated_witness_replay_count
    );
    return 0;
}
