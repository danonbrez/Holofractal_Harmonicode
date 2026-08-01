#include "hhs_pass188_bott_runtime.h"

#include <inttypes.h>
#include <stdio.h>
#include <string.h>

#define CHECK(condition, message) do { \
    if (!(condition)) { \
        fprintf(stderr, "FAIL: %s at line %d\n", (message), __LINE__); \
        return 1; \
    } \
} while (0)

int main(void) {
    static const uint8_t expected[8] = {1U, 0U, 0U, 0U, 0U, 0U, 7U, 6U};
    static const char *const tags[8] = {"x", "y", "z", "w", "xy", "yx", "zw", "wz"};
    uint32_t i;
    HHS188HydrationSummary summary;

    for (i = 0; i < 8U; ++i) {
        CHECK(hhs188_bott_step((uint8_t)i) == expected[i], "C transition table");
        CHECK(hhs188_bott_step_x86_64((uint8_t)i) == expected[i], "x86_64 transition table");
        CHECK(strcmp(hhs188_ordered_tag((uint8_t)i), tags[i]) == 0, "ordered tag preservation");
    }
    CHECK(hhs188_bott_step(0U) == 1U && hhs188_bott_step(1U) == 0U, "x/y period two");
    CHECK(hhs188_bott_step(6U) == 7U && hhs188_bott_step(7U) == 6U, "zw/wz period two");
    CHECK(hhs188_bott_step(2U) == 0U && hhs188_bott_step(3U) == 0U &&
          hhs188_bott_step(4U) == 0U && hhs188_bott_step(5U) == 0U,
          "asymmetric collapse");

    CHECK(hhs188_decode_projected(HHS188_HYDRATED_STATES, NULL) == HHS188_STATUS_NULL,
          "null rejection precedes range");
    {
        HHS188Coordinate coordinate;
        CHECK(hhs188_decode_projected(HHS188_HYDRATED_STATES, &coordinate) == HHS188_STATUS_RANGE,
              "range rejection");
    }

    for (i = 0; i < HHS188_HYDRATED_STATES; ++i) {
        HHS188Transition transition;
        CHECK(hhs188_transition_projected(i, &transition) == HHS188_STATUS_OK,
              "projected transition");
        CHECK(transition.input.g243 == transition.output.g243, "G243 preservation");
        CHECK(transition.input.vm81_cell == transition.output.vm81_cell, "VM81 preservation");
        CHECK(transition.input.operation_class8 == transition.output.operation_class8,
              "operation-class preservation");
        CHECK(hhs188_replay_transition(&transition) == HHS188_STATUS_OK, "deterministic replay");
    }

    CHECK(hhs188_hydrate(&summary) == HHS188_STATUS_OK, "full hydration");
    CHECK(summary.hydrated_states == HHS188_HYDRATED_STATES, "hydrated state count");
    CHECK(summary.active_period_two_states == UINT64_C(629856), "active count");
    CHECK(summary.asymmetric_collapse_states == UINT64_C(629856), "collapse count");
    CHECK(summary.gear_preserved_states == HHS188_HYDRATED_STATES, "gear count");
    CHECK(summary.coordinate_drift_states == 0U, "coordinate drift count");
    CHECK(summary.deterministic_checksum == HHS188_CHECKSUM_EXPECTED, "checksum continuity");

    printf("HHS_PASS_188_BOTT_RUNTIME_PASS states=%" PRIu64
           " active=%" PRIu64 " collapse=%" PRIu64
           " checksum=%016" PRIx64 "\n",
           summary.hydrated_states,
           summary.active_period_two_states,
           summary.asymmetric_collapse_states,
           summary.deterministic_checksum);
    return 0;
}
