#include "hhs_pass219_lane5_t5184_phase_support_1_49.h"

#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static void fail(const char *message) {
    fprintf(stderr, "FAIL: %s\n", message);
    exit(1);
}

static void expected_slot(
    uint32_t local64,
    uint8_t *phase_bearing,
    uint8_t *phase_code,
    int8_t *phase_sign,
    uint8_t *representative,
    uint32_t *ordinal
) {
    *phase_bearing = 0U;
    *phase_code = HHS_EXACT_PASS219_LANE5_T5184_PHASE_NONE;
    *phase_sign = 0;
    *representative = HHS_EXACT_PASS219_LANE5_T5184_PHASE_NONE;
    *ordinal = UINT32_MAX;

    if (local64 >= 4U && local64 <= 7U) {
        *phase_bearing = 1U;
        *phase_code = HHS_EXACT_PASS219_LANE5_T5184_PHASE_XY;
        *phase_sign = 1;
        *representative = HHS_EXACT_PASS219_LANE5_T5184_PHASE_XY;
        *ordinal = local64 - 4U;
    } else if (local64 >= 16U && local64 <= 19U) {
        *phase_bearing = 1U;
        *phase_code = HHS_EXACT_PASS219_LANE5_T5184_PHASE_YX;
        *phase_sign = -1;
        *representative = HHS_EXACT_PASS219_LANE5_T5184_PHASE_YX;
        *ordinal = 4U + local64 - 16U;
    } else if (local64 >= 44U && local64 <= 47U) {
        *phase_bearing = 1U;
        *phase_code = HHS_EXACT_PASS219_LANE5_T5184_PHASE_ZW;
        *phase_sign = 1;
        *representative = HHS_EXACT_PASS219_LANE5_T5184_PHASE_XY;
        *ordinal = 8U + local64 - 44U;
    } else if (local64 >= 56U && local64 <= 59U) {
        *phase_bearing = 1U;
        *phase_code = HHS_EXACT_PASS219_LANE5_T5184_PHASE_WZ;
        *phase_sign = -1;
        *representative = HHS_EXACT_PASS219_LANE5_T5184_PHASE_YX;
        *ordinal = 12U + local64 - 56U;
    }
}

int main(void) {
    uint64_t total_checks = 0U;
    uint64_t phase_bearing_checks = 0U;
    uint64_t non_phase_checks = 0U;
    int64_t P;

    for (P = -36; P <= 36; ++P) {
        int64_t p;
        int64_t q;
        uint32_t vm81;

        if (P == 0)
            continue;

        p = P - 1;
        q = P + 1;

        if (p + q != 2 * P)
            fail("p+q != 2P");
        if (q - p != 2)
            fail("q-p != 2");
        if (p * q != P * P - 1)
            fail("pq != P^2-1");
        if ((q - p) * P != p + q)
            fail("current bridge correction is not exactly 1");
        if (P * P != p * q + 1)
            fail("P^2 != pq+1");

        for (vm81 = 0U; vm81 < 81U; ++vm81) {
            uint32_t local64;

            for (local64 = 0U; local64 < 64U; ++local64) {
                HHSExactPass219Lane5T5184PhaseSlotV1 slot;
                HHSExactStatus status;
                uint8_t expected_bearing;
                uint8_t expected_code;
                int8_t expected_sign;
                uint8_t expected_rep;
                uint32_t expected_ordinal;

                expected_slot(
                    local64,
                    &expected_bearing,
                    &expected_code,
                    &expected_sign,
                    &expected_rep,
                    &expected_ordinal
                );

                status = hhs_exact_pass219_lane5_t5184_phase_support_classify(
                    vm81,
                    local64,
                    &slot
                );
                if (status != HHS_EXACT_STATUS_OK)
                    fail("phase classifier rejected legal slot");

                if (slot.vm81_cell != vm81 ||
                    slot.local64 != local64 ||
                    slot.global5184 != vm81 * 64U + local64)
                    fail("slot address mismatch");

                if (slot.phase_bearing != expected_bearing ||
                    slot.requires_phase_specific_check != expected_bearing ||
                    slot.phase_code != expected_code ||
                    slot.phase_sign != expected_sign ||
                    slot.representative_phase_code != expected_rep ||
                    slot.support_ordinal != expected_ordinal)
                    fail("exact ordered phase classification mismatch");

                if (slot.full_state_identity_required != 1U ||
                    slot.candidate_only != 1U)
                    fail("authority boundary mismatch");

                ++total_checks;
                if (expected_bearing != 0U)
                    ++phase_bearing_checks;
                else
                    ++non_phase_checks;
            }
        }
    }

    if (total_checks != UINT64_C(373248))
        fail("unexpected combined state-slot count");
    if (phase_bearing_checks != UINT64_C(93312))
        fail("unexpected phase-bearing count");
    if (non_phase_checks != UINT64_C(279936))
        fail("unexpected non-phase count");

    printf(
        "{\"schema\":\"HHS_PASS219_RATIONAL_P_MANIFOLD_LANE5_NATIVE_1_50\","
        "\"result\":\"PASS\","
        "\"P_count\":72,"
        "\"state_slot_checks\":%llu,"
        "\"phase_bearing_checks\":%llu,"
        "\"non_phase_checks\":%llu,"
        "\"bridge_correction\":\"1\","
        "\"candidate_only\":true}\n",
        (unsigned long long)total_checks,
        (unsigned long long)phase_bearing_checks,
        (unsigned long long)non_phase_checks
    );
    puts("PASS219_RATIONAL_P_MANIFOLD_LANE5_1_50_PASS");
    return 0;
}
