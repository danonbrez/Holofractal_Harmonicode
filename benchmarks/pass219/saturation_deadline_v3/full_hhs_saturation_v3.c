#define _POSIX_C_SOURCE 200809L
#include "hhs_runtime_exact_abi.h"
#include "saturation_common_v3.h"

#define A_V3_PHASES UINT32_C(4)

typedef struct AV3Context {
    HHSExactPass219H36StackCandidateEvidenceV1 h36[A_V3_PHASES];
    HHSExactPass219H36StackCandidateEvidenceV1 linux[A_V3_PHASES];
    HHSExactPass219H36StackSelectionV1 fresh[A_V3_PHASES];
    HHSExactPass219H36StackCacheV1 stack_cache;
    HHSExactPass219H36BranchReferenceCacheV1 branch_cache;
    uint32_t root_branch_id[A_V3_PHASES];
    uint8_t memo_target_lane[A_V3_PHASES];
    uint32_t memo_threshold;
    HHSExactPass219H36Hash216TransitionBindingV1 binding;
    HHSExactPass219H36Hash216MExponentWitnessV1 m_witness[A_V3_PHASES];
    uint32_t occurrence_index[A_V3_PHASES];
    uint64_t warm_fill_ns;
} AV3Context;

typedef struct AV3Stats {
    uint64_t route_receipts;
    uint64_t fresh_selections;
    uint64_t cache_hits;
    uint64_t branch_resolves;
    uint64_t memoized_compositions;
    uint64_t m_binds;
    uint64_t m_validations;
} AV3Stats;

static const uint32_t A_V3_PHASE_SLOT[A_V3_PHASES] = {0U, 36U, 18U, 54U};
static const uint32_t A_V3_INVERSE_SLOT[A_V3_PHASES] = {36U, 0U, 54U, 18U};
static const uint32_t A_V3_OCCURRENCE[A_V3_PHASES] = {0U, 54U, 108U, 162U};
static const uint64_t A_V3_WORKLOAD[A_V3_PHASES] = {
    UINT64_C(3734727431),
    UINT64_C(4793332410),
    UINT64_C(21509979554),
    UINT64_C(41886677838)
};
static const uint64_t A_V3_SEMANTIC[A_V3_PHASES] = {
    UINT64_C(4176962402124975431),
    UINT64_C(6731027650694893003),
    UINT64_C(1456447110141201574),
    UINT64_C(2318081696571468614)
};
static const uint64_t A_V3_H36_NS[A_V3_PHASES] = {
    UINT64_C(96531), UINT64_C(23033), UINT64_C(23073), UINT64_C(19156)
};
static const uint64_t A_V3_LINUX_NS[A_V3_PHASES] = {
    UINT64_C(873043), UINT64_C(106949), UINT64_C(109553), UINT64_C(501)
};

static HHSExactBigUIntView a_v3_bview8(const uint8_t bytes[8]) {
    HHSExactBigUIntView view;
    view.struct_size = (uint32_t)sizeof(view);
    view.byte_length = 8U;
    view.bytes_be = bytes;
    return view;
}

static void a_v3_init_hash216_binding(
    HHSExactPass219H36Hash216TransitionBindingV1 *binding
) {
    char previous[HHS_EXACT_HASH72_STRLEN];
    char change[HHS_EXACT_HASH72_STRLEN];
    char receipt[HHS_EXACT_HASH72_STRLEN];
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
    HHSExactPass219Hash216TransitionViewV1 transition;
    uint32_t i;

    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i) {
        previous[i] = HHS_EXACT_HASH72_ALPHABET[i];
        change[i] = HHS_EXACT_HASH72_ALPHABET[(i + 1U) % HHS_EXACT_HASH72_LEN];
        receipt[i] = HHS_EXACT_HASH72_ALPHABET[(i + 2U) % HHS_EXACT_HASH72_LEN];
    }
    previous[HHS_EXACT_HASH72_LEN] = '\0';
    change[HHS_EXACT_HASH72_LEN] = '\0';
    receipt[HHS_EXACT_HASH72_LEN] = '\0';
    memset(identity, 'M', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    identity[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';

    SAT_V3_REQUIRE(
        hhs_exact_pass219_hash216_transition_init(
            previous, change, receipt, identity, &transition) ==
        HHS_EXACT_STATUS_OK);
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_hash216_transition_bind(
            &transition, binding) == HHS_EXACT_STATUS_OK);
}

static void a_v3_prepare_optimizer_evidence(AV3Context *ctx) {
    uint32_t slot;
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_stack_cache_init(&ctx->stack_cache) ==
        HHS_EXACT_STATUS_OK);

    for (slot = 0U; slot < A_V3_PHASES; ++slot) {
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_stack_candidate_prepare(
                1U,
                HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10,
                A_V3_WORKLOAD[slot],
                A_V3_SEMANTIC[slot],
                A_V3_H36_NS[slot],
                7U,
                8U,
                5120U,
                8U + slot,
                1U,
                &ctx->h36[slot]) == HHS_EXACT_STATUS_OK);
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_stack_candidate_prepare(
                2U,
                HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64,
                A_V3_WORKLOAD[slot],
                A_V3_SEMANTIC[slot],
                A_V3_LINUX_NS[slot],
                7U,
                8U,
                100U,
                12U + slot,
                1U,
                &ctx->linux[slot]) == HHS_EXACT_STATUS_OK);
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_stack_select(
                &ctx->h36[slot],
                &ctx->linux[slot],
                &ctx->fresh[slot]) == HHS_EXACT_STATUS_OK);
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_stack_cache_store(
                &ctx->stack_cache,
                &ctx->fresh[slot]) == HHS_EXACT_STATUS_OK);
    }
    SAT_V3_REQUIRE(ctx->stack_cache.entry_count == A_V3_PHASES);
}

static void a_v3_prepare_branch_cache(AV3Context *ctx) {
    uint32_t slot;
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_branch_ref_cache_init(
            &ctx->branch_cache,
            &ctx->stack_cache) == HHS_EXACT_STATUS_OK);

    for (slot = 0U; slot < A_V3_PHASES; ++slot) {
        HHSExactPass219H36BranchReceiptV1 receipt;
        memset(&receipt, 0, sizeof(receipt));
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_branch_ref_root(
                &ctx->branch_cache,
                &ctx->stack_cache,
                slot,
                (uint8_t)slot,
                0U,
                &ctx->root_branch_id[slot],
                &receipt) == HHS_EXACT_STATUS_OK);
        SAT_V3_REQUIRE(receipt.exact_replayable == 1U);
        ctx->memo_target_lane[slot] = (uint8_t)((slot + 1U) % A_V3_PHASES);
    }

    ctx->memo_threshold =
        hhs_exact_pass219_h36_branch_ref_memo_threshold(
            ctx->branch_cache.entry_count);
    SAT_V3_REQUIRE(ctx->memo_threshold > 0U);

    for (slot = 0U; slot < A_V3_PHASES; ++slot) {
        uint32_t q;
        HHSExactPass219H36CompositionReceiptMemoV1 receipt;
        memset(&receipt, 0, sizeof(receipt));
        for (q = 0U; q <= ctx->memo_threshold; ++q) {
            SAT_V3_REQUIRE(
                hhs_exact_pass219_h36_branch_ref_composition_receipt(
                    &ctx->branch_cache,
                    &ctx->stack_cache,
                    ctx->root_branch_id[slot],
                    ctx->memo_target_lane[slot],
                    &receipt) == HHS_EXACT_STATUS_OK);
        }
        SAT_V3_REQUIRE(receipt.memoized == 1U);
        SAT_V3_REQUIRE(receipt.exact_replayable == 1U);
    }
}

static void a_v3_prepare_m_witnesses(AV3Context *ctx) {
    uint32_t slot;
    a_v3_init_hash216_binding(&ctx->binding);
    for (slot = 0U; slot < A_V3_PHASES; ++slot) {
        const HHSExactPass219H36Hash216OccurrenceBindingV1 *occurrence;
        ctx->occurrence_index[slot] = A_V3_OCCURRENCE[slot];
        SAT_V3_REQUIRE(
            ctx->occurrence_index[slot] < HHS_EXACT_PASS219_HASH216_OCCURRENCES);
        occurrence = &ctx->binding.occurrences[ctx->occurrence_index[slot]];
        memset(&ctx->m_witness[slot], 0, sizeof(ctx->m_witness[slot]));
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_hash216_m_exponent_bind(
                occurrence,
                &ctx->m_witness[slot]) == HHS_EXACT_STATUS_OK);
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_hash216_m_exponent_validate(
                occurrence,
                &ctx->m_witness[slot]) == HHS_EXACT_STATUS_OK);
        SAT_V3_REQUIRE(ctx->m_witness[slot].direct_shared_m_binding == 1U);
        SAT_V3_REQUIRE(ctx->m_witness[slot].translator_required == 0U);
    }
}

static void a_v3_context_init(AV3Context *ctx) {
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 authority;
    uint64_t started;
    memset(ctx, 0, sizeof(*ctx));
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
    a_v3_prepare_optimizer_evidence(ctx);
    a_v3_prepare_branch_cache(ctx);
    a_v3_prepare_m_witnesses(ctx);
    ctx->warm_fill_ns = sat_v3_monotonic_ns() - started;
}

static void a_v3_build_route(
    const uint8_t record[SAT_V3_RECORD_BYTES],
    uint32_t slot,
    HHSExactPass219Lane5UnboundedWorkloadRouteV1 *route,
    uint8_t previous[8],
    uint8_t current[8],
    uint8_t goal[8]
) {
    memcpy(previous, record + 0U, 8U);
    memcpy(current, record + 8U, 8U);
    memcpy(goal, record + 16U, 8U);
    previous[0] |= 1U;
    current[0] |= 1U;
    goal[0] |= 1U;

    memset(route, 0, sizeof(*route));
    route->struct_size = (uint32_t)sizeof(*route);
    route->version = HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION;
    route->previous_address = a_v3_bview8(previous);
    route->current_address = a_v3_bview8(current);
    route->goal_address = a_v3_bview8(goal);
    route->candidate_address = a_v3_bview8(goal);
    memcpy(route->workload_sha256, record + 32U, 32U);
    memcpy(route->provenance_sha256, record + 64U, 32U);
    memcpy(route->forbidden_boundary_sha256, record + 96U, 32U);
    memcpy(route->reciprocal_witness_sha256, record + 128U, 32U);
    memcpy(route->route_witness_sha256, record + 160U, 32U);
    route->workload_byte_count = SAT_V3_RECORD_BYTES;
    route->evidence_count = 5U;
    route->contradiction_check_count = 1U;
    route->integer_route_cost = UINT64_C(7);
    route->materialized_intermediate_states = 0U;
    route->phase_slot = A_V3_PHASE_SLOT[slot];
    route->inverse_phase_slot = A_V3_INVERSE_SLOT[slot];
    route->trinary_collapse = (int8_t)((int)(record[192U] % 3U) - 1);
    route->binary_collapse = (uint8_t)(record[193U] & 1U);
    route->nested_zero_slot = route->binary_collapse == 0U ? 1U : 0U;
    route->workload_serialization_exact = 1U;
    route->source_digest_verified = 1U;
    route->replay_witness_verified = 1U;
    route->exact_goal_reached = 1U;
    route->contradiction_free = 1U;
    route->goal_forbidden_conflict = 0U;
    route->reciprocal_phase_verified = 1U;
    route->bigint_serialization_addressed = 1U;
    route->candidate_only = 1U;
    route->canonical_mutation_authority = 0U;
    route->canonical_hash72_authority = 0U;
    route->canonical_hash216_authority = 0U;
    route->canonical_persistence_authority = 0U;
    route->pqc_key_authority = 0U;
    route->receipt_clock_authority = 0U;
    route->requires_signed_environmental_vm81_admission = 1U;
}

static void a_v3_base_and_route(
    const uint8_t record[SAT_V3_RECORD_BYTES],
    uint32_t slot,
    uint8_t out[SAT_V3_RECORD_BYTES]
) {
    HHSExactVM81Frame frame;
    size_t out_length = 0U;
    HHSExactPass219Lane5UnboundedWorkloadRouteV1 route;
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 route_receipt;
    uint8_t previous[8];
    uint8_t current[8];
    uint8_t goal[8];

    SAT_V3_REQUIRE(
        hhs_exact_vm81_frame_import_le(
            record,
            (size_t)SAT_V3_RECORD_BYTES,
            &frame) == HHS_EXACT_STATUS_OK);
    SAT_V3_REQUIRE(
        hhs_exact_vm81_frame_export_le(
            &frame,
            out,
            (size_t)SAT_V3_RECORD_BYTES,
            &out_length) == HHS_EXACT_STATUS_OK);
    SAT_V3_REQUIRE(out_length == (size_t)SAT_V3_RECORD_BYTES);
    SAT_V3_REQUIRE(memcmp(record, out, (size_t)SAT_V3_RECORD_BYTES) == 0);

    a_v3_build_route(record, slot, &route, previous, current, goal);
    memset(&route_receipt, 0, sizeof(route_receipt));
    SAT_V3_REQUIRE(
        hhs_exact_pass219_lane5_unbounded_workload_route_validate(
            &route,
            &route_receipt) == HHS_EXACT_STATUS_OK);
    SAT_V3_REQUIRE(route_receipt.accepted == 1U);
    SAT_V3_REQUIRE(route_receipt.candidate_only == 1U);
    SAT_V3_REQUIRE(route_receipt.canonical_mutation_authority == 0U);
    SAT_V3_REQUIRE(route_receipt.canonical_hash72_authority == 0U);
    SAT_V3_REQUIRE(route_receipt.canonical_hash216_authority == 0U);
    SAT_V3_REQUIRE(route_receipt.canonical_persistence_authority == 0U);
    SAT_V3_REQUIRE(route_receipt.requires_signed_environmental_vm81_admission == 1U);
}

static void a_v3_warm_operation(
    AV3Context *ctx,
    const uint8_t record[SAT_V3_RECORD_BYTES],
    uint64_t ordinal,
    uint8_t out[SAT_V3_RECORD_BYTES],
    AV3Stats *stats
) {
    uint32_t slot = (uint32_t)(ordinal % A_V3_PHASES);
    HHSExactPass219H36StackSelectionV1 selected;
    HHSExactPass219H36StackCacheReceiptV1 cache_receipt;
    const HHSExactPass219H36StackSelectionV1 *branch_selection = NULL;
    HHSExactPass219H36BranchReceiptV1 branch_receipt;
    HHSExactPass219H36CompositionReceiptMemoV1 composition_receipt;
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *occurrence;

    a_v3_base_and_route(record, slot, out);
    ++stats->route_receipts;

    memset(&selected, 0, sizeof(selected));
    memset(&cache_receipt, 0, sizeof(cache_receipt));
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_stack_cache_lookup(
            &ctx->stack_cache,
            ctx->fresh[slot].workload_signature36,
            ctx->fresh[slot].semantic_result_signature64,
            ctx->fresh[slot].selected_vector_key216,
            &selected,
            &cache_receipt) == HHS_EXACT_STATUS_OK);
    SAT_V3_REQUIRE(cache_receipt.cache_hit == 1U);
    SAT_V3_REQUIRE(cache_receipt.exact_replayable == 1U);
    SAT_V3_REQUIRE(cache_receipt.stale_signature_rejected == 1U);
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
            &selected,
            &ctx->fresh[slot]) == HHS_EXACT_STATUS_OK);
    ++stats->cache_hits;

    memset(&branch_receipt, 0, sizeof(branch_receipt));
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_branch_ref_resolve(
            &ctx->branch_cache,
            &ctx->stack_cache,
            ctx->root_branch_id[slot],
            &branch_selection,
            &branch_receipt) == HHS_EXACT_STATUS_OK);
    SAT_V3_REQUIRE(branch_selection != NULL);
    SAT_V3_REQUIRE(branch_receipt.exact_replayable == 1U);
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
            branch_selection,
            &ctx->fresh[slot]) == HHS_EXACT_STATUS_OK);
    ++stats->branch_resolves;

    memset(&composition_receipt, 0, sizeof(composition_receipt));
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_branch_ref_composition_receipt(
            &ctx->branch_cache,
            &ctx->stack_cache,
            ctx->root_branch_id[slot],
            ctx->memo_target_lane[slot],
            &composition_receipt) == HHS_EXACT_STATUS_OK);
    SAT_V3_REQUIRE(composition_receipt.memoized == 1U);
    SAT_V3_REQUIRE(composition_receipt.exact_replayable == 1U);
    ++stats->memoized_compositions;

    occurrence = &ctx->binding.occurrences[ctx->occurrence_index[slot]];
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_hash216_m_exponent_validate(
            occurrence,
            &ctx->m_witness[slot]) == HHS_EXACT_STATUS_OK);
    ++stats->m_validations;
}

static void a_v3_cold_operation(
    AV3Context *ctx,
    const uint8_t record[SAT_V3_RECORD_BYTES],
    uint64_t ordinal,
    uint8_t out[SAT_V3_RECORD_BYTES],
    AV3Stats *stats
) {
    uint32_t slot = (uint32_t)(ordinal % A_V3_PHASES);
    HHSExactPass219H36StackSelectionV1 selected;
    HHSExactPass219H36Hash216MExponentWitnessV1 witness;
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *occurrence;

    a_v3_base_and_route(record, slot, out);
    ++stats->route_receipts;

    memset(&selected, 0, sizeof(selected));
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_stack_select(
            &ctx->h36[slot],
            &ctx->linux[slot],
            &selected) == HHS_EXACT_STATUS_OK);
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
            &selected,
            &ctx->fresh[slot]) == HHS_EXACT_STATUS_OK);
    ++stats->fresh_selections;

    occurrence = &ctx->binding.occurrences[ctx->occurrence_index[slot]];
    memset(&witness, 0, sizeof(witness));
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_hash216_m_exponent_bind(
            occurrence,
            &witness) == HHS_EXACT_STATUS_OK);
    ++stats->m_binds;
    SAT_V3_REQUIRE(
        hhs_exact_pass219_h36_hash216_m_exponent_validate(
            occurrence,
            &witness) == HHS_EXACT_STATUS_OK);
    ++stats->m_validations;
}

static void a_v3_preflight(
    AV3Context *ctx,
    const SatV3Workset *workset
) {
    uint32_t slot;
    for (slot = 0U; slot < A_V3_PHASES; ++slot) {
        HHSExactPass219H36StackSelectionV1 cached;
        HHSExactPass219H36StackCacheReceiptV1 cache_receipt;
        const HHSExactPass219H36StackSelectionV1 *branch_selection = NULL;
        HHSExactPass219H36BranchReceiptV1 branch_receipt;
        HHSExactPass219H36CompositionReceiptMemoV1 composition_receipt;
        const uint8_t *record = sat_v3_record(workset, slot);
        uint8_t out[SAT_V3_RECORD_BYTES];
        AV3Stats cold_stats;
        AV3Stats warm_stats;

        memset(&cached, 0, sizeof(cached));
        memset(&cache_receipt, 0, sizeof(cache_receipt));
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_stack_cache_lookup(
                &ctx->stack_cache,
                ctx->fresh[slot].workload_signature36,
                ctx->fresh[slot].semantic_result_signature64,
                ctx->fresh[slot].selected_vector_key216,
                &cached,
                &cache_receipt) == HHS_EXACT_STATUS_OK);
        SAT_V3_REQUIRE(cache_receipt.cache_hit == 1U);
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
                &cached,
                &ctx->fresh[slot]) == HHS_EXACT_STATUS_OK);

        memset(&branch_receipt, 0, sizeof(branch_receipt));
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_branch_ref_resolve(
                &ctx->branch_cache,
                &ctx->stack_cache,
                ctx->root_branch_id[slot],
                &branch_selection,
                &branch_receipt) == HHS_EXACT_STATUS_OK);
        SAT_V3_REQUIRE(branch_selection != NULL);
        SAT_V3_REQUIRE(branch_receipt.exact_replayable == 1U);

        memset(&composition_receipt, 0, sizeof(composition_receipt));
        SAT_V3_REQUIRE(
            hhs_exact_pass219_h36_branch_ref_composition_receipt(
                &ctx->branch_cache,
                &ctx->stack_cache,
                ctx->root_branch_id[slot],
                ctx->memo_target_lane[slot],
                &composition_receipt) == HHS_EXACT_STATUS_OK);
        SAT_V3_REQUIRE(composition_receipt.memoized == 1U);

        memset(&cold_stats, 0, sizeof(cold_stats));
        memset(&warm_stats, 0, sizeof(warm_stats));
        a_v3_cold_operation(ctx, record, slot, out, &cold_stats);
        a_v3_warm_operation(ctx, record, slot, out, &warm_stats);
        SAT_V3_REQUIRE(cold_stats.route_receipts == 1U);
        SAT_V3_REQUIRE(warm_stats.route_receipts == 1U);
        SAT_V3_REQUIRE(cold_stats.fresh_selections == 1U);
        SAT_V3_REQUIRE(warm_stats.cache_hits == 1U);
        SAT_V3_REQUIRE(warm_stats.branch_resolves == 1U);
        SAT_V3_REQUIRE(warm_stats.memoized_compositions == 1U);
    }
}

static void a_v3_run_loop(
    const SatV3Args *args,
    const SatV3Workset *workset,
    AV3Context *ctx,
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
                a_v3_warm_operation(ctx, record, ordinal, out, stats);
            else
                a_v3_cold_operation(ctx, record, ordinal, out, stats);
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
    fprintf(stderr, "full HHS saturation v3 requires Linux x86_64\n");
    return 2;
#else
    const char *mode = getenv("HHS_SAT_V3_A_MODE");
    int warm = 1;
    SatV3Args args = sat_v3_parse_args(argc, argv);
    SatV3Workset workset = sat_v3_workset_init();
    AV3Context *ctx = (AV3Context *)calloc(1U, sizeof(*ctx));
    SatV3LoopResult result;
    AV3Stats stats;
    char extra[1024];

    SAT_V3_REQUIRE(ctx != NULL);
    if (mode != NULL && strcmp(mode, "cold") == 0)
        warm = 0;
    else if (mode != NULL)
        SAT_V3_REQUIRE(strcmp(mode, "warm") == 0);

    a_v3_context_init(ctx);
    a_v3_preflight(ctx, &workset);
    a_v3_run_loop(&args, &workset, ctx, warm, &result, &stats);

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
    }

    snprintf(
        extra,
        sizeof(extra),
        "\"aggregate_abi_linked\":true,\"pass219_features_linked\":true,"
        "\"lane5_route_called\":true,\"mode\":\"%s\","
        "\"warm_fill_ns\":%" PRIu64 ",\"stack_cache_entries\":%u,"
        "\"branch_cache_entries\":%u,\"memo_threshold\":%u,"
        "\"route_receipts\":%" PRIu64 ",\"fresh_selections\":%" PRIu64 ","
        "\"cache_hits\":%" PRIu64 ",\"branch_resolves\":%" PRIu64 ","
        "\"memoized_compositions\":%" PRIu64 ",\"m_binds\":%" PRIu64 ","
        "\"m_validations\":%" PRIu64 ",\"warm_cache_proved\":%s,"
        "\"canonical_mutation_authority\":false,"
        "\"canonical_hash216_authority\":false",
        warm ? "warm" : "cold",
        ctx->warm_fill_ns,
        ctx->stack_cache.entry_count,
        ctx->branch_cache.entry_count,
        ctx->memo_threshold,
        stats.route_receipts,
        stats.fresh_selections,
        stats.cache_hits,
        stats.branch_resolves,
        stats.memoized_compositions,
        stats.m_binds,
        stats.m_validations,
        warm ? "true" : "false");

    sat_v3_print_common_json(
        warm ? "A_warm" : "A_cold",
        warm
            ? "aggregate_abi_lane5_h36_hash216_warm_reference_stack"
            : "aggregate_abi_lane5_h36_hash216_cold_recompute_stack",
        &args,
        &workset,
        &result,
        extra);

    free(ctx);
    sat_v3_workset_free(&workset);
    return 0;
#endif
}
