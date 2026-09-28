#define _POSIX_C_SOURCE 200809L
#include "hhs_runtime_exact_abi.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define SAMPLES 9U
#define ITERATIONS 64U

static const int8_t scalar_symbols[9] = {-1, 4, -3, -2, 0, 2, 3, -4, 1};
static const int8_t channel_factors[4] = {1, -1, 2, -2};
static const char *channel_names[4] = {"xy", "yx", "zw", "wz"};

static uint64_t elapsed_ns(const struct timespec *start, const struct timespec *end) {
    uint64_t seconds = (uint64_t)(end->tv_sec - start->tv_sec);
    int64_t nanos = (int64_t)end->tv_nsec - (int64_t)start->tv_nsec;
    if (nanos < 0) {
        seconds -= UINT64_C(1);
        nanos += INT64_C(1000000000);
    }
    return seconds * UINT64_C(1000000000) + (uint64_t)nanos;
}

static uint64_t median9(uint64_t values[SAMPLES]) {
    uint32_t i;
    uint32_t j;
    for (i = 1U; i < SAMPLES; ++i) {
        uint64_t key = values[i];
        j = i;
        while (j > 0U && values[j - 1U] > key) {
            values[j] = values[j - 1U];
            --j;
        }
        values[j] = key;
    }
    return values[SAMPLES / 2U];
}

static void source_state(HHSExactPass220PriorityOffsetTaggedCellV1 state[81]) {
    uint32_t i;
    memset(state, 0, sizeof(*state) * 81U);
    for (i = 0U; i < 81U; ++i) {
        state[i].counted_value = (uint64_t)(i % 9U);
        state[i].phase72 = (uint8_t)((i * 8U) % 72U);
        state[i].rotation4 = (uint8_t)(i % 4U);
        state[i].source_index = (uint8_t)i;
    }
}

static HHSExactPass219Lane5MediationRequestV1 template_request(void) {
    HHSExactPass219Lane5MediationRequestV1 r;
    uint32_t i;
    memset(&r, 0, sizeof(r));
    r.struct_size = (uint32_t)sizeof(r);
    r.version = HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION;
    r.namespace_id = HHS_EXACT_PASS219_LANE5_NAMESPACE;
    r.hash216_reference_count = 3U;
    r.capability_reference_count = 4U;
    r.learning_stage = 5U;
    r.request_signature64 = UINT64_C(0x6101);
    r.candidate_signature64 = UINT64_C(0x6102);
    r.parent_hash216_signature64 = UINT64_C(0x6103);
    r.bigint_address_signature64 = UINT64_C(0x6104);
    r.hydration_signature64 = UINT64_C(0x6105);
    r.compression_signature64 = UINT64_C(0x6106);
    r.capability_registry_signature64 = UINT64_C(0x6107);
    r.learning_iteration_signature64 = UINT64_C(0x6108);
    r.rna_prepared_signature64 = UINT64_C(0x6109);
    r.rna_decision_signature64 = UINT64_C(0x6110);
    for (i = 0U; i < r.hash216_reference_count; ++i)
        r.hash216_reference_signature64[i] = UINT64_C(0x6200) + i;
    for (i = 0U; i < r.capability_reference_count; ++i)
        r.capability_reference_signature64[i] = UINT64_C(0x6300) + i;
    return r;
}

static uint32_t exponent_for(uint32_t block, uint32_t channel) {
    int value = (int)scalar_symbols[block] * (int)channel_factors[channel];
    int exponent = value % 9;
    if (exponent < 0)
        exponent += 9;
    return (uint32_t)exponent;
}

static void dense_transform(
    const HHSExactPass220PriorityOffsetTaggedCellV1 source[81],
    uint32_t channel,
    HHSExactPass220PriorityOffsetTaggedCellV1 output[81]
) {
    uint32_t block;
    for (block = 0U; block < 9U; ++block) {
        uint8_t matrix[9][9];
        uint32_t column;
        uint32_t row;
        uint32_t exponent = exponent_for(block, channel);
        uint32_t start = block * 9U;
        memset(matrix, 0, sizeof(matrix));
        for (column = 0U; column < 9U; ++column)
            matrix[(column + exponent) % 9U][column] = 1U;
        for (row = 0U; row < 9U; ++row) {
            int selected = -1;
            for (column = 0U; column < 9U; ++column) {
                if (matrix[row][column] != 0U) {
                    if (selected >= 0) {
                        selected = -2;
                        break;
                    }
                    selected = (int)column;
                }
            }
            if (selected < 0)
                memset(&output[start + row], 0, sizeof(output[start + row]));
            else
                output[start + row] = source[start + (uint32_t)selected];
        }
    }
}

static int run_once(
    int dense,
    const HHSExactPass220PriorityOffsetTaggedCellV1 source[81],
    uint32_t channel,
    const HHSExactPass219Lane5MediationRequestV1 *template_request,
    uint64_t *checksum
) {
    HHSExactPass220PriorityOffsetTaggedCellV1 transformed[81];
    HHSExactPass219Lane5MediationRequestV1 request;
    HHSExactPass219Lane5MediationReceiptV1 receipt;
    HHSExactStatus status;
    if (dense != 0) {
        dense_transform(source, channel, transformed);
    } else {
        status = hhs_exact_pass220_priority_offset_transform(
            source, channel, transformed
        );
        if (status != HHS_EXACT_STATUS_OK)
            return 0;
    }
    status = hhs_exact_pass220_priority_offset_prepare_lane5_request(
        template_request, transformed, channel, &request
    );
    if (status != HHS_EXACT_STATUS_OK)
        return 0;
    memset(&receipt, 0, sizeof(receipt));
    status = hhs_exact_pass219_lane5_mediate_candidate(&request, &receipt);
    if (status != HHS_EXACT_STATUS_OK ||
        receipt.decision != HHS_EXACT_PASS219_LANE5_DECISION_CANDIDATE_READY ||
        receipt.zero_sum_closure_passed != 1U)
        return 0;
    *checksum ^= receipt.mediation_signature64;
    return 1;
}

static uint64_t measure(
    int dense,
    const HHSExactPass220PriorityOffsetTaggedCellV1 source[81],
    uint32_t channel,
    const HHSExactPass219Lane5MediationRequestV1 *template_request,
    uint64_t *checksum
) {
    struct timespec start;
    struct timespec end;
    uint32_t i;
    if (clock_gettime(CLOCK_MONOTONIC, &start) != 0)
        return 0U;
    for (i = 0U; i < ITERATIONS; ++i) {
        if (!run_once(dense, source, channel, template_request, checksum))
            return 0U;
    }
    if (clock_gettime(CLOCK_MONOTONIC, &end) != 0)
        return 0U;
    return elapsed_ns(&start, &end);
}

int main(void) {
    HHSExactPass220PriorityOffsetTaggedCellV1 source[81];
    HHSExactPass220PriorityOffsetTaggedCellV1 dense_out[81];
    HHSExactPass220PriorityOffsetTaggedCellV1 compact_out[81];
    HHSExactPass219Lane5MediationRequestV1 template = template_request();
    uint64_t dense_median[4];
    uint64_t compact_median[4];
    uint64_t checksum = 0U;
    uint32_t channel;
    int all_equal = 1;

    source_state(source);
    for (channel = 0U; channel < 4U; ++channel) {
        uint64_t dense_samples[SAMPLES];
        uint64_t compact_samples[SAMPLES];
        uint32_t sample;
        dense_transform(source, channel, dense_out);
        if (hhs_exact_pass220_priority_offset_transform(
                source, channel, compact_out
            ) != HHS_EXACT_STATUS_OK)
            return 2;
        if (memcmp(dense_out, compact_out, sizeof(dense_out)) != 0)
            all_equal = 0;

        for (sample = 0U; sample < SAMPLES; ++sample) {
            if ((sample & 1U) == 0U) {
                dense_samples[sample] = measure(
                    1, source, channel, &template, &checksum
                );
                compact_samples[sample] = measure(
                    0, source, channel, &template, &checksum
                );
            } else {
                compact_samples[sample] = measure(
                    0, source, channel, &template, &checksum
                );
                dense_samples[sample] = measure(
                    1, source, channel, &template, &checksum
                );
            }
            if (dense_samples[sample] == 0U || compact_samples[sample] == 0U)
                return 3;
        }
        dense_median[channel] = median9(dense_samples);
        compact_median[channel] = median9(compact_samples);
    }

    printf("{");
    printf("\"schema\":\"HHS_PASS220_LANE5_PRIORITY_OFFSET_NATIVE_AB_V1\",");
    printf("\"status\":\"%s\",", all_equal ? "PASS" : "FAIL");
    printf("\"semantic_identity_all_channels\":%s,", all_equal ? "true" : "false");
    printf("\"timing_scope\":\"NATIVE_C_CANDIDATE_PREPARATION_PLUS_LANE5_HNAN_MEDIATION\",");
    printf("\"lane5_mediate_candidate_invoked\":true,");
    printf("\"hnan_global_preflight_invoked_via_lane5\":true,");
    printf("\"priority_offset_native_hydration_applied\":true,");
    printf("\"native_library_constructor_hydration_applied\":false,");
    printf("\"timing_is_canonical\":false,");
    printf("\"samples\":%u,\"iterations_per_sample\":%u,", SAMPLES, ITERATIONS);
    printf("\"logical_storage\":{");
    printf("\"dense_matrix_cells_all_channels\":2916,");
    printf("\"compact_vector_refs_all_channels\":324,");
    printf("\"compact_scalar_controls_all_channels\":36,");
    printf("\"compact_total_controls_all_channels\":360},");
    printf("\"channels\":[");
    for (channel = 0U; channel < 4U; ++channel) {
        if (channel != 0U)
            printf(",");
        printf("{");
        printf("\"channel\":\"%s\",", channel_names[channel]);
        printf("\"dense_median_batch_ns\":%" PRIu64 ",", dense_median[channel]);
        printf("\"compact_median_batch_ns\":%" PRIu64 ",", compact_median[channel]);
        printf("\"dense_median_per_candidate_ns\":%" PRIu64 ",", dense_median[channel] / ITERATIONS);
        printf("\"compact_median_per_candidate_ns\":%" PRIu64 ",", compact_median[channel] / ITERATIONS);
        printf("\"speedup_ratio_exact\":\"%" PRIu64 "/%" PRIu64 "\",", dense_median[channel], compact_median[channel]);
        printf("\"compact_faster\":%s", compact_median[channel] < dense_median[channel] ? "true" : "false");
        printf("}");
    }
    printf("],");
    printf("\"canonical_vm81_mutation_authority\":false,");
    printf("\"canonical_hash72_authority\":false,");
    printf("\"canonical_hash216_authority\":false,");
    printf("\"checksum\":%" PRIu64, checksum);
    printf("}\n");
    return all_equal ? 0 : 4;
}
