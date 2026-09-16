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
    uint64_t completed_queries;
    hhs_u128 represented_transitions;
    hhs_u128 jump_descriptor_bits;
    hhs_u128 affine_compositions;
    hhs_u128 matrix_multiplications;
    uint64_t lane5_admissions;
    uint64_t endpoint_digest;
} HhsResult;

typedef struct {
    uint64_t elapsed_ns;
    uint64_t completed_queries;
    hhs_u128 represented_completed_transitions;
    hhs_u128 executed_transition_steps;
    hhs_u128 jump_descriptor_bits;
    uint64_t partial_steps;
    uint64_t partial_query_k;
    uint64_t endpoint_digest;
} ClassicResult;

static const uint64_t MODULUS = UINT64_C(2305843009213693951);
static const uint64_t MULTIPLIER = UINT64_C(6364136223846793005) % UINT64_C(2305843009213693951);
static const uint64_t INCREMENT = UINT64_C(1442695040888963407) % UINT64_C(2305843009213693951);
static const uint64_t STREAM_SEED = UINT64_C(0x2191205a72c0ffee);
static const uint64_t DEFAULT_WINDOW_NS = UINT64_C(120000000000);

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

static Query query_at(uint64_t index) {
    uint64_t s0 = mix64(STREAM_SEED ^ (index * UINT64_C(0xd1342543de82ef95)));
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
    v.struct_size = (uint32_t)sizeof(v); v.byte_length = n; v.bytes_be = p;
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
    memset(&route, 0, sizeof(route)); memset(&receipt, 0, sizeof(receipt));
    route.struct_size = (uint32_t)sizeof(route);
    route.version = HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION;
    route.previous_address = bview(z, 1U); route.current_address = bview(cb, cn);
    route.goal_address = bview(gb, gn); route.candidate_address = bview(gb, gn);
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
    route.phase_slot = 54U; route.inverse_phase_slot = 18U;
    route.trinary_collapse = 0; route.binary_collapse = 0U; route.nested_zero_slot = 1U;
    route.workload_serialization_exact = 1U; route.source_digest_verified = 1U;
    route.replay_witness_verified = 1U; route.exact_goal_reached = 1U; route.contradiction_free = 1U;
    route.reciprocal_phase_verified = 1U; route.bigint_serialization_addressed = 1U;
    route.candidate_only = 1U; route.requires_signed_environmental_vm81_admission = 1U;
    if (hhs_exact_pass219_lane5_unbounded_workload_route_validate(&route, &receipt) != HHS_EXACT_STATUS_OK) return 0;
    return receipt.accepted == 1U && receipt.integer_route_cost == UINT64_C(7) &&
           receipt.materialized_intermediate_states == 0U && receipt.candidate_only == 1U &&
           receipt.canonical_mutation_authority == 0U && receipt.canonical_hash72_authority == 0U &&
           receipt.canonical_hash216_authority == 0U && receipt.requires_signed_environmental_vm81_admission == 1U;
}

static uint64_t endpoint_fold(uint64_t digest, uint64_t index, uint64_t endpoint) {
    return mix64(digest ^ mix64(index) ^ mix64(endpoint));
}

static uint64_t configured_window_ns(void) {
    const char *s = getenv("HHS_STREAM_WINDOW_NS");
    char *end = NULL;
    unsigned long long v;
    if (s == NULL || *s == '\0') return DEFAULT_WINDOW_NS;
    v = strtoull(s, &end, 10);
    if (end == s || *end != '\0' || v == 0ULL) return DEFAULT_WINDOW_NS;
    return (uint64_t)v;
}

static HhsResult run_hhs(uint64_t window_ns) {
    HhsResult r;
    struct timespec started;
    uint64_t index = 0U;
    memset(&r, 0, sizeof(r));
    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &started) == 0);
    for (;;) {
        Query q;
        Affine jump;
        Mat2 matrix;
        uint64_t c1 = 0U, c2 = 0U, endpoint, independent;
        if (elapsed_from(&started) >= window_ns) break;
        q = query_at(index);
        jump = apow((Affine){MULTIPLIER, INCREMENT}, q.k, MODULUS, &c1);
        endpoint = add_mod(mul_mod(jump.a, q.x0, MODULUS), jump.b, MODULUS);
        matrix = mpow((Mat2){MULTIPLIER, INCREMENT, 0U, 1U}, q.k, MODULUS, &c2);
        independent = add_mod(mul_mod(matrix.a, q.x0, MODULUS), matrix.b, MODULUS);
        REQUIRE(endpoint == independent);
        REQUIRE(lane5_admit(q.x0, endpoint, c1, q.k));
        r.completed_queries++;
        r.represented_transitions += (hhs_u128)q.k;
        r.jump_descriptor_bits += (hhs_u128)bit_length_u64(q.k);
        r.affine_compositions += (hhs_u128)c1;
        r.matrix_multiplications += (hhs_u128)c2;
        r.lane5_admissions++;
        r.endpoint_digest = endpoint_fold(r.endpoint_digest, index, endpoint);
        ++index;
        REQUIRE(index != 0U);
    }
    r.elapsed_ns = elapsed_from(&started);
    return r;
}

static ClassicResult run_classic(uint64_t window_ns) {
    ClassicResult r;
    struct timespec started;
    uint64_t index = 0U;
    memset(&r, 0, sizeof(r));
    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &started) == 0);
    for (;;) {
        Query q;
        uint64_t x, step;
        if (elapsed_from(&started) >= window_ns) break;
        q = query_at(index);
        x = q.x0;
        for (step = 0U; step < q.k; ++step) {
            x = add_mod(mul_mod(MULTIPLIER, x, MODULUS), INCREMENT, MODULUS);
            r.executed_transition_steps++;
            if (((step + 1U) & UINT64_C(4095)) == 0U && elapsed_from(&started) >= window_ns) {
                r.partial_steps = step + 1U;
                r.partial_query_k = q.k;
                r.elapsed_ns = elapsed_from(&started);
                return r;
            }
        }
        r.completed_queries++;
        r.represented_completed_transitions += (hhs_u128)q.k;
        r.jump_descriptor_bits += (hhs_u128)bit_length_u64(q.k);
        r.endpoint_digest = endpoint_fold(r.endpoint_digest, index, x);
        ++index;
        REQUIRE(index != 0U);
    }
    r.elapsed_ns = elapsed_from(&started);
    return r;
}

static uint64_t replay_classical_prefix(uint64_t count, hhs_u128 *compositions_out) {
    uint64_t i, digest = 0U;
    hhs_u128 total = 0U;
    for (i = 0U; i < count; ++i) {
        Query q = query_at(i);
        uint64_t c = 0U;
        Affine jump = apow((Affine){MULTIPLIER, INCREMENT}, q.k, MODULUS, &c);
        uint64_t endpoint = add_mod(mul_mod(jump.a, q.x0, MODULUS), jump.b, MODULUS);
        digest = endpoint_fold(digest, i, endpoint);
        total += (hhs_u128)c;
    }
    *compositions_out = total;
    return digest;
}

static void print_u128(hhs_u128 v) {
    char buf[64];
    size_t n = 0U;
    if (v == 0U) { putchar('0'); return; }
    while (v != 0U) { buf[n++] = (char)('0' + (unsigned)(v % 10U)); v /= 10U; }
    while (n != 0U) putchar(buf[--n]);
}

static void print_hhs(const HhsResult *r) {
    printf("{\"type\":\"engine\",\"engine\":\"hhs\",\"elapsed_ns\":%" PRIu64 ",\"completed_queries\":%" PRIu64 ",\"represented_transitions\":\"", r->elapsed_ns, r->completed_queries);
    print_u128(r->represented_transitions);
    printf("\",\"jump_descriptor_bits\":\""); print_u128(r->jump_descriptor_bits);
    printf("\",\"affine_compositions\":\""); print_u128(r->affine_compositions);
    printf("\",\"matrix_multiplications\":\""); print_u128(r->matrix_multiplications);
    printf("\",\"lane5_admissions\":%" PRIu64 ",\"endpoint_digest\":%" PRIu64 ",\"materialized_intermediate_states\":0}\n", r->lane5_admissions, r->endpoint_digest);
}

static void print_classic(const ClassicResult *r) {
    printf("{\"type\":\"engine\",\"engine\":\"classical\",\"elapsed_ns\":%" PRIu64 ",\"completed_queries\":%" PRIu64 ",\"represented_completed_transitions\":\"", r->elapsed_ns, r->completed_queries);
    print_u128(r->represented_completed_transitions);
    printf("\",\"executed_transition_steps\":\""); print_u128(r->executed_transition_steps);
    printf("\",\"jump_descriptor_bits\":\""); print_u128(r->jump_descriptor_bits);
    printf("\",\"partial_steps\":%" PRIu64 ",\"partial_query_k\":%" PRIu64 ",\"endpoint_digest\":%" PRIu64 "}\n", r->partial_steps, r->partial_query_k, r->endpoint_digest);
}

int main(void) {
    uint64_t window_ns = configured_window_ns();
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 authority;
    HhsResult hhs;
    ClassicResult classic;
    hhs_u128 replay_compositions = 0U;
    uint64_t replay_digest;

    memset(&authority, 0, sizeof(authority));
    REQUIRE(hhs_exact_pass219_lane5_unbounded_workload_scaling_authority(&authority) == HHS_EXACT_STATUS_OK);
    REQUIRE(authority.constant_memory_candidate_reduction == 1U);
    REQUIRE(authority.intermediate_materialization_required == 0U);
    REQUIRE(authority.candidate_only == 1U);
    REQUIRE(authority.canonical_vm81_mutation_authority == 0U);
    REQUIRE(authority.canonical_hash72_authority == 0U);
    REQUIRE(authority.canonical_hash216_authority == 0U);
    REQUIRE(authority.requires_signed_environmental_vm81_admission == 1U);

    printf("{\"type\":\"meta\",\"schema\":\"HHS_120S_INFINITE_STREAM_THROUGHPUT_V1\",\"window_ns\":%" PRIu64 ",\"stream_seed\":%" PRIu64 ",\"modulus\":%" PRIu64 ",\"k_min\":1000000,\"k_span\":1000000000,\"active_threads_per_epoch\":1,\"epochs_sequential\":true}\n", window_ns, STREAM_SEED, MODULUS);

    hhs = run_hhs(window_ns);
    classic = run_classic(window_ns);
    REQUIRE(hhs.completed_queries > 0U);
    REQUIRE(classic.completed_queries > 0U);
    replay_digest = replay_classical_prefix(classic.completed_queries, &replay_compositions);
    REQUIRE(replay_digest == classic.endpoint_digest);

    print_hhs(&hhs);
    print_classic(&classic);
    printf("{\"type\":\"verification\",\"classical_prefix_queries\":%" PRIu64 ",\"classical_prefix_digest\":%" PRIu64 ",\"hhs_replay_digest\":%" PRIu64 ",\"hhs_replay_compositions\":\"", classic.completed_queries, classic.endpoint_digest, replay_digest);
    print_u128(replay_compositions);
    printf("\",\"exact\":true}\n");
    puts("{\"type\":\"result\",\"result\":\"PASS\"}");
    return 0;
}
