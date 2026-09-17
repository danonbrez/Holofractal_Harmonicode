#define _POSIX_C_SOURCE 200809L
#include "hhs_runtime_exact_abi.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define REQUIRE(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "REQUIRE failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        exit(EXIT_FAILURE); \
    } \
} while (0)

typedef struct PhaseSpec {
    const char *name;
    uint32_t phase_slot;
    uint32_t inverse_phase_slot;
    uint32_t occurrence_offset;
} PhaseSpec;

typedef struct ArmResult {
    uint64_t elapsed_ns;
    uint64_t completed;
    uint64_t route_digest;
    uint64_t proof_digest;
    uint64_t route_receipts;
    uint64_t m_witnesses;
    uint8_t dataset_complete;
} ArmResult;

static const PhaseSpec PHASES[4] = {
    {"xy", 0U, 36U, 0U},
    {"yx", 36U, 0U, 54U},
    {"zw", 18U, 54U, 108U},
    {"wz", 54U, 18U, 162U}
};

static const uint64_t DEFAULT_GLOBAL_BUDGET_NS = UINT64_C(1200000000);
static const uint64_t DEFAULT_LEG_BUDGET_NS = UINT64_C(15000000);
static const uint64_t TIMER_TOLERANCE_NS = UINT64_C(150000000);
static const uint64_t DEFAULT_BASE_ITERATIONS = UINT64_C(8);
static const uint32_t DIFFICULTY_RANKS = 9U;
static const uint32_t LOGICAL_TENSOR_ENERGY_UNITS = 225U;
static const uint32_t LOGICAL_RECIPROCAL_PAIR_ENERGY_UNITS = 450U;

static uint64_t monotonic_ns(void) {
    struct timespec ts;
    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &ts) == 0);
    return (uint64_t)ts.tv_sec * UINT64_C(1000000000) + (uint64_t)ts.tv_nsec;
}

static uint64_t mix64(uint64_t x) {
    x += UINT64_C(0x9e3779b97f4a7c15);
    x = (x ^ (x >> 30U)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27U)) * UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31U);
}

static uint64_t env_u64(const char *name, uint64_t fallback) {
    const char *s = getenv(name);
    char *end = NULL;
    unsigned long long v;
    if (s == NULL || *s == '\0') return fallback;
    v = strtoull(s, &end, 10);
    if (end == s || *end != '\0' || v == 0ULL) return fallback;
    return (uint64_t)v;
}

static uint32_t encode_u64(uint64_t value, uint8_t out[8]) {
    uint32_t i;
    uint32_t first = 0U;
    if (value == 0U) {
        out[0] = 0U;
        return 1U;
    }
    for (i = 0U; i < 8U; ++i)
        out[7U - i] = (uint8_t)(value >> (8U * i));
    while (first < 7U && out[first] == 0U) ++first;
    if (first != 0U) memmove(out, out + first, 8U - first);
    return 8U - first;
}

static HHSExactBigUIntView bview(const uint8_t *bytes, uint32_t length) {
    HHSExactBigUIntView view;
    view.struct_size = (uint32_t)sizeof(view);
    view.byte_length = length;
    view.bytes_be = bytes;
    return view;
}

static void fill_digest(uint8_t out[32], uint64_t seed) {
    uint64_t x = seed ^ UINT64_C(0x243f6a8885a308d3);
    uint32_t i;
    for (i = 0U; i < 32U; ++i) {
        x ^= x >> 12U;
        x ^= x << 25U;
        x ^= x >> 27U;
        x *= UINT64_C(2685821657736338717);
        out[i] = (uint8_t)(x >> 56U);
    }
}

static uint64_t fold64(uint64_t state, uint64_t value) {
    return mix64(state ^ mix64(value));
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

    REQUIRE(hhs_exact_pass219_hash216_transition_init(
        previous, change, receipt, identity, &transition) == HHS_EXACT_STATUS_OK);
    REQUIRE(hhs_exact_pass219_h36_hash216_transition_bind(
        &transition, binding) == HHS_EXACT_STATUS_OK);
}

static HHSExactStatus build_route(
    const PhaseSpec *phase,
    uint64_t iteration,
    HHSExactPass219Lane5UnboundedWorkloadRouteV1 *route,
    uint8_t previous_bytes[8],
    uint8_t current_bytes[8],
    uint8_t goal_bytes[8]
) {
    uint64_t previous = mix64(UINT64_C(0x10000000) ^ iteration ^ phase->phase_slot);
    uint64_t current = mix64(UINT64_C(0x20000000) ^ iteration ^ phase->inverse_phase_slot);
    uint64_t goal = mix64(previous ^ current ^ UINT64_C(0x30000000));
    uint32_t previous_length = encode_u64(previous, previous_bytes);
    uint32_t current_length = encode_u64(current, current_bytes);
    uint32_t goal_length = encode_u64(goal, goal_bytes);

    memset(route, 0, sizeof(*route));
    route->struct_size = (uint32_t)sizeof(*route);
    route->version = HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION;
    route->previous_address = bview(previous_bytes, previous_length);
    route->current_address = bview(current_bytes, current_length);
    route->goal_address = bview(goal_bytes, goal_length);
    route->candidate_address = bview(goal_bytes, goal_length);
    fill_digest(route->workload_sha256, iteration ^ goal ^ UINT64_C(0x41));
    fill_digest(route->provenance_sha256, previous ^ UINT64_C(0x42));
    fill_digest(route->forbidden_boundary_sha256, current ^ UINT64_C(0x43));
    fill_digest(route->reciprocal_witness_sha256, goal ^ phase->phase_slot ^ UINT64_C(0x44));
    fill_digest(route->route_witness_sha256, goal ^ phase->inverse_phase_slot ^ UINT64_C(0x45));
    route->workload_byte_count = UINT64_C(64) + (iteration & UINT64_C(63));
    route->evidence_count = 5U;
    route->contradiction_check_count = 1U;
    route->integer_route_cost = UINT64_C(7);
    route->materialized_intermediate_states = 0U;
    route->phase_slot = phase->phase_slot;
    route->inverse_phase_slot = phase->inverse_phase_slot;
    route->trinary_collapse = (int8_t)((int)(iteration % 3U) - 1);
    route->binary_collapse = (uint8_t)(iteration & UINT64_C(1));
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
    return HHS_EXACT_STATUS_OK;
}

static ArmResult run_arm(
    const PhaseSpec *phase,
    uint64_t target_iterations,
    uint64_t budget_ns,
    uint8_t full_stack,
    const HHSExactPass219H36Hash216TransitionBindingV1 *binding
) {
    ArmResult result;
    uint64_t started = monotonic_ns();
    uint64_t i;
    memset(&result, 0, sizeof(result));

    for (i = 0U; i < target_iterations; ++i) {
        HHSExactPass219Lane5UnboundedWorkloadRouteV1 route;
        HHSExactPass219Lane5UnboundedWorkloadReceiptV1 receipt;
        HHSExactPass219H36Hash216MExponentWitnessV1 witness;
        uint8_t previous_bytes[8], current_bytes[8], goal_bytes[8];
        uint32_t occurrence_index;

        if (monotonic_ns() - started >= budget_ns) break;
        REQUIRE(build_route(phase, i, &route, previous_bytes, current_bytes, goal_bytes) == HHS_EXACT_STATUS_OK);
        memset(&receipt, 0, sizeof(receipt));
        REQUIRE(hhs_exact_pass219_lane5_unbounded_workload_route_validate(
            &route, &receipt) == HHS_EXACT_STATUS_OK);
        REQUIRE(receipt.accepted == 1U);
        REQUIRE(receipt.phase_slot == phase->phase_slot);
        REQUIRE(receipt.inverse_phase_slot == phase->inverse_phase_slot);
        REQUIRE(receipt.materialized_intermediate_states == 0U);
        REQUIRE(receipt.candidate_only == 1U);
        REQUIRE(receipt.canonical_mutation_authority == 0U);
        REQUIRE(receipt.canonical_hash72_authority == 0U);
        REQUIRE(receipt.canonical_hash216_authority == 0U);
        REQUIRE(receipt.canonical_persistence_authority == 0U);
        REQUIRE(receipt.requires_signed_environmental_vm81_admission == 1U);

        result.route_digest = fold64(
            result.route_digest,
            receipt.route_receipt_signature64 ^ ((uint64_t)phase->phase_slot << 32U) ^ i);
        ++result.route_receipts;

        if (full_stack != 0U) {
            const HHSExactPass219H36Hash216OccurrenceBindingV1 *occurrence;
            occurrence_index = (phase->occurrence_offset + (uint32_t)(i % 54U)) %
                               HHS_EXACT_PASS219_HASH216_OCCURRENCES;
            occurrence = &binding->occurrences[occurrence_index];
            memset(&witness, 0, sizeof(witness));
            REQUIRE(hhs_exact_pass219_h36_hash216_m_exponent_bind(
                occurrence, &witness) == HHS_EXACT_STATUS_OK);
            REQUIRE(hhs_exact_pass219_h36_hash216_m_exponent_validate(
                occurrence, &witness) == HHS_EXACT_STATUS_OK);
            REQUIRE(witness.same_linear5184_identity == 1U);
            REQUIRE(witness.direct_shared_m_binding == 1U);
            REQUIRE(witness.translator_required == 0U);
            REQUIRE(witness.manifold_m.exp2 == 216U && witness.manifold_m.exp3 == 144U);
            REQUIRE(witness.canonical_mutation_authority == 0U);
            REQUIRE(witness.canonical_hash72_authority == 0U);
            REQUIRE(witness.canonical_hash216_authority == 0U);
            REQUIRE(witness.canonical_persistence_authority == 0U);
            REQUIRE(witness.floating_point_authority == 0U);
            result.proof_digest = fold64(
                result.proof_digest,
                (uint64_t)witness.native_hash72_linear5184 ^
                ((uint64_t)witness.manifold_m.exp2 << 16U) ^
                (uint64_t)witness.manifold_m.exp3 ^ i);
            ++result.m_witnesses;
        }
        ++result.completed;
    }

    result.elapsed_ns = monotonic_ns() - started;
    result.dataset_complete = result.completed == target_iterations ? 1U : 0U;
    return result;
}

static void run_negative_controls(
    const HHSExactPass219H36Hash216TransitionBindingV1 *binding
) {
    HHSExactPass219Lane5UnboundedWorkloadRouteV1 route;
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 receipt;
    HHSExactPass219H36Hash216MExponentWitnessV1 witness;
    HHSExactPass219H36Hash216OccurrenceBindingV1 occurrence;
    uint8_t previous_bytes[8], current_bytes[8], goal_bytes[8];

    REQUIRE(build_route(&PHASES[0], 0U, &route, previous_bytes, current_bytes, goal_bytes) == HHS_EXACT_STATUS_OK);
    route.inverse_phase_slot = 18U;
    memset(&receipt, 0, sizeof(receipt));
    REQUIRE(hhs_exact_pass219_lane5_unbounded_workload_route_validate(
        &route, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    occurrence = binding->occurrences[0];
    REQUIRE(hhs_exact_pass219_h36_hash216_m_exponent_bind(
        &occurrence, &witness) == HHS_EXACT_STATUS_OK);
    witness.translator_required = 1U;
    REQUIRE(hhs_exact_pass219_h36_hash216_m_exponent_validate(
        &occurrence, &witness) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    REQUIRE(hhs_exact_pass219_h36_hash216_m_exponent_bind(
        &occurrence, &witness) == HHS_EXACT_STATUS_OK);
    witness.manifold_m.exp2 = 215U;
    REQUIRE(hhs_exact_pass219_h36_hash216_m_exponent_validate(
        &occurrence, &witness) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

static void print_arm(
    uint32_t rank,
    int32_t gradient_numerator,
    const PhaseSpec *phase,
    const char *arm,
    const ArmResult *result,
    uint64_t target_iterations,
    uint64_t leg_budget_ns
) {
    uint64_t rate_floor = result->completed == 0U || result->elapsed_ns == 0U
        ? 0U
        : (result->completed * UINT64_C(1000000000)) / result->elapsed_ns;
    printf(
        "{\"type\":\"arm\",\"schema\":\"HHS_PASS219_FOUR_PHASE_AB_GRADIENT_CALIBRATION_V1\","
        "\"difficulty_rank\":%u,\"gradient\":{\"numerator\":%d,\"denominator\":4},"
        "\"phase\":\"%s\",\"phase_slot\":%u,\"inverse_phase_slot\":%u,"
        "\"arm\":\"%s\",\"target_iterations\":%" PRIu64 ",\"leg_budget_ns\":%" PRIu64 ","
        "\"elapsed_ns\":%" PRIu64 ",\"completed\":%" PRIu64 ",\"rate_per_second_floor\":%" PRIu64 ","
        "\"dataset_complete\":%s,\"route_receipts\":%" PRIu64 ",\"m_witnesses\":%" PRIu64 ","
        "\"route_digest\":%" PRIu64 ",\"proof_digest\":%" PRIu64 ","
        "\"logical_tensor_energy_units\":%u,\"logical_reciprocal_pair_energy_units\":%u,"
        "\"physical_energy_measured\":false}\n",
        rank, gradient_numerator, phase->name, phase->phase_slot, phase->inverse_phase_slot,
        arm, target_iterations, leg_budget_ns, result->elapsed_ns, result->completed, rate_floor,
        result->dataset_complete ? "true" : "false", result->route_receipts, result->m_witnesses,
        result->route_digest, result->proof_digest,
        LOGICAL_TENSOR_ENERGY_UNITS, LOGICAL_RECIPROCAL_PAIR_ENERGY_UNITS);
}

int main(void) {
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 authority;
    HHSExactPass219H36Hash216TransitionBindingV1 binding;
    uint64_t global_budget_ns = env_u64("HHS_FOUR_PHASE_AB_GLOBAL_BUDGET_NS", DEFAULT_GLOBAL_BUDGET_NS);
    uint64_t leg_budget_ns = env_u64("HHS_FOUR_PHASE_AB_LEG_BUDGET_NS", DEFAULT_LEG_BUDGET_NS);
    uint64_t base_iterations = env_u64("HHS_FOUR_PHASE_AB_BASE_ITERATIONS", DEFAULT_BASE_ITERATIONS);
    uint64_t batch_started;
    uint64_t sample_count = 0U;
    uint32_t rank;

    memset(&authority, 0, sizeof(authority));
    REQUIRE(hhs_exact_pass219_lane5_unbounded_workload_scaling_authority(&authority) == HHS_EXACT_STATUS_OK);
    REQUIRE(authority.full_manifold_bigint_addressing == 1U);
    REQUIRE(authority.exact_reciprocal_phase_inversion == 1U);
    REQUIRE(authority.constant_memory_candidate_reduction == 1U);
    REQUIRE(authority.intermediate_materialization_required == 0U);
    REQUIRE(authority.candidate_only == 1U);
    REQUIRE(authority.canonical_vm81_mutation_authority == 0U);
    REQUIRE(authority.canonical_hash72_authority == 0U);
    REQUIRE(authority.canonical_hash216_authority == 0U);
    REQUIRE(authority.canonical_persistence_authority == 0U);
    REQUIRE(authority.requires_signed_environmental_vm81_admission == 1U);
    REQUIRE(authority.floating_point_canonical_authority == 0U);

    memset(&binding, 0, sizeof(binding));
    init_hash216_binding(&binding);
    run_negative_controls(&binding);

    printf(
        "{\"type\":\"meta\",\"schema\":\"HHS_PASS219_FOUR_PHASE_AB_GRADIENT_CALIBRATION_V1\","
        "\"global_budget_ns\":%" PRIu64 ",\"leg_budget_ns\":%" PRIu64 ","
        "\"base_iterations\":%" PRIu64 ",\"difficulty_ranks\":%u,"
        "\"gradient_rule\":\"exact_percentile_gradient(rank,9)\","
        "\"gradient_denominator\":4,\"gradient_scale_factor\":2,"
        "\"phases\":[\"xy\",\"yx\",\"zw\",\"wz\"],"
        "\"arm_A\":\"lane5_route_plus_h36_hash216_m_binding\","
        "\"arm_B\":\"matched_lane5_route_only_control\","
        "\"logical_energy_contract\":\"PASS_067_1_LO_SHU_HARMONIC_PHASE_ENERGY_V1\","
        "\"logical_tensor_energy_units\":%u,\"logical_reciprocal_pair_energy_units\":%u,"
        "\"physical_energy_measured\":false,\"negative_controls_passed\":true}\n",
        global_budget_ns, leg_budget_ns, base_iterations, DIFFICULTY_RANKS,
        LOGICAL_TENSOR_ENERGY_UNITS, LOGICAL_RECIPROCAL_PAIR_ENERGY_UNITS);

    batch_started = monotonic_ns();
    for (rank = 1U; rank <= DIFFICULTY_RANKS; ++rank) {
        uint64_t target_iterations;
        uint32_t phase_index;
        int32_t gradient_numerator = (int32_t)rank - 5;

        if (rank > 1U && base_iterations > (UINT64_MAX >> (rank - 1U))) break;
        target_iterations = base_iterations << (rank - 1U);

        for (phase_index = 0U; phase_index < 4U; ++phase_index) {
            ArmResult a;
            ArmResult b;
            uint64_t elapsed = monotonic_ns() - batch_started;
            const PhaseSpec *phase = &PHASES[phase_index];

            if (elapsed + (2U * leg_budget_ns) > global_budget_ns) goto finished;

            if (((rank + phase_index) & 1U) == 0U) {
                a = run_arm(phase, target_iterations, leg_budget_ns, 1U, &binding);
                b = run_arm(phase, target_iterations, leg_budget_ns, 0U, &binding);
            } else {
                b = run_arm(phase, target_iterations, leg_budget_ns, 0U, &binding);
                a = run_arm(phase, target_iterations, leg_budget_ns, 1U, &binding);
            }

            REQUIRE(a.completed > 0U && b.completed > 0U);
            REQUIRE(a.route_receipts == a.completed && b.route_receipts == b.completed);
            REQUIRE(a.m_witnesses == a.completed && b.m_witnesses == 0U);
            if (a.completed == b.completed)
                REQUIRE(a.route_digest == b.route_digest);

            print_arm(rank, gradient_numerator, phase, "A", &a, target_iterations, leg_budget_ns);
            print_arm(rank, gradient_numerator, phase, "B", &b, target_iterations, leg_budget_ns);
            ++sample_count;
        }
    }

finished:
    {
        uint64_t batch_elapsed_ns = monotonic_ns() - batch_started;
        REQUIRE(batch_elapsed_ns <= global_budget_ns + TIMER_TOLERANCE_NS);
        printf(
            "{\"type\":\"result\",\"schema\":\"HHS_PASS219_FOUR_PHASE_AB_GRADIENT_CALIBRATION_V1\","
            "\"paired_phase_samples\":%" PRIu64 ",\"batch_elapsed_ns\":%" PRIu64 ","
            "\"global_budget_ns\":%" PRIu64 ",\"within_time_bound\":true,"
            "\"candidate_only\":true,\"canonical_vm81_mutation_authority\":false,"
            "\"canonical_hash72_authority\":false,\"canonical_hash216_authority\":false,"
            "\"canonical_persistence_authority\":false,"
            "\"requires_signed_environmental_vm81_admission\":true,"
            "\"translator_required\":false,\"result\":\"PASS\"}\n",
            sample_count, batch_elapsed_ns, global_budget_ns);
    }
    return 0;
}
