#include "hhs_pass219_rna_state_retrieval_1_13.hpp"

#include <cassert>
#include <cstdint>
#include <cstring>
#include <type_traits>

template <class T, class = void>
struct has_commit_member : std::false_type {};

template <class T>
struct has_commit_member<T, std::void_t<decltype(&T::commit)>> : std::true_type {};

template <class T, class = void>
struct has_admit_member : std::false_type {};

template <class T>
struct has_admit_member<T, std::void_t<decltype(&T::admit)>> : std::true_type {};

int main() {
    using namespace hhs::rna;

    HHSExactPass219RNAPriorStateIdentityV1 identity{};
    HHSExactVM81Frame reference{};
    HHSExactVM81Frame replay{};
    HHSExactPass219RNAPriorStateReferenceSealV1 seal{};
    HHSExactPass219RNAIndexedPriorStateV1 indexed{};

    identity.struct_size = static_cast<std::uint32_t>(sizeof(identity));
    identity.version = hhs_exact_pass219_rna_retrieval_version();
    std::memset(identity.program_hash216, '2', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    identity.program_hash216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
    std::memset(identity.predecessor_state_hash216, '1', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    identity.predecessor_state_hash216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
    std::memset(identity.predecessor_hash72, '0', HHS_EXACT_HASH72_LEN);
    identity.predecessor_hash72[HHS_EXACT_HASH72_LEN] = '\0';
    identity.checkpoint_counter = UINT64_C(48);
    for (std::size_t i = 0; i < HHS_EXACT_PASS219_RNA_RETRIEVAL_SHA256_BYTES; ++i) {
        identity.predecessor_hash216_digest_sha256[i] = static_cast<std::uint8_t>(i + 1U);
        identity.retrieval_source_sha256[i] = static_cast<std::uint8_t>(i + 33U);
        identity.authenticated_index_sha256[i] = static_cast<std::uint8_t>(i + 65U);
        identity.dependency_frontier_sha256[i] = static_cast<std::uint8_t>(i + 97U);
    }
    for (std::size_t i = 0; i < HHS_EXACT_VM81_CELLS; ++i) {
        reference.words[i] = UINT64_C(0xAABBCCDD00000000) ^ static_cast<std::uint64_t>(i);
        replay.words[i] = reference.words[i];
    }

    assert(hhs_exact_pass219_rna_reference_seal_from_replay(
        &identity, &reference, &replay, &seal) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_indexed_prior_state_init(
        &identity, &reference, &indexed) == HHS_EXACT_STATUS_OK);

    AuthenticatedPriorState prior{indexed, seal};
    assert(prior.status() == HHS_EXACT_STATUS_OK);
    assert(prior.classification() == HHS_EXACT_RNA_STATE_RETRIEVAL_OK);
    assert(!prior.fallback_required());
    assert(!prior.index_invalidated());
    assert(std::memcmp(&prior.record().predecessor_frame, &reference, sizeof(reference)) == 0);

    indexed.predecessor_frame.words[0] ^= UINT64_C(1);
    AuthenticatedPriorState mismatch{indexed, seal};
    assert(mismatch.status() == HHS_EXACT_STATUS_OK);
    assert(mismatch.classification() == HHS_EXACT_RNA_STATE_RETRIEVAL_MISMATCH);
    assert(mismatch.fallback_required());
    assert(mismatch.index_invalidated());

    static_assert(!has_commit_member<AuthenticatedPriorState>::value,
                  "C++ retrieval wrapper must not expose VM81 commit authority");
    static_assert(!has_admit_member<AuthenticatedPriorState>::value,
                  "C++ retrieval wrapper must not expose VM81 admission authority");
    static_assert(std::is_trivially_copyable_v<HHSExactPass219RNAStateRetrievalV1>);

    return 0;
}
