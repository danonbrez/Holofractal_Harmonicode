#include "hhs_pass219_rna_execution_composer_1_14.hpp"

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
    HHSExactPass219RNAPriorStateReferenceSealV1 seal{};
    HHSExactPass219RNAIndexedPriorStateV1 indexed{};
    HHSExactPass219RNALineageV1 lineage{};
    HHSExactVM81Frame predecessor{};
    HHSExactVM81Frame candidate_frame{};
    HHSExactPass219RNAAdmissionCandidateV1 candidate{};
    std::uint8_t frontier[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES]{};
    std::uint8_t changed_frontier[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES]{};

    identity.struct_size = static_cast<std::uint32_t>(sizeof(identity));
    identity.version = hhs_exact_pass219_rna_retrieval_version();
    std::memset(identity.program_hash216, '2', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    identity.program_hash216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
    std::memset(identity.predecessor_state_hash216, '1', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    identity.predecessor_state_hash216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
    std::memset(identity.predecessor_hash72, '0', HHS_EXACT_HASH72_LEN);
    identity.predecessor_hash72[HHS_EXACT_HASH72_LEN] = '\0';
    identity.checkpoint_counter = UINT64_C(49);
    for (std::size_t i = 0; i < sizeof(frontier); ++i) {
        frontier[i] = static_cast<std::uint8_t>(i * 5U + 7U);
        changed_frontier[i] = frontier[i];
        identity.dependency_frontier_sha256[i] = frontier[i];
    }
    changed_frontier[5] ^= 1U;
    for (std::size_t i = 0; i < HHS_EXACT_PASS219_RNA_RETRIEVAL_SHA256_BYTES; ++i) {
        identity.predecessor_hash216_digest_sha256[i] = static_cast<std::uint8_t>(i + 1U);
        identity.retrieval_source_sha256[i] = static_cast<std::uint8_t>(i + 33U);
        identity.authenticated_index_sha256[i] = static_cast<std::uint8_t>(i + 65U);
    }
    for (std::size_t i = 0; i < HHS_EXACT_VM81_CELLS; ++i) {
        predecessor.words[i] = UINT64_C(0x0101010100000000) ^ static_cast<std::uint64_t>(i);
        candidate_frame.words[i] = UINT64_C(0x0202020200000000) ^ static_cast<std::uint64_t>(i);
    }
    assert(hhs_exact_pass219_rna_reference_seal_from_replay(
        &identity, &predecessor, &predecessor, &seal) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_indexed_prior_state_init(
        &identity, &predecessor, &indexed) == HHS_EXACT_STATUS_OK);

    lineage.struct_size = static_cast<std::uint32_t>(sizeof(lineage));
    lineage.version = hhs_exact_pass219_rna_rule_version();
    assert(hhs_exact_pass219_native_phase_witness(
        HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y, &lineage.native_phase) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_coordinate_from_pass189(
        41U, 0, 1U, 0U, &lineage.coordinate) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_trinary_phase_gate(
        lineage.coordinate.trit, &lineage.trinary_gate) == HHS_EXACT_STATUS_OK);
    std::memset(lineage.predecessor_hash72, '0', HHS_EXACT_HASH72_LEN);
    lineage.predecessor_hash72[HHS_EXACT_HASH72_LEN] = '\0';
    std::memset(lineage.predecessor_hash216_identity, '1', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    lineage.predecessor_hash216_identity[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';

    Domain a{10U, 20U, HHS_EXACT_PHASE_X, 0U, HHS_EXACT_PASS219_RNA_ROLE_TOEHOLD};
    Domain b{20U, 10U, HHS_EXACT_PHASE_Y, 1U, HHS_EXACT_PASS219_RNA_ROLE_HAIRPIN};
    Strand strand{7U};
    assert(strand.add(a) == HHS_EXACT_STATUS_OK);
    assert(strand.add(b) == HHS_EXACT_STATUS_OK);
    TranscriptionProgram program{114U};
    InhibitionGate inhibit{1U, 10U, 20U};
    assert(program.add(inhibit) == HHS_EXACT_STATUS_OK);
    TranscriptionWitness witness{strand, program, lineage};
    assert(witness.status() == HHS_EXACT_STATUS_OK);

    AuthenticatedPriorState prior{indexed, seal};
    assert(prior.status() == HHS_EXACT_STATUS_OK);
    assert(prior.classification() == HHS_EXACT_RNA_STATE_RETRIEVAL_OK);

    ExecutionPlan normal{prior, frontier};
    assert(normal.status() == HHS_EXACT_STATUS_OK);
    assert(normal.route() == HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_INDEXED_CONTINUATION);
    assert(normal.uses_indexed_continuation());
    assert(!normal.genesis_replay_required());
    assert(normal.record().indexed_reuse_count == 1U);
    assert(normal.record().genesis_replay_count == 0U);
    assert(normal.prepare_candidate(prior, witness, candidate_frame, candidate) == HHS_EXACT_STATUS_OK);

    ExecutionPlan proof_export{
        prior, frontier, HHS_EXACT_PASS219_RNA_BYPASS_FIRST_PRINCIPLES_EXPORT};
    assert(proof_export.status() == HHS_EXACT_STATUS_OK);
    assert(proof_export.route() == HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_GENESIS_REPLAY);
    assert(proof_export.effective_bypass_reason() == HHS_EXACT_PASS219_RNA_BYPASS_FIRST_PRINCIPLES_EXPORT);
    assert(proof_export.genesis_replay_required());
    assert(proof_export.record().genesis_replay_count == 1U);
    assert(proof_export.prepare_candidate(prior, witness, candidate_frame, candidate) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    ExecutionPlan dependency_change{prior, changed_frontier};
    assert(dependency_change.status() == HHS_EXACT_STATUS_OK);
    assert(dependency_change.route() == HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_DEPENDENCY_SCOPED_RECOMPUTE);
    assert(dependency_change.effective_bypass_reason() == HHS_EXACT_PASS219_RNA_BYPASS_DEPENDENCY_CHANGED);
    assert(!dependency_change.genesis_replay_required());
    assert(dependency_change.record().unaffected_reuse_preserved == 1U);

    static_assert(!has_commit_member<ExecutionPlan>::value,
                  "C++ execution plan must not expose VM81 commit authority");
    static_assert(!has_admit_member<ExecutionPlan>::value,
                  "C++ execution plan must not expose VM81 admission authority");
    static_assert(!has_commit_member<AuthenticatedPriorState>::value,
                  "C++ retrieval wrapper must remain non-authoritative");
    static_assert(std::is_standard_layout_v<HHSExactPass219RNAExecutionPlanV1>);
    static_assert(std::is_trivially_copyable_v<HHSExactPass219RNAExecutionPlanV1>);

    return 0;
}
