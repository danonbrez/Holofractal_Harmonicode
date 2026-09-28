#include "hhs_pass219_lane5_nine_loop_knowledge_hydration_cell_wall_1_75.hpp"

#include <cstddef>
#include <cinttypes>
#include <cstdio>
#include <cstring>

namespace hhs::lane5 {
namespace {

constexpr char kAdmittedCorpusRootHash72[] =
    "0000000000000000000000000000002721Ip^KPnKF(sDVftNJCSFA1nW1v*8lgdQX?exMhE";
constexpr char kKnowledgeGraphRootHash72[] =
    "0000000000000000000000000000003ZOZmmCFNEq6a!I>kRKjlHqhXFOLxxAN4aleMzR7hM";
constexpr char kAdmissionReplayBundleSha256[] =
    "6d4ab72612278a3b1a27f8cab61a1de6e2a958275817b50aaa71ea11ac9a1b40";
constexpr char kRetrievalReplayBundleSha256[] =
    "9f509009a450e58e9d0fa91041e91dc69c2f20ea63d957f98cbd64526a38731a";

bool hash216_text_valid(const char value[HHS_HASH216_LEN + 1]) noexcept {
    if (value == nullptr || value[HHS_HASH216_LEN] != '\0')
        return false;
    for (std::size_t i = 0U; i < HHS_HASH216_LEN; ++i) {
        if (value[i] == '\0')
            return false;
    }
    return true;
}

template <std::size_t N>
bool exact_text(const char (&value)[N], const char (&expected)[N]) noexcept {
    return std::memcmp(value, expected, N) == 0;
}

bool exact_knowledge_witness(
    const NineLoopKnowledgeHydrationInput& input
) noexcept {
    return exact_text(
               input.admitted_corpus_root_hash72,
               kAdmittedCorpusRootHash72
           ) &&
           exact_text(
               input.knowledge_graph_root_hash72,
               kKnowledgeGraphRootHash72
           ) &&
           exact_text(
               input.admission_replay_bundle_sha256,
               kAdmissionReplayBundleSha256
           ) &&
           exact_text(
               input.retrieval_replay_bundle_sha256,
               kRetrievalReplayBundleSha256
           ) &&
           input.admitted_record_count == UINT32_C(13) &&
           input.admission_replay_count == UINT32_C(13) &&
           input.graph_node_count == UINT32_C(13) &&
           input.graph_edge_count == UINT32_C(12) &&
           input.query_count == UINT32_C(12) &&
           input.all_admission_replays_validated == 1U &&
           input.all_query_replays_validated == 1U &&
           input.knowledge_authority == 1U &&
           input.graph_projection_only == 1U &&
           input.execution_authority_requested == 0U &&
           input.mutation_authority_requested == 0U &&
           input.persistence_authority_requested == 0U &&
           input.canonical_hash_mint_requested == 0U &&
           input.model_weight_update_requested == 0U &&
           input.learning_commit_requested == 0U;
}

}  // namespace

HHSExactStatus NineLoopKnowledgeHydrationCellWall::derive_candidate_hash216(
    const NineLoopKnowledgeHydrationInput& input,
    char out_hash216[HHS_HASH216_LEN + 1]
) noexcept {
    if (out_hash216 == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hash216_text_valid(input.parent_generalization_hash216) ||
        !exact_knowledge_witness(input))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    char material[1400]{};
    const int written = std::snprintf(
        material,
        sizeof(material),
        "HHS-P219-LANE5-NINE-LOOP-1.75|"
        "parent=%s|corpus=%s|graph=%s|admissionReplay=%s|retrievalReplay=%s|"
        "records=%" PRIu32 "|admissionReplays=%" PRIu32
        "|nodes=%" PRIu32 "|edges=%" PRIu32 "|queries=%" PRIu32
        "|admissionReplayValid=%u|queryReplayValid=%u|knowledge=%u|graphOnly=%u|"
        "executionRequest=%u|mutationRequest=%u|persistenceRequest=%u|"
        "hashMintRequest=%u|weightRequest=%u|learningRequest=%u",
        input.parent_generalization_hash216,
        input.admitted_corpus_root_hash72,
        input.knowledge_graph_root_hash72,
        input.admission_replay_bundle_sha256,
        input.retrieval_replay_bundle_sha256,
        input.admitted_record_count,
        input.admission_replay_count,
        input.graph_node_count,
        input.graph_edge_count,
        input.query_count,
        static_cast<unsigned>(input.all_admission_replays_validated),
        static_cast<unsigned>(input.all_query_replays_validated),
        static_cast<unsigned>(input.knowledge_authority),
        static_cast<unsigned>(input.graph_projection_only),
        static_cast<unsigned>(input.execution_authority_requested),
        static_cast<unsigned>(input.mutation_authority_requested),
        static_cast<unsigned>(input.persistence_authority_requested),
        static_cast<unsigned>(input.canonical_hash_mint_requested),
        static_cast<unsigned>(input.model_weight_update_requested),
        static_cast<unsigned>(input.learning_commit_requested)
    );
    if (written <= 0 || static_cast<std::size_t>(written) >= sizeof(material))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    HHSHash216 hash{};
    hhs_hash216_compute(material, static_cast<std::size_t>(written), &hash);
    std::memcpy(out_hash216, hash.value, HHS_HASH216_LEN + 1U);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus NineLoopKnowledgeHydrationCellWall::evaluate(
    const NineLoopKnowledgeHydrationInput& input,
    const char expected_hash216[HHS_HASH216_LEN + 1],
    NineLoopKnowledgeHydrationReceipt& out
) const noexcept {
    out = NineLoopKnowledgeHydrationReceipt{};
    out.version = kNineLoopKnowledgeHydrationVersion;
    out.namespace_id = kNineLoopKnowledgeHydrationNamespace;
    out.candidate_only = 1U;

    NineLoopGeneralizationCellWall parent_wall;
    NineLoopGeneralizationReceipt parent_receipt{};
    HHSExactStatus status = parent_wall.evaluate(
        input.parent_input,
        input.parent_generalization_hash216,
        parent_receipt
    );
    if (status != HHS_EXACT_STATUS_OK ||
        parent_receipt.accepted != 1U ||
        parent_receipt.candidate_only != 1U ||
        parent_receipt.execution_authority != 0U ||
        parent_receipt.model_weight_update_authority != 0U ||
        parent_receipt.learning_commit_authority != 0U ||
        parent_receipt.canonical_vm81_mutation_authority != 0U ||
        parent_receipt.canonical_hash72_authority != 0U ||
        parent_receipt.canonical_hash216_authority != 0U ||
        parent_receipt.canonical_persistence_authority != 0U ||
        parent_receipt.floating_point_canonical_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.parent_1_73_verified = 1U;
    std::memcpy(
        out.parent_hash216,
        parent_receipt.generalization_candidate_hash216,
        HHS_HASH216_LEN + 1U
    );

    if (!exact_knowledge_witness(input))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.frozen_receipts_verified = 1U;
    out.admission_replay_verified = 1U;
    out.retrieval_replay_verified = 1U;
    out.graph_shape_verified = 1U;
    out.knowledge_authority = 1U;
    out.graph_projection_only = 1U;

    status = derive_candidate_hash216(
        input,
        out.knowledge_hydration_candidate_hash216
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!hash216_text_valid(expected_hash216) ||
        std::memcmp(
            expected_hash216,
            out.knowledge_hydration_candidate_hash216,
            HHS_HASH216_LEN + 1U
        ) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.hash216_replay_verified = 1U;
    out.accepted = 1U;
    return HHS_EXACT_STATUS_OK;
}

}  // namespace hhs::lane5
