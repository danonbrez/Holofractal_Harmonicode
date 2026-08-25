#ifndef HHS_PASS219_ORTHOGONAL_GLYPH_MEMBRANE_1_21_HPP
#define HHS_PASS219_ORTHOGONAL_GLYPH_MEMBRANE_1_21_HPP

#include "hhs_pass219_monolithic_constraint_abi_1_20.h"
#include "hhs_hash216_bytes.h"
#include "hhs_pass188_bott_runtime.h"
#include "hhs_pass189_hqlh.h"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <future>
#include <string_view>
#include <vector>

namespace hhs::rna {

class OrthogonalGlyphMembrane final {
public:
    enum class Glyph : std::uint8_t {
        P = 0, t, p, q, Delta, m, b, c, u, s,
        x, y, z, w, xy, yx, zw, wz,
        At, f, Bt, A, B, a2, Count
    };

    enum class ThreadKind : std::uint8_t {
        ParenthesisShell = 1,
        EqualityHalfGate = 2,
        VMIRDerived = 3
    };

    static constexpr std::size_t lane_count = static_cast<std::size_t>(Glyph::Count);
    static constexpr std::size_t vm_thread_count = HHS_EXACT_PHASE_PAIR_COUNT;
    static constexpr std::size_t vm_cells_per_thread = HHS_EXACT_VM81_CELLS;
    static constexpr std::size_t vm_fabric_positions = HHS_EXACT_HASH72_COORDS;
    static constexpr std::size_t bank_count = 9U;
    static constexpr std::size_t cells_per_bank = 9U;

    /* Frozen 1.20 native source topology: 34 matched () shells + 15 literal '=' chars. */
    static constexpr std::size_t parenthesis_thread_count = 34U;
    static constexpr std::size_t equality_half_gate_thread_count = 15U;
    static constexpr std::size_t source_structure_thread_count =
        parenthesis_thread_count + equality_half_gate_thread_count;
    static constexpr std::size_t vmir_derived_thread_count =
        vm_thread_count - source_structure_thread_count;

    struct ExactProjection final {
        std::uint32_t byte_length{};
        std::array<std::uint8_t, HHS_EXACT_UQCEL_MAX_P_BYTES> bytes_be{};
    };

    struct SourceThreadDescriptor final {
        ThreadKind kind{ThreadKind::VMIRDerived};
        std::uint8_t thread_id{};
        std::uint8_t derived_slot{};
        std::uint16_t source_begin{};
        std::uint16_t source_end{};
    };

    struct LaneAssignment final {
        HHSExactVM81Frame frame{};
        HHSExactPass219MonolithicProofV1 proof{};
        std::uint8_t x_cell{};
        std::uint8_t y_cell{};
        std::uint8_t z_cell{};
        std::uint8_t w_cell{};
        std::uint16_t g243{};
        std::uint8_t kappa41{};
    };

    struct Lane final {
        Glyph glyph{Glyph::P};
        std::array<std::uint8_t, HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH> equation{};
        LaneAssignment assignment{};
        bool assigned{false};
    };

    struct ThreadCircuit final {
        SourceThreadDescriptor source{};
        std::uint8_t left_basis{};
        std::uint8_t right_basis{};
        HHSExactPass219OctonionProductV1 product{};
        std::array<std::uint8_t, vm_cells_per_thread> vm81_bits{};
        std::array<std::uint32_t, vm_cells_per_thread> projected_g243{};
        std::array<std::uint32_t, vm_cells_per_thread> contextual_kappa41{};
        std::array<std::uint8_t, vm_cells_per_thread> bott_output_basis{};
        std::array<char, HHS_HASH216_BYTES_STRLEN> thread_hash216{};
    };

    struct LaneComputation final {
        HHSExactStatus status{HHS_EXACT_STATUS_INVALID_ARGUMENT};
        Glyph glyph{Glyph::P};
        HHSExactPass219MonolithicVerificationV1 verification{};
        HHSExactPass219OctonionSurfaceV1 octonion_surface{};
        std::array<ThreadCircuit, vm_thread_count> threads{};
        bool full_vm5184_address_closure{false};
        bool full_hydration_roundtrip{false};
        bool xy_zw_ordered_projection_equal{false};
        bool a2_delta_exact_projection_equal{false};
        bool cross_domain_binding_requires_vm81{true};
        bool native_shared_invariant_proven{false};
        std::array<char, HHS_HASH216_BYTES_STRLEN> lane_hash216{};
    };

    struct ContradictionEquation final {
        Glyph left{Glyph::P};
        Glyph right{Glyph::P};
        std::uint64_t vm_thread_difference_mask{};
        std::uint64_t ordered_product_difference_mask{};
        std::uint32_t vm81_cell_difference_count{};
        std::uint64_t equality_edge_difference_mask{};
        std::uint32_t family_difference_mask{};
        std::uint32_t stage_difference_mask{};
        std::uint32_t verification_difference_mask{};
        bool candidate_state_identity_difference{false};
        bool proof_identity_difference{false};
        std::array<char, HHS_HASH216_BYTES_STRLEN> equation_hash216{};
    };

    struct GlobalComputation final {
        HHSExactStatus status{HHS_EXACT_STATUS_INVALID_ARGUMENT};
        bool source_topology_exact{false};
        bool all_lanes_computed{false};
        bool a2_delta_exact_projection_equal{false};
        bool every_lane_xy_zw_projection_equal{false};
        bool cross_domain_binding_requires_vm81{true};
        bool native_shared_invariant_proven{false};
        bool canonical_proof{false};
        bool requires_vm81_authority{true};
        std::uint32_t rejected_lane_count{};
        std::uint32_t unresolved_lane_count{};
        std::uint32_t proof_packet_complete_lane_count{};
        std::uint32_t emergent_equation_count{};
        std::array<std::array<char, HHS_HASH216_BYTES_STRLEN>, lane_count> lane_hash216{};
        std::array<char, HHS_HASH216_BYTES_STRLEN> source_topology_hash216{};
        std::array<char, HHS_HASH216_BYTES_STRLEN> contradiction_graph_hash216{};
    };

    OrthogonalGlyphMembrane(
        const HHSExactBigUIntView& a2,
        const HHSExactBigUIntView& delta
    ) noexcept {
        if (!copy_projection(a2, a2_) || !copy_projection(delta, delta_)) {
            status_ = HHS_EXACT_STATUS_INVALID_ARGUMENT;
            return;
        }
        if (!same_projection(a2_, delta_)) {
            status_ = HHS_EXACT_STATUS_INVARIANT_FAILURE;
            return;
        }

        std::size_t source_length = 0U;
        status_ = hhs_exact_pass219_monolithic_native_source(
            source_.data(), source_.size(), &source_length);
        if (status_ != HHS_EXACT_STATUS_OK || source_length != source_.size()) {
            status_ = HHS_EXACT_STATUS_INVARIANT_FAILURE;
            return;
        }
        if (!build_source_topology()) {
            status_ = HHS_EXACT_STATUS_INVARIANT_FAILURE;
            return;
        }

        for (std::size_t i = 0U; i < lane_count; ++i) {
            lanes_[i].glyph = static_cast<Glyph>(i);
            lanes_[i].equation = source_;
        }
        status_ = HHS_EXACT_STATUS_OK;
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool computed() const noexcept { return computed_; }

    static constexpr std::string_view glyph_name(Glyph glyph) noexcept {
        switch (glyph) {
            case Glyph::P: return "P";
            case Glyph::t: return "t";
            case Glyph::p: return "p";
            case Glyph::q: return "q";
            case Glyph::Delta: return "Delta";
            case Glyph::m: return "m";
            case Glyph::b: return "b";
            case Glyph::c: return "c";
            case Glyph::u: return "u";
            case Glyph::s: return "s";
            case Glyph::x: return "x";
            case Glyph::y: return "y";
            case Glyph::z: return "z";
            case Glyph::w: return "w";
            case Glyph::xy: return "xy";
            case Glyph::yx: return "yx";
            case Glyph::zw: return "zw";
            case Glyph::wz: return "wz";
            case Glyph::At: return "At";
            case Glyph::f: return "f";
            case Glyph::Bt: return "Bt";
            case Glyph::A: return "A";
            case Glyph::B: return "B";
            case Glyph::a2: return "a^2";
            case Glyph::Count: break;
        }
        return "invalid";
    }

    const Lane& lane(Glyph glyph) const noexcept {
        const std::size_t i = static_cast<std::size_t>(glyph);
        return lanes_[i < lane_count ? i : 0U];
    }

    const LaneComputation& lane_result(Glyph glyph) const noexcept {
        const std::size_t i = static_cast<std::size_t>(glyph);
        return lane_results_[i < lane_count ? i : 0U];
    }

    const std::array<SourceThreadDescriptor, vm_thread_count>& source_threads() const noexcept {
        return source_threads_;
    }

    const std::vector<ContradictionEquation>& contradictions() const noexcept {
        return contradictions_;
    }

    const GlobalComputation& global() const noexcept { return global_; }

    HHSExactStatus assign_lane(Glyph glyph, const LaneAssignment& assignment) noexcept {
        if (status_ != HHS_EXACT_STATUS_OK)
            return status_;
        const std::size_t i = static_cast<std::size_t>(glyph);
        if (i >= lane_count)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        if (assignment.x_cell >= HHS_EXACT_VM81_CELLS ||
            assignment.y_cell >= HHS_EXACT_VM81_CELLS ||
            assignment.z_cell >= HHS_EXACT_VM81_CELLS ||
            assignment.w_cell >= HHS_EXACT_VM81_CELLS ||
            assignment.g243 >= HHS188_G243_CONTROLS ||
            assignment.kappa41 >= HHS189_LOCAL_COORDINATES)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        if (assignment.proof.struct_size < sizeof(assignment.proof) ||
            assignment.proof.version != hhs_exact_pass219_monolithic_version())
            return HHS_EXACT_STATUS_VERSION_MISMATCH;

        HHSExactPass219OctonionSurfaceV1 surface{};
        const HHSExactStatus circuit_status = hhs_exact_pass219_octonion_from_vm81(
            &assignment.frame,
            assignment.x_cell,
            assignment.y_cell,
            assignment.z_cell,
            assignment.w_cell,
            &surface);
        if (circuit_status != HHS_EXACT_STATUS_OK)
            return circuit_status;
        if (!same_octonion_state(surface.state, assignment.proof.octonion_state))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        lanes_[i].assignment = assignment;
        lanes_[i].assigned = true;
        computed_ = false;
        return HHS_EXACT_STATUS_OK;
    }

    HHSExactStatus assign_all(const std::array<LaneAssignment, lane_count>& assignments) noexcept {
        for (std::size_t i = 0U; i < lane_count; ++i) {
            const HHSExactStatus s = assign_lane(static_cast<Glyph>(i), assignments[i]);
            if (s != HHS_EXACT_STATUS_OK)
                return s;
        }
        return HHS_EXACT_STATUS_OK;
    }

    HHSExactStatus compute_parallel() {
        if (status_ != HHS_EXACT_STATUS_OK)
            return status_;
        for (const Lane& lane_state : lanes_) {
            if (!lane_state.assigned)
                return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        }

        std::array<std::future<LaneComputation>, lane_count> futures{};
        try {
            for (std::size_t i = 0U; i < lane_count; ++i)
                futures[i] = std::async(std::launch::async, [this, i]() { return compute_lane(i); });
            for (std::size_t i = 0U; i < lane_count; ++i) {
                lane_results_[i] = futures[i].get();
                if (lane_results_[i].status != HHS_EXACT_STATUS_OK)
                    return lane_results_[i].status;
            }
        } catch (...) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }

        build_global();
        computed_ = true;
        return global_.status;
    }

private:
    struct ParenPair final { std::uint16_t open{}; std::uint16_t close{}; };

    static_assert(lane_count == 24U, "verbatim equation profile contains 24 orthogonal glyph lanes");
    static_assert(vm_thread_count == 64U, "VM81 operation fabric requires 64 ordered threads");
    static_assert(vm_thread_count * vm_cells_per_thread == vm_fabric_positions,
                  "64 ordered threads x 81 VM81 cells must equal 5184 positions");
    static_assert(bank_count * cells_per_bank == vm_cells_per_thread,
                  "each ordered thread must contain nine 3x3 Lo Shu banks");
    static_assert(source_structure_thread_count == 49U,
                  "frozen verbatim source contributes 34 shell + 15 equality-half-gate threads");
    static_assert(source_structure_thread_count + vmir_derived_thread_count == vm_thread_count,
                  "source topology plus VMIR derived slots must close the 64-thread circuit");

    static bool copy_projection(const HHSExactBigUIntView& view, ExactProjection& out) noexcept {
        if (view.struct_size < sizeof(view) || view.bytes_be == nullptr ||
            view.byte_length == 0U || view.byte_length > out.bytes_be.size())
            return false;
        if (view.byte_length > 1U && view.bytes_be[0] == 0U)
            return false;
        out.byte_length = view.byte_length;
        std::memcpy(out.bytes_be.data(), view.bytes_be, view.byte_length);
        return true;
    }

    static bool same_projection(const ExactProjection& a, const ExactProjection& b) noexcept {
        return a.byte_length == b.byte_length &&
               std::memcmp(a.bytes_be.data(), b.bytes_be.data(), a.byte_length) == 0;
    }

    static bool same_octonion_state(
        const HHSExactPass219OctonionStateV1& a,
        const HHSExactPass219OctonionStateV1& b
    ) noexcept {
        return a.struct_size == b.struct_size && a.version == b.version &&
               a.x == b.x && a.y == b.y && a.z == b.z && a.w == b.w &&
               a.xy == b.xy && a.yx == b.yx && a.zw == b.zw && a.wz == b.wz;
    }

    static bool same_proof_identity(
        const HHSExactPass219MonolithicProofV1& a,
        const HHSExactPass219MonolithicProofV1& b
    ) noexcept {
        if (a.struct_size != b.struct_size || a.version != b.version ||
            a.completed_stage_mask != b.completed_stage_mask ||
            a.resolved_family_mask != b.resolved_family_mask ||
            a.edge_satisfied_mask != b.edge_satisfied_mask ||
            a.edge_failed_mask != b.edge_failed_mask ||
            a.edge_unresolved_mask != b.edge_unresolved_mask ||
            a.all_values_exact != b.all_values_exact ||
            a.one_candidate_state != b.one_candidate_state ||
            a.lhs_rhs_equal != b.lhs_rhs_equal ||
            !same_octonion_state(a.octonion_state, b.octonion_state))
            return false;
        if (std::memcmp(a.source_sha256, b.source_sha256,
                        HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES) != 0 ||
            std::memcmp(a.source_hash216, b.source_hash216,
                        HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN) != 0 ||
            std::memcmp(a.ast_hash216, b.ast_hash216,
                        HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN) != 0 ||
            std::memcmp(a.constraint_graph_hash216, b.constraint_graph_hash216,
                        HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN) != 0 ||
            std::memcmp(a.vmir_hash216, b.vmir_hash216,
                        HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN) != 0 ||
            std::memcmp(a.candidate_state_hash216, b.candidate_state_hash216,
                        HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN) != 0 ||
            std::memcmp(a.proof_hash216, b.proof_hash216,
                        HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN) != 0 ||
            std::memcmp(a.family_witness_hash216, b.family_witness_hash216,
                        sizeof(a.family_witness_hash216)) != 0 ||
            std::memcmp(a.receipt_hash72, b.receipt_hash72,
                        HHS_EXACT_HASH72_STRLEN) != 0)
            return false;
        return true;
    }

    static void append_u16(std::vector<std::uint8_t>& out, std::uint16_t value) {
        out.push_back(static_cast<std::uint8_t>(value & 0xFFU));
        out.push_back(static_cast<std::uint8_t>((value >> 8U) & 0xFFU));
    }

    static void append_u32(std::vector<std::uint8_t>& out, std::uint32_t value) {
        for (std::uint32_t shift = 0U; shift < 32U; shift += 8U)
            out.push_back(static_cast<std::uint8_t>((value >> shift) & 0xFFU));
    }

    static void append_u64(std::vector<std::uint8_t>& out, std::uint64_t value) {
        for (std::uint32_t shift = 0U; shift < 64U; shift += 8U)
            out.push_back(static_cast<std::uint8_t>((value >> shift) & 0xFFU));
    }

    static void append_projection(
        std::vector<std::uint8_t>& out,
        const ExactProjection& projection
    ) {
        append_u32(out, projection.byte_length);
        out.insert(
            out.end(), projection.bytes_be.begin(),
            projection.bytes_be.begin() + projection.byte_length);
    }

    static void append_proof_identity(
        std::vector<std::uint8_t>& out,
        const HHSExactPass219MonolithicProofV1& proof
    ) {
        append_u32(out, proof.struct_size);
        append_u32(out, proof.version);
        append_u32(out, proof.completed_stage_mask);
        append_u32(out, proof.resolved_family_mask);
        append_u64(out, proof.edge_satisfied_mask);
        append_u64(out, proof.edge_failed_mask);
        append_u64(out, proof.edge_unresolved_mask);
        out.insert(out.end(), proof.source_sha256,
                   proof.source_sha256 + HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES);
        out.push_back(proof.all_values_exact);
        out.push_back(proof.one_candidate_state);
        out.push_back(proof.lhs_rhs_equal);
        append_u32(out, proof.octonion_state.struct_size);
        append_u32(out, proof.octonion_state.version);
        out.push_back(proof.octonion_state.x);
        out.push_back(proof.octonion_state.y);
        out.push_back(proof.octonion_state.z);
        out.push_back(proof.octonion_state.w);
        out.push_back(proof.octonion_state.xy);
        out.push_back(proof.octonion_state.yx);
        out.push_back(proof.octonion_state.zw);
        out.push_back(proof.octonion_state.wz);
        out.insert(out.end(), proof.source_hash216,
                   proof.source_hash216 + HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN);
        out.insert(out.end(), proof.ast_hash216,
                   proof.ast_hash216 + HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN);
        out.insert(out.end(), proof.constraint_graph_hash216,
                   proof.constraint_graph_hash216 + HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN);
        out.insert(out.end(), proof.vmir_hash216,
                   proof.vmir_hash216 + HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN);
        out.insert(out.end(), proof.candidate_state_hash216,
                   proof.candidate_state_hash216 + HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN);
        out.insert(out.end(), proof.proof_hash216,
                   proof.proof_hash216 + HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN);
        for (std::size_t family = 0U;
             family < HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT;
             ++family) {
            out.insert(
                out.end(), proof.family_witness_hash216[family],
                proof.family_witness_hash216[family] +
                    HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN);
        }
        out.insert(out.end(), proof.receipt_hash72,
                   proof.receipt_hash72 + HHS_EXACT_HASH72_LEN);
    }

    static void append_verification_identity(
        std::vector<std::uint8_t>& out,
        const HHSExactPass219MonolithicVerificationV1& verification
    ) {
        append_u32(out, verification.struct_size);
        append_u32(out, verification.version);
        append_u32(out, verification.decision);
        append_u32(out, verification.completed_stage_mask);
        append_u32(out, verification.resolved_family_mask);
        append_u32(out, verification.missing_stage_mask);
        append_u32(out, verification.missing_family_mask);
        append_u64(out, verification.edge_satisfied_mask);
        append_u64(out, verification.edge_failed_mask);
        append_u64(out, verification.edge_unresolved_mask);
        out.push_back(verification.source_identity_valid);
        out.push_back(verification.ordered_xy_bound);
        out.push_back(verification.proof_identity_valid);
        out.push_back(verification.proof_packet_complete);
        out.push_back(verification.requires_vm81_authority);
        out.push_back(verification.monolithic_chain_ok);
        append_u32(out, verification.floating_point_authority);
        append_u32(out, verification.vm81_mutation_authority);
        append_u32(out, verification.hash72_commit_authority);
    }

    static std::uint32_t verification_difference(
        const HHSExactPass219MonolithicVerificationV1& left,
        const HHSExactPass219MonolithicVerificationV1& right
    ) noexcept {
        std::uint32_t mask = 0U;
        if (left.decision != right.decision) mask |= UINT32_C(1) << 0U;
        if (left.source_identity_valid != right.source_identity_valid) mask |= UINT32_C(1) << 1U;
        if (left.ordered_xy_bound != right.ordered_xy_bound) mask |= UINT32_C(1) << 2U;
        if (left.proof_identity_valid != right.proof_identity_valid) mask |= UINT32_C(1) << 3U;
        if (left.proof_packet_complete != right.proof_packet_complete) mask |= UINT32_C(1) << 4U;
        if (left.requires_vm81_authority != right.requires_vm81_authority) mask |= UINT32_C(1) << 5U;
        if (left.monolithic_chain_ok != right.monolithic_chain_ok) mask |= UINT32_C(1) << 6U;
        if (left.missing_stage_mask != right.missing_stage_mask) mask |= UINT32_C(1) << 7U;
        if (left.missing_family_mask != right.missing_family_mask) mask |= UINT32_C(1) << 8U;
        if (left.floating_point_authority != right.floating_point_authority ||
            left.vm81_mutation_authority != right.vm81_mutation_authority ||
            left.hash72_commit_authority != right.hash72_commit_authority)
            mask |= UINT32_C(1) << 9U;
        return mask;
    }

    bool build_source_topology() noexcept {
        std::array<std::uint16_t, vm_thread_count> stack{};
        std::array<ParenPair, parenthesis_thread_count> pairs{};
        std::array<std::uint16_t, equality_half_gate_thread_count> equal_offsets{};
        std::size_t depth = 0U;
        std::size_t pair_count = 0U;
        std::size_t equality_count = 0U;

        for (std::size_t i = 0U; i < source_.size(); ++i) {
            const std::uint8_t ch = source_[i];
            if (ch == static_cast<std::uint8_t>('(')) {
                if (depth >= stack.size()) return false;
                stack[depth++] = static_cast<std::uint16_t>(i);
            } else if (ch == static_cast<std::uint8_t>(')')) {
                if (depth == 0U || pair_count >= pairs.size()) return false;
                const std::uint16_t open = stack[--depth];
                pairs[pair_count++] = ParenPair{open, static_cast<std::uint16_t>(i)};
            } else if (ch == static_cast<std::uint8_t>('=')) {
                if (equality_count >= equal_offsets.size()) return false;
                equal_offsets[equality_count++] = static_cast<std::uint16_t>(i);
            }
        }
        if (depth != 0U || pair_count != parenthesis_thread_count ||
            equality_count != equality_half_gate_thread_count)
            return false;

        std::sort(pairs.begin(), pairs.end(), [](const ParenPair& a, const ParenPair& b) {
            return a.open < b.open;
        });

        std::size_t thread = 0U;
        for (const ParenPair& pair : pairs) {
            source_threads_[thread] = SourceThreadDescriptor{
                ThreadKind::ParenthesisShell,
                static_cast<std::uint8_t>(thread),
                0U,
                pair.open,
                pair.close
            };
            ++thread;
        }
        for (const std::uint16_t offset : equal_offsets) {
            source_threads_[thread] = SourceThreadDescriptor{
                ThreadKind::EqualityHalfGate,
                static_cast<std::uint8_t>(thread),
                0U,
                offset,
                offset
            };
            ++thread;
        }
        for (; thread < vm_thread_count; ++thread) {
            source_threads_[thread] = SourceThreadDescriptor{
                ThreadKind::VMIRDerived,
                static_cast<std::uint8_t>(thread),
                static_cast<std::uint8_t>(thread - source_structure_thread_count),
                0U,
                0U
            };
        }

        std::vector<std::uint8_t> material;
        material.insert(material.end(), source_.begin(), source_.end());
        for (const SourceThreadDescriptor& d : source_threads_) {
            material.push_back(static_cast<std::uint8_t>(d.kind));
            material.push_back(d.thread_id);
            material.push_back(d.derived_slot);
            append_u16(material, d.source_begin);
            append_u16(material, d.source_end);
        }
        hhs_hash216_compute_bytes(material.data(), material.size(), source_topology_hash216_.data());
        return true;
    }

    HHSExactStatus build_thread(
        const Lane& lane_state,
        const HHSExactPass219OctonionSurfaceV1& surface,
        std::size_t thread_id,
        ThreadCircuit& out
    ) const {
        out.source = source_threads_[thread_id];
        out.left_basis = static_cast<std::uint8_t>(thread_id / HHS_EXACT_PHASE_BASIS_COUNT);
        out.right_basis = static_cast<std::uint8_t>(thread_id % HHS_EXACT_PHASE_BASIS_COUNT);
        out.product = surface.products[thread_id];

        std::vector<std::uint8_t> material;
        material.reserve(2048U);
        material.push_back(static_cast<std::uint8_t>(out.source.kind));
        material.push_back(out.source.thread_id);
        material.push_back(out.source.derived_slot);
        append_u16(material, out.source.source_begin);
        append_u16(material, out.source.source_end);
        material.push_back(out.left_basis);
        material.push_back(out.right_basis);
        material.push_back(out.product.left_phase);
        material.push_back(out.product.right_phase);
        material.push_back(out.product.raw_additive_phase);
        material.push_back(out.product.phase);
        material.push_back(out.product.orientation);
        append_u16(material, out.product.ordered_tag);

        for (std::size_t cell = 0U; cell < vm_cells_per_thread; ++cell) {
            std::uint16_t permanent = 0U;
            const HHSExactStatus encoded = hhs_exact_vm5184_address_encode(
                static_cast<std::uint8_t>(cell), out.left_basis, out.right_basis, &permanent);
            if (encoded != HHS_EXACT_STATUS_OK ||
                permanent != cell * vm_thread_count + thread_id)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;

            std::uint8_t decoded_cell = 0U;
            std::uint8_t decoded_left = 0U;
            std::uint8_t decoded_right = 0U;
            if (hhs_exact_vm5184_address_decode(
                    permanent, &decoded_cell, &decoded_left, &decoded_right) != HHS_EXACT_STATUS_OK ||
                decoded_cell != cell || decoded_left != out.left_basis || decoded_right != out.right_basis)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;

            const std::uint32_t projected =
                static_cast<std::uint32_t>(permanent) * HHS188_G243_CONTROLS +
                static_cast<std::uint32_t>(lane_state.assignment.g243);
            HHS188Coordinate bott_coord{};
            if (hhs188_decode_projected(projected, &bott_coord) != HHS188_STATUS_OK ||
                bott_coord.permanent_state != permanent ||
                bott_coord.vm81_cell != cell || bott_coord.operation64 != thread_id ||
                bott_coord.g243 != lane_state.assignment.g243)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;

            HHS188Transition transition{};
            if (hhs188_transition_projected(projected, &transition) != HHS188_STATUS_OK ||
                hhs188_replay_transition(&transition) != HHS188_STATUS_OK)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;

            HHS189ContextAddress context{};
            context.cell81 = static_cast<std::uint8_t>(cell);
            context.operation64 = static_cast<std::uint8_t>(thread_id);
            context.g243 = lane_state.assignment.g243;
            context.kappa41 = lane_state.assignment.kappa41;
            std::uint32_t extended = 0U;
            if (hhs189_encode_context(&context, &extended) != HHS189_OK)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            HHS189ContextAddress decoded_context{};
            if (hhs189_decode_context(extended, &decoded_context) != HHS189_OK ||
                decoded_context.cell81 != cell || decoded_context.operation64 != thread_id ||
                decoded_context.g243 != lane_state.assignment.g243 ||
                decoded_context.kappa41 != lane_state.assignment.kappa41)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;

            const std::uint8_t bit = static_cast<std::uint8_t>(
                (lane_state.assignment.frame.words[cell] >> thread_id) & UINT64_C(1));
            out.vm81_bits[cell] = bit;
            out.projected_g243[cell] = projected;
            out.contextual_kappa41[cell] = extended;
            out.bott_output_basis[cell] = transition.output.basis8;

            material.push_back(bit);
            append_u32(material, projected);
            append_u32(material, extended);
            material.push_back(transition.output.basis8);
        }

        hhs_hash216_compute_bytes(material.data(), material.size(), out.thread_hash216.data());
        return HHS_EXACT_STATUS_OK;
    }

    LaneComputation compute_lane(std::size_t index) const {
        LaneComputation result{};
        const Lane& lane_state = lanes_[index];
        result.glyph = lane_state.glyph;
        result.a2_delta_exact_projection_equal = same_projection(a2_, delta_);

        result.status = hhs_exact_pass219_monolithic_verify_proof(
            &lane_state.assignment.proof, &result.verification);
        if (result.status != HHS_EXACT_STATUS_OK)
            return result;

        result.status = hhs_exact_pass219_octonion_from_vm81(
            &lane_state.assignment.frame,
            lane_state.assignment.x_cell,
            lane_state.assignment.y_cell,
            lane_state.assignment.z_cell,
            lane_state.assignment.w_cell,
            &result.octonion_surface);
        if (result.status != HHS_EXACT_STATUS_OK)
            return result;
        if (hhs_exact_pass219_octonion_validate_surface(&result.octonion_surface) != HHS_EXACT_STATUS_OK ||
            !same_octonion_state(
                result.octonion_surface.state,
                lane_state.assignment.proof.octonion_state)) {
            result.status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
            return result;
        }

        result.xy_zw_ordered_projection_equal =
            result.octonion_surface.state.xy == result.octonion_surface.state.zw;

        for (std::size_t thread = 0U; thread < vm_thread_count; ++thread) {
            result.status = build_thread(lane_state, result.octonion_surface, thread, result.threads[thread]);
            if (result.status != HHS_EXACT_STATUS_OK)
                return result;
        }
        result.full_vm5184_address_closure = true;
        result.full_hydration_roundtrip = true;

        std::array<std::uint8_t, HHS_EXACT_VM81_FRAME_BYTES> frame_bytes{};
        std::size_t frame_length = 0U;
        if (hhs_exact_vm81_frame_export_le(
                &lane_state.assignment.frame,
                frame_bytes.data(), frame_bytes.size(), &frame_length) != HHS_EXACT_STATUS_OK ||
            frame_length != frame_bytes.size()) {
            result.status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
            return result;
        }

        std::vector<std::uint8_t> material;
        material.reserve(24000U);
        material.push_back(static_cast<std::uint8_t>(lane_state.glyph));
        material.insert(material.end(), lane_state.equation.begin(), lane_state.equation.end());
        material.insert(material.end(), frame_bytes.begin(), frame_bytes.end());
        material.push_back(lane_state.assignment.x_cell);
        material.push_back(lane_state.assignment.y_cell);
        material.push_back(lane_state.assignment.z_cell);
        material.push_back(lane_state.assignment.w_cell);
        append_u16(material, lane_state.assignment.g243);
        material.push_back(lane_state.assignment.kappa41);
        material.insert(
            material.end(), source_topology_hash216_.begin(),
            source_topology_hash216_.begin() + HHS_HASH216_BYTES_LEN);
        for (const ThreadCircuit& thread : result.threads) {
            material.insert(
                material.end(), thread.thread_hash216.begin(),
                thread.thread_hash216.begin() + HHS_HASH216_BYTES_LEN);
        }
        append_proof_identity(material, lane_state.assignment.proof);
        append_verification_identity(material, result.verification);
        hhs_hash216_compute_bytes(material.data(), material.size(), result.lane_hash216.data());
        result.status = HHS_EXACT_STATUS_OK;
        return result;
    }

    void hash_contradiction(
        ContradictionEquation& equation,
        const LaneComputation& left,
        const LaneComputation& right
    ) const {
        std::vector<std::uint8_t> material;
        material.reserve(HHS_HASH216_BYTES_LEN * 2U + 96U);
        material.push_back(static_cast<std::uint8_t>(equation.left));
        material.push_back(static_cast<std::uint8_t>(equation.right));
        append_u64(material, equation.vm_thread_difference_mask);
        append_u64(material, equation.ordered_product_difference_mask);
        append_u32(material, equation.vm81_cell_difference_count);
        append_u64(material, equation.equality_edge_difference_mask);
        append_u32(material, equation.family_difference_mask);
        append_u32(material, equation.stage_difference_mask);
        append_u32(material, equation.verification_difference_mask);
        material.push_back(equation.candidate_state_identity_difference ? 1U : 0U);
        material.push_back(equation.proof_identity_difference ? 1U : 0U);
        material.insert(material.end(), left.lane_hash216.begin(), left.lane_hash216.begin() + HHS_HASH216_BYTES_LEN);
        material.insert(material.end(), right.lane_hash216.begin(), right.lane_hash216.begin() + HHS_HASH216_BYTES_LEN);
        hhs_hash216_compute_bytes(material.data(), material.size(), equation.equation_hash216.data());
    }

    void build_global() {
        global_ = GlobalComputation{};
        contradictions_.clear();
        global_.status = HHS_EXACT_STATUS_OK;
        global_.source_topology_exact = true;
        global_.all_lanes_computed = true;
        global_.a2_delta_exact_projection_equal = same_projection(a2_, delta_);
        global_.every_lane_xy_zw_projection_equal = true;
        global_.cross_domain_binding_requires_vm81 = true;
        global_.native_shared_invariant_proven = false;
        global_.canonical_proof = false;
        global_.requires_vm81_authority = true;
        global_.source_topology_hash216 = source_topology_hash216_;

        for (std::size_t i = 0U; i < lane_count; ++i) {
            global_.lane_hash216[i] = lane_results_[i].lane_hash216;
            global_.every_lane_xy_zw_projection_equal =
                global_.every_lane_xy_zw_projection_equal &&
                lane_results_[i].xy_zw_ordered_projection_equal;
            if (lane_results_[i].verification.decision == HHS_EXACT_PASS219_MONOLITHIC_REJECTED)
                ++global_.rejected_lane_count;
            else if (lane_results_[i].verification.decision == HHS_EXACT_PASS219_MONOLITHIC_UNRESOLVED)
                ++global_.unresolved_lane_count;
            if (lane_results_[i].verification.proof_packet_complete == 1U)
                ++global_.proof_packet_complete_lane_count;
        }

        for (std::size_t i = 0U; i < lane_count; ++i) {
            for (std::size_t j = i + 1U; j < lane_count; ++j) {
                ContradictionEquation equation{};
                equation.left = static_cast<Glyph>(i);
                equation.right = static_cast<Glyph>(j);

                for (std::size_t thread = 0U; thread < vm_thread_count; ++thread) {
                    if (lane_results_[i].threads[thread].thread_hash216 !=
                        lane_results_[j].threads[thread].thread_hash216)
                        equation.vm_thread_difference_mask |= UINT64_C(1) << thread;
                    const auto& lp = lane_results_[i].octonion_surface.products[thread];
                    const auto& rp = lane_results_[j].octonion_surface.products[thread];
                    if (lp.left_phase != rp.left_phase || lp.right_phase != rp.right_phase ||
                        lp.raw_additive_phase != rp.raw_additive_phase || lp.phase != rp.phase ||
                        lp.orientation != rp.orientation || lp.ordered_tag != rp.ordered_tag)
                        equation.ordered_product_difference_mask |= UINT64_C(1) << thread;
                }
                for (std::size_t cell = 0U; cell < HHS_EXACT_VM81_CELLS; ++cell) {
                    if (lanes_[i].assignment.frame.words[cell] != lanes_[j].assignment.frame.words[cell])
                        ++equation.vm81_cell_difference_count;
                }
                equation.equality_edge_difference_mask =
                    (lane_results_[i].verification.edge_satisfied_mask ^ lane_results_[j].verification.edge_satisfied_mask) |
                    (lane_results_[i].verification.edge_failed_mask ^ lane_results_[j].verification.edge_failed_mask) |
                    (lane_results_[i].verification.edge_unresolved_mask ^ lane_results_[j].verification.edge_unresolved_mask);
                equation.family_difference_mask =
                    lane_results_[i].verification.resolved_family_mask ^
                    lane_results_[j].verification.resolved_family_mask;
                equation.stage_difference_mask =
                    lane_results_[i].verification.completed_stage_mask ^
                    lane_results_[j].verification.completed_stage_mask;
                equation.verification_difference_mask = verification_difference(
                    lane_results_[i].verification,
                    lane_results_[j].verification);
                equation.candidate_state_identity_difference =
                    std::memcmp(
                        lanes_[i].assignment.proof.candidate_state_hash216,
                        lanes_[j].assignment.proof.candidate_state_hash216,
                        HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) != 0;
                equation.proof_identity_difference =
                    !same_proof_identity(
                        lanes_[i].assignment.proof,
                        lanes_[j].assignment.proof);

                const bool contradiction =
                    equation.vm_thread_difference_mask != 0U ||
                    equation.ordered_product_difference_mask != 0U ||
                    equation.vm81_cell_difference_count != 0U ||
                    equation.equality_edge_difference_mask != 0U ||
                    equation.family_difference_mask != 0U ||
                    equation.stage_difference_mask != 0U ||
                    equation.verification_difference_mask != 0U ||
                    equation.candidate_state_identity_difference ||
                    equation.proof_identity_difference;
                if (contradiction) {
                    hash_contradiction(equation, lane_results_[i], lane_results_[j]);
                    contradictions_.push_back(equation);
                }
            }
        }
        global_.emergent_equation_count = static_cast<std::uint32_t>(contradictions_.size());

        std::vector<std::uint8_t> material;
        material.reserve(24000U);
        material.insert(
            material.end(), source_topology_hash216_.begin(),
            source_topology_hash216_.begin() + HHS_HASH216_BYTES_LEN);
        append_projection(material, a2_);
        append_projection(material, delta_);
        for (const auto& lane_hash : global_.lane_hash216)
            material.insert(material.end(), lane_hash.begin(), lane_hash.begin() + HHS_HASH216_BYTES_LEN);
        for (const ContradictionEquation& equation : contradictions_)
            material.insert(
                material.end(), equation.equation_hash216.begin(),
                equation.equation_hash216.begin() + HHS_HASH216_BYTES_LEN);
        material.push_back(global_.a2_delta_exact_projection_equal ? 1U : 0U);
        material.push_back(global_.every_lane_xy_zw_projection_equal ? 1U : 0U);
        material.push_back(global_.cross_domain_binding_requires_vm81 ? 1U : 0U);
        hhs_hash216_compute_bytes(
            material.data(), material.size(), global_.contradiction_graph_hash216.data());

        if (!global_.source_topology_exact || !global_.a2_delta_exact_projection_equal ||
            !global_.every_lane_xy_zw_projection_equal || global_.rejected_lane_count != 0U)
            global_.status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
    bool computed_{false};
    ExactProjection a2_{};
    ExactProjection delta_{};
    std::array<std::uint8_t, HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH> source_{};
    std::array<SourceThreadDescriptor, vm_thread_count> source_threads_{};
    std::array<char, HHS_HASH216_BYTES_STRLEN> source_topology_hash216_{};
    std::array<Lane, lane_count> lanes_{};
    std::array<LaneComputation, lane_count> lane_results_{};
    std::vector<ContradictionEquation> contradictions_{};
    GlobalComputation global_{};
};

}  // namespace hhs::rna

#endif