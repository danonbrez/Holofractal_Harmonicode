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

typedef struct DatasetRecord {
    uint64_t previous;
    uint64_t current;
    uint64_t goal;
    uint8_t workload_sha256[32];
    uint8_t provenance_sha256[32];
    uint8_t forbidden_boundary_sha256[32];
    uint8_t reciprocal_witness_sha256[32];
    uint8_t route_witness_sha256[32];
    uint64_t workload_byte_count;
    uint64_t integer_route_cost;
    uint32_t evidence_count;
    uint32_t contradiction_check_count;
    uint32_t phase_slot;
    uint32_t inverse_phase_slot;
    int8_t trinary_collapse;
    uint8_t binary_collapse;
    uint8_t nested_zero_slot;
    uint64_t identity64;
} DatasetRecord;

typedef struct ArmResult {
    uint64_t elapsed_ns;
    uint64_t completed;
    uint64_t dataset_digest;
    uint64_t route_digest;
    uint64_t proof_digest;
    uint64_t raw_digest;
    uint64_t route_receipts;
    uint64_t m_witnesses;
    uint64_t raw_validations;
    uint8_t dataset_complete;
} ArmResult;

enum ArmKind {
    ARM_FULL_LANE5 = 0,
    ARM_ROUTE_ONLY = 1,
    ARM_RAW_RUNNER = 2
};

static const PhaseSpec PHASES[4] = {
    {"xy", 0U, 36U, 0U},
    {"yx", 36U, 0U, 54U},
    {"zw", 18U, 54U, 108U},
    {"wz", 54U, 18U, 162U}
};

static const uint64_t DEFAULT_GLOBAL_BUDGET_NS = UINT64_C(1800000000);
static const uint64_t DEFAULT_LEG_BUDGET_NS = UINT64_C(15000000);
static const uint64_t TIMER_TOLERANCE_NS = UINT64_C(150000000);
static const uint64_t DEFAULT_BASE_ITERATIONS = UINT64_C(8);
static const uint64_t DEFAULT_WARMUP_ITERATIONS = UINT64_C(64);
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

static uint64_t fold64(uint64_t state, uint64_t value) {
    return mix64(state ^ mix64(value));
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

static uint64_t fold_bytes(uint64_t state, const uint8_t *bytes, uint32_t length) {
    uint32_t i;
    for (i = 0U; i < length; ++i)
        state = fold64(state, (uint64_t)bytes[i] ^ ((uint64_t)i << 8U));
    return state;
}

static uint64_t dataset_identity(const DatasetRecord *record) {
    uint64_t state = UINT64_C(0x6a09e667f3bcc909);
    state = fold64(state, record->previous);
    state = fold64(state, record->current);
    state = fold64(state, record->goal);
    state = fold_bytes(state, record->workload_sha256, 32U);
    state = fold_bytes(state, record->provenance_sha256, 32U);
    state = fold_bytes(state, record->forbidden_boundary_sha256, 32U);
    state = fold_bytes(state, record->reciprocal_witness_sha256, 32U);
    state = fold_bytes(state, record->route_witness_sha256, 32U);
    state = fold64(state, record->workload_byte_count);
    state = fold64(state, record->integer_route_cost);
    state = fold64(state, (uint64_t)record->evidence_count);
    state = fold64(state, (uint64_t)record->contradiction_check_count);
    state = fold64(state, ((uint64_t)record->phase_slot << 32U) | record->inverse_phase_slot);
    state = fold64(state, (uint64_t)(uint8_t)(record->trinary_collapse + 1));
    state = fold64(state, ((uint64_t)record->binary_collapse << 8U) | record->nested_zero_slot);
    return state;
}

static void make_dataset(const PhaseSpec *phase, uint64_t iteration, DatasetRecord *record) {
    memset(record, 0, sizeof(*record));
    record->previous = mix64(UINT64_C(0x10000000) ^ iteration ^ phase->phase_slot);
    record->current = mix64(UINT64_C(0x20000000) ^ iteration ^ phase->inverse_phase_slot);
    record->goal = mix64(record->previous ^ record->current ^ UINT64_C(0x30000000));
    fill_digest(record->workload_sha256, iteration ^ record->goal ^ UINT64_C(0x41));
    fill_digest(record->provenance_sha256, record->previous ^ UINT64_C(0x42));
    fill_digest(record->forbidden_boundary_sha256, record->current ^ UINT64_C(0x43));
    fill_digest(record->reciprocal_witness_sha256, record->goal ^ phase->phase_slot ^ UINT64_C(0x44));
    fill_digest(record->route_witness_sha256, record->goal ^ phase->inverse_phase_slot ^ UINT64_C(0x45));
    record->workload_byte_count = UINT64_C(64) + (iteration & UINT64_C(63));
    record->integer_route_cost = UINT64_C(7);
    record->evidence_count = 5U;
    record->contradiction_check_count = 1U;
    record->phase_slot = phase->phase_slot;
    record->inverse_phase_slot = phase->inverse_phase_slot;
    record->trinary_collapse = (int8_t)((int)(iteration % 3U) - 1);
    record->binary_collapse = (uint8_t)(iteration & UINT64_C(1));
    record->nested_zero_slot = record->binary_collapse == 0U ? 1U : 0U;
    record->identity64 = dataset_identity(record);
}

static uint8_t same_record(const DatasetRecord *left, const DatasetRecord *right) {
    return (uint8_t)(
        left->previous == right->previous &&
        left->current == right->current &&
        left->goal == right->goal &&
        memcmp(left->workload_sha256, right->workload_sha256, 32U) == 0 &&
        memcmp(left->provenance_sha256, right->provenance_sha256, 32U) == 0 &&
        memcmp(left->forbidden_boundary_sha256, right->forbidden_boundary_sha256, 32U) == 0 &&
        memcmp(left->reciprocal_witness_sha256, right->reciprocal_witness_sha256, 32U) == 0 &&
        memcmp(left->route_witness_sha256, right->route_witness_sha256, 32U) == 0 &&
        left->workload_byte_count == right->workload_byte_count &&
        left->integer_route_cost == right->integer_route_cost &&
        left->evidence_count == right->evidence_count &&
        left->contradiction_check_count == right->contradiction_check_count &&
        left->phase_slot == right->phase_slot &&
        left->inverse_phase_slot == right->inverse_phase_slot &&
        left->trinary_collapse == right->trinary_collapse &&
        left->binary_collapse == right->binary_collapse &&
        left->nested_zero_slot == right->nested_zero_slot &&
        left->identity64 == right->identity64);
}

static uint8_t raw_validate_record(
    const PhaseSpec *phase,
    uint64_t iteration,
    const DatasetRecord *record,
    uint64_t *out_validation_digest
) {
    DatasetRecord expected;
    make_dataset(phase, iteration, &expected);
    if (!same_record(record, &expected)) return 0U;
    if (record->phase_slot != phase->phase_slot ||
        record->inverse_phase_slot != phase->inverse_phase_slot) return 0U;
    if (record->evidence_count != 5U || record->contradiction_check_count != 1U) return 0U;
    if (record->integer_route_cost != UINT64_C(7)) return 0U;
    if (record->binary_collapse > 1U) return 0U;
    if (record->nested_zero_slot != (record->binary_collapse == 0U ? 1U : 0U)) return 0U;
    *out_validation_digest = fold64(record->identity64, expected.identity64 ^ iteration);
    return 1U;
}

static void build_route_from_dataset(
    const DatasetRecord *record,
    HHSExactPass219Lane5UnboundedWorkloadRouteV1 *route,
    uint8_t previous_bytes[8],
    uint8_t current_bytes[8],
    uint8_t goal_bytes[8]
) {
    uint32_t previous_length = encode_u64(record->previous, previous_bytes);
    uint32_t current_length = encode_u64(record->current, current_bytes);
    uint32_t goal_length = encode_u64(record->goal, goal_bytes);

    memset(route, 0, sizeof(*route));
    route->struct_size = (uint32_t)sizeof(*route);
    route->version = HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION;
    route->previous_address = bview(previous_bytes, previous_length);
    route->current_address = bview(current_bytes, current_length);
    route->goal_address = bview(goal_bytes, goal_length);
    route->candidate_address = bview(goal_bytes, goal_length);
    memcpy(route->workload_sha256, record->workload_sha256, 32U);
    memcpy(route->provenance_sha256, record->provenance_sha256, 32U);
    memcpy(route->forbidden_boundary_sha256, record->forbidden_boundary_sha256, 32U);
    memcpy(route->reciprocal_witness_sha256, record->reciprocal_witness_sha256, 32U);
    memcpy(route->route_witness_sha256, record->route_witness_sha256, 32U);
    route->workload_byte_count = record->workload_byte_count;
    route->integer_route_cost = record->integer_route_cost;
    route->evidence_count = record->evidence_count;
    route->contradiction_check_count = record->contradiction_check_count;
    route->materialized_intermediate_states = 0U;
    route->phase_slot = record->phase_slot;
    route->inverse_phase_slot = record->inverse_phase_slot;
    route->trinary_collapse = record->trinary_collapse;
    route->binary_collapse = record->binary_collapse;
    route->nested_zero_slot = record->nested_zero_slot;
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

static ArmResult run_arm(
    const PhaseSpec *phase,
    uint64_t target_iterations,
    uint64_t budget_ns,
    enum ArmKind kind,
    const HHSExactPass219H36Hash216TransitionBindingV1 *binding
) {
    ArmResult result;
    uint64_t started = monotonic_ns();
    uint64_t i;
    memset(&result, 0, sizeof(result));

    for (i = 0U; i < target_iterations; ++i) {
        DatasetRecord record;
        if (monotonic_ns() - started >= budget_ns) break;
        make_dataset(phase, i, &record);
        result.dataset_digest = fold64(result.dataset_digest, record.identity64 ^ i);

        if (kind == ARM_RAW_RUNNER) {
            uint64_t validation_digest = 0U;
            REQUIRE(raw_validate_record(phase, i, &record, &validation_digest) == 1U);
            result.raw_digest = fold64(result.raw_digest, validation_digest);
            ++result.raw_validations;
        } else {
            HHSExactPass219Lane5UnboundedWorkloadRouteV1 route;
            HHSExactPass219Lane5UnboundedWorkloadReceiptV1 receipt;
            uint8_t previous_bytes[8], current_bytes[8], goal_bytes[8];
            build_route_from_dataset(&record, &route, previous_bytes, current_bytes, goal_bytes);
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

            if (kind == ARM_FULL_LANE5) {
                const HHSExactPass219H36Hash216OccurrenceBindingV1 *occurrence;
                HHSExactPass219H36Hash216MExponentWitnessV1 witness;
                uint32_t occurrence_index =
                    (phase->occurrence_offset + (uint32_t)(i % 54U)) % HHS_EXACT_PASS219_HASH216_OCCURRENCES;
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
    DatasetRecord record;
    HHSExactPass219Lane5UnboundedWorkloadRouteV1 route;
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 receipt;
    HHSExactPass219H36Hash216MExponentWitnessV1 witness;
    HHSExactPass219H36Hash216OccurrenceBindingV1 occurrence;
    uint8_t previous_bytes[8], current_bytes[8], goal_bytes[8];
    uint64_t raw_digest = 0U;

    make_dataset(&PHASES[0], 0U, &record);
    build_route_from_dataset(&record, &route, previous_bytes, current_bytes, goal_bytes);
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

    make_dataset(&PHASES[0], 0U, &record);
    record.goal ^= UINT64_C(1);
    REQUIRE(raw_validate_record(&PHASES[0], 0U, &record, &raw_digest) == 0U);
}

static void run_warmup(
    uint64_t warmup_iterations,
    const HHSExactPass219H36Hash216TransitionBindingV1 *binding
) {
    uint32_t p;
    const uint64_t warmup_budget_ns = UINT64_C(100000000);
    for (p = 0U; p < 4U; ++p) {
        ArmResult a = run_arm(&PHASES[p], warmup_iterations, warmup_budget_ns, ARM_FULL_LANE5, binding);
        ArmResult b = run_arm(&PHASES[p], warmup_iterations, warmup_budget_ns, ARM_ROUTE_ONLY, binding);
        ArmResult c = run_arm(&PHASES[p], warmup_iterations, warmup_budget_ns, ARM_RAW_RUNNER, binding);
        REQUIRE(a.dataset_complete == 1U && b.dataset_complete == 1U && c.dataset_complete == 1U);
        REQUIRE(a.dataset_digest == b.dataset_digest && b.dataset_digest == c.dataset_digest);
    }
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
        "{\"type\":\"arm\",\"schema\":\"HHS_PASS219_RAW_RUNNER_ABC_NORMALIZATION_V1\","
        "\"difficulty_rank\":%u,\"gradient\":{\"numerator\":%d,\"denominator\":4},"
        "\"phase\":\"%s\",\"phase_slot\":%u,\"inverse_phase_slot\":%u,"
        "\"arm\":\"%s\",\"target_iterations\":%" PRIu64 ",\"leg_budget_ns\":%" PRIu64 ","
        "\"elapsed_ns\":%" PRIu64 ",\"completed\":%" PRIu64 ",\"rate_per_second_floor\":%" PRIu64 ","
        "\"dataset_complete\":%s,\"dataset_digest\":%" PRIu64 ","
        "\"route_receipts\":%" PRIu64 ",\"m_witnesses\":%" PRIu64 ",\"raw_validations\":%" PRIu64 ","
        "\"route_digest\":%" PRIu64 ",\"proof_digest\":%" PRIu64 ",\"raw_digest\":%" PRIu64 ","
        "\"calibration_tensor_energy_units\":%u,\"calibration_reciprocal_pair_energy_units\":%u,"
        "\"physical_energy_measured\":false}\n",
        rank, gradient_numerator, phase->name, phase->phase_slot, phase->inverse_phase_slot,
        arm, target_iterations, leg_budget_ns, result->elapsed_ns, result->completed, rate_floor,
        result->dataset_complete ? "true" : "false", result->dataset_digest,
        result->route_receipts, result->m_witnesses, result->raw_validations,
        result->route_digest, result->proof_digest, result->raw_digest,
        LOGICAL_TENSOR_ENERGY_UNITS, LOGICAL_RECIPROCAL_PAIR_ENERGY_UNITS);
}

int main(void) {
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 authority;
    HHSExactPass219H36Hash216TransitionBindingV1 binding;
    uint64_t global_budget_ns = env_u64("HHS_RAW_RUNNER_ABC_GLOBAL_BUDGET_NS", DEFAULT_GLOBAL_BUDGET_NS);
    uint64_t leg_budget_ns = env_u64("HHS_RAW_RUNNER_ABC_LEG_BUDGET_NS", DEFAULT_LEG_BUDGET_NS);
    uint64_t base_iterations = env_u64("HHS_RAW_RUNNER_ABC_BASE_ITERATIONS", DEFAULT_BASE_ITERATIONS);
    uint64_t warmup_iterations = env_u64("HHS_RAW_RUNNER_ABC_WARMUP_ITERATIONS", DEFAULT_WARMUP_ITERATIONS);
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
    run_warmup(warmup_iterations, &binding);

    printf(
        "{\"type\":\"meta\",\"schema\":\"HHS_PASS219_RAW_RUNNER_ABC_NORMALIZATION_V1\","
        "\"global_budget_ns\":%" PRIu64 ",\"leg_budget_ns\":%" PRIu64 ","
        "\"base_iterations\":%" PRIu64 ",\"warmup_iterations\":%" PRIu64 ",\"difficulty_ranks\":%u,"
        "\"gradient_rule\":\"exact_percentile_gradient(rank,9)\","
        "\"gradient_denominator\":4,\"gradient_scale_factor\":2,"
        "\"phases\":[\"xy\",\"yx\",\"zw\",\"wz\"],"
        "\"arm_A\":\"lane5_route_plus_h36_hash216_m_binding\","
        "\"arm_B\":\"matched_lane5_route_only_control\","
        "\"arm_C\":\"raw_native_runner_same_dataset_validation\","
        "\"same_dataset_digest_required\":true,\"arm_order_rotation\":\"ABC/BCA/CAB\","
        "\"calibration_energy_contract\":\"PASS_067_1_LO_SHU_HARMONIC_PHASE_ENERGY_V1\","
        "\"calibration_tensor_energy_units\":%u,\"calibration_reciprocal_pair_energy_units\":%u,"
        "\"raw_arm_hhs_energy_authority\":false,\"physical_energy_measured\":false,"
        "\"negative_controls_passed\":true}\n",
        global_budget_ns, leg_budget_ns, base_iterations, warmup_iterations, DIFFICULTY_RANKS,
        LOGICAL_TENSOR_ENERGY_UNITS, LOGICAL_RECIPROCAL_PAIR_ENERGY_UNITS);

    batch_started = monotonic_ns();
    for (rank = 1U; rank <= DIFFICULTY_RANKS; ++rank) {
        uint64_t target_iterations;
        uint32_t phase_index;
        int32_t gradient_numerator = (int32_t)rank - 5;

        if (rank > 1U && base_iterations > (UINT64_MAX >> (rank - 1U))) break;
        target_iterations = base_iterations << (rank - 1U);

        for (phase_index = 0U; phase_index < 4U; ++phase_index) {
            ArmResult a, b, c;
            uint64_t elapsed = monotonic_ns() - batch_started;
            const PhaseSpec *phase = &PHASES[phase_index];
            uint32_t order = (rank + phase_index) % 3U;

            if (elapsed + (3U * leg_budget_ns) > global_budget_ns) goto finished;

            if (order == 0U) {
                a = run_arm(phase, target_iterations, leg_budget_ns, ARM_FULL_LANE5, &binding);
                b = run_arm(phase, target_iterations, leg_budget_ns, ARM_ROUTE_ONLY, &binding);
                c = run_arm(phase, target_iterations, leg_budget_ns, ARM_RAW_RUNNER, &binding);
            } else if (order == 1U) {
                b = run_arm(phase, target_iterations, leg_budget_ns, ARM_ROUTE_ONLY, &binding);
                c = run_arm(phase, target_iterations, leg_budget_ns, ARM_RAW_RUNNER, &binding);
                a = run_arm(phase, target_iterations, leg_budget_ns, ARM_FULL_LANE5, &binding);
            } else {
                c = run_arm(phase, target_iterations, leg_budget_ns, ARM_RAW_RUNNER, &binding);
                a = run_arm(phase, target_iterations, leg_budget_ns, ARM_FULL_LANE5, &binding);
                b = run_arm(phase, target_iterations, leg_budget_ns, ARM_ROUTE_ONLY, &binding);
            }

            REQUIRE(a.dataset_complete == 1U && b.dataset_complete == 1U && c.dataset_complete == 1U);
            REQUIRE(a.completed == target_iterations && b.completed == target_iterations && c.completed == target_iterations);
            REQUIRE(a.dataset_digest == b.dataset_digest && b.dataset_digest == c.dataset_digest);
            REQUIRE(a.route_receipts == a.completed && b.route_receipts == b.completed);
            REQUIRE(a.m_witnesses == a.completed && b.m_witnesses == 0U);
            REQUIRE(c.route_receipts == 0U && c.m_witnesses == 0U && c.raw_validations == c.completed);
            REQUIRE(a.raw_validations == 0U && b.raw_validations == 0U);
            REQUIRE(a.route_digest == b.route_digest);

            print_arm(rank, gradient_numerator, phase, "A", &a, target_iterations, leg_budget_ns);
            print_arm(rank, gradient_numerator, phase, "B", &b, target_iterations, leg_budget_ns);
            print_arm(rank, gradient_numerator, phase, "C", &c, target_iterations, leg_budget_ns);
            ++sample_count;
        }
    }

finished:
    {
        uint64_t batch_elapsed_ns = monotonic_ns() - batch_started;
        REQUIRE(batch_elapsed_ns <= global_budget_ns + TIMER_TOLERANCE_NS);
        printf(
            "{\"type\":\"result\",\"schema\":\"HHS_PASS219_RAW_RUNNER_ABC_NORMALIZATION_V1\","
            "\"triplet_phase_samples\":%" PRIu64 ",\"batch_elapsed_ns\":%" PRIu64 ","
            "\"global_budget_ns\":%" PRIu64 ",\"within_time_bound\":true,"
            "\"same_dataset_verified\":true,\"raw_runner_control_present\":true,"
            "\"candidate_only\":true,\"canonical_vm81_mutation_authority\":false,"
            "\"canonical_hash72_authority\":false,\"canonical_hash216_authority\":false,"
            "\"canonical_persistence_authority\":false,"
            "\"requires_signed_environmental_vm81_admission\":true,"
            "\"translator_required\":false,\"result\":\"PASS\"}\n",
            sample_count, batch_elapsed_ns, global_budget_ns);
    }
    return 0;
}
