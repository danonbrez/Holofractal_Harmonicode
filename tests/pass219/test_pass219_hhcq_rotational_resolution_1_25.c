#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

static int only_two_three(uint16_t value) {
    uint32_t v = value;
    while ((v % 2U) == 0U)
        v /= 2U;
    while ((v % 3U) == 0U)
        v /= 3U;
    return v == 1U;
}

int main(void) {
    HHSExactPass219HHCQResolutionDescriptorV1 descriptor;
    HHSExactVM81Frame frame;
    uint8_t seen_phase[HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS];
    uint8_t seen_resolution[HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT];
    uint32_t x;
    uint32_t y;
    uint32_t i;
    uint32_t phase_count = 0U;
    uint32_t resolution_count = 0U;

    assert(hhs_exact_pass219_hhcq_resolution_version() == HHS_EXACT_PASS219_HHCQ_RESOLUTION_VERSION);
    assert(hhs_exact_pass219_hhcq_resolution_descriptor(&descriptor) == HHS_EXACT_STATUS_OK);
    assert(descriptor.parameter_count == 5184U);
    assert(descriptor.phase_modulus == 72U);
    assert(descriptor.divisor_count == 35U);
    assert(descriptor.trinary_step == 5U);
    assert(descriptor.complete_2a3b_divisor_lattice == 1U);
    assert(descriptor.ordered_xz_over_yw_phase_quotient == 1U);
    assert(descriptor.dyadic_trinary_dual_primitive == 1U);
    assert(descriptor.exact_orthogonal_decomposition == 1U);
    assert(descriptor.core_equation_constructor_bound == 1U);
    assert(descriptor.u72_rotational_ring == 1U);
    assert(descriptor.candidate_only == 1U);
    assert(descriptor.exact_integer_only == 1U);
    assert(descriptor.canonical_mutation_authority == 0U);
    assert(descriptor.canonical_hash72_authority == 0U);
    assert(descriptor.canonical_hash216_authority == 0U);
    assert(descriptor.canonical_persistence_authority == 0U);
    assert(descriptor.floating_point_authority == 0U);

    for (i = 0U; i < HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT; ++i) {
        uint16_t divisor = 0U;
        assert(hhs_exact_pass219_hhcq_resolution_divisor((uint8_t)i, &divisor) == HHS_EXACT_STATUS_OK);
        assert(divisor > 0U);
        assert((HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT % divisor) == 0U);
        assert(only_two_three(divisor));
        if (i > 0U) {
            uint16_t prior = 0U;
            assert(hhs_exact_pass219_hhcq_resolution_divisor((uint8_t)(i - 1U), &prior) == HHS_EXACT_STATUS_OK);
            assert(prior > divisor);
        }
    }
    {
        uint16_t dummy = 0U;
        assert(hhs_exact_pass219_hhcq_resolution_divisor(
            (uint8_t)HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT, &dummy) == HHS_EXACT_STATUS_RANGE_ERROR);
    }

    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        frame.words[i] = UINT64_C(0x9e3779b97f4a7c15) ^
            (UINT64_C(0x100000001b3) * (uint64_t)(i + 1U));

    memset(seen_phase, 0, sizeof(seen_phase));
    memset(seen_resolution, 0, sizeof(seen_resolution));

    for (x = 0U; x < HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS; ++x) {
        for (y = 0U; y < HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS; ++y) {
            int direction;
            for (direction = -1; direction <= 1; ++direction) {
                HHSExactPass219HHCQResolutionSelectionV1 selection;
                HHSExactStatus status = hhs_exact_pass219_hhcq_resolution_select(
                    (uint8_t)x, (uint8_t)y, UINT8_C(0), UINT8_C(0),
                    (int8_t)direction, &selection);
                assert(status == HHS_EXACT_STATUS_OK);
                assert(selection.quotient_phase72 < 72U);
                assert(selection.rotated_phase72 < 72U);
                assert(selection.resolution_index < 35U);
                assert(selection.resolution_parameters > 0U);
                assert((5184U % selection.resolution_parameters) == 0U);
                assert((uint32_t)selection.resolution_parameters * selection.region_count == 5184U);
                assert(selection.candidate_only == 1U);
                assert(selection.exact_integer_only == 1U);
                assert(selection.canonical_mutation_authority == 0U);
                assert(selection.canonical_hash72_authority == 0U);
                assert(selection.canonical_hash216_authority == 0U);
                assert(selection.canonical_persistence_authority == 0U);
                assert(selection.floating_point_authority == 0U);

                if (seen_phase[selection.quotient_phase72] == 0U) {
                    seen_phase[selection.quotient_phase72] = 1U;
                    ++phase_count;
                }
                if (seen_resolution[selection.resolution_index] == 0U) {
                    HHSExactVM81Frame reconstructed;
                    HHSExactPass219HHCQRoundtripReportV1 report;
                    HHSExactPass219HHCQParameterCoordinateV1 first;
                    HHSExactPass219HHCQParameterCoordinateV1 last;
                    seen_resolution[selection.resolution_index] = 1U;
                    ++resolution_count;
                    assert(hhs_exact_pass219_hhcq_parameter_locate(&selection, 0U, &first) == HHS_EXACT_STATUS_OK);
                    assert(hhs_exact_pass219_hhcq_parameter_locate(&selection, 5183U, &last) == HHS_EXACT_STATUS_OK);
                    assert(first.region_index == 0U && first.local_offset == 0U);
                    assert((uint32_t)last.region_start + last.local_offset == 5183U);
                    assert(hhs_exact_pass219_hhcq_decompose_recompose(
                        &frame, &selection, &reconstructed, &report) == HHS_EXACT_STATUS_OK);
                    assert(memcmp(&frame, &reconstructed, sizeof(frame)) == 0);
                    assert(report.parameters_visited == 5184U);
                    assert(report.orthogonal_partition_complete == 1U);
                    assert(report.no_overlap == 1U);
                    assert(report.no_gap == 1U);
                    assert(report.exact_recomposition == 1U);
                    assert(report.candidate_only == 1U);
                    assert(report.exact_integer_only == 1U);
                    assert(report.canonical_authority_changed == 0U);
                    assert(report.floating_point_authority == 0U);
                }
            }
        }
    }

    assert(phase_count == HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS);
    assert(resolution_count == HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT);

    {
        HHSExactPass219HHCQResolutionSelectionV1 selection;
        HHSExactPass219HHCQParameterCoordinateV1 coordinate;
        assert(hhs_exact_pass219_hhcq_resolution_select(72U, 0U, 0U, 0U, 0, &selection) == HHS_EXACT_STATUS_RANGE_ERROR);
        assert(hhs_exact_pass219_hhcq_resolution_select(0U, 0U, 0U, 0U, 2, &selection) == HHS_EXACT_STATUS_RANGE_ERROR);
        assert(hhs_exact_pass219_hhcq_resolution_select(0U, 0U, 0U, 0U, 0, &selection) == HHS_EXACT_STATUS_OK);
        assert(hhs_exact_pass219_hhcq_parameter_locate(&selection, 5184U, &coordinate) == HHS_EXACT_STATUS_RANGE_ERROR);
    }

    return 0;
}
