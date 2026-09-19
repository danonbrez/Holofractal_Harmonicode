#define _POSIX_C_SOURCE 200809L
#include "hhs_runtime_exact_abi_v1_1_base.h"
#include "saturation_common_v3.h"

static void run_loop(
    const SatV3Args *args,
    const SatV3Workset *workset,
    SatV3LoopResult *result
) {
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
            HHSExactVM81Frame frame;
            uint8_t out[SAT_V3_RECORD_BYTES];
            size_t out_length = 0U;
            if (result->target_mode && local_index >= target_worker)
                break;
            ordinal = sat_v3_ordinal(
                local_index, args->worker_id, args->worker_count);
            record = sat_v3_record(workset, ordinal);
            SAT_V3_REQUIRE(
                hhs_exact_vm81_frame_import_le(
                    record,
                    (size_t)SAT_V3_RECORD_BYTES,
                    &frame) == HHS_EXACT_STATUS_OK);
            SAT_V3_REQUIRE(
                hhs_exact_vm81_frame_export_le(
                    &frame,
                    out,
                    sizeof(out),
                    &out_length) == HHS_EXACT_STATUS_OK);
            SAT_V3_REQUIRE(out_length == (size_t)SAT_V3_RECORD_BYTES);
            SAT_V3_REQUIRE(
                memcmp(record, out, (size_t)SAT_V3_RECORD_BYTES) == 0);
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
    fprintf(stderr, "base ABI saturation v3 requires Linux x86_64\n");
    return 2;
#else
    SatV3Args args = sat_v3_parse_args(argc, argv);
    SatV3Workset workset = sat_v3_workset_init();
    SatV3LoopResult result;

    SAT_V3_REQUIRE(hhs_exact_abi_validate() == HHS_EXACT_STATUS_OK);
    run_loop(&args, &workset, &result);
    sat_v3_print_common_json(
        "B",
        "immutable_v1_1_base_abi_vm81_import_export",
        &args,
        &workset,
        &result,
        "\"aggregate_abi_linked\":false,\"pass219_features_linked\":false");
    sat_v3_workset_free(&workset);
    return 0;
#endif
}
