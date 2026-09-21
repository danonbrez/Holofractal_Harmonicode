#define _POSIX_C_SOURCE 200809L
#include "hhs_runtime_exact_abi_v1_1_base.h"
#include "native_bench_common_v2.h"

static uint64_t process_segment(
    const BenchDataset *ds,
    uint64_t offset_records,
    uint64_t count
) {
    uint64_t digest = BENCH_FNV_OFFSET;
    uint64_t i;
    for (i = 0U; i < count; ++i) {
        const uint8_t *record = ds->bytes + (size_t)(offset_records + i) * BENCH_RECORD_BYTES;
        HHSExactVM81Frame frame;
        uint8_t out[BENCH_RECORD_BYTES];
        size_t out_length = 0U;
        BENCH_REQUIRE(hhs_exact_vm81_frame_import_le(record, BENCH_RECORD_BYTES, &frame) == HHS_EXACT_STATUS_OK);
        BENCH_REQUIRE(hhs_exact_vm81_frame_export_le(&frame, out, sizeof(out), &out_length) == HHS_EXACT_STATUS_OK);
        BENCH_REQUIRE(out_length == BENCH_RECORD_BYTES);
        BENCH_REQUIRE(memcmp(record, out, BENCH_RECORD_BYTES) == 0);
        digest = bench_fnv1a_update(digest, out, BENCH_RECORD_BYTES);
    }
    return digest;
}

int main(int argc, char **argv) {
    BenchDataset ds;
    uint64_t offset_records;
    uint64_t count;
    uint64_t phase_slot;
    uint64_t inverse_phase_slot;
    uint64_t input_digest;
    uint64_t output_digest;
    uint64_t warmup;
    uint64_t started;
    uint64_t elapsed;
    volatile uint64_t warmup_sink = 0U;

    BENCH_REQUIRE(argc == 6);
    offset_records = bench_parse_u64(argv[2]);
    count = bench_parse_u64(argv[3]);
    phase_slot = bench_parse_u64(argv[4]);
    inverse_phase_slot = bench_parse_u64(argv[5]);
    BENCH_REQUIRE(phase_slot < 72U && inverse_phase_slot < 72U);

    ds = bench_load_dataset(argv[1]);
    BENCH_REQUIRE(offset_records <= ds.record_count);
    BENCH_REQUIRE(count > 0U && count <= ds.record_count - offset_records);
    BENCH_REQUIRE(hhs_exact_abi_validate() == HHS_EXACT_STATUS_OK);

    input_digest = bench_segment_input_digest(&ds, offset_records, count);
    warmup = bench_warmup_count(count);
    warmup_sink ^= process_segment(&ds, offset_records, warmup);

    started = bench_monotonic_ns();
    output_digest = process_segment(&ds, offset_records, count);
    elapsed = bench_monotonic_ns() - started;

    BENCH_REQUIRE(output_digest == input_digest);
    BENCH_REQUIRE(warmup_sink != UINT64_C(0xffffffffffffffff));

    printf(
        "{\"schema\":\"HHS_PASS219_ISOLATED_STACK_BENCHMARK_V2\","
        "\"arm\":\"B\",\"implementation\":\"exact_v1_1_base_abi_only\","
        "\"offset_records\":%" PRIu64 ",\"completed\":%" PRIu64 ","
        "\"elapsed_ns\":%" PRIu64 ",\"input_digest\":%" PRIu64 ","
        "\"payload_digest\":%" PRIu64 ",\"phase_slot_metadata\":%" PRIu64 ","
        "\"inverse_phase_slot_metadata\":%" PRIu64 ","
        "\"aggregate_abi_linked\":false,\"pass219_features_linked\":false,"
        "\"lane5_called\":false,\"h36_hash216_m_called\":false}\n",
        offset_records, count, elapsed, input_digest, output_digest,
        phase_slot, inverse_phase_slot);

    bench_free_dataset(&ds);
    return 0;
}
