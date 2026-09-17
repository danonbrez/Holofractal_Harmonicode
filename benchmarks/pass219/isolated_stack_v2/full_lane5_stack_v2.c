#define _POSIX_C_SOURCE 200809L
#include "hhs_runtime_exact_abi.h"
#include "native_bench_common_v2.h"

static HHSExactBigUIntView bview8(const uint8_t bytes[8]) {
    HHSExactBigUIntView view;
    view.struct_size = (uint32_t)sizeof(view);
    view.byte_length = 8U;
    view.bytes_be = bytes;
    return view;
}

static void init_hash216_binding(HHSExactPass219H36Hash216TransitionBindingV1 *binding) {
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

    BENCH_REQUIRE(hhs_exact_pass219_hash216_transition_init(
        previous, change, receipt, identity, &transition) == HHS_EXACT_STATUS_OK);
    BENCH_REQUIRE(hhs_exact_pass219_h36_hash216_transition_bind(
        &transition, binding) == HHS_EXACT_STATUS_OK);
}

static void build_route_from_record(
    const uint8_t record[BENCH_RECORD_BYTES],
    uint64_t record_ordinal,
    uint32_t phase_slot,
    uint32_t inverse_phase_slot,
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
    route->previous_address = bview8(previous);
    route->current_address = bview8(current);
    route->goal_address = bview8(goal);
    route->candidate_address = bview8(goal);
    memcpy(route->workload_sha256, record + 32U, 32U);
    memcpy(route->provenance_sha256, record + 64U, 32U);
    memcpy(route->forbidden_boundary_sha256, record + 96U, 32U);
    memcpy(route->reciprocal_witness_sha256, record + 128U, 32U);
    memcpy(route->route_witness_sha256, record + 160U, 32U);
    route->workload_byte_count = BENCH_RECORD_BYTES;
    route->evidence_count = 5U;
    route->contradiction_check_count = 1U;
    route->integer_route_cost = UINT64_C(7) + (record_ordinal & UINT64_C(3));
    route->materialized_intermediate_states = 0U;
    route->phase_slot = phase_slot;
    route->inverse_phase_slot = inverse_phase_slot;
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

static uint64_t process_segment(
    const BenchDataset *ds,
    uint64_t offset_records,
    uint64_t count,
    uint32_t phase_slot,
    uint32_t inverse_phase_slot,
    const HHSExactPass219H36Hash216TransitionBindingV1 *binding
) {
    uint64_t digest = BENCH_FNV_OFFSET;
    uint64_t i;

    for (i = 0U; i < count; ++i) {
        const uint64_t ordinal = offset_records + i;
        const uint8_t *record = ds->bytes + (size_t)ordinal * BENCH_RECORD_BYTES;
        HHSExactVM81Frame frame;
        uint8_t out[BENCH_RECORD_BYTES];
        size_t out_length = 0U;
        HHSExactPass219Lane5UnboundedWorkloadRouteV1 route;
        HHSExactPass219Lane5UnboundedWorkloadReceiptV1 route_receipt;
        HHSExactPass219H36Hash216MExponentWitnessV1 witness;
        const HHSExactPass219H36Hash216OccurrenceBindingV1 *occurrence;
        uint8_t previous[8], current[8], goal[8];
        uint32_t occurrence_index;

        BENCH_REQUIRE(hhs_exact_vm81_frame_import_le(record, BENCH_RECORD_BYTES, &frame) == HHS_EXACT_STATUS_OK);
        BENCH_REQUIRE(hhs_exact_vm81_frame_export_le(&frame, out, sizeof(out), &out_length) == HHS_EXACT_STATUS_OK);
        BENCH_REQUIRE(out_length == BENCH_RECORD_BYTES);
        BENCH_REQUIRE(memcmp(record, out, BENCH_RECORD_BYTES) == 0);

        build_route_from_record(
            record, ordinal, phase_slot, inverse_phase_slot,
            &route, previous, current, goal);
        memset(&route_receipt, 0, sizeof(route_receipt));
        BENCH_REQUIRE(hhs_exact_pass219_lane5_unbounded_workload_route_validate(
            &route, &route_receipt) == HHS_EXACT_STATUS_OK);
        BENCH_REQUIRE(route_receipt.accepted == 1U);
        BENCH_REQUIRE(route_receipt.candidate_only == 1U);
        BENCH_REQUIRE(route_receipt.canonical_mutation_authority == 0U);
        BENCH_REQUIRE(route_receipt.canonical_hash72_authority == 0U);
        BENCH_REQUIRE(route_receipt.canonical_hash216_authority == 0U);
        BENCH_REQUIRE(route_receipt.canonical_persistence_authority == 0U);
        BENCH_REQUIRE(route_receipt.requires_signed_environmental_vm81_admission == 1U);

        occurrence_index = (uint32_t)((ordinal + (uint64_t)phase_slot * 3U) %
                                      HHS_EXACT_PASS219_HASH216_OCCURRENCES);
        occurrence = &binding->occurrences[occurrence_index];
        memset(&witness, 0, sizeof(witness));
        BENCH_REQUIRE(hhs_exact_pass219_h36_hash216_m_exponent_bind(
            occurrence, &witness) == HHS_EXACT_STATUS_OK);
        BENCH_REQUIRE(hhs_exact_pass219_h36_hash216_m_exponent_validate(
            occurrence, &witness) == HHS_EXACT_STATUS_OK);
        BENCH_REQUIRE(witness.direct_shared_m_binding == 1U);
        BENCH_REQUIRE(witness.translator_required == 0U);
        BENCH_REQUIRE(witness.manifold_m.exp2 == 216U && witness.manifold_m.exp3 == 144U);
        BENCH_REQUIRE(witness.canonical_mutation_authority == 0U);
        BENCH_REQUIRE(witness.canonical_hash72_authority == 0U);
        BENCH_REQUIRE(witness.canonical_hash216_authority == 0U);
        BENCH_REQUIRE(witness.canonical_persistence_authority == 0U);
        BENCH_REQUIRE(witness.floating_point_authority == 0U);

        digest = bench_fnv1a_update(digest, out, BENCH_RECORD_BYTES);
    }
    return digest;
}

int main(int argc, char **argv) {
    BenchDataset ds;
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 authority;
    HHSExactPass219H36Hash216TransitionBindingV1 binding;
    uint64_t offset_records;
    uint64_t count;
    uint32_t phase_slot;
    uint32_t inverse_phase_slot;
    uint64_t input_digest;
    uint64_t output_digest;
    uint64_t warmup;
    uint64_t started;
    uint64_t elapsed;
    volatile uint64_t warmup_sink = 0U;

    BENCH_REQUIRE(argc == 6);
    offset_records = bench_parse_u64(argv[2]);
    count = bench_parse_u64(argv[3]);
    phase_slot = (uint32_t)bench_parse_u64(argv[4]);
    inverse_phase_slot = (uint32_t)bench_parse_u64(argv[5]);
    BENCH_REQUIRE(phase_slot < 72U && inverse_phase_slot < 72U);

    ds = bench_load_dataset(argv[1]);
    BENCH_REQUIRE(offset_records <= ds.record_count);
    BENCH_REQUIRE(count > 0U && count <= ds.record_count - offset_records);

    memset(&authority, 0, sizeof(authority));
    BENCH_REQUIRE(hhs_exact_pass219_lane5_unbounded_workload_scaling_authority(&authority) == HHS_EXACT_STATUS_OK);
    BENCH_REQUIRE(authority.candidate_only == 1U);
    BENCH_REQUIRE(authority.canonical_vm81_mutation_authority == 0U);
    BENCH_REQUIRE(authority.canonical_hash72_authority == 0U);
    BENCH_REQUIRE(authority.canonical_hash216_authority == 0U);
    BENCH_REQUIRE(authority.canonical_persistence_authority == 0U);
    BENCH_REQUIRE(authority.requires_signed_environmental_vm81_admission == 1U);
    BENCH_REQUIRE(authority.floating_point_canonical_authority == 0U);

    memset(&binding, 0, sizeof(binding));
    init_hash216_binding(&binding);

    input_digest = bench_segment_input_digest(&ds, offset_records, count);
    warmup = bench_warmup_count(count);
    warmup_sink ^= process_segment(
        &ds, offset_records, warmup, phase_slot, inverse_phase_slot, &binding);

    started = bench_monotonic_ns();
    output_digest = process_segment(
        &ds, offset_records, count, phase_slot, inverse_phase_slot, &binding);
    elapsed = bench_monotonic_ns() - started;

    BENCH_REQUIRE(output_digest == input_digest);
    BENCH_REQUIRE(warmup_sink != UINT64_C(0xffffffffffffffff));

    printf(
        "{\"schema\":\"HHS_PASS219_ISOLATED_STACK_BENCHMARK_V2\","
        "\"arm\":\"A\",\"implementation\":\"aggregate_abi_plus_lane5_plus_h36_hash216_m\","
        "\"offset_records\":%" PRIu64 ",\"completed\":%" PRIu64 ","
        "\"elapsed_ns\":%" PRIu64 ",\"input_digest\":%" PRIu64 ","
        "\"payload_digest\":%" PRIu64 ",\"phase_slot\":%u,"
        "\"inverse_phase_slot\":%u,\"aggregate_abi_linked\":true,"
        "\"pass219_features_linked\":true,\"lane5_called\":true,"
        "\"h36_hash216_m_called\":true,\"candidate_only\":true,"
        "\"canonical_mutation_authority\":false}\n",
        offset_records, count, elapsed, input_digest, output_digest,
        phase_slot, inverse_phase_slot);

    bench_free_dataset(&ds);
    return 0;
}
