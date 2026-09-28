#include "hhs_pass219_lane5_nine_loop_large_artifact_cell_wall_1_69.hpp"

#include <cstddef>
#include <cinttypes>
#include <cstdio>
#include <cstring>

namespace hhs::lane5 {
namespace {

constexpr char kP1SourceSha256[] =
    "75a52ebb4526bdb788ae8101e4908d52579637b6aaca1a308e4d783b4a8afe86";
constexpr char kP2SourceSha256[] =
    "13c231664403d35e8ad68747302c7bc26bcc9b1b567d0da0d65444c980c8eb97";
constexpr char kComparisonSourceSha256[] =
    "d01e62885b74d13650b44baf8da3e42d15bab35c99f6ee778e66df4059ecf37d";
constexpr char kSeptupleSourceSha256[] =
    "082abcea6a66fb434b24938236f443f2703e7e76ded8911f46ffffa292a2c5e1";
constexpr char kE0SupportSha256[] =
    "64cd7ae9027ef41969948efc35b1273ba03ba3f759c076700d8a09940ebbf54d";
constexpr char kComparisonNormalizedSha256[] =
    "884b05ed4118ed372329c8b002b895dfa98bd92fe72cdd0f88b47cef94448d11";
constexpr char kSeptupleStructureSha256[] =
    "606c5db22ac881a92835cf12e7077d0093c8b599b5205d3e0752be91e82c3967";
constexpr char kRelationSha256[] =
    "4acc66c250129d5a42f976d673027313707633012b2de6f85d6491a4083ed73a";

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

bool exact_large_witness(const NineLoopLargeArtifactInput& input) noexcept {
    return exact_text(input.p1_source_sha256, kP1SourceSha256) &&
           exact_text(input.p2_source_sha256, kP2SourceSha256) &&
           exact_text(input.comparison_source_sha256, kComparisonSourceSha256) &&
           exact_text(input.septuple_source_sha256, kSeptupleSourceSha256) &&
           exact_text(input.e0_support_sha256, kE0SupportSha256) &&
           exact_text(
               input.comparison_normalized_sha256,
               kComparisonNormalizedSha256
           ) &&
           exact_text(
               input.septuple_structure_sha256,
               kSeptupleStructureSha256
           ) &&
           exact_text(input.relation_sha256, kRelationSha256) &&
           input.matrix_rows == kNineLoopMatrixRows &&
           input.matrix_columns == kNineLoopMatrixColumns &&
           input.matrix_nonzero == kNineLoopMatrixNonzero &&
           input.comparison_rows == kNineLoopComparisonRows &&
           input.source_manifest_verified == 1U &&
           input.logical_equivalence_verified == 1U &&
           input.archive_integrity_verified == 1U &&
           input.comparison_integrity_verified == 1U;
}

}  // namespace

HHSExactStatus NineLoopLargeArtifactCellWall::derive_candidate_hash216(
    const NineLoopLargeArtifactInput& input,
    char out_hash216[HHS_HASH216_LEN + 1]
) noexcept {
    if (out_hash216 == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hash216_text_valid(input.parent_source_hash216) ||
        !exact_large_witness(input))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    char material[1400]{};
    const int written = std::snprintf(
        material,
        sizeof(material),
        "HHS-P219-LANE5-NINE-LOOP-1.69|"
        "parent=%s|p1=%s|p2=%s|comparison=%s|septuple=%s|"
        "support=%s|comparisonNormalized=%s|septupleStructure=%s|"
        "relation=%s|rows=%" PRIu32 "|cols=%" PRIu32
        "|nonzero=%" PRIu32 "|comparisonRows=%" PRIu32
        "|manifest=%u|logical=%u|archive=%u|comparisonIntegrity=%u",
        input.parent_source_hash216,
        input.p1_source_sha256,
        input.p2_source_sha256,
        input.comparison_source_sha256,
        input.septuple_source_sha256,
        input.e0_support_sha256,
        input.comparison_normalized_sha256,
        input.septuple_structure_sha256,
        input.relation_sha256,
        input.matrix_rows,
        input.matrix_columns,
        input.matrix_nonzero,
        input.comparison_rows,
        static_cast<unsigned>(input.source_manifest_verified),
        static_cast<unsigned>(input.logical_equivalence_verified),
        static_cast<unsigned>(input.archive_integrity_verified),
        static_cast<unsigned>(input.comparison_integrity_verified)
    );
    if (written <= 0 || static_cast<std::size_t>(written) >= sizeof(material))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    HHSHash216 hash{};
    hhs_hash216_compute(material, static_cast<std::size_t>(written), &hash);
    std::memcpy(out_hash216, hash.value, HHS_HASH216_LEN + 1U);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus NineLoopLargeArtifactCellWall::evaluate(
    const NineLoopLargeArtifactInput& input,
    const char expected_hash216[HHS_HASH216_LEN + 1],
    NineLoopLargeArtifactReceipt& out
) const noexcept {
    out = NineLoopLargeArtifactReceipt{};
    out.version = kNineLoopLargeArtifactVersion;
    out.namespace_id = kNineLoopLargeArtifactNamespace;
    out.candidate_only = 1U;

    NineLoopSourceAttestationCellWall parent_wall;
    NineLoopSourceAttestationReceipt parent_receipt{};
    HHSExactStatus status = parent_wall.evaluate(
        input.parent_input,
        input.parent_source_hash216,
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

    out.parent_1_68_verified = 1U;
    std::memcpy(
        out.parent_hash216,
        parent_receipt.source_candidate_hash216,
        HHS_HASH216_LEN + 1U
    );

    if (!exact_large_witness(input))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out.source_identities_verified = 1U;
    out.matrix_geometry_verified = 1U;
    out.support_geometry_verified = 1U;
    out.comparison_verified = 1U;
    out.archive_verified = 1U;
    out.relation_identity_verified = 1U;

    status = derive_candidate_hash216(
        input,
        out.large_artifact_candidate_hash216
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!hash216_text_valid(expected_hash216) ||
        std::memcmp(
            expected_hash216,
            out.large_artifact_candidate_hash216,
            HHS_HASH216_LEN + 1U
        ) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.hash216_replay_verified = 1U;
    out.accepted = 1U;
    return HHS_EXACT_STATUS_OK;
}

}  // namespace hhs::lane5
