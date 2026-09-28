#include "hhs_pass219_lane5_vm5184_hash216_training_1_72.hpp"

#include <cinttypes>
#include <cstdio>
#include <cstring>

namespace hhs::lane5 {
namespace {

constexpr std::uint32_t target_bit(TrainingTarget target) noexcept {
    const auto value = static_cast<std::uint32_t>(target);
    return value == 0U ? 0U : (UINT32_C(1) << (value - 1U));
}

constexpr TrainingMethodDescriptor method_descriptor(
    TrainingMode mode,
    TrainingTemporal temporal,
    TrainingTarget primary_target,
    std::uint32_t target_mask,
    const char *method_id,
    std::uint8_t requires_oracle,
    std::uint8_t natural_language_native,
    std::uint8_t ethical_text_supervisor
) noexcept {
    return TrainingMethodDescriptor{
        mode,
        temporal,
        primary_target,
        target_mask,
        method_id,
        requires_oracle,
        1U,
        1U,
        1U,
        1U,
        1U,
        1U,
        natural_language_native,
        ethical_text_supervisor,
        0U
    };
}

constexpr TrainingMethodDescriptor kMethods[] = {
    method_descriptor(
        TrainingMode::RealtimeHash216,
        TrainingTemporal::Realtime,
        TrainingTarget::Relation,
        target_bit(TrainingTarget::Relation) |
            target_bit(TrainingTarget::Constructor) |
            target_bit(TrainingTarget::Invariant) |
            target_bit(TrainingTarget::Weight),
        "REALTIME_HASH216",
        0U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::WolframFormalization,
        TrainingTemporal::Manual,
        TrainingTarget::Proof,
        target_bit(TrainingTarget::Proof) |
            target_bit(TrainingTarget::Relation) |
            target_bit(TrainingTarget::Constructor),
        "WOLFRAM_FORMALIZATION",
        1U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::ExternalLibraryReconstruction,
        TrainingTemporal::Manual,
        TrainingTarget::Constructor,
        target_bit(TrainingTarget::Constructor) |
            target_bit(TrainingTarget::Behavior) |
            target_bit(TrainingTarget::Codec),
        "EXTERNAL_LIBRARY_RECONSTRUCTION",
        1U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::PalindromicRoundTrip,
        TrainingTemporal::RoundTrip,
        TrainingTarget::Codec,
        target_bit(TrainingTarget::Codec) |
            target_bit(TrainingTarget::Behavior),
        "PALINDROMIC_ROUND_TRIP",
        1U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::PullRequestHydration,
        TrainingTemporal::RepositoryDelta,
        TrainingTarget::RepositoryTransition,
        target_bit(TrainingTarget::RepositoryTransition) |
            target_bit(TrainingTarget::Relation) |
            target_bit(TrainingTarget::Constructor),
        "PULL_REQUEST_HYDRATION",
        1U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::MultimodalIngress,
        TrainingTemporal::Realtime,
        TrainingTarget::Invariant,
        target_bit(TrainingTarget::Invariant) |
            target_bit(TrainingTarget::Weight) |
            target_bit(TrainingTarget::Relation),
        "MULTIMODAL_INGRESS",
        0U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::LinguisticOperator,
        TrainingTemporal::Batch,
        TrainingTarget::Relation,
        target_bit(TrainingTarget::Relation) |
            target_bit(TrainingTarget::Behavior) |
            target_bit(TrainingTarget::Invariant),
        "LINGUISTIC_OPERATOR",
        0U,
        1U,
        0U),
    method_descriptor(
        TrainingMode::EthicalText,
        TrainingTemporal::Batch,
        TrainingTarget::Invariant,
        target_bit(TrainingTarget::Invariant) |
            target_bit(TrainingTarget::Behavior) |
            target_bit(TrainingTarget::Relation),
        "ETHICAL_TEXT",
        0U,
        1U,
        1U),
    method_descriptor(
        TrainingMode::RNACellWallAlignment,
        TrainingTemporal::Replay,
        TrainingTarget::Weight,
        target_bit(TrainingTarget::Weight) |
            target_bit(TrainingTarget::Invariant) |
            target_bit(TrainingTarget::Relation),
        "RNA_CELL_WALL_ALIGNMENT",
        1U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::Curriculum,
        TrainingTemporal::Batch,
        TrainingTarget::Relation,
        target_bit(TrainingTarget::Relation) |
            target_bit(TrainingTarget::Invariant) |
            target_bit(TrainingTarget::Constructor),
        "CURRICULUM",
        0U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::CallableCorpus,
        TrainingTemporal::Batch,
        TrainingTarget::Behavior,
        target_bit(TrainingTarget::Behavior) |
            target_bit(TrainingTarget::Constructor) |
            target_bit(TrainingTarget::Relation),
        "CALLABLE_CORPUS",
        1U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::CanonicalCorpus,
        TrainingTemporal::Batch,
        TrainingTarget::Proof,
        target_bit(TrainingTarget::Proof) |
            target_bit(TrainingTarget::Relation) |
            target_bit(TrainingTarget::Constructor),
        "CANONICAL_CORPUS",
        1U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::WorkloadCalibration,
        TrainingTemporal::Batch,
        TrainingTarget::Schedule,
        target_bit(TrainingTarget::Schedule) |
            target_bit(TrainingTarget::Weight) |
            target_bit(TrainingTarget::Relation),
        "WORKLOAD_CALIBRATION",
        1U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::AntiForgettingReplay,
        TrainingTemporal::Replay,
        TrainingTarget::Behavior,
        target_bit(TrainingTarget::Behavior) |
            target_bit(TrainingTarget::Invariant) |
            target_bit(TrainingTarget::Weight),
        "ANTI_FORGETTING_REPLAY",
        1U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::ABHydrationCalibration,
        TrainingTemporal::Batch,
        TrainingTarget::Weight,
        target_bit(TrainingTarget::Weight) |
            target_bit(TrainingTarget::Relation) |
            target_bit(TrainingTarget::Schedule),
        "AB_HYDRATION_CALIBRATION",
        1U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::ProjectionCorpus,
        TrainingTemporal::Batch,
        TrainingTarget::Relation,
        target_bit(TrainingTarget::Relation) |
            target_bit(TrainingTarget::Codec) |
            target_bit(TrainingTarget::Invariant),
        "PROJECTION_CORPUS",
        1U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::InverseRenderHydration,
        TrainingTemporal::Batch,
        TrainingTarget::Constructor,
        target_bit(TrainingTarget::Constructor) |
            target_bit(TrainingTarget::Codec) |
            target_bit(TrainingTarget::Behavior),
        "INVERSE_RENDER_HYDRATION",
        1U,
        0U,
        0U),
    method_descriptor(
        TrainingMode::RepositoryHydration,
        TrainingTemporal::RepositoryDelta,
        TrainingTarget::RepositoryTransition,
        target_bit(TrainingTarget::RepositoryTransition) |
            target_bit(TrainingTarget::Relation) |
            target_bit(TrainingTarget::Constructor),
        "REPOSITORY_HYDRATION",
        1U)
};

static_assert(
    sizeof(kMethods) / sizeof(kMethods[0]) == kVM5184Hash216TrainingMethodCount,
    "Lane 5 training registry count drift"
);

bool hash216_text_valid(const char value[HHS_HASH216_LEN + 1]) noexcept {
    if (value == nullptr || value[HHS_HASH216_LEN] != '\0')
        return false;
    for (std::size_t i = 0U; i < HHS_HASH216_LEN; ++i) {
        if (value[i] == '\0' ||
            std::strchr(HHS_HASH72_ALPHABET, value[i]) == nullptr)
            return false;
    }
    return true;
}

std::size_t descriptor_index(
    const TrainingMethodDescriptor *descriptor
) noexcept {
    if (descriptor == nullptr)
        return kVM5184Hash216TrainingMethodCount;
    return static_cast<std::size_t>(descriptor - &kMethods[0]);
}

bool routed_candidate_valid(
    const HHSExactPass219Holo4PreparedV1& prepared,
    const HHSExactPass219Holo4DecisionV1& decision
) noexcept {
    return prepared.struct_size == sizeof(prepared) &&
           prepared.version == HHS_EXACT_PASS219_HOLO4_VERSION &&
           prepared.word_visits == HHS_EXACT_VM81_CELLS &&
           prepared.graph_edge_visits ==
               HHS_EXACT_PASS219_HOLO4_DIRECTED_GRAPH_EDGES &&
           prepared.hash216_positions_complete == 1U &&
           prepared.candidate_only == 1U &&
           prepared.exact_integer_only == 1U &&
           prepared.canonical_mutation_authority == 0U &&
           prepared.canonical_hash72_authority == 0U &&
           prepared.canonical_hash216_authority == 0U &&
           prepared.canonical_persistence_authority == 0U &&
           prepared.floating_point_authority == 0U &&
           decision.struct_size == sizeof(decision) &&
           decision.version == HHS_EXACT_PASS219_HOLO4_VERSION &&
           decision.selected_lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT &&
           decision.candidate_only == 1U &&
           decision.exact_integer_only == 1U &&
           decision.canonical_mutation_authority == 0U &&
           decision.canonical_hash72_authority == 0U &&
           decision.canonical_hash216_authority == 0U &&
           decision.canonical_persistence_authority == 0U &&
           decision.floating_point_authority == 0U;
}

HHSExactStatus validate_specimen(
    const TrainingSpecimen& specimen,
    const TrainingMethodDescriptor& descriptor
) noexcept {
    if (specimen.struct_size != sizeof(specimen) ||
        specimen.version != kVM5184Hash216TrainingVersion)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (specimen.mode != descriptor.mode ||
        specimen.temporal != descriptor.temporal ||
        !VM5184Hash216TrainingAPI::target_allowed(descriptor, specimen.target))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!hash216_text_valid(specimen.source_identity216) ||
        !hash216_text_valid(specimen.oracle_identity216))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (specimen.adapter_signature64 == 0U ||
        specimen.executor_signature64 == 0U ||
        specimen.validator_signature64 == 0U ||
        specimen.replay_signature64 == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (descriptor.requires_oracle != 0U && specimen.oracle_verified != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (descriptor.requires_negative_controls != 0U &&
        (specimen.negative_controls_verified != 1U ||
         specimen.negative_control_signature64 == 0U))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (descriptor.requires_replay != 0U && specimen.replay_verified != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (descriptor.preserves_ingress_egress != 0U &&
        specimen.ingress_egress_preserved != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (specimen.candidate_only_acknowledged != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (specimen.natural_language_training > 1U ||
        specimen.ethical_text_supervision_verified > 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (descriptor.natural_language_native != 0U &&
        specimen.natural_language_training != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (specimen.natural_language_training == 1U) {
        if (specimen.ethical_text_supervision_verified != 1U ||
            specimen.ethical_text_supervisor_signature64 == 0U ||
            !hash216_text_valid(
                specimen.ethical_text_supervisor_identity216))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

}  // namespace

std::size_t VM5184Hash216TrainingAPI::method_count() noexcept {
    return kVM5184Hash216TrainingMethodCount;
}

const TrainingMethodDescriptor *VM5184Hash216TrainingAPI::method_by_index(
    std::size_t index
) noexcept {
    if (index >= kVM5184Hash216TrainingMethodCount)
        return nullptr;
    return &kMethods[index];
}

const TrainingMethodDescriptor *VM5184Hash216TrainingAPI::method(
    TrainingMode mode
) noexcept {
    for (const auto& descriptor : kMethods) {
        if (descriptor.mode == mode)
            return &descriptor;
    }
    return nullptr;
}

bool VM5184Hash216TrainingAPI::target_allowed(
    const TrainingMethodDescriptor& descriptor,
    TrainingTarget target
) noexcept {
    const std::uint32_t bit = target_bit(target);
    return bit != 0U && (descriptor.target_mask & bit) != 0U;
}

HHSExactStatus VM5184Hash216TrainingAPI::derive_candidate_hash216(
    const TrainingSpecimen& specimen,
    const HHSExactPass219Hash216TransitionViewV1& transition,
    const HHSExactPass219Holo4PreparedV1& prepared,
    const HHSExactPass219Holo4DecisionV1& decision,
    char out_hash216[HHS_HASH216_LEN + 1]
) noexcept {
    if (out_hash216 == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    std::memset(out_hash216, 0, HHS_HASH216_LEN + 1U);

    const TrainingMethodDescriptor *descriptor = method(specimen.mode);
    if (descriptor == nullptr ||
        validate_specimen(specimen, *descriptor) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&transition) !=
            HHS_EXACT_STATUS_OK ||
        !routed_candidate_valid(prepared, decision))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    char material[1800]{};
    const int written = std::snprintf(
        material,
        sizeof(material),
        "HHS-P219-LANE5-VM5184-HASH216-TRAINING-1.72|"
        "method=%s|mode=%" PRIu32 "|temporal=%" PRIu32
        "|target=%" PRIu32 "|source=%s|oracle=%s|transition=%s|"
        "naturalLanguage=%u|ethicalSupervisor=%s|ethicalSignature=%" PRIu64
        "|ethicalVerified=%u|adapter=%" PRIu64 "|executor=%" PRIu64
        "|validator=%" PRIu64 "|negative=%" PRIu64
        "|replay=%" PRIu64 "|lane=%u|graph=%" PRIu64
        "|tensor=%" PRIu64 "|decision=%" PRIu64,
        descriptor->method_id,
        static_cast<std::uint32_t>(specimen.mode),
        static_cast<std::uint32_t>(specimen.temporal),
        static_cast<std::uint32_t>(specimen.target),
        specimen.source_identity216,
        specimen.oracle_identity216,
        transition.transition_identity216,
        static_cast<unsigned>(specimen.natural_language_training),
        specimen.natural_language_training == 1U
            ? specimen.ethical_text_supervisor_identity216
            : "NONE",
        specimen.ethical_text_supervisor_signature64,
        static_cast<unsigned>(specimen.ethical_text_supervision_verified),
        specimen.adapter_signature64,
        specimen.executor_signature64,
        specimen.validator_signature64,
        specimen.negative_control_signature64,
        specimen.replay_signature64,
        static_cast<unsigned>(decision.selected_lane),
        prepared.graph_signature64,
        prepared.tensor_signature64,
        decision.decision_signature64
    );
    if (written <= 0 || static_cast<std::size_t>(written) >= sizeof(material))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    HHSHash216 hash{};
    hhs_hash216_compute(material, static_cast<std::size_t>(written), &hash);
    std::memcpy(out_hash216, hash.value, HHS_HASH216_LEN + 1U);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus VM5184Hash216TrainingAPI::evaluate(
    const TrainingSpecimen& specimen,
    const HHSExactUQCELInputV1& input,
    const HHSExactVM81Frame& frame,
    const HHSExactPass219Hash216TransitionViewV1& transition,
    std::uint8_t feedback_lane,
    std::int8_t feedback_trinary,
    TrainingReceipt& out
) const noexcept {
    out = TrainingReceipt{};
    out.version = kVM5184Hash216TrainingVersion;
    out.namespace_id = kVM5184Hash216TrainingNamespace;
    out.mode = specimen.mode;
    out.temporal = specimen.temporal;
    out.target = specimen.target;
    out.candidate_only = 1U;

    const TrainingMethodDescriptor *descriptor = method(specimen.mode);
    if (descriptor == nullptr)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    const std::size_t index = descriptor_index(descriptor);
    if (index >= kVM5184Hash216TrainingMethodCount)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out.method_index = static_cast<std::uint32_t>(index);

    HHSExactStatus status = validate_specimen(specimen, *descriptor);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    out.registry_verified = 1U;
    out.specimen_identity_verified = 1U;
    out.oracle_verified =
        descriptor->requires_oracle == 0U ? 1U : specimen.oracle_verified;
    out.negative_controls_verified = specimen.negative_controls_verified;
    out.replay_verified = specimen.replay_verified;
    out.ingress_egress_preserved = specimen.ingress_egress_preserved;
    out.natural_language_training = specimen.natural_language_training;
    out.ethical_text_supervision_required =
        specimen.natural_language_training == 1U ? 1U : 0U;
    out.ethical_text_supervision_verified =
        specimen.natural_language_training == 1U
            ? specimen.ethical_text_supervision_verified
            : 0U;
    if (specimen.natural_language_training == 1U) {
        std::memcpy(
            out.ethical_text_supervisor_identity216,
            specimen.ethical_text_supervisor_identity216,
            HHS_HASH216_LEN + 1U
        );
    }

    HHSExactPass219Holo4PreparedV1 prepared{};
    HHSExactPass219Holo4DecisionV1 decision{};
    status = hhs_exact_pass219_rna_vm5184_route(
        &input,
        &frame,
        &transition,
        feedback_lane,
        feedback_trinary,
        &prepared,
        &decision
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!routed_candidate_valid(prepared, decision))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.vm5184_routed = 1U;
    out.rna_prepared = prepared;
    out.rna_decision = decision;
    std::memcpy(
        out.source_identity216,
        specimen.source_identity216,
        HHS_HASH216_LEN + 1U
    );
    std::memcpy(
        out.oracle_identity216,
        specimen.oracle_identity216,
        HHS_HASH216_LEN + 1U
    );

    status = derive_candidate_hash216(
        specimen,
        transition,
        prepared,
        decision,
        out.training_candidate_hash216
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out.hash216_candidate_derived = 1U;
    out.accepted = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus VM5184Hash216TrainingAPI::evaluate_raw(
    const TrainingSpecimen& specimen,
    const HHSExactUQCELInputV1& input,
    const std::uint8_t *raw_frame_le,
    std::size_t raw_frame_length,
    const HHSExactPass219Hash216TransitionViewV1& transition,
    std::uint8_t feedback_lane,
    std::int8_t feedback_trinary,
    TrainingReceipt& out
) const noexcept {
    out = TrainingReceipt{};
    if (raw_frame_le == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (raw_frame_length != HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    HHSExactVM81Frame frame{};
    const HHSExactStatus status = hhs_exact_vm81_frame_import_le(
        raw_frame_le,
        raw_frame_length,
        &frame
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return evaluate(
        specimen,
        input,
        frame,
        transition,
        feedback_lane,
        feedback_trinary,
        out
    );
}

}  // namespace hhs::lane5
