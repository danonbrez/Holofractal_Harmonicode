#include "hhs_pass219_lane5_vm5184_hash216_training_1_74.hpp"

#include <cstdint>
#include <cstdio>
#include <cstring>

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

namespace {

HHSExactUQCELInputV1 input_fixture() {
    static std::uint8_t one = 1U;
    HHSExactUQCELInputV1 input{};
    input.struct_size = static_cast<std::uint32_t>(sizeof(input));
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.delta.struct_size = static_cast<std::uint32_t>(sizeof(input.delta));
    input.delta.byte_length = 1U;
    input.delta.bytes_be = &one;
    return input;
}

HHSExactVM81Frame frame_fixture() {
    HHSExactVM81Frame frame{};
    for (std::size_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        frame.words[i] =
            UINT64_C(0x9E3779B97F4A7C15) ^
            (static_cast<std::uint64_t>(i) * UINT64_C(0x100000001B3));
    }
    return frame;
}

hhs::lane5::TrainingSpecimen specimen_for(
    const hhs::lane5::TrainingMethodDescriptor& descriptor,
    const HHSExactPass219Hash216TransitionViewV1& transition,
    std::uint64_t salt
) {
    using namespace hhs::lane5;
    TrainingSpecimen specimen{};
    specimen.struct_size = static_cast<std::uint32_t>(sizeof(specimen));
    specimen.version = kVM5184Hash216TrainingVersion;
    specimen.mode = descriptor.mode;
    specimen.temporal = descriptor.temporal;
    specimen.target = descriptor.primary_target;
    std::memcpy(
        specimen.source_identity216,
        transition.transition_identity216,
        HHS_HASH216_LEN + 1U
    );
    std::memcpy(
        specimen.oracle_identity216,
        transition.transition_identity216,
        HHS_HASH216_LEN + 1U
    );
    specimen.adapter_signature64 = UINT64_C(0x1000) + salt;
    specimen.executor_signature64 = UINT64_C(0x2000) + salt;
    specimen.validator_signature64 = UINT64_C(0x3000) + salt;
    specimen.negative_control_signature64 = UINT64_C(0x4000) + salt;
    specimen.replay_signature64 = UINT64_C(0x5000) + salt;
    if (descriptor.natural_language_native != 0U) {
        std::memcpy(
            specimen.ethical_text_supervisor_identity216,
            transition.transition_identity216,
            HHS_HASH216_LEN + 1U
        );
        specimen.ethical_text_supervisor_signature64 =
            UINT64_C(0x6000) + salt;
        specimen.natural_language_training = 1U;
        specimen.ethical_text_supervision_verified = 1U;
    }
    specimen.oracle_verified = 1U;
    specimen.negative_controls_verified = 1U;
    specimen.replay_verified = 1U;
    specimen.ingress_egress_preserved = 1U;
    specimen.candidate_only_acknowledged = 1U;
    return specimen;
}


bool receipts_equal(
    const hhs::lane5::TrainingReceipt& left,
    const hhs::lane5::TrainingReceipt& right
) {
    return left.version == right.version &&
           left.namespace_id == right.namespace_id &&
           left.mode == right.mode &&
           left.temporal == right.temporal &&
           left.target == right.target &&
           left.method_index == right.method_index &&
           left.accepted == right.accepted &&
           left.registry_verified == right.registry_verified &&
           left.specimen_identity_verified == right.specimen_identity_verified &&
           left.oracle_verified == right.oracle_verified &&
           left.negative_controls_verified == right.negative_controls_verified &&
           left.replay_verified == right.replay_verified &&
           left.ingress_egress_preserved == right.ingress_egress_preserved &&
           left.natural_language_training == right.natural_language_training &&
           left.ethical_text_supervision_required ==
               right.ethical_text_supervision_required &&
           left.ethical_text_supervision_verified ==
               right.ethical_text_supervision_verified &&
           left.vm5184_routed == right.vm5184_routed &&
           left.hash216_candidate_derived == right.hash216_candidate_derived &&
           left.candidate_only == right.candidate_only &&
           left.canonical_vm81_mutation_authority ==
               right.canonical_vm81_mutation_authority &&
           left.canonical_hash72_authority == right.canonical_hash72_authority &&
           left.canonical_hash216_authority == right.canonical_hash216_authority &&
           left.canonical_persistence_authority ==
               right.canonical_persistence_authority &&
           left.floating_point_canonical_authority ==
               right.floating_point_canonical_authority &&
           std::strcmp(left.source_identity216, right.source_identity216) == 0 &&
           std::strcmp(left.oracle_identity216, right.oracle_identity216) == 0 &&
           std::strcmp(
               left.ethical_text_supervisor_identity216,
               right.ethical_text_supervisor_identity216) == 0 &&
           std::strcmp(
               left.training_candidate_hash216,
               right.training_candidate_hash216) == 0 &&
           left.rna_prepared.graph_signature64 ==
               right.rna_prepared.graph_signature64 &&
           left.rna_prepared.tensor_signature64 ==
               right.rna_prepared.tensor_signature64 &&
           left.rna_prepared.word_visits == right.rna_prepared.word_visits &&
           left.rna_prepared.graph_edge_visits ==
               right.rna_prepared.graph_edge_visits &&
           left.rna_prepared.hash216_positions_complete ==
               right.rna_prepared.hash216_positions_complete &&
           left.rna_decision.selected_lane == right.rna_decision.selected_lane &&
           left.rna_decision.decision_signature64 ==
               right.rna_decision.decision_signature64 &&
           left.rna_decision.candidate_only == right.rna_decision.candidate_only;
}

}  // namespace

int main() {
    using namespace hhs::lane5;

    CHECK(VM5184Hash216TrainingAPI::method_count() ==
          kVM5184Hash216TrainingMethodCount);
    CHECK(kVM5184Hash216TrainingMethodCount > 10U);

    for (std::size_t i = 0U; i < VM5184Hash216TrainingAPI::method_count(); ++i) {
        const TrainingMethodDescriptor *a =
            VM5184Hash216TrainingAPI::method_by_index(i);
        CHECK(a != nullptr);
        CHECK(a->method_id != nullptr);
        CHECK(a->method_id[0] != '\0');
        CHECK(a->routes_through_vm5184 == 1U);
        CHECK(a->emits_candidate_hash216 == 1U);
        CHECK(a->candidate_only == 1U);
        CHECK(a->requires_negative_controls == 1U);
        if (a->mode == TrainingMode::LinguisticOperator)
            CHECK(a->natural_language_native == 1U);
        if (a->mode == TrainingMode::EthicalText) {
            CHECK(a->natural_language_native == 1U);
            CHECK(a->ethical_text_supervisor == 1U);
        }
        CHECK(a->requires_replay == 1U);
        CHECK(a->preserves_ingress_egress == 1U);
        CHECK(VM5184Hash216TrainingAPI::method(a->mode) == a);
        CHECK(VM5184Hash216TrainingAPI::target_allowed(
            *a, a->primary_target));
        for (std::size_t j = i + 1U;
             j < VM5184Hash216TrainingAPI::method_count(); ++j) {
            const TrainingMethodDescriptor *b =
                VM5184Hash216TrainingAPI::method_by_index(j);
            CHECK(b != nullptr);
            CHECK(a->mode != b->mode);
            CHECK(std::strcmp(a->method_id, b->method_id) != 0);
        }
    }
    CHECK(VM5184Hash216TrainingAPI::method_by_index(
              kVM5184Hash216TrainingMethodCount) == nullptr);
    CHECK(VM5184Hash216TrainingAPI::method(
              static_cast<TrainingMode>(999U)) == nullptr);

    HHSExactPass219Hash216TransitionViewV1 transition{};
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&transition) ==
          HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&transition) ==
          HHS_EXACT_STATUS_OK);

    const HHSExactUQCELInputV1 input = input_fixture();
    const HHSExactVM81Frame frame = frame_fixture();
    VM5184Hash216TrainingAPI api;
    char candidates[kVM5184Hash216TrainingMethodCount][HHS_HASH216_LEN + 1]{};

    for (std::size_t i = 0U; i < VM5184Hash216TrainingAPI::method_count(); ++i) {
        const TrainingMethodDescriptor *descriptor =
            VM5184Hash216TrainingAPI::method_by_index(i);
        CHECK(descriptor != nullptr);
        const TrainingSpecimen specimen =
            specimen_for(*descriptor, transition, static_cast<std::uint64_t>(i + 1U));

        TrainingReceipt first{};
        TrainingReceipt replay{};
        CHECK(api.evaluate(
                  specimen,
                  input,
                  frame,
                  transition,
                  HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
                  0,
                  first) == HHS_EXACT_STATUS_OK);
        CHECK(api.evaluate(
                  specimen,
                  input,
                  frame,
                  transition,
                  HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
                  0,
                  replay) == HHS_EXACT_STATUS_OK);

        CHECK(first.accepted == 1U);
        CHECK(first.registry_verified == 1U);
        CHECK(first.specimen_identity_verified == 1U);
        CHECK(first.oracle_verified == 1U);
        CHECK(first.negative_controls_verified == 1U);
        CHECK(first.replay_verified == 1U);
        CHECK(first.ingress_egress_preserved == 1U);
        CHECK(first.natural_language_training ==
              descriptor->natural_language_native);
        CHECK(first.ethical_text_supervision_required ==
              descriptor->natural_language_native);
        CHECK(first.ethical_text_supervision_verified ==
              descriptor->natural_language_native);
        CHECK(first.vm5184_routed == 1U);
        CHECK(first.hash216_candidate_derived == 1U);
        CHECK(first.candidate_only == 1U);
        CHECK(first.canonical_vm81_mutation_authority == 0U);
        CHECK(first.canonical_hash72_authority == 0U);
        CHECK(first.canonical_hash216_authority == 0U);
        CHECK(first.canonical_persistence_authority == 0U);
        CHECK(first.floating_point_canonical_authority == 0U);
        CHECK(first.rna_prepared.word_visits == HHS_EXACT_VM81_CELLS);
        CHECK(first.rna_prepared.hash216_positions_complete == 1U);
        CHECK(first.rna_prepared.candidate_only == 1U);
        CHECK(first.rna_decision.candidate_only == 1U);
        CHECK(first.training_candidate_hash216[HHS_HASH216_LEN] == '\0');
        CHECK(first.training_candidate_hash216[0] != '\0');
        CHECK(receipts_equal(first, replay));

        std::memcpy(
            candidates[i],
            first.training_candidate_hash216,
            HHS_HASH216_LEN + 1U
        );
        for (std::size_t j = 0U; j < i; ++j) {
            CHECK(std::strcmp(candidates[i], candidates[j]) != 0);
        }
    }

    const TrainingMethodDescriptor *bounded =
        VM5184Hash216TrainingAPI::method(
            TrainingMode::BoundedTokenGeneralization);
    CHECK(bounded != nullptr);
    CHECK(std::strcmp(
              bounded->method_id,
              "BOUNDED_TOKEN_GENERALIZATION") == 0);
    CHECK(bounded->temporal == TrainingTemporal::Batch);
    CHECK(bounded->primary_target == TrainingTarget::Relation);
    CHECK(bounded->requires_oracle == 1U);

    const TrainingMethodDescriptor *realtime =
        VM5184Hash216TrainingAPI::method(TrainingMode::RealtimeHash216);
    CHECK(realtime != nullptr);
    TrainingSpecimen specimen = specimen_for(*realtime, transition, UINT64_C(99));

    std::uint8_t raw[HHS_EXACT_VM81_FRAME_BYTES]{};
    std::size_t written = 0U;
    CHECK(hhs_exact_vm81_frame_export_le(
              &frame, raw, sizeof(raw), &written) == HHS_EXACT_STATUS_OK);
    CHECK(written == HHS_EXACT_VM81_FRAME_BYTES);

    TrainingReceipt frame_receipt{};
    TrainingReceipt raw_receipt{};
    CHECK(api.evaluate(
              specimen,
              input,
              frame,
              transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
              0,
              frame_receipt) == HHS_EXACT_STATUS_OK);
    CHECK(api.evaluate_raw(
              specimen,
              input,
              raw,
              sizeof(raw),
              transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
              0,
              raw_receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipts_equal(frame_receipt, raw_receipt));

    TrainingReceipt negative{};
    TrainingSpecimen bad = specimen;
    bad.temporal = TrainingTemporal::Manual;
    CHECK(api.evaluate(
              bad, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, negative) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    bad = specimen;
    bad.target = TrainingTarget::RepositoryTransition;
    CHECK(api.evaluate(
              bad, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, negative) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    bad = specimen;
    bad.negative_controls_verified = 0U;
    CHECK(api.evaluate(
              bad, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, negative) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    bad = specimen;
    bad.replay_verified = 0U;
    CHECK(api.evaluate(
              bad, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, negative) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    bad = specimen;
    bad.ingress_egress_preserved = 0U;
    CHECK(api.evaluate(
              bad, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, negative) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    bad = specimen;
    bad.source_identity216[0] = '\0';
    CHECK(api.evaluate(
              bad, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, negative) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    bad = specimen;
    bad.mode = static_cast<TrainingMode>(999U);
    CHECK(api.evaluate(
              bad, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, negative) ==
          HHS_EXACT_STATUS_RANGE_ERROR);

    CHECK(api.evaluate_raw(
              specimen,
              input,
              raw,
              sizeof(raw) - 1U,
              transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
              0,
              negative) == HHS_EXACT_STATUS_RANGE_ERROR);

    const TrainingMethodDescriptor *wolfram =
        VM5184Hash216TrainingAPI::method(TrainingMode::WolframFormalization);
    CHECK(wolfram != nullptr && wolfram->requires_oracle == 1U);
    bad = specimen_for(*wolfram, transition, UINT64_C(100));
    bad.oracle_verified = 0U;
    CHECK(api.evaluate(
              bad, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, negative) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);


    const TrainingMethodDescriptor *linguistic =
        VM5184Hash216TrainingAPI::method(TrainingMode::LinguisticOperator);
    CHECK(linguistic != nullptr && linguistic->natural_language_native == 1U);
    TrainingSpecimen language =
        specimen_for(*linguistic, transition, UINT64_C(101));
    TrainingReceipt language_receipt{};
    CHECK(api.evaluate(
              language, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, language_receipt) ==
          HHS_EXACT_STATUS_OK);
    CHECK(language_receipt.natural_language_training == 1U);
    CHECK(language_receipt.ethical_text_supervision_required == 1U);
    CHECK(language_receipt.ethical_text_supervision_verified == 1U);
    CHECK(std::memcmp(
              language_receipt.ethical_text_supervisor_identity216,
              transition.transition_identity216,
              HHS_HASH216_LEN + 1U) == 0);

    bad = language;
    bad.ethical_text_supervision_verified = 0U;
    CHECK(api.evaluate(
              bad, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, negative) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    bad = language;
    bad.ethical_text_supervisor_signature64 = 0U;
    CHECK(api.evaluate(
              bad, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, negative) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    bad = language;
    bad.ethical_text_supervisor_identity216[0] = '\0';
    CHECK(api.evaluate(
              bad, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, negative) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    bad = language;
    bad.natural_language_training = 0U;
    CHECK(api.evaluate(
              bad, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, negative) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    const TrainingMethodDescriptor *multimodal =
        VM5184Hash216TrainingAPI::method(TrainingMode::MultimodalIngress);
    CHECK(multimodal != nullptr && multimodal->natural_language_native == 0U);
    TrainingSpecimen mixed =
        specimen_for(*multimodal, transition, UINT64_C(102));
    mixed.natural_language_training = 1U;
    mixed.ethical_text_supervision_verified = 1U;
    mixed.ethical_text_supervisor_signature64 = UINT64_C(0x6600);
    std::memcpy(
        mixed.ethical_text_supervisor_identity216,
        transition.transition_identity216,
        HHS_HASH216_LEN + 1U
    );
    TrainingReceipt mixed_receipt{};
    CHECK(api.evaluate(
              mixed, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, mixed_receipt) ==
          HHS_EXACT_STATUS_OK);
    CHECK(mixed_receipt.ethical_text_supervision_required == 1U);
    CHECK(mixed_receipt.ethical_text_supervision_verified == 1U);

    bad = mixed;
    bad.ethical_text_supervision_verified = 0U;
    CHECK(api.evaluate(
              bad, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, negative) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    const TrainingMethodDescriptor *ethical =
        VM5184Hash216TrainingAPI::method(TrainingMode::EthicalText);
    CHECK(ethical != nullptr);
    CHECK(ethical->ethical_text_supervisor == 1U);
    TrainingSpecimen ethical_specimen =
        specimen_for(*ethical, transition, UINT64_C(103));
    TrainingReceipt ethical_receipt{};
    CHECK(api.evaluate(
              ethical_specimen, input, frame, transition,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, ethical_receipt) ==
          HHS_EXACT_STATUS_OK);
    CHECK(ethical_receipt.ethical_text_supervision_required == 1U);
    CHECK(ethical_receipt.ethical_text_supervision_verified == 1U);

    std::printf(
        "PASS219_LANE5_UNIFIED_TRAINING_PASS methods=%zu vm5184=%u hash216=%u\n",
        VM5184Hash216TrainingAPI::method_count(),
        HHS_EXACT_VM81_FRAME_BITS,
        HHS_HASH216_LEN
    );
    return 0;
}
