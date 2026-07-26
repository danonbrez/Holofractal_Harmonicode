#include "hhs_pass158_api.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HEADER(value) do { (value).header.struct_size = (uint32_t)sizeof(value); (value).header.struct_version = HHS158_STRUCT_VERSION_1; } while (0)
#define SPAN_TEXT(text) ((HHS158ByteSpan){(const uint8_t *)(text), sizeof(text) - 1u})

static int emit_dynamic(HHS158Status (*function)(HHS158MutableByteSpan *)) {
    HHS158MutableByteSpan span = {0};
    HHS158Status status = function(&span);
    uint8_t *buffer;
    if (status != HHS158_BUFFER_TOO_SMALL) return 1;
    buffer = (uint8_t *)malloc(span.size_written + 1u);
    if (!buffer) return 1;
    span.data = buffer; span.capacity = span.size_written; span.size_written = 0u;
    status = function(&span);
    if (status != HHS158_OK) { free(buffer); return 1; }
    buffer[span.size_written] = '\0';
    puts((const char *)buffer);
    free(buffer);
    return 0;
}

static int run_demo(void) {
    HHS158ContextConfig context_config = {0};
    HHS158Context *context = NULL;
    HHS158DefinitionDescriptor definition_descriptor = {0};
    HHS158Definition *definition = NULL;
    HHS158Receipt *definition_receipt = NULL;
    HHS158InstanceConfig instance_config = {0};
    HHS158Instance *instance = NULL;
    HHS158Receipt *instance_receipt = NULL;
    HHS158CapabilityRequest capability_request = {0};
    HHS158Capability *capability = NULL;
    HHS158Value rational = {0};
    HHS158ValidationPolicy validation_policy = {0};
    HHS158ValidationReport validation_report = {0};
    HHS158Operation operations[2] = {{0}};
    HHS158TransitionDescriptor transition_descriptor = {0};
    HHS158Transition *transition = NULL;
    HHS158ExecutionOptions execution_options = {0};
    HHS158ExecutionResult execution_result = {0};
    HHS158Receipt *commit_receipt = NULL;
    HHS158ReplayOptions replay_options = {0};
    HHS158ReplayResult replay_result = {0};
    HHS158SerializationOptions serialization_options = {0};
    HHS158MutableByteSpan serialized = {0};
    uint8_t *serialized_buffer = NULL;
    uint64_t shape[2] = {9u, 9u};
    uint8_t id_buffer[HHS158_HASH216_LENGTH + 1u];
    HHS158MutableByteSpan id_span = {id_buffer, HHS158_HASH216_LENGTH, 0u};
    HHS158Status status;
    static const uint8_t CONSTRAINTS[] = "A==B==C; O!=Pi; ordered=[x,x,y]; Delta=P^2-pq";
    static const uint8_t SYMBOLS[] = "A,B,C,O,Pi,x,y,Delta,P,p,q";
    static const uint8_t NONCE[] = "pass158-native-demo-0001";
    static const uint8_t RATIONAL[] = "1/3";

    HEADER(context_config);
    context_config.abi_major = HHS158_ABI_VERSION_MAJOR;
    context_config.abi_minor = HHS158_ABI_VERSION_MINOR;
    context_config.max_definitions = 16u;
    context_config.max_instances = 32u;
    context_config.max_receipts = 128u;
    context_config.max_memory_bytes = UINT64_C(16777216);
    context_config.deterministic_epoch_seconds = UINT64_C(1799711799);
    status = hhs158_context_create(&context_config, &context);
    if (status != HHS158_OK) return 1;

    HEADER(definition_descriptor);
    definition_descriptor.contract_id = SPAN_TEXT("HHS-P158-LLABI-NFTC-API");
    definition_descriptor.schema_version = SPAN_TEXT("1.0.0");
    definition_descriptor.canonical_name = SPAN_TEXT("PASS158_NATIVE_DEMO");
    definition_descriptor.object_class = SPAN_TEXT("NON_FUNGIBLE_TENSOR_CONSTRAINT");
    definition_descriptor.canonical_constraints.data = CONSTRAINTS;
    definition_descriptor.canonical_constraints.size = sizeof(CONSTRAINTS) - 1u;
    definition_descriptor.symbol_table.data = SYMBOLS;
    definition_descriptor.symbol_table.size = sizeof(SYMBOLS) - 1u;
    definition_descriptor.numeric_policy = SPAN_TEXT("EXACT_SYMBOLIC");
    definition_descriptor.operator_policy = SPAN_TEXT("HHS_TYPED_OPERATORS");
    definition_descriptor.authority_root = SPAN_TEXT("PASS_158_INHERITED_ROOT");
    definition_descriptor.ancestry = SPAN_TEXT("P154|P155|P156|P156.1|P157");
    definition_descriptor.tensor_rank = 2u;
    definition_descriptor.tensor_shape = shape;
    status = hhs158_definition_register(context, &definition_descriptor, &definition, &definition_receipt);
    if (status != HHS158_OK) goto fail;

    HEADER(instance_config);
    instance_config.instance_nonce.data = NONCE;
    instance_config.instance_nonce.size = sizeof(NONCE) - 1u;
    instance_config.max_vm81_steps = UINT64_C(100000);
    instance_config.max_recursion_depth = 72u;
    instance_config.max_state_bytes = UINT64_C(16777216);
    instance_config.max_receipt_bytes = UINT64_C(1048576);
    instance_config.projection_profile_mask = 0xffffffffu;
    status = hhs158_instance_create(context, definition, &instance_config, &instance, &instance_receipt);
    if (status != HHS158_OK) goto fail;
    status = hhs158_instance_id(instance, &id_span);
    if (status != HHS158_OK) goto fail;
    id_buffer[HHS158_HASH216_LENGTH] = '\0';

    HEADER(capability_request);
    capability_request.issuer = SPAN_TEXT("HHS_PASS158_AUTHORITY");
    capability_request.subject = SPAN_TEXT("native-demo");
    capability_request.application_id = SPAN_TEXT("org.hhs.pass158.native-demo");
    capability_request.object_scope.data = id_buffer;
    capability_request.object_scope.size = HHS158_HASH216_LENGTH;
    capability_request.operation_scope = HHS158_CAP_VALIDATE | HHS158_CAP_EXECUTE | HHS158_CAP_COMMIT |
        HHS158_CAP_PROJECT | HHS158_CAP_SERIALIZE | HHS158_CAP_REPLAY;
    capability_request.mutation_scope = HHS158_MUTATION_INSTANCE;
    capability_request.max_vm81_steps = UINT64_C(100000);
    capability_request.issued_at = UINT64_C(1799711700);
    capability_request.expires_at = UINT64_C(1799719999);
    status = hhs158_capability_open(context, &capability_request, &capability);
    if (status != HHS158_OK) goto fail;

    HEADER(rational);
    rational.kind = HHS158_VALUE_RATIONAL;
    rational.flags = HHS158_FLAG_AUTHORITATIVE | HHS158_FLAG_IMMUTABLE;
    rational.canonical_payload.data = RATIONAL;
    rational.canonical_payload.size = sizeof(RATIONAL) - 1u;
    status = hhs158_instance_bind(instance, SPAN_TEXT("x"), &rational);
    if (status != HHS158_OK) goto fail;

    HEADER(validation_policy);
    validation_policy.mode = 3u;
    validation_policy.max_vm81_steps = UINT64_C(100000);
    validation_policy.max_recursion_depth = 72u;
    validation_policy.max_dependency_depth = 72u;
    validation_policy.max_tensor_elements = 5184u;
    status = hhs158_instance_validate_static(instance, &validation_policy, &validation_report);
    if (status != HHS158_OK) goto fail;

    HEADER(operations[0]);
    operations[0].opcode = HHS158_OP_BIND_EQ;
    operations[0].operands = SPAN_TEXT("A,B");
    HEADER(operations[1]);
    operations[1].opcode = HHS158_OP_CHAIN_APPEND;
    operations[1].operands = SPAN_TEXT("B,C");
    HEADER(transition_descriptor);
    transition_descriptor.operations = operations;
    transition_descriptor.operation_count = 2u;
    transition_descriptor.expected_pre_state_root.data = (const uint8_t *)validation_report.state_root;
    transition_descriptor.expected_pre_state_root.size = HHS158_HASH216_LENGTH;
    transition_descriptor.max_vm81_steps = UINT64_C(10000);
    transition_descriptor.max_recursion_depth = 72u;
    transition_descriptor.max_output_bytes = UINT64_C(1048576);
    transition_descriptor.commit_policy = HHS158_TRANSITION_EXECUTE_AND_COMMIT;
    status = hhs158_transition_create(instance, capability, &transition_descriptor, &transition);
    if (status != HHS158_OK) goto fail;

    HEADER(execution_options);
    execution_options.max_vm81_steps = UINT64_C(10000);
    execution_options.atomic_execute_and_commit = 1u;
    status = hhs158_transition_execute(transition, &execution_options, &execution_result, &commit_receipt);
    if (status != HHS158_OK) goto fail;

    HEADER(replay_options);
    replay_options.verify_hash72 = 1u;
    replay_options.verify_hash216 = 1u;
    replay_options.verify_semantic_root = 1u;
    status = hhs158_receipt_replay(context, commit_receipt, &replay_options, &replay_result);
    if (status != HHS158_OK || !replay_result.matched) goto fail;

    HEADER(serialization_options);
    serialization_options.format = HHS158_SERIALIZE_CANONICAL_JSON;
    serialization_options.preserve_unknown_fields = 1u;
    serialization_options.max_output_bytes = UINT64_C(1048576);
    status = hhs158_instance_serialize(instance, &serialization_options, &serialized);
    if (status != HHS158_BUFFER_TOO_SMALL) goto fail;
    serialized_buffer = (uint8_t *)malloc(serialized.size_written + 1u);
    if (!serialized_buffer) goto fail;
    serialized.data = serialized_buffer;
    serialized.capacity = serialized.size_written;
    status = hhs158_instance_serialize(instance, &serialization_options, &serialized);
    if (status != HHS158_OK) goto fail;
    serialized_buffer[serialized.size_written] = '\0';

    printf("{\"contract_id\":\"%s\",\"definition\":\"%s\",\"instance\":\"%s\","
           "\"validation\":\"%s\",\"transition\":\"%s\",\"receipt\":\"%s\","
           "\"replay\":\"%s\",\"serialization_bytes\":%lu}\n",
        hhs158_contract_id(), "HHS_P158_NFT_DEFINITION_REGISTERED", (const char *)id_buffer,
        validation_report.classification, execution_result.classification, commit_receipt->classification,
        replay_result.classification, (unsigned long)serialized.size_written);
    free(serialized_buffer);
    hhs158_context_release(context);
    return 0;

fail:
    fprintf(stderr, "pass158 demo failed: %s (%d)\n", hhs158_status_classification(status), (int)status);
    free(serialized_buffer);
    hhs158_context_release(context);
    return 1;
}

int main(int argc, char **argv) {
    if (argc < 2 || strcmp(argv[1], "demo") == 0) return run_demo();
    if (strcmp(argv[1], "capabilities") == 0) return emit_dynamic(hhs158_capabilities_json);
    if (strcmp(argv[1], "abi") == 0) return emit_dynamic(hhs158_abi_descriptor_json);
    if (strcmp(argv[1], "opcodes") == 0) return emit_dynamic(hhs158_opcode_descriptor_json);
    if (strcmp(argv[1], "verify") == 0) {
        if (run_demo() != 0) return 1;
        puts("{\"classification\":\"HHS_PASS_158_NATIVE_CORE_VERIFIED\"}");
        return 0;
    }
    fprintf(stderr, "usage: hhs-pass158 [demo|verify|capabilities|abi|opcodes]\n");
    return 2;
}
