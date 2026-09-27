#include "hhs_pass219_lane5_nine_loop_cell_wall_1_67.hpp"

#include <cstdio>
#include <cstring>

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static hhs::lane5::NineLoopForeignMetadata exact_metadata() {
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

int main() {
    using hhs::lane5::NineLoopEquivalenceReceipt;
    using hhs::lane5::NineLoopForeignEquivalenceCellWall;

    auto metadata = exact_metadata();
    char first[HHS_HASH216_LEN + 1]{};
    char replay[HHS_HASH216_LEN + 1]{};

    CHECK(
        NineLoopForeignEquivalenceCellWall::derive_candidate_hash216(metadata, first) ==
        HHS_EXACT_STATUS_OK
    );
    CHECK(std::strlen(first) == HHS_HASH216_LEN);
    CHECK(
        NineLoopForeignEquivalenceCellWall::derive_candidate_hash216(metadata, replay) ==
        HHS_EXACT_STATUS_OK
    );
    CHECK(std::strcmp(first, replay) == 0);

    NineLoopForeignEquivalenceCellWall membrane;
    NineLoopEquivalenceReceipt receipt{};
    CHECK(membrane.evaluate(metadata, first, receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.accepted == 1U);
    CHECK(receipt.parent_1_66_verified == 1U);
    CHECK(receipt.monolithic_source_identity_verified == 1U);
    CHECK(receipt.foreign_delta_quarantine_verified == 1U);
    CHECK(receipt.exact_sample_oracle_verified == 1U);
    CHECK(receipt.structure_counts_verified == 1U);
    CHECK(receipt.dual_route_metadata_verified == 1U);
    CHECK(receipt.hash216_composition_validated == 1U);
    CHECK(receipt.candidate_only == 1U);
    CHECK(receipt.canonical_vm81_mutation_authority == 0U);
    CHECK(receipt.canonical_hash72_authority == 0U);
    CHECK(receipt.canonical_hash216_authority == 0U);
    CHECK(receipt.canonical_persistence_authority == 0U);
    CHECK(receipt.floating_point_canonical_authority == 0U);
    CHECK(std::strcmp(first, receipt.candidate_hash216) == 0);

    char wrong[HHS_HASH216_LEN + 1]{};
    std::memcpy(wrong, first, sizeof(wrong));
    wrong[37] = wrong[37] == 'A' ? 'B' : 'A';
    CHECK(
        membrane.evaluate(metadata, wrong, receipt) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE
    );

    auto delta_alias = exact_metadata();
    delta_alias.delta_alias_authorized = 1U;
    CHECK(
        membrane.evaluate(delta_alias, first, receipt) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE
    );

    auto residue_tamper = exact_metadata();
    residue_tamper.sample_residues[0] += 1U;
    CHECK(
        membrane.evaluate(residue_tamper, first, receipt) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE
    );

    auto shape_tamper = exact_metadata();
    shape_tamper.quintuple_coproduct_count = 423U;
    CHECK(
        membrane.evaluate(shape_tamper, first, receipt) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE
    );

    return 0;
}
