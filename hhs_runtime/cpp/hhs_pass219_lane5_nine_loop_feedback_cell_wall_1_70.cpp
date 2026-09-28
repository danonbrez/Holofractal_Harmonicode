#include "hhs_pass219_lane5_nine_loop_feedback_cell_wall_1_70.hpp"

#include <cstddef>
#include <cinttypes>
#include <cstdio>
#include <cstring>

namespace hhs::lane5 {
namespace {

constexpr char kParentRelationSha256[] =
    "4acc66c250129d5a42f976d673027313707633012b2de6f85d6491a4083ed73a";
constexpr char kParentSupportSha256[] =
    "64cd7ae9027ef41969948efc35b1273ba03ba3f759c076700d8a09940ebbf54d";
constexpr char kWolframFeedbackMaterialSha256[] =
    "ba58c70820f0f3e5bd3a352b89441face87d07ea7ce776b1b8481c21393c69e1";
constexpr char kFeedbackPayloadSha256[] =
    "78f2cc37e9304017cf0b6a233f2cb5ab080757fec57e6eb5897295bf0d2bed70";
constexpr char kGenesisIdentity[] =
    "F(x,y,a,b)=(x+y)^2+(xy-a^2)^2+(a^2-b)^2+(a^4-2)^2";

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

bool exact_genesis(const NineLoopFeedbackInput& input) noexcept {
    if (std::memcmp(
            input.genesis_identity,
            kGenesisIdentity,
            sizeof(kGenesisIdentity)
        ) != 0)
        return false;
    for (std::size_t i = sizeof(kGenesisIdentity);
         i < sizeof(input.genesis_identity); ++i) {
        if (input.genesis_identity[i] != '\0')
            return false;
    }
    return true;
}

bool exact_feedback_witness(const NineLoopFeedbackInput& input) noexcept {
    return exact_text(input.parent_relation_sha256, kParentRelationSha256) &&
           exact_text(input.parent_support_sha256, kParentSupportSha256) &&
           exact_text(
               input.wolfram_feedback_material_sha256,
               kWolframFeedbackMaterialSha256
           ) &&
           exact_text(input.feedback_payload_sha256, kFeedbackPayloadSha256) &&
           exact_genesis(input) &&
           input.root_seed_numerator == UINT64_C(179971179971) &&
           input.root_seed_denominator == UINT32_C(1000000) &&
           input.certified_rational_coordinates == UINT32_C(1014476) &&
           input.two_prime_only_coordinates == UINT32_C(3821) &&
           input.total_nonzero_coordinates == UINT32_C(1018297) &&
           input.certified_rational_coordinates +
               input.two_prime_only_coordinates ==
               input.total_nonzero_coordinates &&
           input.comparison_rows == UINT32_C(107053) &&
           input.comparison_two_prime_only_rows == UINT32_C(3401) &&
           input.literal_container_identity_assumption == -1 &&
           input.logical_representation_equivalence == 1 &&
           input.support_geometry == 1 &&
           input.foreign_rational_reconstruction_complete == -1 &&
           input.wolfram_receipt_verified == 1U &&
           input.deviation_vector_verified == 1U;
}

}  // namespace

HHSExactStatus NineLoopFeedbackCellWall::derive_candidate_hash216(
    const NineLoopFeedbackInput& input,
    char out_hash216[HHS_HASH216_LEN + 1]
) noexcept {
    if (out_hash216 == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hash216_text_valid(input.parent_large_artifact_hash216) ||
        !exact_feedback_witness(input))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    char material[1500]{};
    const int written = std::snprintf(
        material,
        sizeof(material),
        "HHS-P219-LANE5-NINE-LOOP-1.70|"
        "parent=%s|relation=%s|support=%s|wolfram=%s|payload=%s|"
        "root=%" PRIu64 "/%" PRIu32 "|certified=%" PRIu32
        "|total=%" PRIu32 "|twoPrime=%" PRIu32
        "|comparison=%" PRIu32 "|comparisonTwoPrime=%" PRIu32
        "|container=%d|logical=%d|supportState=%d|reconstruction=%d|"
        "wolframVerified=%u|deviationVerified=%u|genesis=%s",
        input.parent_large_artifact_hash216,
        input.parent_relation_sha256,
        input.parent_support_sha256,
        input.wolfram_feedback_material_sha256,
        input.feedback_payload_sha256,
        input.root_seed_numerator,
        input.root_seed_denominator,
        input.certified_rational_coordinates,
        input.total_nonzero_coordinates,
        input.two_prime_only_coordinates,
        input.comparison_rows,
        input.comparison_two_prime_only_rows,
        static_cast<int>(input.literal_container_identity_assumption),
        static_cast<int>(input.logical_representation_equivalence),
        static_cast<int>(input.support_geometry),
        static_cast<int>(input.foreign_rational_reconstruction_complete),
        static_cast<unsigned>(input.wolfram_receipt_verified),
        static_cast<unsigned>(input.deviation_vector_verified),
        input.genesis_identity
    );
    if (written <= 0 || static_cast<std::size_t>(written) >= sizeof(material))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    HHSHash216 hash{};
    hhs_hash216_compute(material, static_cast<std::size_t>(written), &hash);
    std::memcpy(out_hash216, hash.value, HHS_HASH216_LEN + 1U);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus NineLoopFeedbackCellWall::evaluate(
    const NineLoopFeedbackInput& input,
    const char expected_hash216[HHS_HASH216_LEN + 1],
    NineLoopFeedbackReceipt& out
) const noexcept {
    out = NineLoopFeedbackReceipt{};
    out.version = kNineLoopFeedbackVersion;
    out.namespace_id = kNineLoopFeedbackNamespace;
    out.candidate_only = 1U;

    NineLoopLargeArtifactCellWall parent_wall;
    NineLoopLargeArtifactReceipt parent_receipt{};
    HHSExactStatus status = parent_wall.evaluate(
        input.parent_input,
        input.parent_large_artifact_hash216,
        parent_receipt
    );
    if (status != HHS_EXACT_STATUS_OK ||
        parent_receipt.accepted != 1U ||
        parent_receipt.candidate_only != 1U ||
        parent_receipt.canonical_vm81_mutation_authority != 0U ||
        parent_receipt.canonical_hash72_authority != 0U ||
        parent_receipt.canonical_hash216_authority != 0U ||
        parent_receipt.canonical_persistence_authority != 0U ||
        parent_receipt.floating_point_canonical_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.parent_1_69_verified = 1U;
    std::memcpy(
        out.parent_hash216,
        parent_receipt.large_artifact_candidate_hash216,
        HHS_HASH216_LEN + 1U
    );

    if (!exact_feedback_witness(input))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out.relation_identity_verified = 1U;
    out.wolfram_receipt_verified = 1U;
    out.feedback_payload_verified = 1U;
    out.coverage_verified = 1U;
    out.genesis_identity_verified = 1U;
    out.deviation_vector_verified = 1U;

    status = derive_candidate_hash216(input, out.feedback_candidate_hash216);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!hash216_text_valid(expected_hash216) ||
        std::memcmp(
            expected_hash216,
            out.feedback_candidate_hash216,
            HHS_HASH216_LEN + 1U
        ) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.hash216_replay_verified = 1U;
    out.accepted = 1U;
    return HHS_EXACT_STATUS_OK;
}

}  // namespace hhs::lane5
