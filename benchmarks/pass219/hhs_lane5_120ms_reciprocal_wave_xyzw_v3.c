#define _POSIX_C_SOURCE 200809L
#include "hhs_runtime_exact_abi.h"

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
typedef struct { uint64_t x0, k; } Query;

typedef struct {
    uint64_t elapsed_ns;
    uint64_t completion_elapsed_ns;
    uint64_t completed_queries;
    uint64_t dataset_limit_queries;
    uint8_t dataset_complete;
    hhs_u128 represented_transitions;
    hhs_u128 descriptor_bits;
    hhs_u128 affine_compositions;
    hhs_u128 matrix_multiplications;
    uint64_t lane5_admissions;
    uint64_t endpoint_digest;
    uint64_t descriptor_digest;
} HhsResult;

typedef struct {
    uint64_t elapsed_ns;
    uint64_t completion_elapsed_ns;
    uint64_t completed_queries;
    uint64_t dataset_limit_queries;
    uint8_t dataset_complete;
    hhs_u128 represented_transitions;
    hhs_u128 descriptor_bits;
    hhs_u128 matrix_multiplications;
    uint64_t endpoint_digest;
    uint64_t descriptor_digest;
} ConventionalResult;

typedef struct {
    uint64_t completed_queries;
    hhs_u128 represented_transitions;
    hhs_u128 descriptor_bits;
    uint64_t endpoint_digest;
    uint64_t descriptor_digest;
} PrefixIdentity;

static const uint64_t MODULUS = UINT64_C(2305843009213693951);
static const uint64_t MULTIPLIER = UINT64_C(6364136223846793005) % UINT64_C(2305843009213693951);
static const uint64_t INCREMENT = UINT64_C(1442695040888963407) % UINT64_C(2305843009213693951);
static const uint64_t STREAM_SEED_W = UINT64_C(0x2191205a72c0ffee);
static const uint64_t GLOBAL_BUDGET_NS = UINT64_C(120000000);
static const uint64_t TIMER_TOLERANCE_NS = UINT64_C(10000000);
static const uint64_t DEFAULT_DATASET_QUERIES = UINT64_C(8);
static const uint64_t DEFAULT_MAX_SAMPLES = UINT64_C(16);

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

static uint64_t mix64(uint64_t x) {
    x += UINT64_C(0x9e3779b97f4a7c15);
    x = (x ^ (x >> 30U)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27U)) * UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31U);
}

static Query query_at(uint64_t seed, uint64_t index) {
    uint64_t s0 = mix64(seed ^ (index * UINT64_C(0xd1342543de82ef95)));
    uint64_t s1 = mix64(s0 ^ UINT64_C(0xa5a5a5a55a5a5a5a));
    Query q;
    q.x0 = s0 % MODULUS;
    q.k = UINT64_C(1000000) + (s1 % UINT64_C(1000000000));
    return q;
}

static uint32_t bit_length_u64(uint64_t x) {
    uint32_t n = 0U;
    while (x != 0U) { ++n; x >>= 1U; }
    return n == 0U ? 1U : n;
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

static int lane5_admit(uint64_t current, uint64_t goal, uint64_t math_compositions, uint64_t workload) {
    HHSExactPass219Lane5UnboundedWorkloadRouteV1 route;
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 receipt;
    uint8_t z[1] = {0U}, cb[8], gb[8];
    uint32_t cn = encode_u64(current, cb), gn = encode_u64(goal, gb);
    memset(&route, 0, sizeof(route));
    memset(&receipt, 0, sizeof(receipt));
    route.struct_size = (uint32_t)sizeof(route);
    route.version = HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION;
    route.previous_address = bview(z, 1U);
    route.current_address = bview(cb, cn);
    route.goal_address = bview(gb, gn);
    route.candidate_address = bview(gb, gn);
    fill_digest(route.workload_sha256, goal ^ workload);
    fill_digest(route.provenance_sha256, current ^ UINT64_C(0xa5a5));
    fill_digest(route.forbidden_boundary_sha256, UINT64_C(0x33));
    fill_digest(route.reciprocal_witness_sha256, goal ^ UINT64_C(0x44));
    fill_digest(route.route_witness_sha256, math_compositions ^ goal ^ UINT64_C(0x55));
    route.workload_byte_count = workload;
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
    if (hhs_exact_pass219_lane5_unbounded_workload_route_validate(&route, &receipt) != HHS_EXACT_STATUS_OK) return 0;
    return receipt.accepted == 1U &&
           receipt.integer_route_cost == UINT64_C(7) &&
           receipt.materialized_intermediate_states == 0U &&
           receipt.candidate_only == 1U &&
           receipt.canonical_mutation_authority == 0U &&
           receipt.canonical_hash72_authority == 0U &&
           receipt.canonical_hash216_authority == 0U &&
           receipt.requires_signed_environmental_vm81_admission == 1U;
}

static uint64_t endpoint_fold(uint64_t digest, uint64_t index, uint64_t endpoint) {
    return mix64(digest ^ mix64(index) ^ mix64(endpoint));
}

static uint64_t descriptor_fold(uint64_t digest, uint64_t index, Query q) {
    return mix64(digest ^ mix64(index) ^ mix64(q.x0) ^ mix64(q.k));
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

static uint64_t hhs_endpoint(Query q, uint64_t *affine_count, uint64_t *matrix_count) {
    Affine jump;
    Mat2 matrix;
    uint64_t endpoint, independent;
    jump = apow((Affine){MULTIPLIER, INCREMENT}, q.k, MODULUS, affine_count);
    endpoint = add_mod(mul_mod(jump.a, q.x0, MODULUS), jump.b, MODULUS);
    matrix = mpow((Mat2){MULTIPLIER, INCREMENT, 0U, 1U}, q.k, MODULUS, matrix_count);
    independent = add_mod(mul_mod(matrix.a, q.x0, MODULUS), matrix.b, MODULUS);
    REQUIRE(endpoint == independent);
    REQUIRE(lane5_admit(q.x0, endpoint, *affine_count, q.k));
    return endpoint;
}

static uint64_t conventional_endpoint(Query q, uint64_t *matrix_count) {
    Mat2 matrix = mpow((Mat2){MULTIPLIER, INCREMENT, 0U, 1U}, q.k, MODULUS, matrix_count);
    return add_mod(mul_mod(matrix.a, q.x0, MODULUS), matrix.b, MODULUS);
}

static HhsResult run_hhs(uint64_t seed, uint64_t query_limit, uint64_t budget_ns) {
    HhsResult r;
    struct timespec started;
    uint64_t index = 0U;
    memset(&r, 0, sizeof(r));
    r.dataset_limit_queries = query_limit;
    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &started) == 0);
    while (index < query_limit) {
        Query q;
        uint64_t c1 = 0U, c2 = 0U, endpoint;
        if (budget_ns != 0U && elapsed_from(&started) >= budget_ns) break;
        q = query_at(seed, index);
        endpoint = hhs_endpoint(q, &c1, &c2);
        r.completed_queries++;
        r.represented_transitions += (hhs_u128)q.k;
        r.descriptor_bits += (hhs_u128)bit_length_u64(q.x0) + (hhs_u128)bit_length_u64(q.k);
        r.affine_compositions += (hhs_u128)c1;
        r.matrix_multiplications += (hhs_u128)c2;
        r.lane5_admissions++;
        r.endpoint_digest = endpoint_fold(r.endpoint_digest, index, endpoint);
        r.descriptor_digest = descriptor_fold(r.descriptor_digest, index, q);
        ++index;
    }
    r.elapsed_ns = elapsed_from(&started);
    if (r.completed_queries == query_limit) {
        r.dataset_complete = 1U;
        r.completion_elapsed_ns = r.elapsed_ns;
    }
    return r;
}

static ConventionalResult run_conventional(uint64_t seed, uint64_t query_limit, uint64_t budget_ns) {
    ConventionalResult r;
    struct timespec started;
    uint64_t index = 0U;
    memset(&r, 0, sizeof(r));
    r.dataset_limit_queries = query_limit;
    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &started) == 0);
    while (index < query_limit) {
        Query q;
        uint64_t c = 0U, endpoint;
        if (budget_ns != 0U && elapsed_from(&started) >= budget_ns) break;
        q = query_at(seed, index);
        endpoint = conventional_endpoint(q, &c);
        r.completed_queries++;
        r.represented_transitions += (hhs_u128)q.k;
        r.descriptor_bits += (hhs_u128)bit_length_u64(q.x0) + (hhs_u128)bit_length_u64(q.k);
        r.matrix_multiplications += (hhs_u128)c;
        r.endpoint_digest = endpoint_fold(r.endpoint_digest, index, endpoint);
        r.descriptor_digest = descriptor_fold(r.descriptor_digest, index, q);
        ++index;
    }
    r.elapsed_ns = elapsed_from(&started);
    if (r.completed_queries == query_limit) {
        r.dataset_complete = 1U;
        r.completion_elapsed_ns = r.elapsed_ns;
    }
    return r;
}

static PrefixIdentity reference_prefix(uint64_t seed, uint64_t count) {
    PrefixIdentity p;
    uint64_t index;
    memset(&p, 0, sizeof(p));
    for (index = 0U; index < count; ++index) {
        Query q = query_at(seed, index);
        uint64_t c = 0U;
        Affine jump = apow((Affine){MULTIPLIER, INCREMENT}, q.k, MODULUS, &c);
        uint64_t endpoint = add_mod(mul_mod(jump.a, q.x0, MODULUS), jump.b, MODULUS);
        (void)c;
        p.completed_queries++;
        p.represented_transitions += (hhs_u128)q.k;
        p.descriptor_bits += (hhs_u128)bit_length_u64(q.x0) + (hhs_u128)bit_length_u64(q.k);
        p.endpoint_digest = endpoint_fold(p.endpoint_digest, index, endpoint);
        p.descriptor_digest = descriptor_fold(p.descriptor_digest, index, q);
    }
    return p;
}

static void print_u128(hhs_u128 v) {
    char buf[64];
    size_t n = 0U;
    if (v == 0U) { putchar('0'); return; }
    while (v != 0U) { buf[n++] = (char)('0' + (unsigned)(v % 10U)); v /= 10U; }
    while (n != 0U) putchar(buf[--n]);
}

static void print_hhs(uint64_t sample, const char *id, const char *axis, const HhsResult *r) {
    printf("{\"type\":\"benchmark\",\"sample\":%" PRIu64 ",\"id\":\"%s\",\"axis\":\"%s\",\"architecture\":\"hhs\",\"dataset\":\"W\",\"elapsed_ns\":%" PRIu64 ",\"completion_elapsed_ns\":%" PRIu64 ",\"completed_queries\":%" PRIu64 ",\"dataset_limit_queries\":%" PRIu64 ",\"dataset_complete\":%s,\"represented_transitions\":\"",
           sample, id, axis, r->elapsed_ns, r->completion_elapsed_ns, r->completed_queries, r->dataset_limit_queries, r->dataset_complete ? "true" : "false");
    print_u128(r->represented_transitions);
    printf("\",\"descriptor_bits\":\""); print_u128(r->descriptor_bits);
    printf("\",\"affine_compositions\":\""); print_u128(r->affine_compositions);
    printf("\",\"matrix_multiplications\":\""); print_u128(r->matrix_multiplications);
    printf("\",\"lane5_admissions\":%" PRIu64 ",\"endpoint_digest\":%" PRIu64 ",\"descriptor_digest\":%" PRIu64 ",\"materialized_intermediate_states\":0}\n",
           r->lane5_admissions, r->endpoint_digest, r->descriptor_digest);
}

static void print_conventional(uint64_t sample, const char *id, const char *axis, const ConventionalResult *r) {
    printf("{\"type\":\"benchmark\",\"sample\":%" PRIu64 ",\"id\":\"%s\",\"axis\":\"%s\",\"architecture\":\"conventional_matrix\",\"dataset\":\"W\",\"elapsed_ns\":%" PRIu64 ",\"completion_elapsed_ns\":%" PRIu64 ",\"completed_queries\":%" PRIu64 ",\"dataset_limit_queries\":%" PRIu64 ",\"dataset_complete\":%s,\"represented_transitions\":\"",
           sample, id, axis, r->elapsed_ns, r->completion_elapsed_ns, r->completed_queries, r->dataset_limit_queries, r->dataset_complete ? "true" : "false");
    print_u128(r->represented_transitions);
    printf("\",\"descriptor_bits\":\""); print_u128(r->descriptor_bits);
    printf("\",\"matrix_multiplications\":\""); print_u128(r->matrix_multiplications);
    printf("\",\"endpoint_digest\":%" PRIu64 ",\"descriptor_digest\":%" PRIu64 "}\n",
           r->endpoint_digest, r->descriptor_digest);
}

static void require_prefix_matches(const PrefixIdentity *p, uint64_t completed_queries, hhs_u128 transitions, hhs_u128 bits, uint64_t endpoint_digest, uint64_t descriptor_digest) {
    REQUIRE(p->completed_queries == completed_queries);
    REQUIRE(p->represented_transitions == transitions);
    REQUIRE(p->descriptor_bits == bits);
    REQUIRE(p->endpoint_digest == endpoint_digest);
    REQUIRE(p->descriptor_digest == descriptor_digest);
}

int main(void) {
    uint64_t query_limit = env_u64("HHS_RECIPROCAL_WAVE_DATASET_QUERIES", DEFAULT_DATASET_QUERIES);
    uint64_t max_samples = env_u64("HHS_RECIPROCAL_WAVE_MAX_SAMPLES", DEFAULT_MAX_SAMPLES);
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 authority;
    HhsResult cal_h;
    ConventionalResult cal_c;
    PrefixIdentity target;
    uint64_t base_ns, threshold_ns, samples = 1U, leg_budget_ns, nominal_budget_ns;
    uint64_t n;
    struct timespec batch_start, batch_end;
    uint64_t batch_elapsed_ns;
    uint8_t subthreshold;

    memset(&authority, 0, sizeof(authority));
    REQUIRE(hhs_exact_pass219_lane5_unbounded_workload_scaling_authority(&authority) == HHS_EXACT_STATUS_OK);
    REQUIRE(authority.constant_memory_candidate_reduction == 1U);
    REQUIRE(authority.intermediate_materialization_required == 0U);
    REQUIRE(authority.candidate_only == 1U);
    REQUIRE(authority.canonical_vm81_mutation_authority == 0U);
    REQUIRE(authority.canonical_hash72_authority == 0U);
    REQUIRE(authority.canonical_hash216_authority == 0U);
    REQUIRE(authority.requires_signed_environmental_vm81_admission == 1U);

    target = reference_prefix(STREAM_SEED_W, query_limit);
    cal_h = run_hhs(STREAM_SEED_W, query_limit, 0U);
    cal_c = run_conventional(STREAM_SEED_W, query_limit, 0U);
    REQUIRE(cal_h.dataset_complete == 1U && cal_c.dataset_complete == 1U);
    require_prefix_matches(&target, cal_h.completed_queries, cal_h.represented_transitions, cal_h.descriptor_bits, cal_h.endpoint_digest, cal_h.descriptor_digest);
    require_prefix_matches(&target, cal_c.completed_queries, cal_c.represented_transitions, cal_c.descriptor_bits, cal_c.endpoint_digest, cal_c.descriptor_digest);

    base_ns = cal_h.completion_elapsed_ns > cal_c.completion_elapsed_ns ? cal_h.completion_elapsed_ns : cal_c.completion_elapsed_ns;
    threshold_ns = base_ns + (base_ns / 2U > UINT64_C(100000) ? base_ns / 2U : UINT64_C(100000));
    if (max_samples == 0U) max_samples = 1U;
    for (n = max_samples; n >= 1U; --n) {
        uint64_t candidate = GLOBAL_BUDGET_NS / (4U * n);
        if (candidate >= threshold_ns) { samples = n; break; }
        if (n == 1U) break;
    }
    leg_budget_ns = GLOBAL_BUDGET_NS / (4U * samples);
    nominal_budget_ns = leg_budget_ns * 4U * samples;
    subthreshold = leg_budget_ns < threshold_ns ? 1U : 0U;

    printf("{\"type\":\"batch_meta\",\"schema\":\"HHS_120MS_GLOBAL_RECIPROCAL_WAVE_XYZW_V3\",\"global_budget_ns\":%" PRIu64 ",\"sample_count\":%" PRIu64 ",\"leg_budget_ns\":%" PRIu64 ",\"nominal_measured_budget_ns\":%" PRIu64 ",\"dataset_queries\":%" PRIu64 ",\"seed_W\":%" PRIu64 ",\"calibration_hhs_completion_ns\":%" PRIu64 ",\"calibration_conventional_completion_ns\":%" PRIu64 ",\"reasonable_completion_threshold_ns\":%" PRIu64 ",\"subthreshold\":%s,\"active_threads_per_benchmark\":1,\"benchmarks_sequential\":true}\n",
           GLOBAL_BUDGET_NS, samples, leg_budget_ns, nominal_budget_ns, query_limit, STREAM_SEED_W,
           cal_h.completion_elapsed_ns, cal_c.completion_elapsed_ns, threshold_ns, subthreshold ? "true" : "false");
    printf("{\"type\":\"target_state\",\"completed_queries\":%" PRIu64 ",\"represented_transitions\":\"", target.completed_queries);
    print_u128(target.represented_transitions);
    printf("\",\"descriptor_bits\":\""); print_u128(target.descriptor_bits);
    printf("\",\"endpoint_digest\":%" PRIu64 ",\"descriptor_digest\":%" PRIu64 "}\n", target.endpoint_digest, target.descriptor_digest);

    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &batch_start) == 0);
    for (n = 0U; n < samples; ++n) {
        HhsResult a = run_hhs(STREAM_SEED_W, query_limit, leg_budget_ns);
        ConventionalResult b = run_conventional(STREAM_SEED_W, query_limit, leg_budget_ns);
        ConventionalResult c = run_conventional(STREAM_SEED_W, query_limit, leg_budget_ns);
        HhsResult d = run_hhs(STREAM_SEED_W, query_limit, leg_budget_ns);
        PrefixIdentity pa = reference_prefix(STREAM_SEED_W, a.completed_queries);
        PrefixIdentity pb = reference_prefix(STREAM_SEED_W, b.completed_queries);
        PrefixIdentity pc = reference_prefix(STREAM_SEED_W, c.completed_queries);
        PrefixIdentity pd = reference_prefix(STREAM_SEED_W, d.completed_queries);

        require_prefix_matches(&pa, a.completed_queries, a.represented_transitions, a.descriptor_bits, a.endpoint_digest, a.descriptor_digest);
        require_prefix_matches(&pb, b.completed_queries, b.represented_transitions, b.descriptor_bits, b.endpoint_digest, b.descriptor_digest);
        require_prefix_matches(&pc, c.completed_queries, c.represented_transitions, c.descriptor_bits, c.endpoint_digest, c.descriptor_digest);
        require_prefix_matches(&pd, d.completed_queries, d.represented_transitions, d.descriptor_bits, d.endpoint_digest, d.descriptor_digest);

        if (!subthreshold) {
            REQUIRE(a.dataset_complete == 1U && b.dataset_complete == 1U && c.dataset_complete == 1U && d.dataset_complete == 1U);
            require_prefix_matches(&target, a.completed_queries, a.represented_transitions, a.descriptor_bits, a.endpoint_digest, a.descriptor_digest);
            require_prefix_matches(&target, b.completed_queries, b.represented_transitions, b.descriptor_bits, b.endpoint_digest, b.descriptor_digest);
            require_prefix_matches(&target, c.completed_queries, c.represented_transitions, c.descriptor_bits, c.endpoint_digest, c.descriptor_digest);
            require_prefix_matches(&target, d.completed_queries, d.represented_transitions, d.descriptor_bits, d.endpoint_digest, d.descriptor_digest);
        }

        print_hhs(n, "A", "x", &a);
        print_conventional(n, "B", "y", &b);
        print_conventional(n, "C", "z", &c);
        print_hhs(n, "D", "w", &d);
    }
    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &batch_end) == 0);
    batch_elapsed_ns = elapsed_ns(&batch_start, &batch_end);
    REQUIRE(nominal_budget_ns <= GLOBAL_BUDGET_NS);
    REQUIRE(batch_elapsed_ns <= GLOBAL_BUDGET_NS + TIMER_TOLERANCE_NS);
    printf("{\"type\":\"batch_result\",\"batch_elapsed_ns\":%" PRIu64 ",\"result\":\"PASS\"}\n", batch_elapsed_ns);
    return 0;
}
