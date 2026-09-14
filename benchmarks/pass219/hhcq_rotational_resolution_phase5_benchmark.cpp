#include "hhs_runtime_exact_abi.h"

#include <array>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>

namespace {

[[noreturn]] void fail(const char *message) {
    std::cerr << message << '\n';
    std::exit(2);
}

void require(bool condition, const char *message) {
    if (!condition)
        fail(message);
}

std::uint64_t mix64(std::uint64_t x) {
    x ^= x >> 30U;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27U;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31U;
    return x;
}

}  // namespace

int main() {
    HHSExactPass219HHCQResolutionDescriptorV1 descriptor{};
    std::array<bool, HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS> quotient_seen{};
    std::array<bool, HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS> rotated_seen{};
    std::array<bool, HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT> resolution_seen{};
    std::array<std::uint64_t, HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT> resolution_counts{};
    std::array<std::uint16_t, HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT> divisors{};
    HHSExactVM81Frame frame{};
    std::uint64_t selection_signature = UINT64_C(0x2190007200000125);
    std::uint64_t roundtrip_signature = UINT64_C(0x2195184000000125);
    std::uint64_t selection_count = 0U;
    std::uint64_t coordinate_checks = 0U;
    std::uint32_t quotient_count = 0U;
    std::uint32_t rotated_count = 0U;
    std::uint32_t resolution_count = 0U;
    std::uint32_t roundtrip_count = 0U;

    require(hhs_exact_pass219_hhcq_resolution_descriptor(&descriptor) == HHS_EXACT_STATUS_OK,
            "descriptor failed");
    require(descriptor.parameter_count == 5184U, "parameter count mismatch");
    require(descriptor.phase_modulus == 72U, "phase modulus mismatch");
    require(descriptor.divisor_count == 35U, "divisor count mismatch");
    require(descriptor.trinary_step == 5U, "trinary step mismatch");
    require(descriptor.candidate_only == 1U, "candidate-only invariant failed");
    require(descriptor.exact_integer_only == 1U, "integer-only invariant failed");
    require(descriptor.canonical_mutation_authority == 0U &&
            descriptor.canonical_hash72_authority == 0U &&
            descriptor.canonical_hash216_authority == 0U &&
            descriptor.canonical_persistence_authority == 0U &&
            descriptor.floating_point_authority == 0U,
            "authority invariant failed");

    for (std::uint32_t i = 0U; i < HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT; ++i) {
        std::uint16_t divisor = 0U;
        require(hhs_exact_pass219_hhcq_resolution_divisor(static_cast<std::uint8_t>(i), &divisor) ==
                    HHS_EXACT_STATUS_OK,
                "divisor lookup failed");
        require(divisor > 0U && (5184U % divisor) == 0U, "non-exact divisor");
        divisors[i] = divisor;
    }

    for (std::uint32_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        frame.words[i] = UINT64_C(0xd6e8feb86659fd93) ^
                         (UINT64_C(0x9e3779b97f4a7c15) * static_cast<std::uint64_t>(i + 1U));
    }

    for (std::uint32_t x = 0U; x < HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS; ++x) {
        for (std::uint32_t y = 0U; y < HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS; ++y) {
            for (int direction = -1; direction <= 1; ++direction) {
                HHSExactPass219HHCQResolutionSelectionV1 selection{};
                require(hhs_exact_pass219_hhcq_resolution_select(
                            static_cast<std::uint8_t>(x), static_cast<std::uint8_t>(y),
                            UINT8_C(0), UINT8_C(0), static_cast<std::int8_t>(direction),
                            &selection) == HHS_EXACT_STATUS_OK,
                        "resolution selection failed");
                ++selection_count;
                if (!quotient_seen[selection.quotient_phase72]) {
                    quotient_seen[selection.quotient_phase72] = true;
                    ++quotient_count;
                }
                if (!rotated_seen[selection.rotated_phase72]) {
                    rotated_seen[selection.rotated_phase72] = true;
                    ++rotated_count;
                }
                ++resolution_counts[selection.resolution_index];
                selection_signature = mix64(
                    selection_signature ^ selection.selection_signature64 ^
                    (static_cast<std::uint64_t>(selection.resolution_index) << 56U) ^
                    selection_count);

                if (!resolution_seen[selection.resolution_index]) {
                    HHSExactVM81Frame reconstructed{};
                    HHSExactPass219HHCQRoundtripReportV1 report{};
                    resolution_seen[selection.resolution_index] = true;
                    ++resolution_count;

                    for (std::uint32_t parameter = 0U;
                         parameter < HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT; ++parameter) {
                        HHSExactPass219HHCQParameterCoordinateV1 coordinate{};
                        require(hhs_exact_pass219_hhcq_parameter_locate(
                                    &selection, static_cast<std::uint16_t>(parameter), &coordinate) ==
                                    HHS_EXACT_STATUS_OK,
                                "parameter locate failed");
                        require(static_cast<std::uint32_t>(coordinate.region_start) +
                                    coordinate.local_offset == parameter,
                                "coordinate identity mismatch");
                        require(coordinate.region_index < selection.region_count,
                                "coordinate region out of range");
                        ++coordinate_checks;
                    }

                    require(hhs_exact_pass219_hhcq_decompose_recompose(
                                &frame, &selection, &reconstructed, &report) == HHS_EXACT_STATUS_OK,
                            "decompose/recompose failed");
                    require(std::memcmp(&frame, &reconstructed, sizeof(frame)) == 0,
                            "recomposition byte mismatch");
                    require(report.parameters_visited == 5184U &&
                            report.orthogonal_partition_complete == 1U &&
                            report.no_overlap == 1U && report.no_gap == 1U &&
                            report.exact_recomposition == 1U,
                            "roundtrip proof mismatch");
                    require(report.candidate_only == 1U &&
                            report.exact_integer_only == 1U &&
                            report.canonical_authority_changed == 0U &&
                            report.floating_point_authority == 0U,
                            "roundtrip authority mismatch");
                    ++roundtrip_count;
                    roundtrip_signature = mix64(
                        roundtrip_signature ^ report.decomposition_signature64 ^
                        report.input_signature64 ^
                        (static_cast<std::uint64_t>(selection.resolution_parameters) << 32U));
                }
            }
        }
    }

    require(selection_count == UINT64_C(15552), "selection count mismatch");
    require(quotient_count == 72U, "quotient ring coverage incomplete");
    require(rotated_count == 72U, "rotated ring coverage incomplete");
    require(resolution_count == 35U, "resolution lattice coverage incomplete");
    require(roundtrip_count == 35U, "roundtrip resolution coverage incomplete");
    require(coordinate_checks == UINT64_C(181440), "coordinate coverage mismatch");
    for (std::uint32_t i = 0U; i < HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT; ++i)
        require(resolution_counts[i] > 0U, "unreached resolution");

    std::cout << "{";
    std::cout << "\"schema\":\"HHS_PASS219_HHCQ_ROTATIONAL_RESOLUTION_PHASE5_V1\",";
    std::cout << "\"parameter_count\":5184,";
    std::cout << "\"phase_modulus\":72,";
    std::cout << "\"trinary_step\":5,";
    std::cout << "\"selection_count\":" << selection_count << ',';
    std::cout << "\"quotient_phase_coverage\":" << quotient_count << ',';
    std::cout << "\"rotated_phase_coverage\":" << rotated_count << ',';
    std::cout << "\"resolution_count\":" << resolution_count << ',';
    std::cout << "\"roundtrip_resolution_count\":" << roundtrip_count << ',';
    std::cout << "\"coordinate_identity_checks\":" << coordinate_checks << ',';
    std::cout << "\"divisors\":[";
    for (std::size_t i = 0U; i < divisors.size(); ++i) {
        if (i != 0U) std::cout << ',';
        std::cout << divisors[i];
    }
    std::cout << "],\"resolution_selection_counts\":[";
    for (std::size_t i = 0U; i < resolution_counts.size(); ++i) {
        if (i != 0U) std::cout << ',';
        std::cout << resolution_counts[i];
    }
    std::cout << "],";
    std::cout << "\"selection_signature64\":" << selection_signature << ',';
    std::cout << "\"roundtrip_signature64\":" << roundtrip_signature << ',';
    std::cout << "\"ordered_xz_over_yw_phase_quotient\":true,";
    std::cout << "\"complete_2a3b_divisor_lattice\":true,";
    std::cout << "\"dyadic_trinary_dual_primitive\":true,";
    std::cout << "\"exact_orthogonal_decomposition\":true,";
    std::cout << "\"candidate_only\":true,";
    std::cout << "\"canonical_authority_changed\":false,";
    std::cout << "\"floating_point_authority\":false";
    std::cout << "}\n";
    return 0;
}
