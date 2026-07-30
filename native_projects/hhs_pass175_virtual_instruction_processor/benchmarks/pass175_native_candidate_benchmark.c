#define _POSIX_C_SOURCE 200809L
#include <inttypes.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define CELLS 81u
#define OPS 64u
#define STATES (CELLS * OPS)
#define CONTROLS 243u
#define DEFAULT_LOOPS 20000u
#define DEFAULT_REPEATS 7u

static const uint8_t phase_table[OPS] = {
    0,0,36,0,54,0,54,18,36,36,18,18,36,54,54,54,
    54,54,36,36,54,36,18,54,54,0,36,0,18,36,36,0,
    54,0,0,0,54,36,18,18,0,18,54,36,18,18,0,18,
    0,36,36,54,18,18,54,36,36,18,18,0,36,54,18,36
};

static volatile uint64_t global_sink = 0;

static inline uint64_t mix64(uint64_t x) {
    x ^= x >> 30;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31;
    return x;
}

static double now_seconds(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

static int compare_double(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    return (da > db) - (da < db);
}

static double median(double *values, unsigned n) {
    qsort(values, n, sizeof(*values), compare_double);
    if (n & 1u) return values[n / 2u];
    return (values[n / 2u - 1u] + values[n / 2u]) / 2.0;
}

static inline uint64_t candidate_value(uint64_t epoch, uint32_t state) {
    uint32_t cell = state / OPS;
    uint32_t operation = state % OPS;
    uint32_t phase = phase_table[operation];
    uint32_t g = (uint32_t)((epoch + state * 17u + operation * 29u) % CONTROLS);
    uint64_t packed = (epoch << 32)
        ^ ((uint64_t)state << 19)
        ^ ((uint64_t)cell << 12)
        ^ ((uint64_t)operation << 6)
        ^ ((uint64_t)phase << 1)
        ^ (uint64_t)g;
    return mix64(packed ^ UINT64_C(0x1755184243));
}

static uint64_t serial_commit(const uint64_t *candidates, uint64_t epoch, uint64_t prior) {
    uint64_t root = mix64(prior ^ epoch ^ UINT64_C(0x484153483732));
    for (uint32_t state = 0; state < STATES; ++state) {
        root = mix64(root ^ candidates[state] ^ ((uint64_t)state << 32) ^ state);
    }
    return root;
}

static double run_candidate_only(unsigned threads, unsigned loops, uint64_t *root_out) {
    uint64_t *candidates = aligned_alloc(64, STATES * sizeof(uint64_t));
    if (!candidates) { perror("aligned_alloc"); exit(2); }
    uint64_t check = 0;
    double start = now_seconds();
    for (unsigned loop = 0; loop < loops; ++loop) {
        uint64_t epoch = UINT64_C(175000000) + loop;
        #pragma omp parallel for schedule(static) num_threads(threads)
        for (uint32_t state = 0; state < STATES; ++state) {
            candidates[state] = candidate_value(epoch, state);
        }
        check ^= candidates[(loop * 73u) % STATES];
    }
    double elapsed = now_seconds() - start;
    *root_out = mix64(check);
    global_sink ^= *root_out;
    free(candidates);
    return elapsed;
}

static double run_candidate_commit(unsigned threads, unsigned loops, uint64_t *root_out) {
    uint64_t *candidates = aligned_alloc(64, STATES * sizeof(uint64_t));
    if (!candidates) { perror("aligned_alloc"); exit(2); }
    uint64_t root = UINT64_C(0x50415353313735);
    double start = now_seconds();
    for (unsigned loop = 0; loop < loops; ++loop) {
        uint64_t epoch = UINT64_C(175000000) + loop;
        #pragma omp parallel for schedule(static) num_threads(threads)
        for (uint32_t state = 0; state < STATES; ++state) {
            candidates[state] = candidate_value(epoch, state);
        }
        /* Singular ordered commit authority: always serial state order. */
        root = serial_commit(candidates, epoch, root);
    }
    double elapsed = now_seconds() - start;
    *root_out = root;
    global_sink ^= root;
    free(candidates);
    return elapsed;
}

int main(int argc, char **argv) {
    unsigned loops = argc > 1 ? (unsigned)strtoul(argv[1], NULL, 10) : DEFAULT_LOOPS;
    unsigned repeats = argc > 2 ? (unsigned)strtoul(argv[2], NULL, 10) : DEFAULT_REPEATS;
    const unsigned requested[] = {1u, 2u, 4u, 5u};
    const unsigned cases = sizeof(requested) / sizeof(requested[0]);
    int max_threads = omp_get_max_threads();

    printf("{\n");
    printf("  \"schema\": \"HHS_PASS_175_NATIVE_CANDIDATE_BENCHMARK_V1\",\n");
    printf("  \"classification\": \"PRECONTRACT_NATIVE_CANDIDATE_EVIDENCE\",\n");
    printf("  \"states\": %u,\n", STATES);
    printf("  \"loops\": %u,\n", loops);
    printf("  \"transitions_per_run\": %" PRIu64 ",\n", (uint64_t)loops * STATES);
    printf("  \"repeats\": %u,\n", repeats);
    printf("  \"omp_max_threads\": %d,\n", max_threads);
    printf("  \"results\": [\n");

    uint64_t canonical_commit_root = 0;
    int first = 1;
    for (unsigned ci = 0; ci < cases; ++ci) {
        unsigned threads = requested[ci];
        if ((int)threads > max_threads) continue;
        double *candidate_rates = calloc(repeats, sizeof(double));
        double *end_to_end_rates = calloc(repeats, sizeof(double));
        if (!candidate_rates || !end_to_end_rates) return 3;
        uint64_t candidate_root = 0, commit_root = 0;
        int roots_stable = 1;
        uint64_t first_commit = 0;
        for (unsigned rep = 0; rep < repeats; ++rep) {
            uint64_t candidate_rep = 0, commit_rep = 0;
            double csec = run_candidate_only(threads, loops, &candidate_rep);
            double esec = run_candidate_commit(threads, loops, &commit_rep);
            candidate_rates[rep] = ((double)loops * STATES) / csec;
            end_to_end_rates[rep] = ((double)loops * STATES) / esec;
            candidate_root ^= candidate_rep;
            if (rep == 0) first_commit = commit_rep;
            roots_stable &= (commit_rep == first_commit);
            commit_root = commit_rep;
        }
        if (canonical_commit_root == 0) canonical_commit_root = commit_root;
        int cross_thread_equal = (commit_root == canonical_commit_root);
        double candidate_median = median(candidate_rates, repeats);
        double end_to_end_median = median(end_to_end_rates, repeats);
        if (!first) printf(",\n");
        first = 0;
        printf("    {\"threads\": %u, \"candidate_median_transitions_per_second\": %.3f, ", threads, candidate_median);
        printf("\"candidate_ns_per_transition\": %.6f, ", 1e9 / candidate_median);
        printf("\"end_to_end_median_transitions_per_second\": %.3f, ", end_to_end_median);
        printf("\"end_to_end_ns_per_transition\": %.6f, ", 1e9 / end_to_end_median);
        printf("\"commit_root\": \"%016" PRIx64 "\", ", commit_root);
        printf("\"repeat_roots_stable\": %s, \"cross_thread_commit_root_equal\": %s}",
               roots_stable ? "true" : "false", cross_thread_equal ? "true" : "false");
        free(candidate_rates);
        free(end_to_end_rates);
    }

    printf("\n  ],\n");
    printf("  \"canonical_commit_root\": \"%016" PRIx64 "\",\n", canonical_commit_root);
    printf("  \"parallel_candidates_singular_commit\": true,\n");
    printf("  \"global_sink\": \"%016" PRIx64 "\"\n", global_sink);
    printf("}\n");
    return 0;
}
