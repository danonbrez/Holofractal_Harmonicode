#ifndef HHS_PASS219_ORTHOGONAL_GLYPH_MEMBRANE_1_21_HPP
#define HHS_PASS219_ORTHOGONAL_GLYPH_MEMBRANE_1_21_HPP

#include "hhs_pass219_monolithic_constraint_abi_1_20.h"
#include "hhs_hash216_bytes.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <future>
#include <string_view>
#include <utility>
#include <vector>

namespace hhs::rna {

class OrthogonalGlyphMembrane final {
public:
    enum class Glyph : std::uint8_t {
        P = 0,
        t,
        p,
        q,
        Delta,
        m,
        b,
        c,
        u,
        s,
        x,
        y,
        z,
        w,
        xy,
        yx,
        zw,
        wz,
        At,
        f,
        Bt,
        A,
        B,
        a2,
        Count
    };

    static constexpr std::size_t lane_count = static_cast<std::size_t>(Glyph::Count);
    static constexpr std::size_t lane_width = HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN;
    static constexpr std::size_t hydration_fabric_size = HHS_EXACT_HASH72_COORDS;
    static constexpr std::uint8_t canonical_a2 = 1U;

    struct HydrationBand final {
        std::uint16_t lane_ordinal{};
        std::uint16_t begin{};
        std::uint16_t end{};
    };

    struct Lane final {
        Glyph glyph{Glyph::P};
        HydrationBand hydration{};
        std::array<std::uint8_t, HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH> equation{};
        HHSExactPass219MonolithicProofV1 proof{};
        bool assigned{false};
    };

    struct LaneComputation final {
        HHSExactStatus status{HHS_EXACT_STATUS_INVALID_ARGUMENT};
        Glyph glyph{Glyph::P};
        HydrationBand hydration{};
        HHSExactPass219MonolithicVerificationV1 verification{};
        bool intrinsic_phase_defined{false};
        std::uint8_t intrinsic_phase{0U};
        std::array<char, HHS_HASH216_BYTES_STRLEN> lane_hash216{};
    };

    struct ContradictionEquation final {
        Glyph left{Glyph::P};
        Glyph right{Glyph::P};
        std::uint16_t left_lane{};
        std::uint16_t right_lane{};
        std::uint64_t edge_state_xor{};
        std::uint32_t family_state_xor{};
        std::uint32_t stage_state_xor{};
        bool phase_contradiction{false};
        bool decision_contradiction{false};
        bool candidate_state_contradiction{false};
    };

    struct GlobalComputation final {
        HHSExactStatus status{HHS_EXACT_STATUS_INVALID_ARGUMENT};
        bool invariant_xy_zw_a2_delta{false};
        bool all_lanes_computed{false};
        bool canonical_proof{false};
        bool requires_vm81_authority{true};
        std::uint32_t rejected_lane_count{};
        std::uint32_t unresolved_lane_count{};
        std::uint32_t proof_packet_complete_lane_count{};
        std::uint32_t emergent_equation_count{};
        std::uint64_t emergent_edge_mask{};
        std::uint32_t emergent_family_mask{};
        std::uint32_t emergent_stage_mask{};
        std::array<char, hydration_fabric_size> lane_hash216_fabric{};
        std::array<char, HHS_HASH216_BYTES_STRLEN> contradiction_graph_hash216{};
    };

    OrthogonalGlyphMembrane(
        const HHSExactPass219OctonionStateV1& octonion_state,
        const HHSExactBigUIntView& delta
    ) noexcept
        : octonion_state_(octonion_state) {
        if (delta.struct_size < sizeof(delta) || delta.bytes_be == nullptr ||
            delta.byte_length != 1U || delta.bytes_be[0] != canonical_a2) {
            status_ = HHS_EXACT_STATUS_INVARIANT_FAILURE;
            return;
        }
        if (hhs_exact_pass219_octonion_validate_state(&octonion_state_) != HHS_EXACT_STATUS_OK) {
            status_ = HHS_EXACT_STATUS_INVARIANT_FAILURE;
            return;
        }
        if (octonion_state_.xy != canonical_a2 ||
            octonion_state_.zw != canonical_a2) {
            status_ = HHS_EXACT_STATUS_INVARIANT_FAILURE;
            return;
        }

        std::array<std::uint8_t, HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH> source{};
        std::size_t source_length = 0U;
        const HHSExactStatus source_status = hhs_exact_pass219_monolithic_native_source(
            source.data(), source.size(), &source_length);
        if (source_status != HHS_EXACT_STATUS_OK || source_length != source.size()) {
            status_ = source_status == HHS_EXACT_STATUS_OK
                ? HHS_EXACT_STATUS_INVARIANT_FAILURE
                : source_status;
            return;
        }

        for (std::size_t i = 0; i < lane_count; ++i) {
            lanes_[i].glyph = static_cast<Glyph>(i);
            lanes_[i].hydration.lane_ordinal = static_cast<std::uint16_t>(i);
            lanes_[i].hydration.begin = static_cast<std::uint16_t>(i * lane_width);
            lanes_[i].hydration.end = static_cast<std::uint16_t>((i + 1U) * lane_width - 1U);
            lanes_[i].equation = source;
        }
        invariant_closed_ = true;
        status_ = HHS_EXACT_STATUS_OK;
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool invariant_closed() const noexcept { return invariant_closed_; }

    const HHSExactPass219OctonionStateV1& octonion_state() const noexcept {
        return octonion_state_;
    }

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
        const std::size_t index = static_cast<std::size_t>(glyph);
        return lanes_[index < lane_count ? index : 0U];
    }

    const LaneComputation& lane_result(Glyph glyph) const noexcept {
        const std::size_t index = static_cast<std::size_t>(glyph);
        return lane_results_[index < lane_count ? index : 0U];
    }

    const std::vector<ContradictionEquation>& contradictions() const noexcept {
        return contradictions_;
    }

    const GlobalComputation& global() const noexcept { return global_; }

    HHSExactStatus assign_lane(
        Glyph glyph,
        const HHSExactPass219MonolithicProofV1& proof
    ) noexcept {
        if (status_ != HHS_EXACT_STATUS_OK)
            return status_;
        const std::size_t index = static_cast<std::size_t>(glyph);
        if (index >= lane_count)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        if (proof.struct_size < sizeof(proof) ||
            proof.version != hhs_exact_pass219_monolithic_version())
            return HHS_EXACT_STATUS_VERSION_MISMATCH;
        if (!same_octonion_state(proof.octonion_state, octonion_state_))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        lanes_[index].proof = proof;
        lanes_[index].assigned = true;
        computed_ = false;
        return HHS_EXACT_STATUS_OK;
    }

    HHSExactStatus assign_all(
        const std::array<HHSExactPass219MonolithicProofV1, lane_count>& proofs
    ) noexcept {
        for (std::size_t i = 0; i < lane_count; ++i) {
            const HHSExactStatus lane_status = assign_lane(static_cast<Glyph>(i), proofs[i]);
            if (lane_status != HHS_EXACT_STATUS_OK)
                return lane_status;
        }
        return HHS_EXACT_STATUS_OK;
    }

    HHSExactStatus compute_parallel() {
        if (status_ != HHS_EXACT_STATUS_OK)
            return status_;
        for (const Lane& current : lanes_) {
            if (!current.assigned)
                return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        }

        std::array<std::future<LaneComputation>, lane_count> futures{};
        try {
            for (std::size_t i = 0; i < lane_count; ++i) {
                futures[i] = std::async(std::launch::async, [this, i]() {
                    return compute_lane(i);
                });
            }
            for (std::size_t i = 0; i < lane_count; ++i) {
                lane_results_[i] = futures[i].get();
                if (lane_results_[i].status != HHS_EXACT_STATUS_OK)
                    return lane_results_[i].status;
            }
        } catch (...) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }

        build_global_computation();
        computed_ = true;
        return global_.status;
    }

    bool computed() const noexcept { return computed_; }

private:
    static_assert(lane_count == 24U, "orthogonal glyph registry must contain 24 lanes");
    static_assert(lane_count * lane_width == hydration_fabric_size,
                  "24 Hash216 glyph lanes must close the 5184 hydration fabric");
    static_assert(lane_width == HHS_HASH216_BYTES_LEN,
                  "each orthogonal glyph lane must occupy one Hash216-width band");

    static bool same_octonion_state(
        const HHSExactPass219OctonionStateV1& left,
        const HHSExactPass219OctonionStateV1& right
    ) noexcept {
        return left.struct_size == right.struct_size &&
               left.version == right.version &&
               left.x == right.x && left.y == right.y &&
               left.z == right.z && left.w == right.w &&
               left.xy == right.xy && left.yx == right.yx &&
               left.zw == right.zw && left.wz == right.wz;
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

    std::pair<bool, std::uint8_t> intrinsic_phase(Glyph glyph) const noexcept {
        switch (glyph) {
            case Glyph::x: return {true, octonion_state_.x};
            case Glyph::y: return {true, octonion_state_.y};
            case Glyph::z: return {true, octonion_state_.z};
            case Glyph::w: return {true, octonion_state_.w};
            case Glyph::xy: return {true, octonion_state_.xy};
            case Glyph::yx: return {true, octonion_state_.yx};
            case Glyph::zw: return {true, octonion_state_.zw};
            case Glyph::wz: return {true, octonion_state_.wz};
            case Glyph::Delta: return {true, canonical_a2};
            case Glyph::a2: return {true, canonical_a2};
            default: return {false, 0U};
        }
    }

    LaneComputation compute_lane(std::size_t index) const {
        LaneComputation result{};
        const Lane& current = lanes_[index];
        result.glyph = current.glyph;
        result.hydration = current.hydration;
        result.status = hhs_exact_pass219_monolithic_verify_proof(
            &current.proof, &result.verification);
        if (result.status != HHS_EXACT_STATUS_OK)
            return result;

        const auto phase = intrinsic_phase(current.glyph);
        result.intrinsic_phase_defined = phase.first;
        result.intrinsic_phase = phase.second;

        std::vector<std::uint8_t> material;
        material.reserve(
            current.equation.size() + HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN + 64U);
        material.push_back(static_cast<std::uint8_t>(current.glyph));
        append_u16(material, current.hydration.lane_ordinal);
        append_u16(material, current.hydration.begin);
        append_u16(material, current.hydration.end);
        material.insert(material.end(), current.equation.begin(), current.equation.end());
        append_u32(material, result.verification.decision);
        append_u32(material, result.verification.completed_stage_mask);
        append_u32(material, result.verification.resolved_family_mask);
        append_u64(material, result.verification.edge_satisfied_mask);
        append_u64(material, result.verification.edge_failed_mask);
        append_u64(material, result.verification.edge_unresolved_mask);
        material.push_back(result.verification.source_identity_valid);
        material.push_back(result.verification.ordered_xy_bound);
        material.push_back(result.verification.proof_identity_valid);
        material.push_back(result.verification.proof_packet_complete);
        material.push_back(result.verification.requires_vm81_authority);
        material.push_back(result.verification.monolithic_chain_ok);
        material.push_back(result.intrinsic_phase_defined ? 1U : 0U);
        material.push_back(result.intrinsic_phase);
        material.insert(
            material.end(),
            current.proof.candidate_state_hash216,
            current.proof.candidate_state_hash216 + HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN);

        hhs_hash216_compute_bytes(
            material.data(), material.size(), result.lane_hash216.data());
        return result;
    }

    void build_global_computation() {
        contradictions_.clear();
        global_ = GlobalComputation{};
        global_.status = HHS_EXACT_STATUS_OK;
        global_.invariant_xy_zw_a2_delta = invariant_closed_ &&
            octonion_state_.xy == canonical_a2 &&
            octonion_state_.zw == canonical_a2;
        global_.all_lanes_computed = true;
        global_.canonical_proof = false;
        global_.requires_vm81_authority = true;

        for (std::size_t i = 0; i < lane_count; ++i) {
            const LaneComputation& result = lane_results_[i];
            if (result.verification.decision == HHS_EXACT_PASS219_MONOLITHIC_REJECTED)
                ++global_.rejected_lane_count;
            if (result.verification.decision == HHS_EXACT_PASS219_MONOLITHIC_UNRESOLVED)
                ++global_.unresolved_lane_count;
            if (result.verification.proof_packet_complete == 1U)
                ++global_.proof_packet_complete_lane_count;
            std::memcpy(
                global_.lane_hash216_fabric.data() + i * lane_width,
                result.lane_hash216.data(), lane_width);
        }

        for (std::size_t left_index = 0; left_index < lane_count; ++left_index) {
            for (std::size_t right_index = left_index + 1U;
                 right_index < lane_count;
                 ++right_index) {
                const LaneComputation& left_result = lane_results_[left_index];
                const LaneComputation& right_result = lane_results_[right_index];
                const Lane& left_lane = lanes_[left_index];
                const Lane& right_lane = lanes_[right_index];

                ContradictionEquation equation{};
                equation.left = left_lane.glyph;
                equation.right = right_lane.glyph;
                equation.left_lane = static_cast<std::uint16_t>(left_index);
                equation.right_lane = static_cast<std::uint16_t>(right_index);
                equation.edge_state_xor =
                    (left_result.verification.edge_satisfied_mask ^
                     right_result.verification.edge_satisfied_mask) |
                    (left_result.verification.edge_failed_mask ^
                     right_result.verification.edge_failed_mask) |
                    (left_result.verification.edge_unresolved_mask ^
                     right_result.verification.edge_unresolved_mask);
                equation.family_state_xor =
                    left_result.verification.resolved_family_mask ^
                    right_result.verification.resolved_family_mask;
                equation.stage_state_xor =
                    left_result.verification.completed_stage_mask ^
                    right_result.verification.completed_stage_mask;
                equation.phase_contradiction =
                    left_result.intrinsic_phase_defined &&
                    right_result.intrinsic_phase_defined &&
                    left_result.intrinsic_phase != right_result.intrinsic_phase;
                equation.decision_contradiction =
                    left_result.verification.decision != right_result.verification.decision;
                equation.candidate_state_contradiction =
                    std::memcmp(
                        left_lane.proof.candidate_state_hash216,
                        right_lane.proof.candidate_state_hash216,
                        HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) != 0;

                if (equation.edge_state_xor != 0U ||
                    equation.family_state_xor != 0U ||
                    equation.stage_state_xor != 0U ||
                    equation.phase_contradiction ||
                    equation.decision_contradiction ||
                    equation.candidate_state_contradiction) {
                    global_.emergent_edge_mask |= equation.edge_state_xor;
                    global_.emergent_family_mask |= equation.family_state_xor;
                    global_.emergent_stage_mask |= equation.stage_state_xor;
                    contradictions_.push_back(equation);
                }
            }
        }

        global_.emergent_equation_count =
            static_cast<std::uint32_t>(contradictions_.size());

        std::vector<std::uint8_t> graph_material;
        graph_material.reserve(
            global_.lane_hash216_fabric.size() + contradictions_.size() * 32U + 32U);
        graph_material.insert(
            graph_material.end(),
            global_.lane_hash216_fabric.begin(),
            global_.lane_hash216_fabric.end());
        graph_material.push_back(global_.invariant_xy_zw_a2_delta ? 1U : 0U);
        append_u32(graph_material, global_.rejected_lane_count);
        append_u32(graph_material, global_.unresolved_lane_count);
        append_u32(graph_material, global_.proof_packet_complete_lane_count);
        append_u32(graph_material, global_.emergent_equation_count);
        append_u64(graph_material, global_.emergent_edge_mask);
        append_u32(graph_material, global_.emergent_family_mask);
        append_u32(graph_material, global_.emergent_stage_mask);

        for (const ContradictionEquation& equation : contradictions_) {
            graph_material.push_back(static_cast<std::uint8_t>(equation.left));
            graph_material.push_back(static_cast<std::uint8_t>(equation.right));
            append_u16(graph_material, equation.left_lane);
            append_u16(graph_material, equation.right_lane);
            append_u64(graph_material, equation.edge_state_xor);
            append_u32(graph_material, equation.family_state_xor);
            append_u32(graph_material, equation.stage_state_xor);
            graph_material.push_back(equation.phase_contradiction ? 1U : 0U);
            graph_material.push_back(equation.decision_contradiction ? 1U : 0U);
            graph_material.push_back(equation.candidate_state_contradiction ? 1U : 0U);
        }

        hhs_hash216_compute_bytes(
            graph_material.data(),
            graph_material.size(),
            global_.contradiction_graph_hash216.data());

        if (!global_.invariant_xy_zw_a2_delta || global_.rejected_lane_count != 0U)
            global_.status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    HHSExactPass219OctonionStateV1 octonion_state_{};
    std::array<Lane, lane_count> lanes_{};
    std::array<LaneComputation, lane_count> lane_results_{};
    std::vector<ContradictionEquation> contradictions_{};
    GlobalComputation global_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
    bool invariant_closed_{false};
    bool computed_{false};
};

static_assert(OrthogonalGlyphMembrane::lane_count == 24U);
static_assert(
    OrthogonalGlyphMembrane::lane_count * OrthogonalGlyphMembrane::lane_width ==
    OrthogonalGlyphMembrane::hydration_fabric_size);

}  // namespace hhs::rna

#endif
