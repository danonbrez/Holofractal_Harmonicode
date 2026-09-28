#include "hhs_pass219_lane5_vm5184_hash216_training_c_abi_1_73.h"
#include "hhs_pass219_lane5_vm5184_hash216_training_1_73.hpp"

#include <cstring>

namespace {

using hhs::lane5::TrainingMethodDescriptor;
using hhs::lane5::TrainingMode;
using hhs::lane5::TrainingReceipt;
using hhs::lane5::TrainingSpecimen;
using hhs::lane5::TrainingTarget;
using hhs::lane5::TrainingTemporal;
using hhs::lane5::VM5184Hash216TrainingAPI;

void clear_method(HHSExactPass219Lane5TrainingMethodV1 *value) noexcept {
    if (value != nullptr)
        std::memset(value, 0, sizeof(*value));
}

void clear_receipt(HHSExactPass219Lane5TrainingReceiptV1 *value) noexcept {
    if (value != nullptr)
        std::memset(value, 0, sizeof(*value));
}

HHSExactStatus copy_specimen(
    const HHSExactPass219Lane5TrainingSpecimenV1& source,
    TrainingSpecimen& target
) noexcept {
    if (source.struct_size != sizeof(source) ||
        source.version != hhs::lane5::kVM5184Hash216TrainingVersion)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    target = TrainingSpecimen{};
    target.struct_size = static_cast<std::uint32_t>(sizeof(target));
    target.version = hhs::lane5::kVM5184Hash216TrainingVersion;
    target.mode = static_cast<TrainingMode>(source.mode);
    target.temporal = static_cast<TrainingTemporal>(source.temporal);
    target.target = static_cast<TrainingTarget>(source.target);
    std::memcpy(
        target.source_identity216,
        source.source_identity216,
        HHS_HASH216_LEN + 1U
    );
    std::memcpy(
        target.oracle_identity216,
        source.oracle_identity216,
        HHS_HASH216_LEN + 1U
    );
    std::memcpy(
        target.ethical_text_supervisor_identity216,
        source.ethical_text_supervisor_identity216,
        HHS_HASH216_LEN + 1U
    );
    target.adapter_signature64 = source.adapter_signature64;
    target.executor_signature64 = source.executor_signature64;
    target.validator_signature64 = source.validator_signature64;
    target.negative_control_signature64 = source.negative_control_signature64;
    target.replay_signature64 = source.replay_signature64;
    target.ethical_text_supervisor_signature64 =
        source.ethical_text_supervisor_signature64;
    target.oracle_verified = source.oracle_verified;
    target.negative_controls_verified = source.negative_controls_verified;
    target.replay_verified = source.replay_verified;
    target.ingress_egress_preserved = source.ingress_egress_preserved;
    target.candidate_only_acknowledged = source.candidate_only_acknowledged;
    target.natural_language_training = source.natural_language_training;
    target.ethical_text_supervision_verified =
        source.ethical_text_supervision_verified;
    return HHS_EXACT_STATUS_OK;
}

void copy_receipt(
    const TrainingReceipt& source,
    HHSExactPass219Lane5TrainingReceiptV1& target
) noexcept {
    target = HHSExactPass219Lane5TrainingReceiptV1{};
    target.struct_size = static_cast<std::uint32_t>(sizeof(target));
    target.version = source.version;
    target.namespace_id = source.namespace_id;
    target.mode = static_cast<std::uint32_t>(source.mode);
    target.temporal = static_cast<std::uint32_t>(source.temporal);
    target.target = static_cast<std::uint32_t>(source.target);
    target.method_index = source.method_index;
    target.selected_lane = source.rna_decision.selected_lane;
    target.graph_signature64 = source.rna_prepared.graph_signature64;
    target.tensor_signature64 = source.rna_prepared.tensor_signature64;
    target.decision_signature64 = source.rna_decision.decision_signature64;
    std::memcpy(
        target.source_identity216,
        source.source_identity216,
        HHS_HASH216_LEN + 1U
    );
    std::memcpy(
        target.oracle_identity216,
        source.oracle_identity216,
        HHS_HASH216_LEN + 1U
    );
    std::memcpy(
        target.ethical_text_supervisor_identity216,
        source.ethical_text_supervisor_identity216,
        HHS_HASH216_LEN + 1U
    );
    std::memcpy(
        target.training_candidate_hash216,
        source.training_candidate_hash216,
        HHS_HASH216_LEN + 1U
    );
    target.accepted = source.accepted;
    target.registry_verified = source.registry_verified;
    target.specimen_identity_verified = source.specimen_identity_verified;
    target.oracle_verified = source.oracle_verified;
    target.negative_controls_verified = source.negative_controls_verified;
    target.replay_verified = source.replay_verified;
    target.ingress_egress_preserved = source.ingress_egress_preserved;
    target.natural_language_training = source.natural_language_training;
    target.ethical_text_supervision_required =
        source.ethical_text_supervision_required;
    target.ethical_text_supervision_verified =
        source.ethical_text_supervision_verified;
    target.vm5184_routed = source.vm5184_routed;
    target.hash216_candidate_derived = source.hash216_candidate_derived;
    target.candidate_only = source.candidate_only;
    target.canonical_vm81_mutation_authority =
        source.canonical_vm81_mutation_authority;
    target.canonical_hash72_authority = source.canonical_hash72_authority;
    target.canonical_hash216_authority = source.canonical_hash216_authority;
    target.canonical_persistence_authority =
        source.canonical_persistence_authority;
    target.floating_point_canonical_authority =
        source.floating_point_canonical_authority;
}

}  // namespace

extern "C" uint32_t hhs_exact_pass219_lane5_training_c_abi_version(void) {
    return HHS_EXACT_PASS219_LANE5_TRAINING_C_ABI_VERSION;
}

extern "C" uint32_t hhs_exact_pass219_lane5_training_method_count(void) {
    return static_cast<uint32_t>(VM5184Hash216TrainingAPI::method_count());
}

extern "C" HHSExactStatus hhs_exact_pass219_lane5_training_method(
    uint32_t index,
    HHSExactPass219Lane5TrainingMethodV1 *out_method
) {
    clear_method(out_method);
    if (out_method == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    const TrainingMethodDescriptor *descriptor =
        VM5184Hash216TrainingAPI::method_by_index(index);
    if (descriptor == nullptr)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    out_method->struct_size = static_cast<uint32_t>(sizeof(*out_method));
    out_method->version = hhs::lane5::kVM5184Hash216TrainingVersion;
    out_method->mode = static_cast<uint32_t>(descriptor->mode);
    out_method->temporal = static_cast<uint32_t>(descriptor->temporal);
    out_method->primary_target =
        static_cast<uint32_t>(descriptor->primary_target);
    out_method->target_mask = descriptor->target_mask;
    if (descriptor->method_id == nullptr)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    const std::size_t method_len = std::strlen(descriptor->method_id);
    if (method_len + 1U >
        HHS_EXACT_PASS219_LANE5_TRAINING_METHOD_ID_BYTES)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    std::memcpy(out_method->method_id, descriptor->method_id, method_len + 1U);
    out_method->requires_oracle = descriptor->requires_oracle;
    out_method->requires_negative_controls =
        descriptor->requires_negative_controls;
    out_method->requires_replay = descriptor->requires_replay;
    out_method->preserves_ingress_egress =
        descriptor->preserves_ingress_egress;
    out_method->routes_through_vm5184 = descriptor->routes_through_vm5184;
    out_method->emits_candidate_hash216 =
        descriptor->emits_candidate_hash216;
    out_method->candidate_only = descriptor->candidate_only;
    out_method->natural_language_native =
        descriptor->natural_language_native;
    out_method->ethical_text_supervisor =
        descriptor->ethical_text_supervisor;
    return HHS_EXACT_STATUS_OK;
}

extern "C" HHSExactStatus
hhs_exact_pass219_lane5_training_genesis_identity216(
    char out_identity216[HHS_HASH216_LEN + 1]
) {
    if (out_identity216 == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    std::memset(out_identity216, 0, HHS_HASH216_LEN + 1U);

    HHSExactPass219Hash216TransitionViewV1 transition{};
    const HHSExactStatus status =
        hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&transition);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    std::memcpy(
        out_identity216,
        transition.transition_identity216,
        HHS_HASH216_LEN + 1U
    );
    return HHS_EXACT_STATUS_OK;
}

extern "C" HHSExactStatus hhs_exact_pass219_lane5_training_evaluate_raw(
    const HHSExactPass219Lane5TrainingSpecimenV1 *specimen,
    uint32_t uqcel_profile,
    const uint8_t *delta_be,
    size_t delta_length,
    const uint8_t *raw_frame_le,
    size_t raw_frame_length,
    const char previous_hash72[HHS_EXACT_HASH72_STRLEN],
    const char change_hash72[HHS_EXACT_HASH72_STRLEN],
    const char receipt_hash72[HHS_EXACT_HASH72_STRLEN],
    uint8_t use_genesis_transition,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219Lane5TrainingReceiptV1 *out_receipt
) {
    clear_receipt(out_receipt);
    if (specimen == nullptr || delta_be == nullptr ||
        raw_frame_le == nullptr || out_receipt == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (delta_length == 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (use_genesis_transition > 1U)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    TrainingSpecimen native_specimen{};
    HHSExactStatus status = copy_specimen(*specimen, native_specimen);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    HHSExactUQCELInputV1 input{};
    input.struct_size = static_cast<uint32_t>(sizeof(input));
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = uqcel_profile;
    input.delta.struct_size = static_cast<uint32_t>(sizeof(input.delta));
    input.delta.byte_length = delta_length;
    input.delta.bytes_be = delta_be;

    HHSExactPass219Hash216TransitionViewV1 transition{};
    if (use_genesis_transition != 0U) {
        status =
            hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&transition);
    } else {
        if (previous_hash72 == nullptr || change_hash72 == nullptr ||
            receipt_hash72 == nullptr)
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        status = hhs_exact_pass219_vm81_pqc_hash216_reference_init(
            previous_hash72,
            change_hash72,
            receipt_hash72,
            &transition
        );
    }
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    TrainingReceipt native_receipt{};
    const VM5184Hash216TrainingAPI api;
    status = api.evaluate_raw(
        native_specimen,
        input,
        raw_frame_le,
        raw_frame_length,
        transition,
        feedback_lane,
        feedback_trinary,
        native_receipt
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    copy_receipt(native_receipt, *out_receipt);
    return HHS_EXACT_STATUS_OK;
}
