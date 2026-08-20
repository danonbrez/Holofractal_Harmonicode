#include "hhs_pass219_orthogonal_glyph_membrane_1_21.hpp"

#include <array>
#include <cstdio>
#include <cstring>

using hhs::rna::OrthogonalGlyphMembrane;

static void fill_hash(char* out, std::size_t length, char symbol) {
    std::memset(out, static_cast<unsigned char>(symbol), length);
    out[length] = '\0';
}

static bool build_state(HHSExactPass219OctonionStateV1& state) {
    return hhs_exact_pass219_octonion_expand(0U, 1U, 0U, 1U, &state) ==
               HHS_EXACT_STATUS_OK &&
           state.xy == OrthogonalGlyphMembrane::canonical_a2 &&
           state.zw == OrthogonalGlyphMembrane::canonical_a2 &&
           state.yx != state.xy && state.wz != state.zw;
}

static HHSExactPass219MonolithicProofV1 build_proof(
    const HHSExactPass219OctonionStateV1& state,
    std::size_t lane_index
) {
    HHSExactPass219MonolithicDescriptorV1 descriptor{};
    HHSExactPass219MonolithicProofV1 proof{};
    (void)hhs_exact_pass219_monolithic_descriptor(&descriptor);

    proof.struct_size = static_cast<std::uint32_t>(sizeof(proof));
    proof.version = hhs_exact_pass219_monolithic_version();
    proof.completed_stage_mask = HHS_EXACT_PASS219_STAGE_REQUIRED;
    proof.resolved_family_mask = HHS_EXACT_PASS219_FAMILY_REQUIRED;
    proof.edge_satisfied_mask = HHS_EXACT_PASS219_MONOLITHIC_ALL_EDGE_MASK;
    std::memcpy(
        proof.source_sha256,
        descriptor.machine_source_sha256,
        HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES);
    proof.all_values_exact = 1U;
    proof.one_candidate_state = 1U;
    proof.lhs_rhs_equal = 1U;
    proof.octonion_state = state;

    fill_hash(proof.source_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN, '0');
    fill_hash(proof.ast_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN, '1');
    fill_hash(proof.constraint_graph_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN, '2');
    fill_hash(proof.vmir_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN, '3');
    fill_hash(
        proof.candidate_state_hash216,
        HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN,
        HHS_EXACT_HASH72_ALPHABET[(lane_index + 4U) % HHS_EXACT_HASH72_LEN]);
    fill_hash(proof.proof_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN, '5');
    for (std::size_t family = 0;
         family < HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT;
         ++family) {
        fill_hash(
            proof.family_witness_hash216[family],
            HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN,
            HHS_EXACT_HASH72_ALPHABET[(family + 6U) % HHS_EXACT_HASH72_LEN]);
    }
    fill_hash(proof.receipt_hash72, HHS_EXACT_HASH72_LEN, 'a');
    return proof;
}

static bool has_phase_contradiction(
    const OrthogonalGlyphMembrane& membrane,
    OrthogonalGlyphMembrane::Glyph left,
    OrthogonalGlyphMembrane::Glyph right
) {
    for (const auto& equation : membrane.contradictions()) {
        const bool same_pair =
            (equation.left == left && equation.right == right) ||
            (equation.left == right && equation.right == left);
        if (same_pair)
            return equation.phase_contradiction;
    }
    return false;
}

int main(int argc, char** argv) {
    HHSExactPass219OctonionStateV1 state{};
    if (!build_state(state))
        return 1;

    std::uint8_t delta_byte = OrthogonalGlyphMembrane::canonical_a2;
    HHSExactBigUIntView delta{
        static_cast<std::uint32_t>(sizeof(HHSExactBigUIntView)),
        1U,
        &delta_byte
    };
    OrthogonalGlyphMembrane membrane(state, delta);
    if (membrane.status() != HHS_EXACT_STATUS_OK || !membrane.invariant_closed())
        return 2;

    if (OrthogonalGlyphMembrane::lane_count != 24U ||
        OrthogonalGlyphMembrane::lane_width != 216U ||
        OrthogonalGlyphMembrane::hydration_fabric_size != 5184U)
        return 3;

    for (std::size_t i = 0; i < OrthogonalGlyphMembrane::lane_count; ++i) {
        const auto glyph = static_cast<OrthogonalGlyphMembrane::Glyph>(i);
        const auto& lane = membrane.lane(glyph);
        if (lane.glyph != glyph ||
            lane.hydration.lane_ordinal != i ||
            lane.hydration.begin != i * OrthogonalGlyphMembrane::lane_width ||
            lane.hydration.end != (i + 1U) * OrthogonalGlyphMembrane::lane_width - 1U)
            return 4;
        if (lane.equation != membrane.lane(OrthogonalGlyphMembrane::Glyph::P).equation)
            return 5;
    }
    if (membrane.lane(OrthogonalGlyphMembrane::Glyph::B).hydration.end != 4967U ||
        membrane.lane(OrthogonalGlyphMembrane::Glyph::a2).hydration.end != 5183U)
        return 6;

    if (argc == 2 && std::strcmp(argv[1], "--dump-source") == 0) {
        const auto& equation = membrane.lane(OrthogonalGlyphMembrane::Glyph::P).equation;
        return std::fwrite(equation.data(), 1U, equation.size(), stdout) == equation.size()
            ? 0
            : 7;
    }

    std::array<HHSExactPass219MonolithicProofV1, OrthogonalGlyphMembrane::lane_count> proofs{};
    for (std::size_t i = 0; i < proofs.size(); ++i)
        proofs[i] = build_proof(state, i);
    if (membrane.assign_all(proofs) != HHS_EXACT_STATUS_OK)
        return 8;

    if (membrane.compute_parallel() != HHS_EXACT_STATUS_OK || !membrane.computed())
        return 9;

    const auto& global = membrane.global();
    if (!global.invariant_xy_zw_a2_delta || !global.all_lanes_computed ||
        global.canonical_proof || !global.requires_vm81_authority ||
        global.rejected_lane_count != 0U ||
        global.unresolved_lane_count != OrthogonalGlyphMembrane::lane_count ||
        global.proof_packet_complete_lane_count != OrthogonalGlyphMembrane::lane_count)
        return 10;

    constexpr std::uint32_t expected_pair_count =
        static_cast<std::uint32_t>(
            (OrthogonalGlyphMembrane::lane_count *
             (OrthogonalGlyphMembrane::lane_count - 1U)) / 2U);
    if (global.emergent_equation_count != expected_pair_count ||
        membrane.contradictions().size() != expected_pair_count)
        return 11;

    for (char symbol : global.lane_hash216_fabric) {
        if (std::strchr(HHS_EXACT_HASH72_ALPHABET, symbol) == nullptr)
            return 12;
    }
    if (global.contradiction_graph_hash216[HHS_HASH216_BYTES_LEN] != '\0')
        return 13;

    if (!has_phase_contradiction(
            membrane,
            OrthogonalGlyphMembrane::Glyph::xy,
            OrthogonalGlyphMembrane::Glyph::yx) ||
        !has_phase_contradiction(
            membrane,
            OrthogonalGlyphMembrane::Glyph::zw,
            OrthogonalGlyphMembrane::Glyph::wz))
        return 14;

    if (has_phase_contradiction(
            membrane,
            OrthogonalGlyphMembrane::Glyph::xy,
            OrthogonalGlyphMembrane::Glyph::zw) ||
        has_phase_contradiction(
            membrane,
            OrthogonalGlyphMembrane::Glyph::Delta,
            OrthogonalGlyphMembrane::Glyph::a2))
        return 15;

    const auto fabric_before = global.lane_hash216_fabric;
    const auto graph_before = global.contradiction_graph_hash216;
    if (membrane.compute_parallel() != HHS_EXACT_STATUS_OK)
        return 16;
    if (fabric_before != membrane.global().lane_hash216_fabric ||
        graph_before != membrane.global().contradiction_graph_hash216)
        return 17;

    std::uint8_t bad_delta_byte = 2U;
    HHSExactBigUIntView bad_delta{
        static_cast<std::uint32_t>(sizeof(HHSExactBigUIntView)),
        1U,
        &bad_delta_byte
    };
    OrthogonalGlyphMembrane bad_delta_membrane(state, bad_delta);
    if (bad_delta_membrane.status() != HHS_EXACT_STATUS_INVARIANT_FAILURE)
        return 18;

    HHSExactPass219OctonionStateV1 bad_state{};
    if (hhs_exact_pass219_octonion_expand(0U, 0U, 0U, 0U, &bad_state) !=
        HHS_EXACT_STATUS_OK)
        return 19;
    OrthogonalGlyphMembrane bad_state_membrane(bad_state, delta);
    if (bad_state_membrane.status() != HHS_EXACT_STATUS_INVARIANT_FAILURE)
        return 20;

    OrthogonalGlyphMembrane mismatch_membrane(state, delta);
    auto mismatch_proof = build_proof(state, 0U);
    mismatch_proof.octonion_state = bad_state;
    if (mismatch_membrane.assign_lane(
            OrthogonalGlyphMembrane::Glyph::P,
            mismatch_proof) != HHS_EXACT_STATUS_INVARIANT_FAILURE)
        return 21;

    OrthogonalGlyphMembrane incomplete_membrane(state, delta);
    if (incomplete_membrane.assign_lane(
            OrthogonalGlyphMembrane::Glyph::P,
            proofs[0]) != HHS_EXACT_STATUS_OK)
        return 22;
    if (incomplete_membrane.compute_parallel() != HHS_EXACT_STATUS_INVALID_ARGUMENT)
        return 23;

    std::puts("PASS219_ORTHOGONAL_GLYPH_MEMBRANE_1_21_OK");
    return 0;
}
