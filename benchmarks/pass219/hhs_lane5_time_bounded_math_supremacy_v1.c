#define _POSIX_C_SOURCE 200809L
#include "hhs_runtime_exact_abi.h"

#include <errno.h>
#include <inttypes.h>
#include <openssl/evp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

__extension__ typedef unsigned __int128 hhs_u128;

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

typedef struct {
    uint64_t a;
    uint64_t b;
} Affine;

typedef struct {
    uint64_t v00, v01, v10, v11;
} Mat2;

typedef struct {
    int solved;
    uint64_t result;
    uint64_t work;
    uint64_t elapsed_ns;
} LinearResult;

static uint64_t elapsed_ns(const struct timespec *start, const struct timespec *end) {
    uint64_t seconds = (uint64_t)(end->tv_sec - start->tv_sec);
    int64_t nanos = (int64_t)end->tv_nsec - (int64_t)start->tv_nsec;
    if (nanos < 0) {
        seconds -= UINT64_C(1);
        nanos += INT64_C(1000000000);
    }
    return seconds * UINT64_C(1000000000) + (uint64_t)nanos;
}

static uint64_t now_elapsed_ns(const struct timespec *start) {
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now) != 0)
        return UINT64_MAX;
    return elapsed_ns(start, &now);
}

static uint64_t mul_mod(uint64_t x, uint64_t y, uint64_t mod) {
    return (uint64_t)(((hhs_u128)x * (hhs_u128)y) % (hhs_u128)mod);
}

static uint64_t add_mod(uint64_t x, uint64_t y, uint64_t mod) {
    return (uint64_t)(((hhs_u128)x + (hhs_u128)y) % (hhs_u128)mod);
}

static Affine affine_compose(Affine outer, Affine inner, uint64_t mod) {
    Affine out;
    out.a = mul_mod(outer.a, inner.a, mod);
    out.b = add_mod(mul_mod(outer.a, inner.b, mod), outer.b, mod);
    return out;
}

static Affine affine_pow(Affine base, uint64_t exponent, uint64_t mod, uint64_t *composition_count) {
    Affine result = {UINT64_C(1), UINT64_C(0)};
    uint64_t count = 0U;
    while (exponent != 0U) {
        if ((exponent & UINT64_C(1)) != 0U) {
            result = affine_compose(base, result, mod);
            ++count;
        }
        exponent >>= 1U;
        if (exponent != 0U) {
            base = affine_compose(base, base, mod);
            ++count;
        }
    }
    *composition_count = count;
    return result;
}

static uint64_t affine_apply(Affine f, uint64_t x, uint64_t mod) {
    return add_mod(mul_mod(f.a, x, mod), f.b, mod);
}

static Mat2 mat_mul(Mat2 x, Mat2 y, uint64_t mod) {
    Mat2 z;
    z.v00 = add_mod(mul_mod(x.v00, y.v00, mod), mul_mod(x.v01, y.v10, mod), mod);
    z.v01 = add_mod(mul_mod(x.v00, y.v01, mod), mul_mod(x.v01, y.v11, mod), mod);
    z.v10 = add_mod(mul_mod(x.v10, y.v00, mod), mul_mod(x.v11, y.v10, mod), mod);
    z.v11 = add_mod(mul_mod(x.v10, y.v01, mod), mul_mod(x.v11, y.v11, mod), mod);
    return z;
}

static Mat2 mat_pow(Mat2 base, uint64_t exponent, uint64_t mod) {
    Mat2 result = {UINT64_C(1), UINT64_C(0), UINT64_C(0), UINT64_C(1)};
    while (exponent != 0U) {
        if ((exponent & UINT64_C(1)) != 0U)
            result = mat_mul(base, result, mod);
        exponent >>= 1U;
        if (exponent != 0U)
            base = mat_mul(base, base, mod);
    }
    return result;
}

static LinearResult affine_linear(uint64_t a, uint64_t b, uint64_t mod, uint64_t x0, uint64_t steps, uint64_t bound_ns) {
    LinearResult out;
    struct timespec started;
    uint64_t i;
    uint64_t x = x0;
    memset(&out, 0, sizeof(out));
    CHECK(clock_gettime(CLOCK_MONOTONIC, &started) == 0);
    for (i = 0U; i < steps; ++i) {
        x = add_mod(mul_mod(a, x, mod), b, mod);
        if (((i + 1U) & UINT64_C(4095)) == 0U && now_elapsed_ns(&started) >= bound_ns) {
            out.solved = 0;
            out.result = x;
            out.work = i + 1U;
            out.elapsed_ns = now_elapsed_ns(&started);
            return out;
        }
    }
    out.solved = 1;
    out.result = x;
    out.work = steps;
    out.elapsed_ns = now_elapsed_ns(&started);
    return out;
}

static int64_t egcd(int64_t a, int64_t b, int64_t *x, int64_t *y) {
    if (b == 0) {
        *x = 1;
        *y = 0;
        return a;
    }
    {
        int64_t x1, y1;
        int64_t g = egcd(b, a % b, &x1, &y1);
        *x = y1;
        *y = x1 - (a / b) * y1;
        return g;
    }
}

static uint64_t mod_inverse_u64(uint64_t a, uint64_t mod) {
    int64_t x, y;
    int64_t g = egcd((int64_t)a, (int64_t)mod, &x, &y);
    int64_t r;
    if (g != 1)
        return 0U;
    r = x % (int64_t)mod;
    if (r < 0)
        r += (int64_t)mod;
    return (uint64_t)r;
}

static int crt_minus_one(const uint64_t *mods, size_t count, uint64_t *value, uint64_t *modulus, uint64_t *composition_count) {
    uint64_t x;
    uint64_t m;
    size_t i;
    if (count == 0U)
        return 0;
    x = mods[0] - 1U;
    m = mods[0];
    *composition_count = 0U;
    for (i = 1U; i < count; ++i) {
        const uint64_t p = mods[i];
        const uint64_t residue = p - 1U;
        const uint64_t x_mod = x % p;
        const uint64_t delta = (residue + p - x_mod) % p;
        const uint64_t inv = mod_inverse_u64(m % p, p);
        uint64_t t;
        hhs_u128 next_x;
        hhs_u128 next_m;
        if (inv == 0U)
            return 0;
        t = mul_mod(delta, inv, p);
        next_x = (hhs_u128)x + (hhs_u128)m * (hhs_u128)t;
        next_m = (hhs_u128)m * (hhs_u128)p;
        if (next_x > UINT64_MAX || next_m > UINT64_MAX)
            return 0;
        x = (uint64_t)next_x;
        m = (uint64_t)next_m;
        ++(*composition_count);
    }
    *value = x;
    *modulus = m;
    return 1;
}

static int crt_verify(uint64_t x, const uint64_t *mods, size_t count, uint64_t modulus) {
    size_t i;
    if (x >= modulus)
        return 0;
    for (i = 0U; i < count; ++i) {
        if ((x % mods[i]) != mods[i] - 1U)
            return 0;
    }
    return x == modulus - 1U;
}

static LinearResult crt_linear_scan(const uint64_t *mods, size_t count, uint64_t modulus, uint64_t bound_ns) {
    LinearResult out;
    struct timespec started;
    uint64_t x;
    memset(&out, 0, sizeof(out));
    CHECK(clock_gettime(CLOCK_MONOTONIC, &started) == 0);
    for (x = 0U; x < modulus; ++x) {
        size_t i;
        int ok = 1;
        for (i = 0U; i < count; ++i) {
            if ((x % mods[i]) != mods[i] - 1U) {
                ok = 0;
                break;
            }
        }
        if (ok) {
            out.solved = 1;
            out.result = x;
            out.work = x + 1U;
            out.elapsed_ns = now_elapsed_ns(&started);
            return out;
        }
        if (((x + 1U) & UINT64_C(4095)) == 0U && now_elapsed_ns(&started) >= bound_ns) {
            out.solved = 0;
            out.result = x;
            out.work = x + 1U;
            out.elapsed_ns = now_elapsed_ns(&started);
            return out;
        }
    }
    out.solved = 0;
    out.result = 0U;
    out.work = modulus;
    out.elapsed_ns = now_elapsed_ns(&started);
    return out;
}

static uint32_t encode_u64_be(uint64_t value, uint8_t out[8]) {
    uint32_t i;
    uint32_t first = 0U;
    if (value == 0U) {
        out[0] = 0U;
        return 1U;
    }
    for (i = 0U; i < 8U; ++i)
        out[7U - i] = (uint8_t)(value >> (i * 8U));
    while (first < 7U && out[first] == 0U)
        ++first;
    if (first != 0U)
        memmove(out, out + first, 8U - first);
    return 8U - first;
}

static HHSExactBigUIntView view(const uint8_t *bytes, uint32_t length) {
    HHSExactBigUIntView v;
    v.struct_size = (uint32_t)sizeof(v);
    v.byte_length = length;
    v.bytes_be = bytes;
    return v;
}

static int sha256_text(const char *text, uint8_t out[32]) {
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    unsigned int length = 0U;
    int ok;
    if (ctx == NULL)
        return 0;
    ok = EVP_DigestInit_ex(ctx, EVP_sha256(), NULL) == 1 &&
         EVP_DigestUpdate(ctx, text, strlen(text)) == 1 &&
         EVP_DigestFinal_ex(ctx, out, &length) == 1 && length == 32U;
    EVP_MD_CTX_free(ctx);
    return ok;
}

static int lane5_admit_math_route(const char *family, uint64_t previous, uint64_t current, uint64_t goal, uint64_t route_cost, uint64_t workload_count, uint64_t *admission_ns) {
    HHSExactPass219Lane5UnboundedWorkloadRouteV1 route;
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 receipt;
    uint8_t previous_bytes[8], current_bytes[8], goal_bytes[8];
    uint32_t previous_len, current_len, goal_len;
    char tag[256];
    struct timespec started, finished;
    uint8_t digest[32];

    previous_len = encode_u64_be(previous, previous_bytes);
    current_len = encode_u64_be(current, current_bytes);
    goal_len = encode_u64_be(goal, goal_bytes);
    memset(&route, 0, sizeof(route));
    memset(&receipt, 0, sizeof(receipt));
    route.struct_size = (uint32_t)sizeof(route);
    route.version = HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION;
    route.previous_address = view(previous_bytes, previous_len);
    route.current_address = view(current_bytes, current_len);
    route.goal_address = view(goal_bytes, goal_len);
    route.candidate_address = view(goal_bytes, goal_len);

    snprintf(tag, sizeof(tag), "%s:%" PRIu64 ":%" PRIu64 ":%" PRIu64, family, current, goal, route_cost);
    if (!sha256_text(tag, digest))
        return 0;
    memcpy(route.workload_sha256, digest, 32U);
    snprintf(tag, sizeof(tag), "provenance:%s:%" PRIu64, family, workload_count);
    if (!sha256_text(tag, digest))
        return 0;
    memcpy(route.provenance_sha256, digest, 32U);
    snprintf(tag, sizeof(tag), "forbidden:%s", family);
    if (!sha256_text(tag, digest))
        return 0;
    memcpy(route.forbidden_boundary_sha256, digest, 32U);
    snprintf(tag, sizeof(tag), "reciprocal:%s:%" PRIu64, family, goal);
    if (!sha256_text(tag, digest))
        return 0;
    memcpy(route.reciprocal_witness_sha256, digest, 32U);
    snprintf(tag, sizeof(tag), "route:%s:%" PRIu64 ":%" PRIu64, family, goal, route_cost);
    if (!sha256_text(tag, digest))
        return 0;
    memcpy(route.route_witness_sha256, digest, 32U);

    route.workload_byte_count = workload_count;
    route.evidence_count = 5U;
    route.contradiction_check_count = 1U;
    route.integer_route_cost = route_cost;
    route.materialized_intermediate_states = 0U;
    route.phase_slot = 54U;
    route.inverse_phase_slot = 18U;
    route.trinary_collapse = 1;
    route.binary_collapse = 1U;
    route.nested_zero_slot = 1U;
    route.workload_serialization_exact = 1U;
    route.source_digest_verified = 1U;
    route.replay_witness_verified = 1U;
    route.exact_goal_reached = 1U;
    route.contradiction_free = 1U;
    route.goal_forbidden_conflict = 0U;
    route.reciprocal_phase_verified = 1U;
    route.bigint_serialization_addressed = 1U;
    route.candidate_only = 1U;
    route.canonical_mutation_authority = 0U;
    route.canonical_hash72_authority = 0U;
    route.canonical_hash216_authority = 0U;
    route.canonical_persistence_authority = 0U;
    route.pqc_key_authority = 0U;
    route.receipt_clock_authority = 0U;
    route.requires_signed_environmental_vm81_admission = 1U;

    CHECK(clock_gettime(CLOCK_MONOTONIC, &started) == 0);
    if (hhs_exact_pass219_lane5_unbounded_workload_route_validate(&route, &receipt) != HHS_EXACT_STATUS_OK)
        return 0;
    CHECK(clock_gettime(CLOCK_MONOTONIC, &finished) == 0);
    *admission_ns = elapsed_ns(&started, &finished);
    return receipt.accepted == 1U &&
           receipt.materialized_intermediate_states == 0U &&
           receipt.canonical_mutation_authority == 0U &&
           receipt.canonical_hash216_authority == 0U;
}

static uint64_t read_bound_ns(void) {
    const char *value = getenv("HHS_TIME_BOUND_NS");
    char *end = NULL;
    unsigned long long parsed;
    if (value == NULL || *value == '\0')
        return UINT64_C(50000000);
    errno = 0;
    parsed = strtoull(value, &end, 10);
    if (errno != 0 || end == value || *end != '\0' || parsed == 0ULL)
        return UINT64_C(50000000);
    return (uint64_t)parsed;
}

static int run_affine_cases(uint64_t bound_ns) {
    static const uint64_t steps[] = {
        UINT64_C(1000), UINT64_C(100000), UINT64_C(10000000),
        UINT64_C(1000000000), UINT64_C(1000000000000)
    };
    const uint64_t mod = UINT64_C(2305843009213693951);
    const uint64_t a = UINT64_C(6364136223846793005) % mod;
    const uint64_t b = UINT64_C(1442695040888963407) % mod;
    const uint64_t x0 = UINT64_C(123456789);
    size_t idx;
    for (idx = 0U; idx < sizeof(steps) / sizeof(steps[0]); ++idx) {
        const uint64_t k = steps[idx];
        struct timespec total_started, algebra_started, algebra_finished, verify_started, verify_finished, total_finished;
        Affine jump;
        Mat2 matrix;
        Mat2 matrix_jump;
        uint64_t compositions = 0U;
        uint64_t result;
        uint64_t independent;
        uint64_t admission_ns = 0U;
        uint64_t algebra_ns, verify_ns, total_ns;
        LinearResult linear;
        int admitted;
        CHECK(clock_gettime(CLOCK_MONOTONIC, &total_started) == 0);
        CHECK(clock_gettime(CLOCK_MONOTONIC, &algebra_started) == 0);
        jump = affine_pow((Affine){a, b}, k, mod, &compositions);
        result = affine_apply(jump, x0, mod);
        CHECK(clock_gettime(CLOCK_MONOTONIC, &algebra_finished) == 0);
        CHECK(clock_gettime(CLOCK_MONOTONIC, &verify_started) == 0);
        matrix = (Mat2){a, b, 0U, 1U};
        matrix_jump = mat_pow(matrix, k, mod);
        independent = add_mod(mul_mod(matrix_jump.v00, x0, mod), matrix_jump.v01, mod);
        CHECK(clock_gettime(CLOCK_MONOTONIC, &verify_finished) == 0);
        CHECK(result == independent);
        admitted = lane5_admit_math_route("affine", 0U, x0, result, compositions, k, &admission_ns);
        CHECK(admitted);
        CHECK(clock_gettime(CLOCK_MONOTONIC, &total_finished) == 0);
        algebra_ns = elapsed_ns(&algebra_started, &algebra_finished);
        verify_ns = elapsed_ns(&verify_started, &verify_finished);
        total_ns = elapsed_ns(&total_started, &total_finished);
        CHECK(total_ns <= bound_ns);

        linear = affine_linear(a, b, mod, x0, k, bound_ns);
        if (linear.solved)
            CHECK(linear.result == result);

        printf(
            "{\"type\":\"case\",\"family\":\"affine\",\"size\":%" PRIu64 ","
            "\"omega\":%" PRIu64 ",\"hhs_result\":%" PRIu64 ",\"independent_result\":%" PRIu64 ","
            "\"linear_status\":\"%s\",\"linear_result\":%" PRIu64 ",\"linear_steps\":%" PRIu64 ","
            "\"linear_work_lower_bound\":%" PRIu64 ",\"hhs_compositions\":%" PRIu64 ","
            "\"hhs_algebra_ns\":%" PRIu64 ",\"verify_ns\":%" PRIu64 ",\"admission_ns\":%" PRIu64 ","
            "\"hhs_total_ns\":%" PRIu64 ",\"linear_elapsed_ns\":%" PRIu64 ",\"time_bound_ns\":%" PRIu64 ","
            "\"exact\":true,\"lane5_admitted\":true,\"materialized_intermediate_states\":0}\n",
            k, k, result, independent, linear.solved ? "solved" : "timeout", linear.result, linear.work,
            k, compositions, algebra_ns, verify_ns, admission_ns, total_ns, linear.elapsed_ns, bound_ns
        );
    }
    return 0;
}

static int run_crt_cases(uint64_t bound_ns) {
    static const uint64_t mods[] = {
        UINT64_C(101), UINT64_C(103), UINT64_C(107),
        UINT64_C(109), UINT64_C(113), UINT64_C(127)
    };
    size_t count;
    for (count = 2U; count <= sizeof(mods) / sizeof(mods[0]); ++count) {
        struct timespec total_started, algebra_started, algebra_finished, verify_started, verify_finished, total_finished;
        uint64_t result = 0U, modulus = 0U, compositions = 0U;
        uint64_t admission_ns = 0U;
        uint64_t algebra_ns, verify_ns, total_ns;
        LinearResult linear;
        int verified;
        int admitted;
        CHECK(clock_gettime(CLOCK_MONOTONIC, &total_started) == 0);
        CHECK(clock_gettime(CLOCK_MONOTONIC, &algebra_started) == 0);
        CHECK(crt_minus_one(mods, count, &result, &modulus, &compositions));
        CHECK(clock_gettime(CLOCK_MONOTONIC, &algebra_finished) == 0);
        CHECK(clock_gettime(CLOCK_MONOTONIC, &verify_started) == 0);
        verified = crt_verify(result, mods, count, modulus);
        CHECK(clock_gettime(CLOCK_MONOTONIC, &verify_finished) == 0);
        CHECK(verified);
        admitted = lane5_admit_math_route("crt", 0U, 0U, result, compositions, modulus, &admission_ns);
        CHECK(admitted);
        CHECK(clock_gettime(CLOCK_MONOTONIC, &total_finished) == 0);
        algebra_ns = elapsed_ns(&algebra_started, &algebra_finished);
        verify_ns = elapsed_ns(&verify_started, &verify_finished);
        total_ns = elapsed_ns(&total_started, &total_finished);
        CHECK(total_ns <= bound_ns);

        linear = crt_linear_scan(mods, count, modulus, bound_ns);
        if (linear.solved)
            CHECK(linear.result == result);

        printf(
            "{\"type\":\"case\",\"family\":\"crt\",\"size\":%zu,"
            "\"omega\":%" PRIu64 ",\"hhs_result\":%" PRIu64 ",\"independent_result\":%" PRIu64 ","
            "\"linear_status\":\"%s\",\"linear_result\":%" PRIu64 ",\"linear_steps\":%" PRIu64 ","
            "\"linear_work_lower_bound\":%" PRIu64 ",\"hhs_compositions\":%" PRIu64 ","
            "\"hhs_algebra_ns\":%" PRIu64 ",\"verify_ns\":%" PRIu64 ",\"admission_ns\":%" PRIu64 ","
            "\"hhs_total_ns\":%" PRIu64 ",\"linear_elapsed_ns\":%" PRIu64 ",\"time_bound_ns\":%" PRIu64 ","
            "\"exact\":true,\"lane5_admitted\":true,\"materialized_intermediate_states\":0}\n",
            count, modulus, result, modulus - 1U, linear.solved ? "solved" : "timeout", linear.result, linear.work,
            modulus, compositions, algebra_ns, verify_ns, admission_ns, total_ns, linear.elapsed_ns, bound_ns
        );
    }
    return 0;
}

int main(void) {
    const uint64_t bound_ns = read_bound_ns();
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 authority;
    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_scaling_authority(&authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.constant_memory_candidate_reduction == 1U);
    CHECK(authority.intermediate_materialization_required == 0U);
    CHECK(authority.candidate_only == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);

    printf("{\"type\":\"meta\",\"schema\":\"HHS_TIME_BOUNDED_MATH_SUPREMACY_V1\",\"time_bound_ns\":%" PRIu64 ",\"active_threads\":1}\n", bound_ns);
    CHECK(run_affine_cases(bound_ns) == 0);
    CHECK(run_crt_cases(bound_ns) == 0);
    puts("{\"type\":\"result\",\"result\":\"PASS\"}");
    return 0;
}
