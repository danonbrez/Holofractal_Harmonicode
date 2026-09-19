#define _POSIX_C_SOURCE 200809L
#include "saturation_common_v3.h"

static void *(* volatile sat_v3_memcpy_fn)(void *, const void *, size_t) = memcpy;
static int (* volatile sat_v3_memcmp_fn)(const void *, const void *, size_t) = memcmp;

static void run_loop(
    const SatV3Args *args,
    const SatV3Workset *workset,
    SatV3LoopResult *result
) {
    uint8_t out[SAT_V3_RECORD_BYTES];
    uint64_t local_index = 0U;
    uint64_t target_worker;
    uint64_t deadline_ns;
    uint64_t started_ns;
    uint64_t now;
    uint64_t digest = SAT_V3_FNV_OFFSET;

    target_worker = sat_v3_worker_target(
        args->target_total, args->worker_id, args->worker_count);
    sat_v3_wait_until(args->start_ns);
    started_ns = sat_v3_monotonic_ns();
    deadline_ns = args->start_ns + args->window_ns;
    SAT_V3_REQUIRE(deadline_ns >= args->start_ns);

    memset(result, 0, sizeof(*result));
    result->deadline_ns = deadline_ns;
    result->target_worker = target_worker;
    result->target_mode = args->target_total != 0U ? 1U : 0U;
    result->first_ordinal = (uint64_t)args->worker_id;

    for (;;) {
        uint64_t batch;
        for (batch = 0U; batch < SAT_V3_CHECK_BATCH; ++batch) {
            uint64_t ordinal;
            const uint8_t *record;
            if (result->target_mode && local_index >= target_worker)
                break;
            ordinal = sat_v3_ordinal(
                local_index, args->worker_id, args->worker_count);
            record = sat_v3_record(workset, ordinal);
            SAT_V3_REQUIRE(
                sat_v3_memcpy_fn(out, record, (size_t)SAT_V3_RECORD_BYTES) == out);
            SAT_V3_REQUIRE(
                sat_v3_memcmp_fn(out, record, (size_t)SAT_V3_RECORD_BYTES) == 0);
            digest = sat_v3_work_digest_step(digest, ordinal, out);
            result->last_ordinal = ordinal;
            ++local_index;
        }

        now = sat_v3_monotonic_ns();
        if (result->target_mode && local_index >= target_worker)
            break;
        if (now >= deadline_ns)
            break;
    }

    now = sat_v3_monotonic_ns();
    result->completed = local_index;
    result->elapsed_ns = now - started_ns;
    result->work_digest64 = digest;
    result->deadline_met =
        result->target_mode ? (uint8_t)(local_index >= target_worker) : 1U;
}

int main(int argc, char **argv) {
#if !defined(__linux__) || !defined(__x86_64__)
    fprintf(stderr, "plain x86 saturation v3 requires Linux x86_64\n");
    return 2;
#else
    SatV3Args args = sat_v3_parse_args(argc, argv);
    SatV3Workset workset = sat_v3_workset_init();
    SatV3LoopResult result;

    run_loop(&args, &workset, &result);
    sat_v3_print_common_json(
        "C",
        "plain_ubuntu_x86_64_copy_verify",
        &args,
        &workset,
        &result,
        "\"hhs_present\":false,\"raw_copy_verify\":true");
    sat_v3_workset_free(&workset);
    return 0;
#endif
}
