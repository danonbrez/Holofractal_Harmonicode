#ifndef HHS_PASS220_V156_ORDERED_GEOMETRY_RESOURCE_TRANSFER_V1_HPP
#define HHS_PASS220_V156_ORDERED_GEOMETRY_RESOURCE_TRANSFER_V1_HPP

/* Pass 220 V156: owned read-only geometry resource transfer from V153 preflight.
 * This transfers exact position bytes, not a VM81 receipt or a trusted producer
 * certificate. The existing Lane 5 / GFX4 admission is still authoritative.
 */
#include "hhs_pass220_v153_geometry_resource_binding_cell_v1.hpp"
#include <array>
#include <cstddef>
#include <cstdint>
#include <utility>

namespace hhs::game::v156 {

enum class TransferDecision : std::uint8_t {
    Prepared = 0U,
    PreflightRejected = 1U,
    StaleTick = 2U,
    DrawResourceMismatch = 3U,
    SourceChanged = 4U
};

class OrderedGeometryResource final {
public:
    static constexpr std::size_t kBytes = v152::kPositionBytes;
    using Payload = std::array<std::uint8_t, kBytes>;

    explicit OrderedGeometryResource(
        Payload bytes, std::uint64_t tick, std::uint64_t resource
    ) noexcept : bytes_(std::move(bytes)), tick_(tick), resource_(resource) {}

    const Payload& bytes() const noexcept { return bytes_; }
    const std::uint8_t* data() const noexcept { return bytes_.data(); }
    std::size_t size() const noexcept { return bytes_.size(); }
    std::uint64_t producer_tick() const noexcept { return tick_; }
    std::uint64_t draw_resource_id() const noexcept { return resource_; }

private:
    const Payload bytes_;
    const std::uint64_t tick_;
    const std::uint64_t resource_;
};

struct TransferResult final {
    TransferDecision decision{TransferDecision::PreflightRejected};
    v153::BindingDecision inherited_decision{v153::BindingDecision::Missing};
    std::uint64_t producer_tick{};
    std::uint64_t draw_resource_id{};
    std::size_t copied_bytes{};
    std::uint8_t exact_source_content_equal{};
    std::uint8_t physical_source_provenance_verified{};
    std::uint8_t vm81_admission_authority{};
    std::uint8_t physics_mutation_authority{};
};

inline TransferResult prepare_owned_resource(
    const v153::GeometryResourceCandidate& candidate,
    std::uint64_t expected_completed_tick,
    std::uint64_t expected_draw_resource_id,
    OrderedGeometryResource::Payload& out_bytes
) noexcept {
    TransferResult result{};
    const auto inherited = v153::prepare(candidate);
    result.inherited_decision = inherited.decision;
    if (inherited.decision != v153::BindingDecision::Prepared) {
        return result;
    }
    if (candidate.projection.producer_tick != expected_completed_tick) {
        result.decision = TransferDecision::StaleTick;
        return result;
    }
    if (expected_draw_resource_id == 0U ||
        candidate.gfx4_draw_resource_id != expected_draw_resource_id) {
        result.decision = TransferDecision::DrawResourceMismatch;
        return result;
    }

    // Source is validated again after copying. A concurrent write or a
    // changed byte fails closed instead of publishing a torn observation.
    OrderedGeometryResource::Payload copy{};
    for (std::size_t i = 0U; i < copy.size(); ++i) {
        copy[i] = candidate.projection.position_f32le[i];
    }
    for (std::size_t i = 0U; i < copy.size(); ++i) {
        if (copy[i] != candidate.source_position_f32le[i] ||
            copy[i] != candidate.projection.position_f32le[i]) {
            result.decision = TransferDecision::SourceChanged;
            return result;
        }
    }
    out_bytes = std::move(copy);
    result.decision = TransferDecision::Prepared;
    result.producer_tick = expected_completed_tick;
    result.draw_resource_id = expected_draw_resource_id;
    result.copied_bytes = v152::kPositionBytes;
    result.exact_source_content_equal = 1U;
    // Ownership/byte equality is not origin attestation.
    return result;
}

} // namespace hhs::game::v156
#endif
