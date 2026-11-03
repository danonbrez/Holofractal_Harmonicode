#include "hhs_lane5_opcode_bios_controller_v1.hpp"
#include <algorithm>
#include <cstring>
namespace hhs::lane5 {
HHSExactStatus NativeOpcodeBIOSController::bind_verified_candidate(
    const NineLoopKnowledgeHydrationInput& proof,
    const char expected_hash216[HHS_HASH216_LEN + 1],
    const std::uint8_t hash216[HHS_BIOS_HASH216_BYTES],
    const std::uint8_t frame[HHS_BIOS_FRAME_BYTES],
    std::uint64_t generation
) noexcept {
    if (!expected_hash216 || !hash216 || !frame || !generation)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    NineLoopKnowledgeHydrationReceipt witness{};
    const auto status = NineLoopKnowledgeHydrationCellWall{}.evaluate(
        proof, expected_hash216, witness);
    if (status != HHS_EXACT_STATUS_OK || witness.accepted != 1U ||
        witness.candidate_only != 1U ||
        witness.execution_authority != 0U ||
        witness.canonical_vm81_mutation_authority != 0U ||
        witness.canonical_hash72_mint_authority != 0U ||
        witness.canonical_hash216_authority != 0U ||
        witness.canonical_persistence_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    std::lock_guard<std::mutex> lock(mutex_);
    hhs_bios_invalidate(&cache_);
    std::fill(hash216_.begin(), hash216_.end(), 0);
    std::fill(frame_.begin(), frame_.end(), 0);
    std::memcpy(hash216_.data(), hash216, hash216_.size());
    std::memcpy(frame_.data(), frame, frame_.size());
    const hhs_bios_view view{hash216_.data(),frame_.data(),generation};
    if(hhs_bios_bind(&cache_,&view) != HHS_BIOS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}
HHSExactStatus NativeOpcodeBIOSController::bind_indexed_candidate(
    const NineLoopKnowledgeHydrationInput& proof,
    const char expected_hash216[HHS_HASH216_LEN + 1],
    const hhs_hash216_lower_input& lowering,
    const char expected_index_root[65],
    const std::uint8_t frame[HHS_BIOS_FRAME_BYTES],
    std::uint64_t generation
) noexcept {
    if (!expected_hash216 || !expected_index_root || !frame)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    hhs_hash216_lower_output lowered{};
    if (hhs_hash216_lower_pass174(&lowering,&lowered) != 0 ||
        std::memcmp(expected_index_root,lowered.index_root_sha256,65) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    auto status = bind_verified_candidate(
        proof,expected_hash216,
        reinterpret_cast<const std::uint8_t*>(lowered.combined),
        frame,generation);
    if(status != HHS_EXACT_STATUS_OK) return status;
    std::lock_guard<std::mutex> lock(mutex_);
    for(std::size_t i=0;i<index_blocks_.size();++i)
        std::memcpy(index_blocks_[i].data(),lowered.character_indexes_sha256[i],65);
    indexed_=true;
    return HHS_EXACT_STATUS_OK;
}
int NativeOpcodeBIOSController::read_index(
    std::uint64_t generation,std::uint16_t position,char digest_hex[65]
) noexcept {
    if(!digest_hex || position>=216) return HHS_BIOS_BAD_ARGUMENT;
    std::lock_guard<std::mutex> lock(mutex_);
    if(!indexed_ || !cache_.bound || generation!=cache_.bound_generation)
        return HHS_BIOS_STALE;
    std::memcpy(digest_hex,index_blocks_[position].data(),65);
    return HHS_BIOS_OK;
}
int NativeOpcodeBIOSController::dispatch(
    std::uint64_t generation, const hhs_bios_instruction* ops,
    std::size_t count, hhs_bios_result* out) noexcept {
    std::lock_guard<std::mutex> lock(mutex_);
    return hhs_bios_dispatch(&cache_,generation,ops,count,out);
}
int NativeOpcodeBIOSController::read216(
    std::uint64_t generation,std::uint16_t pos,std::uint8_t* out) noexcept {
    std::lock_guard<std::mutex> lock(mutex_);
    return hhs_bios_read216(&cache_,generation,pos,out);
}
void NativeOpcodeBIOSController::invalidate() noexcept {
    std::lock_guard<std::mutex> lock(mutex_);
    hhs_bios_invalidate(&cache_);
    std::fill(hash216_.begin(),hash216_.end(),0);
    std::fill(frame_.begin(),frame_.end(),0);
}
} // namespace hhs::lane5
