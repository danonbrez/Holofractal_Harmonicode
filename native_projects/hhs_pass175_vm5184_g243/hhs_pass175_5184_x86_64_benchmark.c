#define _POSIX_C_SOURCE 200809L
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>

#define STATE_COUNT 5184u
#define REPEATS 20000u

static const uint8_t basis_phase[8] = {18,54,18,54,0,36,0,36};

static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63u;
    return (x << r) | (x >> ((64u - r) & 63u));
}

static inline uint8_t oriented_phase(uint8_t l, uint8_t r) {
    if (l == 0 && r == 1) return 0;
    if (l == 1 && r == 0) return 36;
    if (l == 2 && r == 3) return 0;
    if (l == 3 && r == 2) return 36;
    if ((l == 4 && r == 5) || (l == 5 && r == 4)) return 36;
    if ((l == 6 && r == 7) || (l == 7 && r == 6)) return 36;
    if ((l == 4 && r == 6) || (l == 6 && r == 4)) return 0;
    if ((l == 5 && r == 7) || (l == 7 && r == 5)) return 0;
    return (uint8_t)((basis_phase[l] + basis_phase[r]) % 72u);
}

static inline uint64_t transition(uint32_t state, uint64_t acc) {
    uint32_t cell = state / 64u;
    uint32_t slot = state % 64u;
    uint8_t left = (uint8_t)(slot / 8u);
    uint8_t right = (uint8_t)(slot % 8u);
    uint8_t phase = oriented_phase(left, right);
    uint64_t P = (uint64_t)cell + 1u;
    uint64_t P2 = P * P;
    uint64_t P4 = P2 * P2;
    uint64_t word = ((uint64_t)(state + 1u) * UINT64_C(0x9E3779B185EBCA87))
                  ^ (P4 << (slot % 13u))
                  ^ ((uint64_t)phase << 48u);
    return rotl64(acc ^ word, (unsigned)((phase + cell + slot) & 63u));
}

static uint64_t elapsed_ns(struct timespec a, struct timespec b) {
    return (uint64_t)(b.tv_sec - a.tv_sec) * UINT64_C(1000000000)
         + (uint64_t)(b.tv_nsec - a.tv_nsec);
}

int main(void) {
    struct timespec start, end;
    volatile uint64_t acc = UINT64_C(0x4848533531383451);
    clock_gettime(CLOCK_MONOTONIC, &start);
    for (uint32_t repeat = 0; repeat < REPEATS; ++repeat) {
        for (uint32_t state = 0; state < STATE_COUNT; ++state) {
            acc = transition(state, acc);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    uint64_t ns = elapsed_ns(start, end);
    uint64_t transitions = (uint64_t)STATE_COUNT * (uint64_t)REPEATS;
    double per_second = (double)transitions * 1000000000.0 / (double)ns;
    printf("{\"states\":%u,\"repeats\":%u,\"transitions\":%" PRIu64
           ",\"elapsed_ns\":%" PRIu64 ",\"transitions_per_second\":%.3f,"
           "\"checksum\":\"%016" PRIx64 "\"}\n",
           STATE_COUNT, REPEATS, transitions, ns, per_second, (uint64_t)acc);
    return 0;
}
