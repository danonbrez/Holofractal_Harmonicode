#include "hhs_pass219_lane5_nine_loop_source_cell_wall_1_68.hpp"

#include <cstdio>
#include <cstdlib>
#include <cstring>

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static hhs::lane5::NineLoopForeignMetadata parent_metadata() {
    hhs::lane5::NineLoopForeignMetadata value{};
    value.loop_order = 9U;
    value.symbol_weight = 18U;
    value.primitive_alphabet_count = 9U;
    value.quintuple_coproduct_count = 424U;
    value.weight13_basis_dimension = 5431U;
    value.delta0_octuple_term_count = 295186924U;
    value.septuple_determining_nonzero_coefficients = 107053U;
    value.quintuple_rank = 400U;
    value.sample_numerator = -105757;
    value.sample_denominator = 65536U;
    value.prime_moduli[0] = 2147483647U;
    value.prime_moduli[1] = 2147483629U;
    value.sample_residues[0] = 829521918U;
    value.sample_residues[1] = 1173913588U;
    value.foreign_delta_is_kinematic = 1U;
    value.native_delta_e_is_error_closure = 1U;
    value.delta_alias_authorized = 0U;
    value.dual_route_agreement = 1U;
    return value;
}

static hhs::lane5::NineLoopSourceAttestationInput exact_input() {
    using namespace hhs::lane5;
    NineLoopSourceAttestationInput input{};
    input.parent_metadata = parent_metadata();
    const HHSExactStatus parent_status =
        NineLoopForeignEquivalenceCellWall::derive_candidate_hash216(
            input.parent_metadata,
            input.parent_candidate_hash216
        );
    if (parent_status != HHS_EXACT_STATUS_OK) {
        std::fprintf(stderr, "failed to derive parent Hash216\n");
        std::abort();
    }
    std::strcpy(
        input.manifest_sha256,
        "f96534526482f03e638ee030b1a88968348901f70967bb89618c76420a21ffe5"
    );
    std::strcpy(
        input.sample_sha256,
        "a78557e58efb3e12cccb647974131a3f694322bebb97607a5648db0484099b18"
    );
    std::strcpy(
        input.summary_sha256,
        "fbda1f90205bcf4f02b154aba25346aa83768e6cbbccbeeceaef9187eb691088"
    );
    input.nonzero_rows = 20400U;
    input.zero_rows = 230U;
    input.total_rows = 20630U;
    input.unique_words = 20630U;
    input.manifest_member_verified = 1U;
    input.all_nonzero_rationals_exact = 1U;
    input.all_zero_rows_exact = 1U;
    return input;
}

int main() {
    using namespace hhs::lane5;

    auto input = exact_input();
    char candidate[HHS_HASH216_LEN + 1]{};
    char replay[HHS_HASH216_LEN + 1]{};

    CHECK(
        NineLoopSourceAttestationCellWall::derive_candidate_hash216(input, candidate) ==
        HHS_EXACT_STATUS_OK
    );
    CHECK(std::strlen(candidate) == HHS_HASH216_LEN);
    CHECK(
        NineLoopSourceAttestationCellWall::derive_candidate_hash216(input, replay) ==
        HHS_EXACT_STATUS_OK
    );
    CHECK(std::strcmp(candidate, replay) == 0);

    NineLoopSourceAttestationCellWall wall;
    NineLoopSourceAttestationReceipt receipt{};
    CHECK(wall.evaluate(input, candidate, receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.accepted == 1U);
    CHECK(receipt.parent_1_67_verified == 1U);
    CHECK(receipt.manifest_identity_verified == 1U);
    CHECK(receipt.sample_identity_verified == 1U);
    CHECK(receipt.summary_identity_verified == 1U);
    CHECK(receipt.exact_row_counts_verified == 1U);
    CHECK(receipt.exact_rational_replay_verified == 1U);
    CHECK(receipt.manifest_membership_verified == 1U);
    CHECK(receipt.candidate_only == 1U);
    CHECK(receipt.canonical_vm81_mutation_authority == 0U);
    CHECK(receipt.canonical_hash72_authority == 0U);
    CHECK(receipt.canonical_hash216_authority == 0U);
    CHECK(receipt.canonical_persistence_authority == 0U);
    CHECK(receipt.floating_point_canonical_authority == 0U);
    CHECK(std::strcmp(candidate, receipt.source_candidate_hash216) == 0);

    auto sample_tamper = exact_input();
    sample_tamper.sample_sha256[0] =
        sample_tamper.sample_sha256[0] == 'a' ? 'b' : 'a';
    CHECK(
        wall.evaluate(sample_tamper, candidate, receipt) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE
    );

    auto count_tamper = exact_input();
    count_tamper.nonzero_rows = 20399U;
    CHECK(
        wall.evaluate(count_tamper, candidate, receipt) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE
    );

    auto membership_tamper = exact_input();
    membership_tamper.manifest_member_verified = 0U;
    CHECK(
        wall.evaluate(membership_tamper, candidate, receipt) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE
    );

    auto parent_tamper = exact_input();
    parent_tamper.parent_metadata.delta_alias_authorized = 1U;
    CHECK(
        wall.evaluate(parent_tamper, candidate, receipt) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE
    );

    char wrong[HHS_HASH216_LEN + 1]{};
    std::memcpy(wrong, candidate, sizeof(wrong));
    wrong[11] = wrong[11] == 'A' ? 'B' : 'A';
    CHECK(
        wall.evaluate(input, wrong, receipt) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE
    );

    return 0;
}
