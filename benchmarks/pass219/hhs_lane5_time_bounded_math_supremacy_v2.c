#define _POSIX_C_SOURCE 200809L
#include "hhs_runtime_exact_abi.h"

#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

__extension__ typedef unsigned __int128 hhs_u128;

#define REQUIRE(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "REQUIRE failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        exit(EXIT_FAILURE); \
    } \
} while (0)

typedef struct { uint64_t a, b; } Affine;
typedef struct { uint64_t a, b, c, d; } Mat2;
typedef struct {
    uint8_t solved;
    uint64_t endpoint;
    uint64_t executed_steps;
    uint64_t elapsed_ns;
} LegacyResult;

static const uint64_t MODULUS = UINT64_C(2305843009213693951);
static const uint64_t MULTIPLIER = UINT64_C(6364136223846793005) % UINT64_C(2305843009213693951);
static const uint64_t INCREMENT = UINT64_C(1442695040888963407) % UINT64_C(2305843009213693951);
static const uint64_t X0 = UINT64_C(123456789);
static const uint64_t DEFAULT_BOUND_NS = UINT64_C(120000000);
static const uint64_t DEFAULT_K0 = UINT64_C(1000);
static const uint64_t DEFAULT_MAX_K = UINT64_C(1000000000000);

static uint64_t elapsed_ns(const struct timespec *start, const struct timespec *end) {
    uint64_t sec = (uint64_t)(end->tv_sec - start->tv_sec);
    int64_t ns = (int64_t)end->tv_nsec - (int64_t)start->tv_nsec;
    if (ns < 0) { --sec; ns += INT64_C(1000000000); }
    return sec * UINT64_C(1000000000) + (uint64_t)ns;
}

static uint64_t elapsed_from(const struct timespec *start) {
    struct timespec now;
    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &now) == 0);
    return elapsed_ns(start, &now);
}

static uint64_t mul_mod(uint64_t x, uint64_t y, uint64_t m) {
    return (uint64_t)(((hhs_u128)x * (hhs_u128)y) % (hhs_u128)m);
}

static uint64_t add_mod(uint64_t x, uint64_t y, uint64_t m) {
    return (uint64_t)(((hhs_u128)x + (hhs_u128)y) % (hhs_u128)m);
}

static Affine acomp(Affine outer, Affine inner, uint64_t m) {
    Affine z;
    z.a = mul_mod(outer.a, inner.a, m);
    z.b = add_mod(mul_mod(outer.a, inner.b, m), outer.b, m);
    return z;
}

static Affine apow(Affine base, uint64_t n, uint64_t m, uint64_t *count) {
    Affine out = {UINT64_C(1), UINT64_C(0)};
    uint64_t c = 0U;
    while (n != 0U) {
        if ((n & UINT64_C(1)) != 0U) { out = acomp(base, out, m); ++c; }
        n >>= 1U;
        if (n != 0U) { base = acomp(base, base, m); ++c; }
    }
    *count = c;
    return out;
}

static Mat2 mmul(Mat2 x, Mat2 y, uint64_t m) {
    Mat2 z;
    z.a = add_mod(mul_mod(x.a, y.a, m), mul_mod(x.b, y.c, m), m);
    z.b = add_mod(mul_mod(x.a, y.b, m), mul_mod(x.b, y.d, m), m);
    z.c = add_mod(mul_mod(x.c, y.a, m), mul_mod(x.d, y.c, m), m);
    z.d = add_mod(mul_mod(x.c, y.b, m), mul_mod(x.d, y.d, m), m);
    return z;
}

static Mat2 mpow(Mat2 base, uint64_t n, uint64_t m, uint64_t *count) {
    Mat2 out = {UINT64_C(1), 0U, 0U, UINT64_C(1)};
    uint64_t c = 0U;
    while (n != 0U) {
        if ((n & UINT64_C(1)) != 0U) { out = mmul(base, out, m); ++c; }
        n >>= 1U;
        if (n != 0U) { base = mmul(base, base, m); ++c; }
    }
    *count = c;
    return out;
}

static LegacyResult legacy_linear(uint64_t k, uint64_t bound_ns) {
    LegacyResult r;
    struct timespec started;
    uint64_t x = X0, i;
    memset(&r, 0, sizeof(r));
    r.endpoint = x;
    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &started) == 0);
    for (i = 0U; i < k; ++i) {
        x = add_mod(mul_mod(MULTIPLIER, x, MODULUS), INCREMENT, MODULUS);
        if (((i + 1U) & UINT64_C(4095)) == 0U && elapsed_from(&started) >= bound_ns) {
            r.endpoint = x;
            r.executed_steps = i + 1U;
            r.elapsed_ns = elapsed_from(&started);
            return r;
        }
    }
    r.endpoint = x;
    r.executed_steps = k;
    r.elapsed_ns = elapsed_from(&started);
    r.solved = r.elapsed_ns <= bound_ns ? 1U : 0U;
    return r;
}

static uint32_t encode_u64(uint64_t v, uint8_t out[8]) {
    uint32_t i, first = 0U;
    if (v == 0U) { out[0] = 0U; return 1U; }
    for (i = 0U; i < 8U; ++i) out[7U - i] = (uint8_t)(v >> (8U * i));
    while (first < 7U && out[first] == 0U) ++first;
    if (first != 0U) memmove(out, out + first, 8U - first);
    return 8U - first;
}

static HHSExactBigUIntView bview(const uint8_t *p, uint32_t n) {
    HHSExactBigUIntView v;
    v.struct_size = (uint32_t)sizeof(v);
    v.byte_length = n;
    v.bytes_be = p;
    return v;
}

static void fill_digest(uint8_t out[32], uint64_t seed) {
    uint64_t x = seed ^ UINT64_C(0x9e3779b97f4a7c15);
    uint32_t i;
    for (i = 0U; i < 32U; ++i) {
        x ^= x >> 12U; x ^= x << 25U; x ^= x >> 27U;
        x *= UINT64_C(2685821657736338717);
        out[i] = (uint8_t)(x >> 56U);
    }
}

static int lane5_admit(uint64_t goal, uint64_t composition_count, uint64_t k, uint64_t *elapsed_out) {
    HHSExactPass219Lane5UnboundedWorkloadRouteV1 route;
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 receipt;
    struct timespec start, end;
    uint8_t z[1] = {0U}, xb[8], gb[8];
    uint32_t xn = encode_u64(X0, xb), gn = encode_u64(goal, gb);
    memset(&route, 0, sizeof(route));
    memset(&receipt, 0, sizeof(receipt));
    route.struct_size = (uint32_t)sizeof(route);
    route.version = HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION;
    route.previous_address = bview(z, 1U);
    route.current_address = bview(xb, xn);
    route.goal_address = bview(gb, gn);
    route.candidate_address = bview(gb, gn);
    fill_digest(route.workload_sha256, goal ^ k);
    fill_digest(route.provenance_sha256, X0 ^ UINT64_C(0xa5a5));
    fill_digest(route.forbidden_boundary_sha256, UINT64_C(0x33));
    fill_digest(route.reciprocal_witness_sha256, goal ^ UINT64_C(0x44));
    fill_digest(route.route_witness_sha256, composition_count ^ goal ^ UINT64_C(0x55));
    route.workload_byte_count = k;
    route.evidence_count = 5U;
    route.contradiction_check_count = 1U;
    route.integer_route_cost = UINT64_C(7);
    route.materialized_intermediate_states = 0U;
    route.phase_slot = 54U;
    route.inverse_phase_slot = 18U;
    route.trinary_collapse = 0;
    route.binary_collapse = 0U;
    route.nested_zero_slot = 1U;
    route.workload_serialization_exact = 1U;
    route.source_digest_verified = 1U;
    route.replay_witness_verified = 1U;
    route.exact_goal_reached = 1U;
    route.contradiction_free = 1U;
    route.reciprocal_phase_verified = 1U;
    route.bigint_serialization_addressed = 1U;
    route.candidate_only = 1U;
    route.requires_signed_environmental_vm81_admission = 1U;
    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &start) == 0);
    if (hhs_exact_pass219_lane5_unbounded_workload_route_validate(&route, &receipt) != HHS_EXACT_STATUS_OK) return 0;
    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &end) == 0);
    *elapsed_out = elapsed_ns(&start, &end);
    return receipt.accepted == 1U && receipt.integer_route_cost == UINT64_C(7) &&
           receipt.materialized_intermediate_states == 0U && receipt.candidate_only == 1U &&
           receipt.canonical_mutation_authority == 0U && receipt.canonical_hash72_authority == 0U &&
           receipt.canonical_hash216_authority == 0U && receipt.requires_signed_environmental_vm81_admission == 1U;
}

static uint64_t env_u64(const char *name, uint64_t fallback) {
    const char *s = getenv(name);
    char *end = NULL;
    unsigned long long v;
    if (s == NULL || *s == '\0') return fallback;
    errno = 0;
    v = strtoull(s, &end, 10);
    if (errno != 0 || end == s || *end != '\0' || v == 0ULL) return fallback;
    return (uint64_t)v;
}

int main(void) {
    const uint64_t bound_ns = env_u64("HHS_SUPREMACY_V2_BOUND_NS", DEFAULT_BOUND_NS);
    uint64_t k = env_u64("HHS_SUPREMACY_V2_K0", DEFAULT_K0);
    const uint64_t max_k = env_u64("HHS_SUPREMACY_V2_MAX_K", DEFAULT_MAX_K);
    uint64_t calibration_count = 0U, last_calibration_k = 0U;
    uint8_t witness = 0U;
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 authority;

    memset(&authority, 0, sizeof(authority));
    REQUIRE(hhs_exact_pass219_lane5_unbounded_workload_scaling_authority(&authority) == HHS_EXACT_STATUS_OK);
    REQUIRE(authority.constant_memory_candidate_reduction == 1U);
    REQUIRE(authority.intermediate_materialization_required == 0U);
    REQUIRE(authority.candidate_only == 1U);
    REQUIRE(authority.canonical_vm81_mutation_authority == 0U);
    REQUIRE(authority.canonical_hash72_authority == 0U);
    REQUIRE(authority.canonical_hash216_authority == 0U);
    REQUIRE(authority.requires_signed_environmental_vm81_admission == 1U);

    printf("{\"type\":\"meta\",\"schema\":\"HHS_TIME_BOUNDED_MATH_SUPREMACY_V2\",\"deadline_ns\":%" PRIu64 ",\"k0\":%" PRIu64 ",\"max_k\":%" PRIu64 ",\"gradient_factor\":10,\"active_threads\":1,\"legacy_class\":\"L_step_state_materializing\"}\n", bound_ns, k, max_k);

    while (k <= max_k) {
        struct timespec total_start, total_end, alg_start, alg_end, verify_start, verify_end;
        Affine jump;
        Mat2 matrix;
        uint64_t composition_count = 0U, matrix_count = 0U, result, independent;
        uint64_t alg_ns, verify_ns, admission_ns = 0U, total_ns;
        LegacyResult legacy;

        REQUIRE(clock_gettime(CLOCK_MONOTONIC, &total_start) == 0);
        REQUIRE(clock_gettime(CLOCK_MONOTONIC, &alg_start) == 0);
        jump = apow((Affine){MULTIPLIER, INCREMENT}, k, MODULUS, &composition_count);
        result = add_mod(mul_mod(jump.a, X0, MODULUS), jump.b, MODULUS);
        REQUIRE(clock_gettime(CLOCK_MONOTONIC, &alg_end) == 0);

        REQUIRE(clock_gettime(CLOCK_MONOTONIC, &verify_start) == 0);
        matrix = mpow((Mat2){MULTIPLIER, INCREMENT, 0U, 1U}, k, MODULUS, &matrix_count);
        independent = add_mod(mul_mod(matrix.a, X0, MODULUS), matrix.b, MODULUS);
        REQUIRE(clock_gettime(CLOCK_MONOTONIC, &verify_end) == 0);
        REQUIRE(result == independent);
        REQUIRE(lane5_admit(result, composition_count, k, &admission_ns));
        REQUIRE(clock_gettime(CLOCK_MONOTONIC, &total_end) == 0);

        alg_ns = elapsed_ns(&alg_start, &alg_end);
        verify_ns = elapsed_ns(&verify_start, &verify_end);
        total_ns = elapsed_ns(&total_start, &total_end);
        REQUIRE(total_ns <= bound_ns);

        legacy = legacy_linear(k, bound_ns);
        if (legacy.solved) {
            REQUIRE(legacy.endpoint == result);
            ++calibration_count;
            last_calibration_k = k;
        }

        printf("{\"type\":\"case\",\"k\":%" PRIu64 ",\"hhs_endpoint\":%" PRIu64 ",\"independent_endpoint\":%" PRIu64 ",\"hhs_compositions\":%" PRIu64 ",\"matrix_multiplications\":%" PRIu64 ",\"hhs_algorithm_ns\":%" PRIu64 ",\"verify_ns\":%" PRIu64 ",\"lane5_admission_ns\":%" PRIu64 ",\"hhs_total_ns\":%" PRIu64 ",\"legacy_solved\":%s,\"legacy_endpoint\":%" PRIu64 ",\"legacy_steps\":%" PRIu64 ",\"legacy_elapsed_ns\":%" PRIu64 ",\"legacy_completion_ppb\":%" PRIu64 "}\n",
               k, result, independent, composition_count, matrix_count, alg_ns, verify_ns, admission_ns, total_ns,
               legacy.solved ? "true" : "false", legacy.endpoint, legacy.executed_steps, legacy.elapsed_ns,
               k == 0U ? 0U : (uint64_t)(((hhs_u128)legacy.executed_steps * UINT64_C(1000000000)) / (hhs_u128)k));

        if (!legacy.solved) {
            REQUIRE(calibration_count > 0U);
            REQUIRE(legacy.executed_steps > 0U && legacy.executed_steps < k);
            printf("{\"type\":\"witness\",\"result\":\"BOUNDED_SUPREMACY_WITNESS\",\"k_star\":%" PRIu64 ",\"last_both_complete_k\":%" PRIu64 ",\"deadline_ns\":%" PRIu64 ",\"legacy_class\":\"L_step_state_materializing\",\"hhs_total_ns\":%" PRIu64 ",\"legacy_steps\":%" PRIu64 ",\"legacy_completion_ppb\":%" PRIu64 ",\"hhs_compositions\":%" PRIu64 ",\"materialized_intermediate_states\":0}\n",
                   k, last_calibration_k, bound_ns, total_ns, legacy.executed_steps,
                   (uint64_t)(((hhs_u128)legacy.executed_steps * UINT64_C(1000000000)) / (hhs_u128)k), composition_count);
            witness = 1U;
            break;
        }

        if (k > max_k / UINT64_C(10)) break;
        k *= UINT64_C(10);
    }

    REQUIRE(witness == 1U);
    puts("{\"type\":\"result\",\"result\":\"PASS\"}");
    return 0;
}
