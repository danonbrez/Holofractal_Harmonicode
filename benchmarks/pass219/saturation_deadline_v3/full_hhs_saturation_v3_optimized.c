#define main a_v3_legacy_main
#include "full_hhs_saturation_v3.c"
#undef main

#define A_V3_OPT_CELLS_PER_LANE UINT32_C(36)
#define A_V3_OPT_BRANCHES UINT32_C(144)

typedef struct AV3OptimizedContext {
    AV3Context base;
    uint32_t branch_id[A_V3_PHASES][A_V3_OPT_CELLS_PER_LANE];
    uint32_t memo_branch_id[A_V3_PHASES];
} AV3OptimizedContext;

static void a_v3_opt_build_branch_topology(AV3OptimizedContext *opt) {
    uint32_t lane;

    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_branch_ref_cache_init(
            &opt->base.branch_cache,
            &opt->base.stack_cache) == HHS_EXACT_STATUS_OK);

    for (lane = 0U; lane < A_V3_PHASES; ++lane) {
        HHSExactPass219H36BranchReceiptV1 receipt;
        uint32_t branch_id = 0U;
        uint32_t local;
        memset(&receipt, 0, sizeof(receipt));

        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_branch_ref_root(
                &opt->base.branch_cache,
                &opt->base.stack_cache,
                lane,
                (uint8_t)lane,
                0U,
                &branch_id,
                &receipt) == HHS_EXACT_STATUS_OK);
        SAT_V3_REQUIRE(receipt.exact_replayable == 1U);
        opt->branch_id[lane][0] = branch_id;

        for (local = 0U; local < A_V3_OPT_CELLS_PER_LANE; ++local) {
            uint32_t left = local * 2U + 1U;
            uint32_t right = local * 2U + 2U;
            if (left < A_V3_OPT_CELLS_PER_LANE) {
                SAT_V3_REQUIRE(
                    hhs_exact_pass219_h36_branch_ref_fork(
                        &opt->base.branch_cache,
                        &opt->base.stack_cache,
                        opt->branch_id[lane][local],
                        HHS_EXACT_PASS219_H36_BRANCH_CHILD_LEFT,
                        &branch_id,
                        &receipt) == HHS_EXACT_STATUS_OK);
                opt->branch_id[lane][left] = branch_id;
            }
            if (right < A_V3_OPT_CELLS_PER_LANE) {
                SAT_V3_REQUIRE(
                    hhs_exact_pass219_h36_branch_ref_fork(
                        &opt->base.branch_cache,
                        &opt->base.stack_cache,
                        opt->branch_id[lane][local],
                        HHS_EXACT_PASS219_H36_BRANCH_CHILD_RIGHT,
                        &branch_id,
                        &receipt) == HHS_EXACT_STATUS_OK);
                opt->branch_id[lane][right] = branch_id;
            }
        }
        opt->memo_branch_id[lane] =
            opt->branch_id[lane][A_V3_OPT_CELLS_PER_LANE - 1U];
        opt->base.memo_target_lane[lane] =
            (uint8_t)((lane + 1U) % A_V3_PHASES);
    }

    SAT_V3_REQUIRE(opt->base.branch_cache.entry_count == A_V3_OPT_BRANCHES);
    opt->base.memo_threshold =
        hhs_exact_pass219_h36_branch_ref_memo_threshold(
            opt->base.branch_cache.entry_count);
    SAT_V3_REQUIRE(opt->base.memo_threshold == UINT32_C(3172));

    for (lane = 0U; lane < A_V3_PHASES; ++lane) {
        uint32_t q;
        HHSExactPass219H36CompositionReceiptMemoV1 receipt;
        memset(&receipt, 0, sizeof(receipt));
        for (q = 0U; q <= opt->base.memo_threshold; ++q) {
            SAT_V3_REQUIRE(
                hhs_exact_pass219_h36_branch_ref_composition_receipt(
                    &opt->base.branch_cache,
                    &opt->base.stack_cache,
                    opt->memo_branch_id[lane],
                    opt->base.memo_target_lane[lane],
                    &receipt) == HHS_EXACT_STATUS_OK);
        }
        SAT_V3_REQUIRE(receipt.memoized == 1U);
        SAT_V3_REQUIRE(receipt.exact_replayable == 1U);
    }
}

static void a_v3_opt_context_init(AV3OptimizedContext *opt) {
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 authority;
    uint64_t started;

    memset(opt, 0, sizeof(*opt));
    memset(&authority, 0, sizeof(authority));
    SAT_V3_REQUIRE(hhs_exact_abi_validate() == HHS_EXACT_STATUS_OK);
    SAT_V3_REQUIRE(
        hhs_exact_pass219_lane5_unbounded_workload_scaling_authority(
            &authority) == HHS_EXACT_STATUS_OK);
    SAT_V3_REQUIRE(authority.candidate_only == 1U);
    SAT_V3_REQUIRE(authority.canonical_vm81_mutation_authority == 0U);
    SAT_V3_REQUIRE(authority.canonical_hash72_authority == 0U);
    SAT_V3_REQUIRE(authority.canonical_hash216_authority == 0U);
    SAT_V3_REQUIRE(authority.canonical_persistence_authority == 0U);
    SAT_V3_REQUIRE(authority.requires_signed_environmental_vm81_admission == 1U);
    SAT_V3_REQUIRE(authority.floating_point_canonical_authority == 0U);

    started = sat_v3_monotonic_ns();
    a_v3_prepare_optimizer_evidence(&opt->base);
    a_v3_prepare_m_witnesses(&opt->base);
    a_v3_opt_build_branch_topology(opt);
    opt->base.warm_fill_ns = sat_v3_monotonic_ns() - started;
}

static uint32_t a_v3_opt_branch_for_ordinal(
    const AV3OptimizedContext *opt,
    uint64_t ordinal,
    uint32_t slot
) {
    uint32_t local =
        (uint32_t)((ordinal / (uint64_t)A_V3_PHASES) %
                   (uint64_t)A_V3_OPT_CELLS_PER_LANE);
    SAT_V3_REQUIRE(slot < A_V3_PHASES);
    return opt->branch_id[slot][local];
}

static void a_v3_opt_warm_operation(
    AV3OptimizedContext *opt,
    const uint8_t record[SAT_V3_RECORD_BYTES],
    uint64_t ordinal,
    uint8_t out[SAT_V3_RECORD_BYTES],
    AV3Stats *stats
) {
    uint32_t slot = (uint32_t)(ordinal % A_V3_PHASES);
    uint32_t branch_id = a_v3_opt_branch_for_ordinal(opt, ordinal, slot);
    const HHSExactPass219H36StackSelectionV1 *branch_selection = NULL;
    HHSExactPass219H36BranchReceiptV1 branch_receipt;
    HHSExactPass219H36CompositionReceiptMemoV1 composition_receipt;
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *occurrence;

    a_v3_base_and_route(record, slot, out);
    ++stats->route_receipts;

    /*
     * Optimized hot path: direct immutable branch reference. The parent
     * stack-cache scan is intentionally NOT called here. Parent stack-cache
     * equality/integrity is proven in preflight and the branch resolver
     * validates the frozen parent entry referenced by the branch.
     */
    memset(&branch_receipt, 0, sizeof(branch_receipt));
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_branch_ref_resolve(
            &opt->base.branch_cache,
            &opt->base.stack_cache,
            branch_id,
            &branch_selection,
            &branch_receipt) == HHS_EXACT_STATUS_OK);
    SAT_V3_REQUIRE(branch_selection != NULL);
    SAT_V3_REQUIRE(branch_receipt.exact_replayable == 1U);
    SAT_V3_REQUIRE(branch_receipt.branch_reference_only == 1U);
    SAT_V3_REQUIRE(branch_receipt.canonical_mutation_authority == 0U);
    SAT_V3_REQUIRE(branch_receipt.canonical_hash72_authority == 0U);
    SAT_V3_REQUIRE(branch_receipt.canonical_hash216_authority == 0U);
    SAT_V3_REQUIRE(branch_receipt.canonical_persistence_authority == 0U);
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
            branch_selection,
            &opt->base.fresh[slot]) == HHS_EXACT_STATUS_OK);
    ++stats->cache_hits;
    ++stats->branch_resolves;

    memset(&composition_receipt, 0, sizeof(composition_receipt));
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_branch_ref_composition_receipt(
            &opt->base.branch_cache,
            &opt->base.stack_cache,
            opt->memo_branch_id[slot],
            opt->base.memo_target_lane[slot],
            &composition_receipt) == HHS_EXACT_STATUS_OK);
    SAT_V3_REQUIRE(composition_receipt.memoized == 1U);
    SAT_V3_REQUIRE(composition_receipt.exact_replayable == 1U);
    ++stats->memoized_compositions;

    occurrence =
        &opt->base.binding.occurrences[opt->base.occurrence_index[slot]];
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_hash216_m_exponent_validate(
            occurrence,
            &opt->base.m_witness[slot]) == HHS_EXACT_STATUS_OK);
    ++stats->m_validations;
}

static void a_v3_opt_preflight(
    AV3OptimizedContext *opt,
    const SatV3Workset *workset
) {
    uint32_t slot;
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_branch_ref_cache_validate(
            &opt->base.branch_cache,
            &opt->base.stack_cache) == HHS_EXACT_STATUS_OK);

    for (slot = 0U; slot < A_V3_PHASES; ++slot) {
        HHSExactPass219H36StackSelectionV1 cached;
        HHSExactPass219H36StackCacheReceiptV1 cache_receipt;
        const HHSExactPass219H36StackSelectionV1 *direct = NULL;
        HHSExactPass219H36BranchReceiptV1 branch_receipt;
        HHSExactPass219H36CompositionReceiptMemoV1 composition_receipt;
        const uint8_t *record = sat_v3_record(workset, slot);
        uint8_t out[SAT_V3_RECORD_BYTES];
        AV3Stats cold_stats;
        AV3Stats warm_stats;

        /* Prove inherited parent-cache equality outside the timer. */
        memset(&cached, 0, sizeof(cached));
        memset(&cache_receipt, 0, sizeof(cache_receipt));
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_stack_cache_lookup(
                &opt->base.stack_cache,
                opt->base.fresh[slot].workload_signature36,
                opt->base.fresh[slot].semantic_result_signature64,
                opt->base.fresh[slot].selected_vector_key216,
                &cached,
                &cache_receipt) == HHS_EXACT_STATUS_OK);
        SAT_V3_REQUIRE(cache_receipt.cache_hit == 1U);
        SAT_V3_REQUIRE(cache_receipt.exact_replayable == 1U);
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
                &cached,
                &opt->base.fresh[slot]) == HHS_EXACT_STATUS_OK);

        memset(&branch_receipt, 0, sizeof(branch_receipt));
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_branch_ref_resolve(
                &opt->base.branch_cache,
                &opt->base.stack_cache,
                opt->branch_id[slot][A_V3_OPT_CELLS_PER_LANE - 1U],
                &direct,
                &branch_receipt) == HHS_EXACT_STATUS_OK);
        SAT_V3_REQUIRE(direct != NULL && branch_receipt.exact_replayable == 1U);
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
                direct,
                &opt->base.fresh[slot]) == HHS_EXACT_STATUS_OK);

        memset(&composition_receipt, 0, sizeof(composition_receipt));
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_branch_ref_composition_receipt(
                &opt->base.branch_cache,
                &opt->base.stack_cache,
                opt->memo_branch_id[slot],
                opt->base.memo_target_lane[slot],
                &composition_receipt) == HHS_EXACT_STATUS_OK);
        SAT_V3_REQUIRE(composition_receipt.memoized == 1U);
        SAT_V3_REQUIRE(composition_receipt.exact_replayable == 1U);

        memset(&cold_stats, 0, sizeof(cold_stats));
        memset(&warm_stats, 0, sizeof(warm_stats));
        a_v3_cold_operation(&opt->base, record, slot, out, &cold_stats);
        a_v3_opt_warm_operation(opt, record, slot, out, &warm_stats);
        SAT_V3_REQUIRE(cold_stats.route_receipts == 1U);
        SAT_V3_REQUIRE(cold_stats.fresh_selections == 1U);
        SAT_V3_REQUIRE(warm_stats.route_receipts == 1U);
        SAT_V3_REQUIRE(warm_stats.cache_hits == 1U);
        SAT_V3_REQUIRE(warm_stats.branch_resolves == 1U);
        SAT_V3_REQUIRE(warm_stats.memoized_compositions == 1U);
    }
}

static void a_v3_opt_run_loop(
    const SatV3Args *args,
    const SatV3Workset *workset,
    AV3OptimizedContext *opt,
    int warm,
    SatV3LoopResult *result,
    AV3Stats *stats
) {
    uint64_t local_index = 0U;
    uint64_t target_worker;
    uint64_t deadline_ns;
    uint64_t started_ns;
    uint64_t now;
    uint64_t digest = SAT_V3_FNV_OFFSET;

    memset(stats, 0, sizeof(*stats));
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
            uint8_t out[SAT_V3_RECORD_BYTES];
            if (result->target_mode && local_index >= target_worker)
                break;
            ordinal = sat_v3_ordinal(
                local_index, args->worker_id, args->worker_count);
            record = sat_v3_record(workset, ordinal);
            if (warm)
                a_v3_opt_warm_operation(opt, record, ordinal, out, stats);
            else
                a_v3_cold_operation(&opt->base, record, ordinal, out, stats);
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
        result->target_mode
            ? (uint8_t)(local_index >= target_worker && now <= deadline_ns)
            : 1U;
}

int main(int argc, char **argv) {
#if !defined(__linux__) || !defined(__x86_64__)
    fprintf(stderr, "optimized full HHS saturation v3 requires Linux x86_64\n");
    return 2;
#else
    const char *mode = getenv("HHS_SAT_V3_A_MODE");
    int warm = 1;
    SatV3Args args = sat_v3_parse_args(argc, argv);
    SatV3Workset workset = sat_v3_workset_init();
    AV3OptimizedContext *opt =
        (AV3OptimizedContext *)calloc(1U, sizeof(*opt));
    SatV3LoopResult result;
    AV3Stats stats;
    char extra[2048];

    SAT_V3_REQUIRE(opt != NULL);
    if (mode != NULL && strcmp(mode, "cold") == 0)
        warm = 0;
    else if (mode != NULL)
        SAT_V3_REQUIRE(strcmp(mode, "warm") == 0);

    a_v3_opt_context_init(opt);
    a_v3_opt_preflight(opt, &workset);
    a_v3_opt_run_loop(&args, &workset, opt, warm, &result, &stats);

    SAT_V3_REQUIRE(stats.route_receipts == result.completed);
    SAT_V3_REQUIRE(stats.m_validations == result.completed);
    if (warm) {
        SAT_V3_REQUIRE(stats.cache_hits == result.completed);
        SAT_V3_REQUIRE(stats.branch_resolves == result.completed);
        SAT_V3_REQUIRE(stats.memoized_compositions == result.completed);
        SAT_V3_REQUIRE(stats.fresh_selections == 0U);
        SAT_V3_REQUIRE(stats.m_binds == 0U);
    } else {
        SAT_V3_REQUIRE(stats.fresh_selections == result.completed);
        SAT_V3_REQUIRE(stats.m_binds == result.completed);
        SAT_V3_REQUIRE(stats.cache_hits == 0U);
        SAT_V3_REQUIRE(stats.branch_resolves == 0U);
    }

    snprintf(
        extra,
        sizeof(extra),
        "\"aggregate_abi_linked\":true,\"pass219_features_linked\":true,"
        "\"lane5_route_called\":true,\"mode\":\"%s\","
        "\"warm_fill_ns\":%" PRIu64 ",\"stack_cache_entries\":%u,"
        "\"branch_cache_entries\":%u,\"memo_threshold\":%u,"
        "\"route_receipts\":%" PRIu64 ",\"fresh_selections\":%" PRIu64 ","
        "\"cache_hits\":%" PRIu64 ",\"direct_reference_hits\":%" PRIu64 ","
        "\"branch_resolves\":%" PRIu64 ","
        "\"memoized_compositions\":%" PRIu64 ",\"m_binds\":%" PRIu64 ","
        "\"m_validations\":%" PRIu64 ",\"warm_cache_proved\":%s,"
        "\"stack_cache_lookup_in_timed_loop\":false,"
        "\"direct_reference_hot_path\":%s,"
        "\"canonical_mutation_authority\":false,"
        "\"canonical_hash216_authority\":false",
        warm ? "warm" : "cold",
        opt->base.warm_fill_ns,
        opt->base.stack_cache.entry_count,
        opt->base.branch_cache.entry_count,
        opt->base.memo_threshold,
        stats.route_receipts,
        stats.fresh_selections,
        stats.cache_hits,
        stats.cache_hits,
        stats.branch_resolves,
        stats.memoized_compositions,
        stats.m_binds,
        stats.m_validations,
        warm ? "true" : "false",
        warm ? "true" : "false");

    sat_v3_print_common_json(
        warm ? "A_warm" : "A_cold",
        warm
            ? "aggregate_abi_lane5_h36_hash216_direct_reference_warm_stack"
            : "aggregate_abi_lane5_h36_hash216_cold_recompute_stack",
        &args,
        &workset,
        &result,
        extra);

    free(opt);
    sat_v3_workset_free(&workset);
    return 0;
#endif
}
