#include "hhs_pass219_lane5_nine_loop_generalization_cell_wall_1_73.hpp"

#include <cstdio>
#include <cstdlib>
#include <cstring>

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static hhs::lane5::NineLoopForeignMetadata foreign_metadata() {
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

static hhs::lane5::NineLoopSourceAttestationInput source_input() {
    using namespace hhs::lane5;
    NineLoopSourceAttestationInput input{};
    input.parent_metadata = foreign_metadata();
    if (NineLoopForeignEquivalenceCellWall::derive_candidate_hash216(
            input.parent_metadata, input.parent_candidate_hash216
        ) != HHS_EXACT_STATUS_OK) std::abort();
    std::strcpy(input.manifest_sha256,
        "f96534526482f03e638ee030b1a88968348901f70967bb89618c76420a21ffe5");
    std::strcpy(input.sample_sha256,
        "a78557e58efb3e12cccb647974131a3f694322bebb97607a5648db0484099b18");
    std::strcpy(input.summary_sha256,
        "fbda1f90205bcf4f02b154aba25346aa83768e6cbbccbeeceaef9187eb691088");
    input.nonzero_rows = 20400U;
    input.zero_rows = 230U;
    input.total_rows = 20630U;
    input.unique_words = 20630U;
    input.manifest_member_verified = 1U;
    input.all_nonzero_rationals_exact = 1U;
    input.all_zero_rows_exact = 1U;
    return input;
}

static hhs::lane5::NineLoopLargeArtifactInput large_input() {
    using namespace hhs::lane5;
    NineLoopLargeArtifactInput input{};
    input.parent_input = source_input();
    if (NineLoopSourceAttestationCellWall::derive_candidate_hash216(
            input.parent_input, input.parent_source_hash216
        ) != HHS_EXACT_STATUS_OK) std::abort();
    std::strcpy(input.p1_source_sha256,
        "75a52ebb4526bdb788ae8101e4908d52579637b6aaca1a308e4d783b4a8afe86");
    std::strcpy(input.p2_source_sha256,
        "13c231664403d35e8ad68747302c7bc26bcc9b1b567d0da0d65444c980c8eb97");
    std::strcpy(input.comparison_source_sha256,
        "d01e62885b74d13650b44baf8da3e42d15bab35c99f6ee778e66df4059ecf37d");
    std::strcpy(input.septuple_source_sha256,
        "082abcea6a66fb434b24938236f443f2703e7e76ded8911f46ffffa292a2c5e1");
    std::strcpy(input.e0_support_sha256,
        "64cd7ae9027ef41969948efc35b1273ba03ba3f759c076700d8a09940ebbf54d");
    std::strcpy(input.comparison_normalized_sha256,
        "884b05ed4118ed372329c8b002b895dfa98bd92fe72cdd0f88b47cef94448d11");
    std::strcpy(input.septuple_structure_sha256,
        "606c5db22ac881a92835cf12e7077d0093c8b599b5205d3e0752be91e82c3967");
    std::strcpy(input.relation_sha256,
        "4acc66c250129d5a42f976d673027313707633012b2de6f85d6491a4083ed73a");
    input.matrix_rows = 424U;
    input.matrix_columns = 5431U;
    input.matrix_nonzero = 1018297U;
    input.comparison_rows = 107053U;
    input.source_manifest_verified = 1U;
    input.logical_equivalence_verified = 1U;
    input.archive_integrity_verified = 1U;
    input.comparison_integrity_verified = 1U;
    return input;
}

static hhs::lane5::NineLoopFeedbackInput exact_input() {
    using namespace hhs::lane5;
    NineLoopFeedbackInput input{};
    input.parent_input = large_input();
    if (NineLoopLargeArtifactCellWall::derive_candidate_hash216(
            input.parent_input, input.parent_large_artifact_hash216
        ) != HHS_EXACT_STATUS_OK) std::abort();
    std::strcpy(input.parent_relation_sha256,
        "4acc66c250129d5a42f976d673027313707633012b2de6f85d6491a4083ed73a");
    std::strcpy(input.parent_support_sha256,
        "64cd7ae9027ef41969948efc35b1273ba03ba3f759c076700d8a09940ebbf54d");
    std::strcpy(input.wolfram_feedback_material_sha256,
        "ba58c70820f0f3e5bd3a352b89441face87d07ea7ce776b1b8481c21393c69e1");
    std::strcpy(input.feedback_payload_sha256,
        "78f2cc37e9304017cf0b6a233f2cb5ab080757fec57e6eb5897295bf0d2bed70");
    std::strcpy(input.genesis_identity,
        "F(x,y,a,b)=(x+y)^2+(xy-a^2)^2+(a^2-b)^2+(a^4-2)^2");
    input.root_seed_numerator = UINT64_C(179971179971);
    input.root_seed_denominator = 1000000U;
    input.certified_rational_coordinates = 1014476U;
    input.total_nonzero_coordinates = 1018297U;
    input.two_prime_only_coordinates = 3821U;
    input.comparison_rows = 107053U;
    input.comparison_two_prime_only_rows = 3401U;
    input.literal_container_identity_assumption = -1;
    input.logical_representation_equivalence = 1;
    input.support_geometry = 1;
    input.foreign_rational_reconstruction_complete = -1;
    input.wolfram_receipt_verified = 1U;
    input.deviation_vector_verified = 1U;
    return input;
}


static hhs::lane5::NineLoopTrainingSpecimenInput training_input() {
    using namespace hhs::lane5;
    NineLoopTrainingSpecimenInput input{};
    input.parent_input = exact_input();
    if (NineLoopFeedbackCellWall::derive_candidate_hash216(
            input.parent_input, input.parent_feedback_hash216
        ) != HHS_EXACT_STATUS_OK) std::abort();
    std::strcpy(input.training_specimen_sha256,
        "96a9f686a1ab35c8600ba7a38a367af38339b51a70182c3d7981ee529ff50191");
    std::strcpy(input.parent_feedback_payload_sha256,
        "78f2cc37e9304017cf0b6a233f2cb5ab080757fec57e6eb5897295bf0d2bed70");
    std::strcpy(input.parent_relation_sha256,
        "4acc66c250129d5a42f976d673027313707633012b2de6f85d6491a4083ed73a");
    std::strcpy(input.parent_support_sha256,
        "64cd7ae9027ef41969948efc35b1273ba03ba3f759c076700d8a09940ebbf54d");
    input.training_feedback_label_count = 13U;
    input.learning_objective_count = 5U;
    input.deviation_feature_count = 16U;
    input.source_lineage_verified = 1U;
    input.negative_example_preserved = 1U;
    input.exact_ratio_features_verified = 1U;
    input.trinary_features_verified = 1U;
    input.dataset_preparation_only = 1U;
    input.model_weight_update_requested = 0U;
    input.learning_commit_requested = 0U;
    return input;
}


static hhs::lane5::NineLoopRelationDatasetInput dataset_input() {
    using namespace hhs::lane5;
    NineLoopRelationDatasetInput input{};
    input.parent_input = training_input();
    if (NineLoopTrainingSpecimenCellWall::derive_candidate_hash216(
            input.parent_input, input.parent_training_hash216
        ) != HHS_EXACT_STATUS_OK) std::abort();
    std::strcpy(input.dataset_sha256,
        "dd623f4fc778364274e7ba05c914fb441b724ca3ce41a4eb4df4cdc64935d587");
    std::strcpy(input.ordered_record_chain_sha256,
        "4a951f76afcd3f759e74263bc9cd0019b50f034bc07e93341b73200e0c85bd6a");
    std::strcpy(input.parent_specimen_sha256,
        "96a9f686a1ab35c8600ba7a38a367af38339b51a70182c3d7981ee529ff50191");
    input.record_count = 12U;
    input.additive_record_count = 6U;
    input.neutral_record_count = 4U;
    input.negative_record_count = 2U;
    input.source_bound_features_verified = 1U;
    input.negative_examples_verified = 1U;
    input.ordered_chain_verified = 1U;
    input.dataset_preparation_only = 1U;
    input.model_weight_update_requested = 0U;
    input.learning_commit_requested = 0U;
    return input;
}


static hhs::lane5::NineLoopGeneralizationInput generalization_input() {
    using namespace hhs::lane5;
    NineLoopGeneralizationInput input{};
    input.parent_input = dataset_input();
    if (NineLoopRelationDatasetCellWall::derive_candidate_hash216(
            input.parent_input, input.parent_relation_dataset_hash216
        ) != HHS_EXACT_STATUS_OK) std::abort();
    std::strcpy(input.model_root_hash72,
        "0000000000000000000000000000002rd>Jdh(*jXM9IMuM^931?)TxIUlEV>A5MH81cDfqL");
    std::strcpy(input.validation_receipt_root_hash72,
        "0000000000000000000000000000004uxkwBpAEdc+=PCnAuM+5cGH26usFYmSWD3kSLSkPM");
    std::strcpy(input.replay_bundle_sha256,
        "238556f95e17e77d01a9e37e4be4cbbd56181982f3599dc941cfe77be32aaf69");
    input.training_example_count = 12U;
    input.holdout_example_count = 12U;
    input.rule_count = 12U;
    input.accuracy_numerator = 12U;
    input.accuracy_denominator = 12U;
    input.semantic_drift_count = 0U;
    input.entropy_growth_bits = 0U;
    input.replay_count = 12U;
    input.training_holdout_disjoint = 1U;
    input.all_replays_validated = 1U;
    input.validated_knowledge_model_only = 1U;
    input.model_weight_update_requested = 0U;
    input.learning_commit_requested = 0U;
    input.execution_authority_requested = 0U;
    return input;
}

int main() {
    using namespace hhs::lane5;
    auto input = generalization_input();
    char candidate[HHS_HASH216_LEN + 1]{};
    char replay[HHS_HASH216_LEN + 1]{};

    CHECK(NineLoopGeneralizationCellWall::derive_candidate_hash216(input, candidate) == HHS_EXACT_STATUS_OK);
    CHECK(NineLoopGeneralizationCellWall::derive_candidate_hash216(input, replay) == HHS_EXACT_STATUS_OK);
    CHECK(std::strcmp(candidate, replay) == 0);

    NineLoopGeneralizationCellWall wall;
    NineLoopGeneralizationReceipt receipt{};
    CHECK(wall.evaluate(input, candidate, receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.accepted == 1U);
    CHECK(receipt.parent_1_72_verified == 1U);
    CHECK(receipt.frozen_receipts_verified == 1U);
    CHECK(receipt.exact_holdout_verified == 1U);
    CHECK(receipt.semantic_drift_zero_verified == 1U);
    CHECK(receipt.deterministic_replay_verified == 1U);
    CHECK(receipt.validated_knowledge_model_only == 1U);
    CHECK(receipt.hash216_replay_verified == 1U);
    CHECK(receipt.candidate_only == 1U);
    CHECK(receipt.execution_authority == 0U);
    CHECK(receipt.model_weight_update_authority == 0U);
    CHECK(receipt.learning_commit_authority == 0U);
    CHECK(receipt.canonical_vm81_mutation_authority == 0U);
    CHECK(receipt.canonical_hash72_authority == 0U);
    CHECK(receipt.canonical_hash216_authority == 0U);
    CHECK(receipt.canonical_persistence_authority == 0U);
    CHECK(receipt.floating_point_canonical_authority == 0U);

    auto model = generalization_input(); model.model_root_hash72[31] ^= 1;
    CHECK(wall.evaluate(model, candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    auto validation = generalization_input(); validation.validation_receipt_root_hash72[33] ^= 1;
    CHECK(wall.evaluate(validation, candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    auto replay_bundle = generalization_input(); replay_bundle.replay_bundle_sha256[0] ^= 1;
    CHECK(wall.evaluate(replay_bundle, candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    auto holdout = generalization_input(); holdout.holdout_example_count = 11U;
    CHECK(wall.evaluate(holdout, candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    auto drift = generalization_input(); drift.semantic_drift_count = 1U;
    CHECK(wall.evaluate(drift, candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    auto replay_missing = generalization_input(); replay_missing.all_replays_validated = 0U;
    CHECK(wall.evaluate(replay_missing, candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    auto weight = generalization_input(); weight.model_weight_update_requested = 1U;
    CHECK(wall.evaluate(weight, candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    auto learning = generalization_input(); learning.learning_commit_requested = 1U;
    CHECK(wall.evaluate(learning, candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    auto execution = generalization_input(); execution.execution_authority_requested = 1U;
    CHECK(wall.evaluate(execution, candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    auto parent_bad = generalization_input();
    parent_bad.parent_input.parent_input.parent_input.parent_input.parent_input.parent_metadata.delta_alias_authorized = 1U;
    CHECK(wall.evaluate(parent_bad, candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    char wrong[HHS_HASH216_LEN + 1]{};
    std::memcpy(wrong, candidate, sizeof(wrong));
    wrong[53] = wrong[53] == 'A' ? 'B' : 'A';
    CHECK(wall.evaluate(input, wrong, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    return 0;
}
