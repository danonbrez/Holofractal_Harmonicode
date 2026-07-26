#include "hhs_pass158_api.h"

#include <stdio.h>
#include <string.h>

#define INIT(value) do { memset(&(value), 0, sizeof(value)); (value).header.struct_size = (uint32_t)sizeof(value); (value).header.struct_version = HHS158_STRUCT_VERSION_1; } while (0)
#define SPAN(text) ((HHS158ByteSpan){(const uint8_t *)(text), strlen(text)})

static HHS158Status read_id(HHS158Instance *instance, char output[HHS158_HASH216_LENGTH + 1u]) {
    HHS158MutableByteSpan span = {(uint8_t *)output, HHS158_HASH216_LENGTH, 0u};
    HHS158Status status = hhs158_instance_id(instance, &span);
    output[HHS158_HASH216_LENGTH] = '\0';
    return status;
}

static HHS158Status read_root(HHS158Instance *instance, char output[HHS158_HASH216_LENGTH + 1u]) {
    HHS158MutableByteSpan span = {(uint8_t *)output, HHS158_HASH216_LENGTH, 0u};
    HHS158Status status = hhs158_instance_state_root(instance, &span);
    output[HHS158_HASH216_LENGTH] = '\0';
    return status;
}

int main(void) {
    HHS158ContextConfig context_config;
    HHS158Context *context = NULL;
    HHS158DefinitionDescriptor definition_descriptor;
    HHS158Definition *definition = NULL;
    HHS158Receipt *receipt = NULL;
    HHS158InstanceConfig instance_config;
    HHS158Instance *instance = NULL;
    HHS158CapabilityRequest capability_request;
    HHS158Capability *capability = NULL;
    HHS158Operation operation;
    HHS158TransitionDescriptor transition_descriptor;
    HHS158ExecutionOptions execution_options;
    HHS158ExecutionResult execution_result;
    HHS158Transition *transition = NULL;
    HHS158ReplayOptions replay_options;
    HHS158ReplayResult replay_result;
    char identity_before[HHS158_HASH216_LENGTH + 1u];
    char identity_after[HHS158_HASH216_LENGTH + 1u];
    char root[HHS158_HASH216_LENGTH + 1u];
    uint64_t shape[2] = {1u, 1u};
    HHS158Status status;
    size_t index;

    INIT(context_config);
    context_config.abi_major = HHS158_ABI_VERSION_MAJOR;
    context_config.abi_minor = HHS158_ABI_VERSION_MINOR;
    context_config.max_definitions = 8u;
    context_config.max_instances = 8u;
    context_config.max_receipts = 64u;
    context_config.max_memory_bytes = UINT64_C(16777216);
    context_config.deterministic_epoch_seconds = UINT64_C(1799711799);
    status = hhs158_context_create(&context_config, &context);
    if (status != HHS158_OK) return 1;

    INIT(definition_descriptor);
    definition_descriptor.contract_id = SPAN("HHS-P158-LLABI-NFTC-API");
    definition_descriptor.schema_version = SPAN("1.0.0");
    definition_descriptor.canonical_name = SPAN("IMMUTABLE_INSTANCE_IDENTITY_TEST");
    definition_descriptor.object_class = SPAN("NON_FUNGIBLE_TENSOR_CONSTRAINT");
    definition_descriptor.canonical_constraints = SPAN("A==B;O!=Pi");
    definition_descriptor.symbol_table = SPAN("A,B,O,Pi");
    definition_descriptor.numeric_policy = SPAN("EXACT_SYMBOLIC");
    definition_descriptor.operator_policy = SPAN("HHS_TYPED_OPERATORS");
    definition_descriptor.authority_root = SPAN("PASS_158_INHERITED_ROOT");
    definition_descriptor.ancestry = SPAN("P154|P155|P156|P156.1|P157");
    definition_descriptor.tensor_rank = 2u;
    definition_descriptor.tensor_shape = shape;
    status = hhs158_definition_register(context, &definition_descriptor, &definition, &receipt);
    if (status != HHS158_OK) return 2;

    INIT(instance_config);
    instance_config.instance_nonce = SPAN("immutable-instance-identity");
    instance_config.max_vm81_steps = UINT64_C(100000);
    instance_config.max_recursion_depth = 72u;
    instance_config.max_state_bytes = UINT64_C(16777216);
    instance_config.max_receipt_bytes = UINT64_C(1048576);
    status = hhs158_instance_create(context, definition, &instance_config, &instance, &receipt);
    if (status != HHS158_OK || read_id(instance, identity_before) != HHS158_OK) return 3;

    INIT(capability_request);
    capability_request.issuer = SPAN("HHS_PASS158_AUTHORITY");
    capability_request.subject = SPAN("identity-test");
    capability_request.application_id = SPAN("org.hhs.pass158.identity-test");
    capability_request.object_scope = SPAN(identity_before);
    capability_request.operation_scope = HHS158_CAP_EXECUTE | HHS158_CAP_COMMIT | HHS158_CAP_REPLAY;
    capability_request.mutation_scope = HHS158_MUTATION_INSTANCE;
    capability_request.max_vm81_steps = UINT64_C(100000);
    capability_request.issued_at = UINT64_C(1799711700);
    capability_request.expires_at = UINT64_C(1799719999);
    status = hhs158_capability_open(context, &capability_request, &capability);
    if (status != HHS158_OK) return 4;

    for (index = 0u; index < 18u; ++index) {
        char operands[64];
        int written;
        if (read_root(instance, root) != HHS158_OK) return 5;
        written = snprintf(operands, sizeof(operands), "A%lu,B%lu", (unsigned long)index, (unsigned long)index);
        if (written < 0 || (size_t)written >= sizeof(operands)) return 6;
        INIT(operation);
        operation.opcode = HHS158_OP_BIND_EQ;
        operation.operands = SPAN(operands);
        INIT(transition_descriptor);
        transition_descriptor.operations = &operation;
        transition_descriptor.operation_count = 1u;
        transition_descriptor.expected_pre_state_root = SPAN(root);
        transition_descriptor.max_vm81_steps = 1000u;
        transition_descriptor.max_recursion_depth = 72u;
        transition_descriptor.max_output_bytes = UINT64_C(1048576);
        status = hhs158_transition_create(instance, capability, &transition_descriptor, &transition);
        if (status != HHS158_OK) return 7;
        INIT(execution_options);
        execution_options.max_vm81_steps = 1000u;
        execution_options.atomic_execute_and_commit = 1u;
        status = hhs158_transition_execute(transition, &execution_options, &execution_result, &receipt);
        if (status != HHS158_OK) return 8;
        if (read_id(instance, identity_after) != HHS158_OK || strcmp(identity_before, identity_after) != 0) return 9;
        INIT(replay_options);
        replay_options.verify_hash72 = 1u;
        replay_options.verify_hash216 = 1u;
        replay_options.verify_semantic_root = 1u;
        status = hhs158_receipt_replay(context, receipt, &replay_options, &replay_result);
        if (status != HHS158_OK || !replay_result.matched) return 10;
    }

    printf("{\"classification\":\"HHS_PASS_158_INSTANCE_IDENTITY_IMMUTABLE\",\"commits\":18,\"identity_length\":216}\n");
    hhs158_context_release(context);
    return 0;
}
