#include "hhs_runtime_exact_abi.h"

#include <array>
#include <cstdint>

int main() {
    HHSExactPass219MonolithicDescriptorV1 descriptor{};
    if (hhs_exact_pass219_monolithic_descriptor(&descriptor) != HHS_EXACT_STATUS_OK)
        return 1;
    if (descriptor.version != hhs_exact_pass219_monolithic_version())
        return 2;
    if (descriptor.source_length != HHS_EXACT_PASS219_MONOLITHIC_SOURCE_LENGTH ||
        descriptor.native_source_length != HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH ||
        descriptor.equality_edge_count != 10U ||
        descriptor.binding_edge_count != 5U ||
        descriptor.constraint_edge_count != 5U)
        return 3;
    if (descriptor.monolithic_admission_only != 1U ||
        descriptor.pass159_constraint_graph_required != 1U ||
        descriptor.vm81_proof_required != 1U)
        return 4;

    std::array<std::uint8_t, HHS_EXACT_PASS219_MONOLITHIC_SOURCE_LENGTH> source{};
    std::array<std::uint8_t, HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH> native{};
    std::size_t length = 0U;
    std::size_t native_length = 0U;
    if (hhs_exact_pass219_monolithic_source(source.data(), source.size(), &length) !=
            HHS_EXACT_STATUS_OK ||
        length != source.size())
        return 5;
    if (hhs_exact_pass219_monolithic_native_source(
            native.data(), native.size(), &native_length) != HHS_EXACT_STATUS_OK ||
        native_length != native.size())
        return 6;

    HHSExactPass219MonolithicEdgeV1 first{};
    HHSExactPass219MonolithicEdgeV1 last{};
    HHSExactPass219MonolithicEdgeV1 native_third{};
    HHSExactPass219MonolithicEdgeV1 native_last{};
    if (hhs_exact_pass219_monolithic_edge(0U, &first) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_monolithic_edge(9U, &last) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_monolithic_native_edge(2U, &native_third) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_monolithic_native_edge(9U, &native_last) != HHS_EXACT_STATUS_OK)
        return 7;
    if (first.byte_offset != 11U ||
        first.kind != HHS_EXACT_PASS219_MONOLITHIC_EDGE_BINDING ||
        last.byte_offset != 335U ||
        last.kind != HHS_EXACT_PASS219_MONOLITHIC_EDGE_BINDING ||
        native_third.byte_offset != 39U ||
        native_last.byte_offset != 329U)
        return 8;

    if (descriptor.floating_point_authority != 0U ||
        descriptor.vm81_mutation_authority != 0U ||
        descriptor.hash72_commit_authority != 0U)
        return 9;
    return 0;
}
