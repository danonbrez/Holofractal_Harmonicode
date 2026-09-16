#define main hhs_pass219_reciprocal_wave_v3_legacy_main
#include "hhs_lane5_120ms_reciprocal_wave_xyzw_v3.c"
#undef main

static int strict_invalid(
    const char *reason,
    uint64_t sample,
    const char *leg,
    uint64_t observed_ns,
    uint64_t leg_budget_ns
) {
    fprintf(stderr,
            "{\"type\":\"invalid_trial\",\"sample\":%" PRIu64
            ",\"leg\":\"%s\",\"reason\":\"%s\",\"observed_ns\":%" PRIu64
            ",\"leg_budget_ns\":%" PRIu64 ",\"result\":\"FAIL\"}\n",
            sample, leg, reason, observed_ns, leg_budget_ns);
    return EXIT_FAILURE;
}

static int strict_hhs_leg_ok(
    const HhsResult *r,
    uint64_t leg_budget_ns,
    uint64_t sample,
    const char *leg
) {
    if (!r->dataset_complete)
        return strict_invalid("incomplete_leg", sample, leg, r->elapsed_ns, leg_budget_ns);
    if (r->completion_elapsed_ns == 0U)
        return strict_invalid("zero_completion_time", sample, leg, r->completion_elapsed_ns, leg_budget_ns);
    if (r->completion_elapsed_ns >= leg_budget_ns)
        return strict_invalid("non_positive_leg_residual", sample, leg, r->completion_elapsed_ns, leg_budget_ns);
    return EXIT_SUCCESS;
}

static int strict_conv_leg_ok(
    const ConventionalResult *r,
    uint64_t leg_budget_ns,
    uint64_t sample,
    const char *leg
) {
    if (!r->dataset_complete)
        return strict_invalid("incomplete_leg", sample, leg, r->elapsed_ns, leg_budget_ns);
    if (r->completion_elapsed_ns == 0U)
        return strict_invalid("zero_completion_time", sample, leg, r->completion_elapsed_ns, leg_budget_ns);
    if (r->completion_elapsed_ns >= leg_budget_ns)
        return strict_invalid("non_positive_leg_residual", sample, leg, r->completion_elapsed_ns, leg_budget_ns);
    return EXIT_SUCCESS;
}

static int strict_global_positive(
    const struct timespec *batch_start,
    uint64_t sample,
    const char *leg,
    uint64_t leg_budget_ns
) {
    uint64_t used = elapsed_from(batch_start);
    if (used >= GLOBAL_BUDGET_NS)
        return strict_invalid("non_positive_global_residual", sample, leg, used, leg_budget_ns);
    return EXIT_SUCCESS;
}

int main(void) {
    uint64_t base_queries = env_u64("HHS_RECIPROCAL_WAVE_DATASET_QUERIES", DEFAULT_DATASET_QUERIES);
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 authority;
    HhsResult cal_h;
    ConventionalResult cal_c;
    uint64_t base_ns, predicted_threshold_ns, query_scale, sample_count = 0U;
    struct timespec batch_start, batch_end;
    uint64_t batch_elapsed_ns, remaining_ns;
    const char *stop_reason = "unknown";

    memset(&authority, 0, sizeof(authority));
    REQUIRE(hhs_exact_pass219_lane5_unbounded_workload_scaling_authority(&authority) == HHS_EXACT_STATUS_OK);
    REQUIRE(authority.constant_memory_candidate_reduction == 1U);
    REQUIRE(authority.intermediate_materialization_required == 0U);
    REQUIRE(authority.candidate_only == 1U);
    REQUIRE(authority.canonical_vm81_mutation_authority == 0U);
    REQUIRE(authority.canonical_hash72_authority == 0U);
    REQUIRE(authority.canonical_hash216_authority == 0U);
    REQUIRE(authority.requires_signed_environmental_vm81_admission == 1U);

    cal_h = run_hhs(STREAM_SEED_W, base_queries, 0U);
    cal_c = run_conventional(STREAM_SEED_W, base_queries, 0U);
    REQUIRE(cal_h.dataset_complete == 1U && cal_c.dataset_complete == 1U);
    base_ns = cal_h.completion_elapsed_ns > cal_c.completion_elapsed_ns
        ? cal_h.completion_elapsed_ns : cal_c.completion_elapsed_ns;
    predicted_threshold_ns = base_ns +
        (base_ns / 2U > MIN_LEG_BUDGET_NS ? base_ns / 2U : MIN_LEG_BUDGET_NS);
    query_scale = base_queries;

    printf("{\"type\":\"batch_meta\",\"schema\":\"HHS_120MS_GLOBAL_RECIPROCAL_WAVE_XYZW_V3_STRICT\","
           "\"global_budget_ns\":%" PRIu64 ",\"base_dataset_queries\":%" PRIu64
           ",\"seed_W\":%" PRIu64 ",\"calibration_hhs_completion_ns\":%" PRIu64
           ",\"calibration_conventional_completion_ns\":%" PRIu64
           ",\"initial_reasonable_completion_threshold_ns\":%" PRIu64
           ",\"gradient_factor\":2,\"active_threads_per_benchmark\":1,"
           "\"benchmarks_sequential\":true,\"strict_positive_residual\":true,"
           "\"clamping_permitted\":false}\n",
           GLOBAL_BUDGET_NS, base_queries, STREAM_SEED_W,
           cal_h.completion_elapsed_ns, cal_c.completion_elapsed_ns,
           predicted_threshold_ns);

    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &batch_start) == 0);

    for (;;) {
        uint64_t used = elapsed_from(&batch_start);
        uint64_t leg_budget_ns;
        HhsResult a, d;
        ConventionalResult b, c;
        PrefixIdentity target;
        uint64_t max_leg_elapsed, next_prediction;

        if (used >= GLOBAL_BUDGET_NS)
            return strict_invalid("global_budget_exhausted_before_trial", sample_count, "PRE", used, 0U);

        remaining_ns = GLOBAL_BUDGET_NS - used;
        if (remaining_ns <= 4U * MIN_LEG_BUDGET_NS) {
            stop_reason = "insufficient_minimum_fair_four_leg_slice";
            break;
        }

        leg_budget_ns = remaining_ns / 4U;
        if (leg_budget_ns <= predicted_threshold_ns) {
            stop_reason = "predicted_threshold_exceeds_fair_leg_budget";
            break;
        }

        a = run_hhs(STREAM_SEED_W, query_scale, leg_budget_ns);
        if (strict_hhs_leg_ok(&a, leg_budget_ns, sample_count, "A") != EXIT_SUCCESS)
            return EXIT_FAILURE;
        if (strict_global_positive(&batch_start, sample_count, "A", leg_budget_ns) != EXIT_SUCCESS)
            return EXIT_FAILURE;

        b = run_conventional(STREAM_SEED_W, query_scale, leg_budget_ns);
        if (strict_conv_leg_ok(&b, leg_budget_ns, sample_count, "B") != EXIT_SUCCESS)
            return EXIT_FAILURE;
        if (strict_global_positive(&batch_start, sample_count, "B", leg_budget_ns) != EXIT_SUCCESS)
            return EXIT_FAILURE;

        c = run_conventional(STREAM_SEED_W, query_scale, leg_budget_ns);
        if (strict_conv_leg_ok(&c, leg_budget_ns, sample_count, "C") != EXIT_SUCCESS)
            return EXIT_FAILURE;
        if (strict_global_positive(&batch_start, sample_count, "C", leg_budget_ns) != EXIT_SUCCESS)
            return EXIT_FAILURE;

        d = run_hhs(STREAM_SEED_W, query_scale, leg_budget_ns);
        if (strict_hhs_leg_ok(&d, leg_budget_ns, sample_count, "D") != EXIT_SUCCESS)
            return EXIT_FAILURE;
        if (strict_global_positive(&batch_start, sample_count, "D", leg_budget_ns) != EXIT_SUCCESS)
            return EXIT_FAILURE;

        target = reference_prefix(STREAM_SEED_W, query_scale);
        require_prefix(&target, a.completed_queries, a.represented_transitions, a.descriptor_bits,
                       a.endpoint_digest, a.descriptor_digest);
        require_prefix(&target, b.completed_queries, b.represented_transitions, b.descriptor_bits,
                       b.endpoint_digest, b.descriptor_digest);
        require_prefix(&target, c.completed_queries, c.represented_transitions, c.descriptor_bits,
                       c.endpoint_digest, c.descriptor_digest);
        require_prefix(&target, d.completed_queries, d.represented_transitions, d.descriptor_bits,
                       d.endpoint_digest, d.descriptor_digest);
        if (strict_global_positive(&batch_start, sample_count, "VERIFY", leg_budget_ns) != EXIT_SUCCESS)
            return EXIT_FAILURE;

        print_hhs(sample_count, query_scale, leg_budget_ns, predicted_threshold_ns, "A", "x", &a);
        print_conv(sample_count, query_scale, leg_budget_ns, predicted_threshold_ns, "B", "y", &b);
        print_conv(sample_count, query_scale, leg_budget_ns, predicted_threshold_ns, "C", "z", &c);
        print_hhs(sample_count, query_scale, leg_budget_ns, predicted_threshold_ns, "D", "w", &d);
        printf("{\"type\":\"sample_reference\",\"sample\":%" PRIu64
               ",\"query_scale\":%" PRIu64 ",\"subthreshold\":false,"
               "\"completed_queries\":%" PRIu64 ",\"represented_transitions\":\"",
               sample_count, query_scale, target.completed_queries);
        print_u128(target.represented_transitions);
        printf("\",\"descriptor_bits\":\"");
        print_u128(target.descriptor_bits);
        printf("\",\"endpoint_digest\":%" PRIu64 ",\"descriptor_digest\":%" PRIu64 "}\n",
               target.endpoint_digest, target.descriptor_digest);

        ++sample_count;

        max_leg_elapsed = a.completion_elapsed_ns;
        if (b.completion_elapsed_ns > max_leg_elapsed) max_leg_elapsed = b.completion_elapsed_ns;
        if (c.completion_elapsed_ns > max_leg_elapsed) max_leg_elapsed = c.completion_elapsed_ns;
        if (d.completion_elapsed_ns > max_leg_elapsed) max_leg_elapsed = d.completion_elapsed_ns;
        next_prediction = 2U * max_leg_elapsed;
        next_prediction +=
            (next_prediction / 2U > MIN_LEG_BUDGET_NS ? next_prediction / 2U : MIN_LEG_BUDGET_NS);
        predicted_threshold_ns = next_prediction;

        if (query_scale > UINT64_MAX / 2U) {
            stop_reason = "query_scale_uint64_limit";
            break;
        }
        query_scale *= 2U;
    }

    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &batch_end) == 0);
    batch_elapsed_ns = elapsed_ns(&batch_start, &batch_end);
    if (batch_elapsed_ns >= GLOBAL_BUDGET_NS)
        return strict_invalid("non_positive_final_global_residual", sample_count, "POST", batch_elapsed_ns, 0U);
    remaining_ns = GLOBAL_BUDGET_NS - batch_elapsed_ns;
    if (remaining_ns == 0U)
        return strict_invalid("zero_final_global_residual", sample_count, "POST", batch_elapsed_ns, 0U);
    REQUIRE(sample_count >= 3U);

    printf("{\"type\":\"batch_result\",\"sample_count\":%" PRIu64
           ",\"batch_elapsed_ns\":%" PRIu64 ",\"remaining_budget_ns\":%" PRIu64
           ",\"boundary_sample_seen\":false,\"invalid_trial_seen\":false,"
           "\"stopped_before_unfair_trial\":true,\"stop_reason\":\"%s\","
           "\"result\":\"PASS\"}\n",
           sample_count, batch_elapsed_ns, remaining_ns, stop_reason);
    return EXIT_SUCCESS;
}
