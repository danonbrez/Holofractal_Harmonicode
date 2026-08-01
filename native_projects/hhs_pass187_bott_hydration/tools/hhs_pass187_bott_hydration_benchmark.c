#define _POSIX_C_SOURCE 200809L
#include "hhs_pass186_x64_vm81_q144_abi.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SAMPLES 7U

static uint64_t now_ns(void) {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
        perror("clock_gettime");
        exit(2);
    }
    return (uint64_t)ts.tv_sec * UINT64_C(1000000000) + (uint64_t)ts.tv_nsec;
}

static uint8_t bott_step(uint8_t q) {
    uint32_t value = (uint32_t)q & UINT32_C(7);
    uint32_t mismatch = (((value >> 2U) ^ (value >> 1U)) & UINT32_C(1));
    uint32_t mask = mismatch - UINT32_C(1);
    return (uint8_t)(((value ^ UINT32_C(1)) & mask) & UINT32_C(7));
}

static int compare_u64(const void *a, const void *b) {
    const uint64_t left = *(const uint64_t *)a;
    const uint64_t right = *(const uint64_t *)b;
    return (left > right) - (left < right);
}

int main(void) {
    uint64_t samples[SAMPLES];
    uint64_t checksum_reference = 0;
    uint64_t active_reference = 0;
    uint64_t collapse_reference = 0;
    uint64_t fixed_gear_reference = 0;
    uint32_t sample;

    for (sample = 0; sample < SAMPLES; ++sample) {
        uint64_t checksum = UINT64_C(1469598103934665603);
        uint64_t active = 0;
        uint64_t collapse = 0;
        uint64_t fixed_gear = 0;
        uint32_t projected;
        const uint64_t started = now_ns();

        for (projected = 0; projected < HHS186_HYDRATED_STATES; ++projected) {
            HHS186Quantization q;
            HHS186MappingResult current;
            HHS186Quantization next_q;
            HHS186MappingResult next;
            uint8_t basis;
            uint8_t next_basis;
            uint8_t next_operation;
            uint32_t next_state;
            uint32_t next_projected;

            if (hhs186_x64_vm81_q144_unproject(projected, &q, &current) != HHS186_STATUS_OK) {
                fprintf(stderr, "unproject failed at %" PRIu32 "\n", projected);
                return 3;
            }
            basis = current.ordered_basis;
            next_basis = bott_step(basis);
            next_operation = (uint8_t)((current.operation_class8 << 3U) | next_basis);
            next_state = (uint32_t)current.vm81_cell * HHS186_VM81_OPERATIONS_PER_CELL + next_operation;
            next_projected = next_state * HHS186_G243_CONTROLS + current.g243;

            if (hhs186_x64_vm81_q144_unproject(next_projected, &next_q, &next) != HHS186_STATUS_OK) {
                fprintf(stderr, "next unproject failed at %" PRIu32 "\n", projected);
                return 4;
            }
            if (next.g243 != current.g243 || next.vm81_cell != current.vm81_cell ||
                next.operation_class8 != current.operation_class8 || next.ordered_basis != next_basis) {
                fprintf(stderr, "coordinate drift at %" PRIu32 "\n", projected);
                return 5;
            }
            if (basis == 0U || basis == 1U || basis == 6U || basis == 7U) {
                if (bott_step(next_basis) != basis) {
                    fprintf(stderr, "period-two failure at %" PRIu32 "\n", projected);
                    return 6;
                }
                ++active;
            } else {
                if (next_basis != 0U) {
                    fprintf(stderr, "collapse failure at %" PRIu32 "\n", projected);
                    return 7;
                }
                ++collapse;
            }
            if (next.g243 == current.g243) {
                ++fixed_gear;
            }
            checksum ^= (uint64_t)next_projected + ((uint64_t)basis << 32U) + (uint64_t)next_basis;
            checksum *= UINT64_C(1099511628211);
        }
        samples[sample] = now_ns() - started;
        if (sample == 0U) {
            checksum_reference = checksum;
            active_reference = active;
            collapse_reference = collapse;
            fixed_gear_reference = fixed_gear;
        } else if (checksum != checksum_reference || active != active_reference ||
                   collapse != collapse_reference || fixed_gear != fixed_gear_reference) {
            fprintf(stderr, "nondeterministic benchmark result\n");
            return 8;
        }
    }

    qsort(samples, SAMPLES, sizeof(samples[0]), compare_u64);
    {
        const uint64_t median = samples[SAMPLES / 2U];
        const uint64_t p95 = samples[SAMPLES - 1U];
        const uint64_t states_per_second =
            ((uint64_t)HHS186_HYDRATED_STATES * UINT64_C(1000000000)) / median;
        printf("{\n");
        printf("  \"schema\": \"HHS_PASS_187_BOTT_HYDRATION_BENCHMARK_V1\",\n");
        printf("  \"classification\": \"HHS_PASS_187_BOTT_HYDRATION_SWEEP_VERIFIED\",\n");
        printf("  \"hydrated_states\": %u,\n", HHS186_HYDRATED_STATES);
        printf("  \"samples\": %u,\n", SAMPLES);
        printf("  \"median_ns_nonauthoritative\": %" PRIu64 ",\n", median);
        printf("  \"p95_ns_nonauthoritative\": %" PRIu64 ",\n", p95);
        printf("  \"states_per_second_median_nonauthoritative\": %" PRIu64 ",\n", states_per_second);
        printf("  \"active_period_two_states\": %" PRIu64 ",\n", active_reference);
        printf("  \"drift_collapse_states\": %" PRIu64 ",\n", collapse_reference);
        printf("  \"gear_preserved_states\": %" PRIu64 ",\n", fixed_gear_reference);
        printf("  \"deterministic_checksum_u64\": \"%016" PRIx64 "\",\n", checksum_reference);
        printf("  \"floating_point_authority\": false,\n");
        printf("  \"host_timing_authority\": \"NONAUTHORITATIVE\"\n");
        printf("}\n");
    }
    return 0;
}
