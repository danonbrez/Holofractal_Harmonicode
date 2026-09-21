#ifndef HHS_PASS219_ISOLATED_STACK_NATIVE_BENCH_COMMON_V2_H
#define HHS_PASS219_ISOLATED_STACK_NATIVE_BENCH_COMMON_V2_H

#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define BENCH_RECORD_BYTES 648U
#define BENCH_FNV_OFFSET UINT64_C(1469598103934665603)
#define BENCH_FNV_PRIME UINT64_C(1099511628211)

#define BENCH_REQUIRE(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "BENCH_REQUIRE failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        exit(EXIT_FAILURE); \
    } \
} while (0)

typedef struct BenchDataset {
    uint8_t *bytes;
    size_t byte_count;
    uint64_t record_count;
} BenchDataset;

static uint64_t bench_monotonic_ns(void) {
    struct timespec ts;
    BENCH_REQUIRE(clock_gettime(CLOCK_MONOTONIC, &ts) == 0);
    return (uint64_t)ts.tv_sec * UINT64_C(1000000000) + (uint64_t)ts.tv_nsec;
}

static uint64_t bench_parse_u64(const char *s) {
    char *end = NULL;
    unsigned long long value;
    BENCH_REQUIRE(s != NULL && *s != '\0');
    errno = 0;
    value = strtoull(s, &end, 10);
    BENCH_REQUIRE(errno == 0 && end != s && *end == '\0');
    return (uint64_t)value;
}

static BenchDataset bench_load_dataset(const char *path) {
    BenchDataset ds;
    FILE *f;
    long length;
    size_t got;
    memset(&ds, 0, sizeof(ds));
    f = fopen(path, "rb");
    BENCH_REQUIRE(f != NULL);
    BENCH_REQUIRE(fseek(f, 0, SEEK_END) == 0);
    length = ftell(f);
    BENCH_REQUIRE(length > 0);
    BENCH_REQUIRE(fseek(f, 0, SEEK_SET) == 0);
    BENCH_REQUIRE(((size_t)length % BENCH_RECORD_BYTES) == 0U);
    ds.byte_count = (size_t)length;
    ds.record_count = (uint64_t)(ds.byte_count / BENCH_RECORD_BYTES);
    ds.bytes = (uint8_t *)malloc(ds.byte_count);
    BENCH_REQUIRE(ds.bytes != NULL);
    got = fread(ds.bytes, 1U, ds.byte_count, f);
    BENCH_REQUIRE(got == ds.byte_count);
    BENCH_REQUIRE(fclose(f) == 0);
    return ds;
}

static void bench_free_dataset(BenchDataset *ds) {
    if (ds != NULL) {
        free(ds->bytes);
        ds->bytes = NULL;
        ds->byte_count = 0U;
        ds->record_count = 0U;
    }
}

static uint64_t bench_fnv1a_update(uint64_t state, const uint8_t *bytes, size_t length) {
    size_t i;
    BENCH_REQUIRE(bytes != NULL || length == 0U);
    for (i = 0U; i < length; ++i) {
        state ^= (uint64_t)bytes[i];
        state *= BENCH_FNV_PRIME;
    }
    return state;
}

static uint64_t bench_segment_input_digest(
    const BenchDataset *ds,
    uint64_t offset_records,
    uint64_t count
) {
    uint64_t i;
    uint64_t digest = BENCH_FNV_OFFSET;
    BENCH_REQUIRE(ds != NULL && ds->bytes != NULL);
    BENCH_REQUIRE(offset_records <= ds->record_count);
    BENCH_REQUIRE(count <= ds->record_count - offset_records);
    for (i = 0U; i < count; ++i) {
        const uint8_t *record = ds->bytes + (size_t)(offset_records + i) * BENCH_RECORD_BYTES;
        digest = bench_fnv1a_update(digest, record, BENCH_RECORD_BYTES);
    }
    return digest;
}

static uint64_t bench_warmup_count(uint64_t count) {
    return count < UINT64_C(64) ? count : UINT64_C(64);
}

#endif
