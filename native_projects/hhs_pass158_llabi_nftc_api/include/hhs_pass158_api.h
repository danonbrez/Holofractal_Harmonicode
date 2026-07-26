#ifndef HHS_PASS158_API_H
#define HHS_PASS158_API_H

#include "hhs_pass158_types.h"
#include "hhs_pass158_opcodes.h"

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32)
#define HHS158_API __declspec(dllexport)
#elif defined(__GNUC__) && __GNUC__ >= 4
#define HHS158_API __attribute__((visibility("default")))
#else
#define HHS158_API
#endif

#define HHS158_CONTRACT_ID "HHS-P158-LLABI-NFTC-API"
#define HHS158_CONTRACT_VERSION "1.0.0"
#define HHS158_TERMINAL_CLASSIFICATION "HHS_PASS_158_LOW_LEVEL_ABI_NFT_CONSTRAINT_INTEGRATION_API_VERIFIED"

HHS158_API uint32_t hhs158_abi_version_major(void);
HHS158_API uint32_t hhs158_abi_version_minor(void);
HHS158_API const char *hhs158_contract_id(void);
HHS158_API const char *hhs158_contract_version(void);

HHS158_API HHS158Status hhs158_context_create(
    const HHS158ContextConfig *config,
    HHS158Context **out_context
);
HHS158_API void hhs158_context_release(HHS158Context *context);

HHS158_API HHS158Status hhs158_capability_open(
    HHS158Context *context,
    const HHS158CapabilityRequest *request,
    HHS158Capability **out_capability
);
HHS158_API HHS158Status hhs158_capability_revoke(
    HHS158Capability *capability,
    HHS158ByteSpan revocation_root
);
HHS158_API void hhs158_capability_release(HHS158Capability *capability);

HHS158_API HHS158Status hhs158_definition_register(
    HHS158Context *context,
    const HHS158DefinitionDescriptor *descriptor,
    HHS158Definition **out_definition,
    HHS158Receipt **out_receipt
);
HHS158_API HHS158Status hhs158_definition_open(
    HHS158Context *context,
    HHS158ByteSpan definition_id,
    HHS158Definition **out_definition
);
HHS158_API HHS158Status hhs158_definition_id(
    const HHS158Definition *definition,
    HHS158MutableByteSpan *output
);
HHS158_API void hhs158_definition_release(HHS158Definition *definition);

HHS158_API HHS158Status hhs158_instance_create(
    HHS158Context *context,
    HHS158Definition *definition,
    const HHS158InstanceConfig *config,
    HHS158Instance **out_instance,
    HHS158Receipt **out_receipt
);
HHS158_API HHS158Status hhs158_instance_id(
    const HHS158Instance *instance,
    HHS158MutableByteSpan *output
);
HHS158_API HHS158Status hhs158_instance_state_root(
    const HHS158Instance *instance,
    HHS158MutableByteSpan *output
);
HHS158_API HHS158Status hhs158_instance_lifecycle(
    const HHS158Instance *instance,
    uint32_t *out_lifecycle
);
HHS158_API HHS158Status hhs158_instance_bind(
    HHS158Instance *instance,
    HHS158ByteSpan symbol_name,
    const HHS158Value *value
);
HHS158_API HHS158Status hhs158_instance_validate_static(
    HHS158Instance *instance,
    const HHS158ValidationPolicy *policy,
    HHS158ValidationReport *out_report
);
HHS158_API HHS158Status hhs158_instance_validate_dynamic(
    HHS158Instance *instance,
    const HHS158ExecutionInputs *inputs,
    const HHS158ValidationPolicy *policy,
    HHS158ValidationReport *out_report
);
HHS158_API HHS158Status hhs158_instance_retire(
    HHS158Instance *instance,
    HHS158Capability *capability,
    HHS158Receipt **out_receipt
);
HHS158_API HHS158Status hhs158_instance_quarantine(
    HHS158Instance *instance,
    uint32_t reason_code,
    HHS158Receipt **out_receipt
);
HHS158_API void hhs158_instance_release(HHS158Instance *instance);

HHS158_API HHS158Status hhs158_transition_create(
    HHS158Instance *instance,
    HHS158Capability *capability,
    const HHS158TransitionDescriptor *descriptor,
    HHS158Transition **out_transition
);
HHS158_API HHS158Status hhs158_transition_execute(
    HHS158Transition *transition,
    const HHS158ExecutionOptions *options,
    HHS158ExecutionResult *out_result,
    HHS158Receipt **out_receipt
);
HHS158_API HHS158Status hhs158_transition_commit(
    HHS158Transition *transition,
    HHS158Receipt **out_commit_receipt
);
HHS158_API HHS158Status hhs158_transition_abort(
    HHS158Transition *transition,
    uint32_t reason_code,
    HHS158Receipt **out_abort_receipt
);
HHS158_API void hhs158_transition_release(HHS158Transition *transition);

HHS158_API HHS158Status hhs158_instance_project(
    HHS158Instance *instance,
    const HHS158ProjectionProfile *profile,
    HHS158Value *out_projection,
    HHS158Receipt **out_receipt
);
HHS158_API HHS158Status hhs158_delta_compute(
    const HHS158Value *projected_state,
    const HHS158Value *reference_state,
    const HHS158DeltaPolicy *policy,
    HHS158Value *out_delta_vector
);
HHS158_API HHS158Status hhs158_delta_normalize(
    const HHS158Value *projected_state,
    const HHS158Value *delta_vector,
    HHS158Value *out_normalized_state
);
HHS158_API void hhs158_value_release(HHS158Value *value);

HHS158_API HHS158Status hhs158_instance_serialize(
    HHS158Instance *instance,
    const HHS158SerializationOptions *options,
    HHS158MutableByteSpan *output
);
HHS158_API HHS158Status hhs158_instance_deserialize(
    HHS158Context *context,
    HHS158ByteSpan serialized_object,
    const HHS158DeserializationOptions *options,
    HHS158Instance **out_instance,
    HHS158Receipt **out_receipt
);
HHS158_API HHS158Status hhs158_instance_compose(
    HHS158Context *context,
    HHS158Instance *const *instances,
    size_t instance_count,
    const HHS158CompositionPolicy *policy,
    HHS158Instance **out_composite,
    HHS158Receipt **out_receipt
);

HHS158_API HHS158Status hhs158_receipt_replay(
    HHS158Context *context,
    HHS158Receipt *receipt,
    const HHS158ReplayOptions *options,
    HHS158ReplayResult *out_result
);
HHS158_API HHS158Status hhs158_receipt_serialize(
    HHS158Receipt *receipt,
    HHS158MutableByteSpan *output
);
HHS158_API HHS158Status hhs158_receipt_hash72(
    const HHS158Receipt *receipt,
    HHS158MutableByteSpan *output
);
HHS158_API HHS158Status hhs158_receipt_hash216(
    const HHS158Receipt *receipt,
    HHS158MutableByteSpan *output
);
HHS158_API void hhs158_receipt_release(HHS158Receipt *receipt);

HHS158_API HHS158Status hhs158_abi_descriptor_json(HHS158MutableByteSpan *output);
HHS158_API HHS158Status hhs158_opcode_descriptor_json(HHS158MutableByteSpan *output);
HHS158_API HHS158Status hhs158_capabilities_json(HHS158MutableByteSpan *output);

#ifdef __cplusplus
}
#endif

#endif
