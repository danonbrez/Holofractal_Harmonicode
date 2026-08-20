#include "hhs_pass219_orthogonal_glyph_membrane_1_21.hpp"

#include <array>
#include <cstdio>
#include <cstring>

using hhs::rna::OrthogonalGlyphMembrane;

static void fill_hash(char* out, std::size_t length, char symbol) {
    std::memset(out, static_cast<unsigned char>(symbol), length);
    out[length] = '\0';
}

static bool hash216_valid(const std::array<char, HHS_HASH216_BYTES_STRLEN>& hash) {
    if (hash[HHS_HASH216_BYTES_LEN] != '\0')
        return false;
    for (std::size_t i = 0U; i < HHS_HASH216_BYTES_LEN; ++i) {
        if (std::strchr(HHS_EXACT_HASH72_ALPHABET, hash[i]) == nullptr)
            return false;
    }
    return true;
}

static HHSExactVM81Frame build_frame(std::size_t lane_index) {
    HHSExactVM81Frame frame{};
    frame.words[0] = UINT64_C(0);  // x = 0
    frame.words[1] = UINT64_C(1);  // y = 1
    frame.words[2] = UINT64_C(0);  // z = 0
    frame.words[3] = UINT64_C(1);  // w = 1
    frame.words[10] = static_cast<std::uint64_t>(lane_index + 1U);
    return frame;
}

static bool derive_surface(
    const HHSExactVM81Frame& frame,
    HHSExactPass219OctonionSurfaceV1& surface
) {
    return hhs_exact_pass219_octonion_from_vm81(
               &frame, 0U, 1U, 2U, 3U, &surface) == HHS_EXACT_STATUS_OK &&
           hhs_exact_pass219_octonion_validate_surface(&surface) == HHS_EXACT_STATUS_OK;
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
    for (std::size_t family = 0U;
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

static OrthogonalGlyphMembrane::LaneAssignment build_assignment(std::size_t lane_index) {
    OrthogonalGlyphMembrane::LaneAssignment assignment{};
    assignment.frame = build_frame(lane_index);
    HHSExactPass219OctonionSurfaceV1 surface{};
    if (!derive_surface(assignment.frame, surface))
        return assignment;
    assignment.proof = build_proof(surface.state, lane_index);
    assignment.x_cell = 0U;
    assignment.y_cell = 1U;
    assignment.z_cell = 2U;
    assignment.w_cell = 3U;
    assignment.g243 = static_cast<std::uint16_t>((17U + lane_index) % HHS188_G243_CONTROLS);
    assignment.kappa41 = static_cast<std::uint8_t>((20U + lane_index) % HHS189_LOCAL_COORDINATES);
    return assignment;
}

int main(int argc, char** argv) {
    std::uint8_t a2_byte = 1U;
    std::uint8_t delta_byte = 1U;
    HHSExactBigUIntView a2{
        static_cast<std::uint32_t>(sizeof(HHSExactBigUIntView)), 1U, &a2_byte};
    HHSExactBigUIntView delta{
        static_cast<std::uint32_t>(sizeof(HHSExactBigUIntView)), 1U, &delta_byte};

    OrthogonalGlyphMembrane membrane(a2, delta);
    if (membrane.status() != HHS_EXACT_STATUS_OK)
        return 1;

    if (OrthogonalGlyphMembrane::lane_count != 24U ||
        OrthogonalGlyphMembrane::vm_thread_count != 64U ||
        OrthogonalGlyphMembrane::vm_cells_per_thread != 81U ||
        OrthogonalGlyphMembrane::vm_fabric_positions != 5184U ||
        OrthogonalGlyphMembrane::parenthesis_thread_count != 34U ||
        OrthogonalGlyphMembrane::equality_half_gate_thread_count != 15U ||
        OrthogonalGlyphMembrane::source_structure_thread_count != 49U ||
        OrthogonalGlyphMembrane::vmir_derived_thread_count != 15U)
        return 2;

    const auto& source_threads = membrane.source_threads();
    for (std::size_t i = 0U; i < OrthogonalGlyphMembrane::parenthesis_thread_count; ++i) {
        if (source_threads[i].kind != OrthogonalGlyphMembrane::ThreadKind::ParenthesisShell)
            return 3;
    }
    for (std::size_t i = OrthogonalGlyphMembrane::parenthesis_thread_count;
         i < OrthogonalGlyphMembrane::source_structure_thread_count;
         ++i) {
        if (source_threads[i].kind != OrthogonalGlyphMembrane::ThreadKind::EqualityHalfGate)
            return 4;
    }
    for (std::size_t i = OrthogonalGlyphMembrane::source_structure_thread_count;
         i < OrthogonalGlyphMembrane::vm_thread_count;
         ++i) {
        if (source_threads[i].kind != OrthogonalGlyphMembrane::ThreadKind::VMIRDerived ||
            source_threads[i].derived_slot != i - OrthogonalGlyphMembrane::source_structure_thread_count)
            return 5;
    }

    if (argc == 2 && std::strcmp(argv[1], "--dump-source") == 0) {
        const auto& equation = membrane.lane(OrthogonalGlyphMembrane::Glyph::P).equation;
        return std::fwrite(equation.data(), 1U, equation.size(), stdout) == equation.size()
            ? 0
            : 6;
    }

    std::array<OrthogonalGlyphMembrane::LaneAssignment, OrthogonalGlyphMembrane::lane_count> assignments{};
    for (std::size_t i = 0U; i < assignments.size(); ++i) {
        assignments[i] = build_assignment(i);
        if (assignments[i].proof.struct_size == 0U)
            return 7;
    }
    if (membrane.assign_all(assignments) != HHS_EXACT_STATUS_OK)
        return 8;
    if (membrane.compute_parallel() != HHS_EXACT_STATUS_OK || !membrane.computed())
        return 9;

    for (std::size_t i = 0U; i < OrthogonalGlyphMembrane::lane_count; ++i) {
        const auto glyph = static_cast<OrthogonalGlyphMembrane::Glyph>(i);
        const auto& lane = membrane.lane(glyph);
        const auto& result = membrane.lane_result(glyph);
        if (lane.glyph != glyph ||
            lane.equation != membrane.lane(OrthogonalGlyphMembrane::Glyph::P).equation)
            return 10;
        if (result.status != HHS_EXACT_STATUS_OK ||
            !result.full_vm5184_address_closure || !result.full_hydration_roundtrip ||
            !result.xy_zw_ordered_projection_equal ||
            !result.a2_delta_exact_projection_equal ||
            !result.cross_domain_binding_requires_vm81 ||
            result.native_shared_invariant_proven)
            return 11;
        if (result.octonion_surface.state.xy == result.octonion_surface.state.yx ||
            result.octonion_surface.state.zw == result.octonion_surface.state.wz)
            return 12;
        if (result.threads[1].left_basis != HHS_EXACT_PHASE_X ||
            result.threads[1].right_basis != HHS_EXACT_PHASE_Y ||
            result.threads[1].product.phase != result.octonion_surface.state.xy)
            return 13;
        constexpr std::size_t zw_thread =
            HHS_EXACT_PHASE_Z * HHS_EXACT_PHASE_BASIS_COUNT + HHS_EXACT_PHASE_W;
        if (result.threads[zw_thread].left_basis != HHS_EXACT_PHASE_Z ||
            result.threads[zw_thread].right_basis != HHS_EXACT_PHASE_W ||
            result.threads[zw_thread].product.phase != result.octonion_surface.state.zw)
            return 14;
        for (const auto& thread : result.threads) {
            if (!hash216_valid(thread.thread_hash216))
                return 15;
        }
        if (!hash216_valid(result.lane_hash216))
            return 16;
    }

    const auto& global = membrane.global();
    if (!global.source_topology_exact || !global.all_lanes_computed ||
        !global.a2_delta_exact_projection_equal ||
        !global.every_lane_xy_zw_projection_equal ||
        !global.cross_domain_binding_requires_vm81 ||
        global.native_shared_invariant_proven || global.canonical_proof ||
        !global.requires_vm81_authority || global.rejected_lane_count != 0U ||
        global.unresolved_lane_count != OrthogonalGlyphMembrane::lane_count ||
        global.proof_packet_complete_lane_count != OrthogonalGlyphMembrane::lane_count)
        return 17;

    constexpr std::uint32_t expected_pairs = static_cast<std::uint32_t>(
        (OrthogonalGlyphMembrane::lane_count * (OrthogonalGlyphMembrane::lane_count - 1U)) / 2U);
    if (global.emergent_equation_count != expected_pairs ||
        membrane.contradictions().size() != expected_pairs)
        return 18;
    for (const auto& equation : membrane.contradictions()) {
        if (!hash216_valid(equation.equation_hash216) ||
            equation.vm_thread_difference_mask == 0U ||
            equation.vm81_cell_difference_count == 0U ||
            !equation.candidate_state_identity_difference)
            return 19;
    }
    if (!hash216_valid(global.source_topology_hash216) ||
        !hash216_valid(global.contradiction_graph_hash216))
        return 20;

    const auto graph_before = global.contradiction_graph_hash216;
    const auto lane_before = global.lane_hash216;
    if (membrane.compute_parallel() != HHS_EXACT_STATUS_OK ||
        graph_before != membrane.global().contradiction_graph_hash216 ||
        lane_before != membrane.global().lane_hash216)
        return 21;

    std::uint8_t bad_delta_byte = 2U;
    HHSExactBigUIntView bad_delta{
        static_cast<std::uint32_t>(sizeof(HHSExactBigUIntView)), 1U, &bad_delta_byte};
    OrthogonalGlyphMembrane bad_projection(a2, bad_delta);
    if (bad_projection.status() != HHS_EXACT_STATUS_INVARIANT_FAILURE)
        return 22;

    OrthogonalGlyphMembrane mismatch(a2, delta);
    auto mismatch_assignment = assignments[0];
    mismatch_assignment.frame.words[1] = UINT64_C(2);
    if (mismatch.assign_lane(OrthogonalGlyphMembrane::Glyph::P, mismatch_assignment) !=
        HHS_EXACT_STATUS_INVARIANT_FAILURE)
        return 23;

    OrthogonalGlyphMembrane incomplete(a2, delta);
    if (incomplete.assign_lane(OrthogonalGlyphMembrane::Glyph::P, assignments[0]) !=
            HHS_EXACT_STATUS_OK ||
        incomplete.compute_parallel() != HHS_EXACT_STATUS_INVALID_ARGUMENT)
        return 24;

    OrthogonalGlyphMembrane broken_xyzw(a2, delta);
    auto broken_assignments = assignments;
    broken_assignments[5].frame.words[1] = UINT64_C(2);
    HHSExactPass219OctonionSurfaceV1 broken_surface{};
    if (!derive_surface(broken_assignments[5].frame, broken_surface))
        return 25;
    broken_assignments[5].proof = build_proof(broken_surface.state, 5U);
    if (broken_xyzw.assign_all(broken_assignments) != HHS_EXACT_STATUS_OK)
        return 26;
    if (broken_xyzw.compute_parallel() != HHS_EXACT_STATUS_INVARIANT_FAILURE)
        return 27;

    std::puts("PASS219_ORTHOGONAL_GLYPH_MEMBRANE_1_21_VM81_CIRCUIT_OK");
    return 0;
}
