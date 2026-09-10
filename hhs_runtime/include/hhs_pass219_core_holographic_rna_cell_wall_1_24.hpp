#ifndef HHS_PASS219_CORE_HOLOGRAPHIC_RNA_CELL_WALL_1_24_HPP
#define HHS_PASS219_CORE_HOLOGRAPHIC_RNA_CELL_WALL_1_24_HPP

#include "hhs_pass219_orthogonal_glyph_membrane_1_21.hpp"
#include "hhs_pass219_core_holographic_four_lane_1_24.h"

#include <array>
#include <cstdint>
#include <future>

namespace hhs::rna {

class CoreHolographicRNACellWall final {
public:
    explicit CoreHolographicRNACellWall(OrthogonalGlyphMembrane& membrane) noexcept
        : membrane_(membrane) {}

    HHSExactStatus status() const noexcept {
        return membrane_.status();
    }

    OrthogonalGlyphMembrane& membrane() noexcept {
        return membrane_;
    }

    const OrthogonalGlyphMembrane& membrane() const noexcept {
        return membrane_;
    }

    HHSExactStatus route_parallel(
        const HHSExactVM81Frame& frame,
        const HHSExactPass219Hash216TransitionViewV1& transition,
        std::uint8_t feedback_lane,
        std::int8_t feedback_trinary,
        HHSExactPass219Holo4StateV1& state,
        HHSExactPass219Holo4PreparedV1& prepared,
        HHSExactPass219Holo4DecisionV1& decision
    ) {
        if (membrane_.status() != HHS_EXACT_STATUS_OK)
            return membrane_.status();

        HHSExactStatus result = hhs_exact_pass219_holo4_prepare(
            &frame, &transition, &state, &prepared);
        if (result != HHS_EXACT_STATUS_OK)
            return result;

        struct ScoreResult final {
            HHSExactStatus status{HHS_EXACT_STATUS_INVALID_ARGUMENT};
            HHSExactPass219Holo4LaneScoreV1 score{};
        };

        std::array<std::future<ScoreResult>, HHS_EXACT_PASS219_HOLO4_LANE_COUNT> futures{};
        std::array<HHSExactPass219Holo4LaneScoreV1, HHS_EXACT_PASS219_HOLO4_LANE_COUNT> lanes{};
        try {
            for (std::uint8_t lane = 0U;
                 lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT;
                 ++lane) {
                futures[lane] = std::async(
                    std::launch::async,
                    [&prepared, &state, lane]() {
                        ScoreResult out{};
                        out.status = hhs_exact_pass219_holo4_score_lane(
                            &prepared, &state, lane, &out.score);
                        return out;
                    });
            }
            for (std::uint8_t lane = 0U;
                 lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT;
                 ++lane) {
                ScoreResult out = futures[lane].get();
                if (out.status != HHS_EXACT_STATUS_OK)
                    return out.status;
                lanes[lane] = out.score;
            }
        } catch (...) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }

        return hhs_exact_pass219_holo4_finalize(
            &prepared,
            lanes.data(),
            feedback_lane,
            feedback_trinary,
            &state,
            &decision);
    }

private:
    OrthogonalGlyphMembrane& membrane_;
};

}  // namespace hhs::rna

#endif
