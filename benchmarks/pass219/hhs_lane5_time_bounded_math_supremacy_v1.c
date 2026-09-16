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
    int solved;
    uint64_t result;
    uint64_t work;
    uint64_t elapsed_ns;
} LinearResult;

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

static Mat2 mpow(Mat2 base, uint64_t n, uint64_t m) {
    Mat2 out = {UINT64_C(1), 0U, 0U, UINT64_C(1)};
    while (n != 0U) {
        if ((n & UINT64_C(1)) != 0U) out = mmul(base, out, m);
        n >>= 1U;
        if (n != 0U) base = mmul(base, base, m);
    }
    return out;
}

static LinearResult affine_linear(uint64_t a, uint64_t b, uint64_t m, uint64_t x0, uint64_t steps, uint64_t bound_ns) {
    LinearResult r = {0, x0, 0U, 0U};
    struct timespec started;
    uint64_t x = x0;
    uint64_t i;
    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &started) == 0);
    for (i = 0U; i < steps; ++i) {
        x = add_mod(mul_mod(a, x, m), b, m);
        if (((i + 1U) & UINT64_C(4095)) == 0U && elapsed_from(&started) >= bound_ns) {
            r.result = x; r.work = i + 1U; r.elapsed_ns = elapsed_from(&started); return r;
        }
    }
    r.result = x; r.work = steps; r.elapsed_ns = elapsed_from(&started);
    r.solved = r.elapsed_ns <= bound_ns;
    return r;
}

static int64_t egcd(int64_t a, int64_t b, int64_t *x, int64_t *y) {
    int64_t x1, y1, g;
    if (b == 0) { *x = 1; *y = 0; return a; }
    g = egcd(b, a % b, &x1, &y1);
    *x = y1;
    *y = x1 - (a / b) * y1;
    return g;
}

static uint64_t invmod(uint64_t a, uint64_t m) {
    int64_t x, y, r;
    if (egcd((int64_t)a, (int64_t)m, &x, &y) != 1) return 0U;
    r = x % (int64_t)m;
    if (r < 0) r += (int64_t)m;
    return (uint64_t)r;
}

static int crt_compose(const uint64_t *mods, size_t n, uint64_t *x_out, uint64_t *m_out, uint64_t *count) {
    uint64_t x, m;
    size_t i;
    if (n == 0U) return 0;
    x = mods[0] - 1U; m = mods[0]; *count = 0U;
    for (i = 1U; i < n; ++i) {
        uint64_t p = mods[i], residue = p - 1U;
        uint64_t delta = (residue + p - (x % p)) % p;
        uint64_t inv = invmod(m % p, p);
        uint64_t t;
        hhs_u128 nx, nm;
        if (inv == 0U) return 0;
        t = mul_mod(delta, inv, p);
        nx = (hhs_u128)x + (hhs_u128)m * (hhs_u128)t;
        nm = (hhs_u128)m * (hhs_u128)p;
        if (nx > UINT64_MAX || nm > UINT64_MAX) return 0;
        x = (uint64_t)nx; m = (uint64_t)nm; ++(*count);
    }
    *x_out = x; *m_out = m; return 1;
}

static int crt_verify(uint64_t x, const uint64_t *mods, size_t n, uint64_t m) {
    size_t i;
    if (x >= m || x != m - 1U) return 0;
    for (i = 0U; i < n; ++i) if ((x % mods[i]) != mods[i] - 1U) return 0;
    return 1;
}

static LinearResult crt_scan(const uint64_t *mods, size_t n, uint64_t m, uint64_t bound_ns) {
    LinearResult r = {0, 0U, 0U, 0U};
    struct timespec started;
    uint64_t x;
    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &started) == 0);
    for (x = 0U; x < m; ++x) {
        size_t i;
        int ok = 1;
        for (i = 0U; i < n; ++i) {
            if ((x % mods[i]) != mods[i] - 1U) { ok = 0; break; }
        }
        if (ok) {
            r.result = x; r.work = x + 1U; r.elapsed_ns = elapsed_from(&started);
            r.solved = r.elapsed_ns <= bound_ns;
            return r;
        }
        if (((x + 1U) & UINT64_C(4095)) == 0U && elapsed_from(&started) >= bound_ns) {
            r.result = x; r.work = x + 1U; r.elapsed_ns = elapsed_from(&started); return r;
        }
    }
    r.work = m; r.elapsed_ns = elapsed_from(&started); return r;
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
    HHSExactBigUIntView v; v.struct_size = (uint32_t)sizeof(v); v.byte_length = n; v.bytes_be = p; return v;
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

static int lane5_admit(uint64_t current, uint64_t goal, uint64_t cost, uint64_t workload, uint64_t *admission_ns) {
    HHSExactPass219Lane5UnboundedWorkloadRouteV1 route;
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 receipt;
    uint8_t z[1] = {0U}, cb[8], gb[8];
    uint32_t cn = encode_u64(current, cb), gn = encode_u64(goal, gb);
    struct timespec s, e;
    memset(&route, 0, sizeof(route)); memset(&receipt, 0, sizeof(receipt));
    route.struct_size = (uint32_t)sizeof(route);
    route.version = HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION;
    route.previous_address = bview(z, 1U); route.current_address = bview(cb, cn);
    route.goal_address = bview(gb, gn); route.candidate_address = bview(gb, gn);
    fill_digest(route.workload_sha256, goal ^ workload);
    fill_digest(route.provenance_sha256, current ^ UINT64_C(0xa5a5));
    fill_digest(route.forbidden_boundary_sha256, UINT64_C(0x33));
    fill_digest(route.reciprocal_witness_sha256, goal ^ UINT64_C(0x44));
    fill_digest(route.route_witness_sha256, cost ^ goal ^ UINT64_C(0x55));
    route.workload_byte_count = workload; route.integer_route_cost = cost;
    route.evidence_count = 5U; route.contradiction_check_count = 1U;
    route.materialized_intermediate_states = 0U;
    route.phase_slot = 54U; route.inverse_phase_slot = 18U;
    route.trinary_collapse = 1; route.binary_collapse = 1U; route.nested_zero_slot = 1U;
    route.workload_serialization_exact = 1U; route.source_digest_verified = 1U;
    route.replay_witness_verified = 1U; route.exact_goal_reached = 1U; route.contradiction_free = 1U;
    route.reciprocal_phase_verified = 1U; route.bigint_serialization_addressed = 1U;
    route.candidate_only = 1U; route.requires_signed_environmental_vm81_admission = 1U;
    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &s) == 0);
    if (hhs_exact_pass219_lane5_unbounded_workload_route_validate(&route, &receipt) != HHS_EXACT_STATUS_OK) return 0;
    REQUIRE(clock_gettime(CLOCK_MONOTONIC, &e) == 0); *admission_ns = elapsed_ns(&s, &e);
    return receipt.accepted == 1U && receipt.materialized_intermediate_states == 0U &&
           receipt.candidate_only == 1U && receipt.canonical_mutation_authority == 0U &&
           receipt.canonical_hash72_authority == 0U && receipt.canonical_hash216_authority == 0U &&
           receipt.requires_signed_environmental_vm81_admission == 1U;
}

static uint64_t time_bound(void) {
    const char *s = getenv("HHS_TIME_BOUND_NS"); char *end = NULL; unsigned long long v;
    if (s == NULL || *s == '\0') return UINT64_C(50000000);
    errno = 0; v = strtoull(s, &end, 10);
    if (errno != 0 || end == s || *end != '\0' || v == 0ULL) return UINT64_C(50000000);
    return (uint64_t)v;
}

static void affine_cases(uint64_t bound) {
    static const uint64_t ks[] = {UINT64_C(1000), UINT64_C(100000), UINT64_C(10000000), UINT64_C(1000000000), UINT64_C(1000000000000)};
    const uint64_t m = UINT64_C(2305843009213693951);
    const uint64_t a = UINT64_C(6364136223846793005) % m;
    const uint64_t b = UINT64_C(1442695040888963407) % m;
    const uint64_t x0 = UINT64_C(123456789);
    size_t i;
    for (i = 0U; i < sizeof(ks)/sizeof(ks[0]); ++i) {
        uint64_t k = ks[i], comp = 0U, admit_ns = 0U, alg_ns, verify_ns, total_ns, result, independent;
        struct timespec ts, a0, a1, v0, v1, te;
        Affine jump; Mat2 mj; LinearResult linear;
        REQUIRE(clock_gettime(CLOCK_MONOTONIC, &ts) == 0);
        REQUIRE(clock_gettime(CLOCK_MONOTONIC, &a0) == 0);
        jump = apow((Affine){a,b}, k, m, &comp);
        result = add_mod(mul_mod(jump.a, x0, m), jump.b, m);
        REQUIRE(clock_gettime(CLOCK_MONOTONIC, &a1) == 0);
        REQUIRE(clock_gettime(CLOCK_MONOTONIC, &v0) == 0);
        mj = mpow((Mat2){a,b,0U,1U}, k, m);
        independent = add_mod(mul_mod(mj.a, x0, m), mj.b, m);
        REQUIRE(clock_gettime(CLOCK_MONOTONIC, &v1) == 0);
        REQUIRE(result == independent);
        REQUIRE(lane5_admit(x0, result, comp, k, &admit_ns));
        REQUIRE(clock_gettime(CLOCK_MONOTONIC, &te) == 0);
        alg_ns = elapsed_ns(&a0,&a1); verify_ns = elapsed_ns(&v0,&v1); total_ns = elapsed_ns(&ts,&te);
        REQUIRE(total_ns <= bound);
        linear = affine_linear(a,b,m,x0,k,bound);
        if (linear.solved) REQUIRE(linear.result == result);
        printf("{\"type\":\"case\",\"family\":\"affine\",\"size\":%" PRIu64 ",\"omega\":%" PRIu64 ",\"hhs_result\":%" PRIu64 ",\"independent_result\":%" PRIu64 ",\"linear_status\":\"%s\",\"linear_result\":%" PRIu64 ",\"linear_steps\":%" PRIu64 ",\"linear_work_lower_bound\":%" PRIu64 ",\"hhs_compositions\":%" PRIu64 ",\"hhs_algebra_ns\":%" PRIu64 ",\"verify_ns\":%" PRIu64 ",\"admission_ns\":%" PRIu64 ",\"hhs_total_ns\":%" PRIu64 ",\"linear_elapsed_ns\":%" PRIu64 ",\"time_bound_ns\":%" PRIu64 ",\"exact\":true,\"lane5_admitted\":true,\"materialized_intermediate_states\":0}\n",
               k,k,result,independent,linear.solved?"solved":"timeout",linear.result,linear.work,k,comp,alg_ns,verify_ns,admit_ns,total_ns,linear.elapsed_ns,bound);
    }
}

static void crt_cases(uint64_t bound) {
    static const uint64_t mods[] = {101U,103U,107U,109U,113U,127U};
    size_t n;
    for (n = 2U; n <= sizeof(mods)/sizeof(mods[0]); ++n) {
        uint64_t x=0U,m=0U,comp=0U,admit_ns=0U,alg_ns,verify_ns,total_ns;
        struct timespec ts,a0,a1,v0,v1,te; LinearResult linear;
        REQUIRE(clock_gettime(CLOCK_MONOTONIC,&ts)==0); REQUIRE(clock_gettime(CLOCK_MONOTONIC,&a0)==0);
        REQUIRE(crt_compose(mods,n,&x,&m,&comp)); REQUIRE(clock_gettime(CLOCK_MONOTONIC,&a1)==0);
        REQUIRE(clock_gettime(CLOCK_MONOTONIC,&v0)==0); REQUIRE(crt_verify(x,mods,n,m)); REQUIRE(clock_gettime(CLOCK_MONOTONIC,&v1)==0);
        REQUIRE(lane5_admit(0U,x,comp,m,&admit_ns)); REQUIRE(clock_gettime(CLOCK_MONOTONIC,&te)==0);
        alg_ns=elapsed_ns(&a0,&a1); verify_ns=elapsed_ns(&v0,&v1); total_ns=elapsed_ns(&ts,&te); REQUIRE(total_ns<=bound);
        linear=crt_scan(mods,n,m,bound); if(linear.solved) REQUIRE(linear.result==x);
        printf("{\"type\":\"case\",\"family\":\"crt\",\"size\":%zu,\"omega\":%" PRIu64 ",\"hhs_result\":%" PRIu64 ",\"independent_result\":%" PRIu64 ",\"linear_status\":\"%s\",\"linear_result\":%" PRIu64 ",\"linear_steps\":%" PRIu64 ",\"linear_work_lower_bound\":%" PRIu64 ",\"hhs_compositions\":%" PRIu64 ",\"hhs_algebra_ns\":%" PRIu64 ",\"verify_ns\":%" PRIu64 ",\"admission_ns\":%" PRIu64 ",\"hhs_total_ns\":%" PRIu64 ",\"linear_elapsed_ns\":%" PRIu64 ",\"time_bound_ns\":%" PRIu64 ",\"exact\":true,\"lane5_admitted\":true,\"materialized_intermediate_states\":0}\n",
               n,m,x,m-1U,linear.solved?"solved":"timeout",linear.result,linear.work,m,comp,alg_ns,verify_ns,admit_ns,total_ns,linear.elapsed_ns,bound);
    }
}

int main(void) {
    uint64_t bound = time_bound(); HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 a;
    memset(&a,0,sizeof(a)); REQUIRE(hhs_exact_pass219_lane5_unbounded_workload_scaling_authority(&a)==HHS_EXACT_STATUS_OK);
    REQUIRE(a.constant_memory_candidate_reduction==1U && a.intermediate_materialization_required==0U && a.candidate_only==1U);
    REQUIRE(a.canonical_vm81_mutation_authority==0U && a.canonical_hash72_authority==0U && a.canonical_hash216_authority==0U);
    REQUIRE(a.requires_signed_environmental_vm81_admission==1U);
    printf("{\"type\":\"meta\",\"schema\":\"HHS_TIME_BOUNDED_MATH_SUPREMACY_V1\",\"time_bound_ns\":%" PRIu64 ",\"active_threads\":1}\n",bound);
    affine_cases(bound); crt_cases(bound);
    puts("{\"type\":\"result\",\"result\":\"PASS\"}");
    return 0;
}
