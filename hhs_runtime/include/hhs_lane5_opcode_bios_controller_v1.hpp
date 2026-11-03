#ifndef HHS_LANE5_OPCODE_BIOS_CONTROLLER_V1_HPP
#define HHS_LANE5_OPCODE_BIOS_CONTROLLER_V1_HPP
/* Additive Pass219+ C++ cell-wall controlled opcode channel.
 * The evaluated 1.75 knowledge-hydration receipt gates binding, not the
 * external input's assertions. The BIOS cannot mutate VM81 or mint hashes. */
#include "hhs_pass219_lane5_nine_loop_knowledge_hydration_cell_wall_1_75.hpp"
#include "../acceleration/hhs_lane5_opcode_bios_v1.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <mutex>
namespace hhs::lane5 {
class NativeOpcodeBIOSController final {
public:
    NativeOpcodeBIOSController() noexcept = default;
    NativeOpcodeBIOSController(const NativeOpcodeBIOSController&) = delete;
    NativeOpcodeBIOSController& operator=(const NativeOpcodeBIOSController&) = delete;
    ~NativeOpcodeBIOSController() noexcept { invalidate(); }

    /* Caller supplies already authenticated, immutable SQL-recovered bytes.
     * This gate validates inherited Pass219 1.75 cell-wall evidence.
     * SQL encryption/AAD verification remains owned by Pass174/1.39. */
    HHSExactStatus bind_verified_candidate(
        const NineLoopKnowledgeHydrationInput& proof,
        const char expected_hash216[HHS_HASH216_LEN + 1],
        const std::uint8_t hash216[HHS_BIOS_HASH216_BYTES],
        const std::uint8_t frame[HHS_BIOS_FRAME_BYTES],
        std::uint64_t generation
    ) noexcept;

    int dispatch(std::uint64_t generation,
                 const hhs_bios_instruction* operations,
                 std::size_t count, hhs_bios_result* results) noexcept;
    int read216(std::uint64_t generation, std::uint16_t offset,
                std::uint8_t* value) noexcept;
    void invalidate() noexcept;
private:
    std::mutex mutex_;
    std::array<std::uint8_t,HHS_BIOS_HASH216_BYTES> hash216_{};
    std::array<std::uint8_t,HHS_BIOS_FRAME_BYTES> frame_{};
    hhs_bios_cache cache_{};
};
} // namespace hhs::lane5
#endif
