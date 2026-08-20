#include "hhs_runtime_exact_abi.h"

#include <array>
#include <cstdint>
#include <cstring>

int main() {
    HHSExactPass219MonolithicDescriptorV1 descriptor{};
    if (hhs_exact_pass219_monolithic_descriptor(&descriptor) != HHS_EXACT_STATUS_OK)
        return 1;
    if (descriptor.version != hhs_exact_pass219_monolithic_version())
        return 2;
    if (descriptor.equality_edge_count != 10U ||
        descriptor.binding_edge_count != 5U ||
        descriptor.constraint_edge_count != 5U)
        return 3;
    if (descriptor.monolithic_admission_only != 1U ||
        descriptor.pass159_constraint_graph_required != 1U ||
        descriptor.vm81_proof_required != 1U)
        return 4;

    std::array<std::uint8_t, HHS_EXACT_PASS219_MONOLITHIC_SOURCE_LENGTH> source{};
    std::size_t length = 0U;
    if (hhs_exact_pass219_monolithic_source(source.data(), source.size(), &length) !=
            HHS_EXACT_STATUS_OK ||
        length != source.size())
        return 5;

    HHSExactPass219MonolithicEdgeV1 first{};
    HHSExactPass219MonolithicEdgeV1 last{};
    if (hhs_exact_pass219_monolithic_edge(0U, &first) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_monolithic_edge(9U, &last) != HHS_EXACT_STATUS_OK)
        return 6;
    if (first.byte_offset != 11U ||
        first.kind != HHS_EXACT_PASS219_MONOLITHIC_EDGE_BINDING ||
        last.byte_offset != 335U ||
        last.kind != HHS_EXACT_PASS219_MONOLITHIC_EDGE_BINDING)
        return 7;

    if (descriptor.floating_point_authority != 0U ||
        descriptor.vm81_mutation_authority != 0U ||
        descriptor.hash72_commit_authority != 0U)
        return 8;
    return 0;
}
