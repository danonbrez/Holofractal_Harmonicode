#define _POSIX_C_SOURCE 200809L
#include "hhs_runtime_exact_abi.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static uint64_t elapsed_ns(const struct timespec *start, const struct timespec *end) {
    uint64_t seconds = (uint64_t)(end->tv_sec - start->tv_sec);
    int64_t nanos = (int64_t)end->tv_nsec - (int64_t)start->tv_nsec;
    if (nanos < 0) {
        seconds -= UINT64_C(1);
        nanos += INT64_C(1000000000);
    }
    return seconds * UINT64_C(1000000000) + (uint64_t)nanos;
}

int main(void) {
    const uint64_t items = UINT64_C(1000000);
    const uint64_t historical_span = UINT64_C(256000000);
    const uint64_t route_bytes = (uint64_t)sizeof(HHSExactPass219Lane5UnboundedWorkloadRouteV1);
    const uint64_t stream_bytes = (uint64_t)sizeof(HHSExactPass219Lane5UnboundedWorkloadStreamV1);
    const uint64_t address_bytes = HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES;
    const uint64_t minimal_id_bytes = UINT64_C(8);
    uint64_t *states;
    volatile uint64_t checksum = 0U;
    struct timespec start;
    struct timespec end;
    uint64_t fill_ns;
    uint64_t scan_ns;
    uint64_t i;

    states = (uint64_t *)malloc((size_t)(items * minimal_id_bytes));
    if (states == NULL) {
        fputs("allocation failed\n", stderr);
        return 2;
    }

    if (clock_gettime(CLOCK_MONOTONIC, &start) != 0) return 3;
    for (i = 0U; i < items; ++i)
        states[i] = i;
    if (clock_gettime(CLOCK_MONOTONIC, &end) != 0) return 4;
    fill_ns = elapsed_ns(&start, &end);

    if (clock_gettime(CLOCK_MONOTONIC, &start) != 0) return 5;
    for (i = 0U; i < items; ++i)
        checksum ^= states[i] + (i << 1U);
    if (clock_gettime(CLOCK_MONOTONIC, &end) != 0) return 6;
    scan_ns = elapsed_ns(&start, &end);

    printf(
        "{\"result\":\"PASS\","
        "\"items\":%" PRIu64 ","
        "\"route_struct_bytes\":%" PRIu64 ","
        "\"stream_state_bytes\":%" PRIu64 ","
        "\"fixed_batch_route_bytes_1m\":%" PRIu64 ","
        "\"minimal_id_materialization_bytes_1m\":%" PRIu64 ","
        "\"full_coordinate_materialization_bytes_1m\":%" PRIu64 ","
        "\"minimal_id_materialization_bytes_256m\":%" PRIu64 ","
        "\"full_coordinate_materialization_bytes_256m\":%" PRIu64 ","
        "\"route_batch_to_stream_memory_ratio\":%" PRIu64 ","
        "\"coordinate_materialization_to_stream_ratio_1m\":%" PRIu64 ","
        "\"minimal_id_fill_ns_1m\":%" PRIu64 ","
        "\"minimal_id_scan_ns_1m\":%" PRIu64 ","
        "\"checksum\":%" PRIu64 "}\n",
        items,
        route_bytes,
        stream_bytes,
        items * route_bytes,
        items * minimal_id_bytes,
        items * address_bytes,
        historical_span * minimal_id_bytes,
        historical_span * address_bytes,
        stream_bytes == 0U ? 0U : (items * route_bytes) / stream_bytes,
        stream_bytes == 0U ? 0U : (items * address_bytes) / stream_bytes,
        fill_ns,
        scan_ns,
        (uint64_t)checksum
    );

    free(states);
    return 0;
}
