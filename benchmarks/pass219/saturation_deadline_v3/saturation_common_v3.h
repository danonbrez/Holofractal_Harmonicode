#ifndef HHS_PASS219_SATURATION_COMMON_V3_H
#define HHS_PASS219_SATURATION_COMMON_V3_H

#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define SAT_V3_SCHEMA "HHS_PASS219_SATURATION_DEADLINE_V3"
#define SAT_V3_RECORD_BYTES UINT64_C(648)
#define SAT_V3_WORKSET_RECORDS UINT64_C(65536)
#define SAT_V3_SEMANTIC_SLOTS UINT32_C(4)
#define SAT_V3_CHECK_BATCH UINT64_C(64)
#define SAT_V3_FNV_OFFSET UINT64_C(1469598103934665603)
#define SAT_V3_FNV_PRIME UINT64_C(1099511628211)
#define SAT_V3_SEED UINT64_C(0x2195184722160036)

#define SAT_V3_REQUIRE(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "SAT_V3_REQUIRE failed at %s:%d: %s\n", \
                __FILE__, __LINE__, #expr); \
        exit(EXIT_FAILURE); \
    } \
} while (0)

typedef struct SatV3Workset {
    uint8_t *bytes;
    uint64_t byte_count;
    uint64_t digest64;
} SatV3Workset;

typedef struct SatV3Args {
    uint64_t window_ns;
    uint64_t start_ns;
    uint32_t worker_id;
    uint32_t worker_count;
    uint64_t target_total;
} SatV3Args;

typedef struct SatV3LoopResult {
    uint64_t completed;
    uint64_t elapsed_ns;
    uint64_t deadline_ns;
    uint64_t target_worker;
    uint64_t first_ordinal;
    uint64_t last_ordinal;
    uint64_t work_digest64;
    uint8_t target_mode;
    uint8_t deadline_met;
} SatV3LoopResult;

static uint64_t sat_v3_monotonic_ns(void) {
    struct timespec ts;
    SAT_V3_REQUIRE(clock_gettime(CLOCK_MONOTONIC, &ts) == 0);
    return (uint64_t)ts.tv_sec * UINT64_C(1000000000) +
           (uint64_t)ts.tv_nsec;
}

static uint64_t sat_v3_mix64(uint64_t x) {
    x += UINT64_C(0x9e3779b97f4a7c15);
    x = (x ^ (x >> 30U)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27U)) * UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31U);
}

static uint64_t sat_v3_fold64(uint64_t state, uint64_t value) {
    return sat_v3_mix64(state ^ sat_v3_mix64(value));
}

static uint64_t sat_v3_fnv_update(
    uint64_t state,
    const uint8_t *bytes,
    size_t length
) {
    size_t i;
    for (i = 0U; i < length; ++i) {
        state ^= (uint64_t)bytes[i];
        state *= SAT_V3_FNV_PRIME;
    }
    return state;
}

static void sat_v3_fill_record(uint64_t record_index, uint8_t *out) {
    uint64_t x = sat_v3_mix64(SAT_V3_SEED ^ record_index);
    uint64_t offset;
    for (offset = 0U; offset < SAT_V3_RECORD_BYTES; offset += UINT64_C(8)) {
        uint64_t value;
        uint32_t j;
        x = sat_v3_mix64(x ^ record_index ^ offset);
        value = x;
        for (j = 0U; j < 8U && offset + (uint64_t)j < SAT_V3_RECORD_BYTES; ++j) {
            out[offset + (uint64_t)j] = (uint8_t)(value & UINT64_C(0xff));
            value >>= 8U;
        }
    }
}

static SatV3Workset sat_v3_workset_init(void) {
    SatV3Workset workset;
    uint64_t i;
    const uint64_t byte_count = SAT_V3_RECORD_BYTES * SAT_V3_WORKSET_RECORDS;
    SAT_V3_REQUIRE(byte_count <= (uint64_t)SIZE_MAX);
    workset.bytes = (uint8_t *)malloc((size_t)byte_count);
    SAT_V3_REQUIRE(workset.bytes != NULL);
    workset.byte_count = byte_count;
    workset.digest64 = SAT_V3_FNV_OFFSET;
    for (i = 0U; i < SAT_V3_WORKSET_RECORDS; ++i) {
        uint8_t *record =
            workset.bytes + (size_t)(i * SAT_V3_RECORD_BYTES);
        sat_v3_fill_record(i, record);
        workset.digest64 = sat_v3_fnv_update(
            workset.digest64, record, (size_t)SAT_V3_RECORD_BYTES);
    }
    SAT_V3_REQUIRE(workset.digest64 != 0U);
    return workset;
}

static void sat_v3_workset_free(SatV3Workset *workset) {
    if (workset == NULL)
        return;
    free(workset->bytes);
    workset->bytes = NULL;
    workset->byte_count = 0U;
    workset->digest64 = 0U;
}

static const uint8_t *sat_v3_record(
    const SatV3Workset *workset,
    uint64_t ordinal
) {
    uint64_t index;
    SAT_V3_REQUIRE(workset != NULL && workset->bytes != NULL);
    index = ordinal % SAT_V3_WORKSET_RECORDS;
    return workset->bytes + (size_t)(index * SAT_V3_RECORD_BYTES);
}

static uint64_t sat_v3_parse_u64(const char *s) {
    char *end = NULL;
    unsigned long long value;
    errno = 0;
    SAT_V3_REQUIRE(s != NULL && *s != '\0');
    value = strtoull(s, &end, 10);
    SAT_V3_REQUIRE(errno == 0 && end != s && *end == '\0');
    return (uint64_t)value;
}

static SatV3Args sat_v3_parse_args(int argc, char **argv) {
    SatV3Args args;
    uint64_t worker_id;
    uint64_t worker_count;
    SAT_V3_REQUIRE(argc == 6);
    args.window_ns = sat_v3_parse_u64(argv[1]);
    args.start_ns = sat_v3_parse_u64(argv[2]);
    worker_id = sat_v3_parse_u64(argv[3]);
    worker_count = sat_v3_parse_u64(argv[4]);
    args.target_total = sat_v3_parse_u64(argv[5]);
    SAT_V3_REQUIRE(args.window_ns >= UINT64_C(1000000));
    SAT_V3_REQUIRE(worker_count > 0U && worker_count <= UINT32_MAX);
    SAT_V3_REQUIRE(worker_id < worker_count && worker_id <= UINT32_MAX);
    args.worker_id = (uint32_t)worker_id;
    args.worker_count = (uint32_t)worker_count;
    return args;
}

static uint64_t sat_v3_worker_target(
    uint64_t target_total,
    uint32_t worker_id,
    uint32_t worker_count
) {
    if (target_total == 0U || (uint64_t)worker_id >= target_total)
        return 0U;
    return UINT64_C(1) +
           (target_total - UINT64_C(1) - (uint64_t)worker_id) /
               (uint64_t)worker_count;
}

static uint64_t sat_v3_ordinal(
    uint64_t local_index,
    uint32_t worker_id,
    uint32_t worker_count
) {
    SAT_V3_REQUIRE(
        local_index <=
        (UINT64_MAX - (uint64_t)worker_id) / (uint64_t)worker_count);
    return local_index * (uint64_t)worker_count + (uint64_t)worker_id;
}

static void sat_v3_wait_until(uint64_t start_ns) {
    for (;;) {
        uint64_t now = sat_v3_monotonic_ns();
        if (now >= start_ns)
            return;
        if (start_ns - now > UINT64_C(2000000)) {
            struct timespec req;
            uint64_t wait_ns = start_ns - now - UINT64_C(1000000);
            req.tv_sec = (time_t)(wait_ns / UINT64_C(1000000000));
            req.tv_nsec = (long)(wait_ns % UINT64_C(1000000000));
            (void)nanosleep(&req, NULL);
        }
    }
}

static uint64_t sat_v3_work_digest_step(
    uint64_t state,
    uint64_t ordinal,
    const uint8_t record[SAT_V3_RECORD_BYTES]
) {
    uint64_t first = 0U;
    uint64_t last = 0U;
    memcpy(&first, record, sizeof(first));
    memcpy(&last, record + SAT_V3_RECORD_BYTES - sizeof(last), sizeof(last));
    state = sat_v3_fold64(state, ordinal);
    state = sat_v3_fold64(state, first);
    return sat_v3_fold64(state, last);
}

static void sat_v3_print_common_json(
    const char *arm,
    const char *implementation,
    const SatV3Args *args,
    const SatV3Workset *workset,
    const SatV3LoopResult *result,
    const char *extra_json
) {
    SAT_V3_REQUIRE(arm != NULL && implementation != NULL && args != NULL &&
                   workset != NULL && result != NULL && extra_json != NULL);
    printf(
        "{\"schema\":\"%s\",\"arm\":\"%s\","
        "\"implementation\":\"%s\",\"worker_id\":%u,"
        "\"worker_count\":%u,\"window_ns\":%" PRIu64 ","
        "\"start_ns\":%" PRIu64 ",\"deadline_ns\":%" PRIu64 ","
        "\"target_total\":%" PRIu64 ",\"target_worker\":%" PRIu64 ","
        "\"completed\":%" PRIu64 ",\"elapsed_ns\":%" PRIu64 ","
        "\"first_ordinal\":%" PRIu64 ",\"last_ordinal\":%" PRIu64 ","
        "\"workset_records\":%" PRIu64 ",\"record_bytes\":%" PRIu64 ","
        "\"workset_bytes\":%" PRIu64 ",\"workset_digest64\":%" PRIu64 ","
        "\"work_digest64\":%" PRIu64 ",\"target_mode\":%s,"
        "\"deadline_met\":%s,%s}\n",
        SAT_V3_SCHEMA,
        arm,
        implementation,
        args->worker_id,
        args->worker_count,
        args->window_ns,
        args->start_ns,
        result->deadline_ns,
        args->target_total,
        result->target_worker,
        result->completed,
        result->elapsed_ns,
        result->first_ordinal,
        result->last_ordinal,
        SAT_V3_WORKSET_RECORDS,
        SAT_V3_RECORD_BYTES,
        workset->byte_count,
        workset->digest64,
        result->work_digest64,
        result->target_mode ? "true" : "false",
        result->deadline_met ? "true" : "false",
        extra_json);
}

#endif
