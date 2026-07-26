#include "hhs_pass158_internal.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define INIT(v) do { memset(&(v), 0, sizeof(v)); (v).header.struct_size=(uint32_t)sizeof(v); (v).header.struct_version=HHS158_STRUCT_VERSION_1; } while (0)
#define SPAN(s) ((HHS158ByteSpan){(const uint8_t *)(s), strlen(s)})
#define REQUIRE(x) do { if (!(x)) { fprintf(stderr, "security assertion failed %s:%d: %s\n", __FILE__, __LINE__, #x); return 0; } } while (0)

typedef struct {
    HHS158Context *context;
    HHS158Definition *definition;
    HHS158Instance *instance;
    HHS158Capability *capability;
    HHS158Receipt *definition_receipt;
    HHS158Receipt *instance_receipt;
} SecurityFixture;

static int fixed_value(HHS158Status (*function)(const HHS158Instance *, HHS158MutableByteSpan *),
    const HHS158Instance *instance, char output[HHS158_HASH216_LENGTH + 1u]) {
    HHS158MutableByteSpan span = {(uint8_t *)output, HHS158_HASH216_LENGTH, 0u};
    if (function(instance, &span) != HHS158_OK || span.size_written != HHS158_HASH216_LENGTH) return 0;
    output[HHS158_HASH216_LENGTH] = '\0';
    return 1;
}

static HHS158Status make_fixture(SecurityFixture *fixture, const char *nonce, uint64_t max_receipts,
    uint64_t operations) {
    HHS158ContextConfig context_config;
    HHS158DefinitionDescriptor definition_descriptor;
    HHS158InstanceConfig instance_config;
    HHS158CapabilityRequest capability_request;
    uint64_t shape[2] = {9u, 9u};
    HHS158Status status;
    memset(fixture, 0, sizeof(*fixture));
    INIT(context_config);
    context_config.abi_major = HHS158_ABI_VERSION_MAJOR;
    context_config.abi_minor = HHS158_ABI_VERSION_MINOR;
    context_config.max_definitions = 16u;
    context_config.max_instances = 16u;
    context_config.max_receipts = max_receipts;
    context_config.max_memory_bytes = UINT64_C(16777216);
    context_config.deterministic_epoch_seconds = UINT64_C(1799711799);
    status = hhs158_context_create(&context_config, &fixture->context);
    if (status != HHS158_OK) return status;

    INIT(definition_descriptor);
    definition_descriptor.contract_id = SPAN("HHS-P158-LLABI-NFTC-API");
    definition_descriptor.schema_version = SPAN("1.0.0");
    definition_descriptor.canonical_name = SPAN("PASS158_SECURITY_OBJECT");
    definition_descriptor.object_class = SPAN("NON_FUNGIBLE_TENSOR_CONSTRAINT");
    definition_descriptor.canonical_constraints = SPAN("A==B;O!=Pi;ordered=[x,x,y]");
    definition_descriptor.symbol_table = SPAN("A,B,O,Pi,x,y,ordered");
    definition_descriptor.numeric_policy = SPAN("EXACT_SYMBOLIC");
    definition_descriptor.operator_policy = SPAN("HHS_TYPED_OPERATORS");
    definition_descriptor.authority_root = SPAN("PASS_158_INHERITED_ROOT");
    definition_descriptor.ancestry = SPAN("P154|P155|P156|P156.1|P157");
    definition_descriptor.tensor_rank = 2u;
    definition_descriptor.tensor_shape = shape;
    status = hhs158_definition_register(fixture->context, &definition_descriptor,
        &fixture->definition, &fixture->definition_receipt);
    if (status != HHS158_OK) return status;

    INIT(instance_config);
    instance_config.instance_nonce = SPAN(nonce);
    instance_config.max_vm81_steps = UINT64_C(100000);
    instance_config.max_recursion_depth = 72u;
    instance_config.max_state_bytes = UINT64_C(16777216);
    instance_config.max_receipt_bytes = UINT64_C(1048576);
    instance_config.projection_profile_mask = UINT32_MAX;
    status = hhs158_instance_create(fixture->context, fixture->definition, &instance_config,
        &fixture->instance, &fixture->instance_receipt);
    if (status != HHS158_OK) return status;

    INIT(capability_request);
    capability_request.issuer = SPAN("HHS_PASS158_AUTHORITY");
    capability_request.subject = SPAN("security-test");
    capability_request.application_id = SPAN("org.hhs.pass158.security");
    capability_request.operation_scope = operations;
    capability_request.mutation_scope = HHS158_MUTATION_INSTANCE;
    capability_request.max_vm81_steps = UINT64_C(100000);
    capability_request.issued_at = UINT64_C(1799711700);
    capability_request.expires_at = UINT64_C(1799719999);
    return hhs158_capability_open(fixture->context, &capability_request, &fixture->capability);
}

static void release_fixture(SecurityFixture *fixture) {
    hhs158_context_release(fixture->context);
    memset(fixture, 0, sizeof(*fixture));
}

static HHS158Status bind_rational(SecurityFixture *fixture, const char *symbol, const char *payload,
    HHS158Receipt **out_receipt) {
    HHS158Value value;
    INIT(value);
    value.kind = HHS158_VALUE_RATIONAL;
    value.flags = HHS158_FLAG_AUTHORITATIVE | HHS158_FLAG_IMMUTABLE;
    value.canonical_payload = SPAN(payload);
    return hhs158_instance_bind_authorized(fixture->instance, fixture->capability, SPAN(symbol), &value, out_receipt);
}

static int canonical_receipt_matches(const HHS158Receipt *receipt) {
    char replay_hex[HHS158_MAX_CANONICAL_BYTES * 2u + 1u];
    char canonical[HHS158_MAX_CANONICAL_BYTES];
    char expected[HHS158_HASH72_LENGTH + 1u];
    int written;
    if (!hhs158_hex_encode((const uint8_t *)receipt->replay_material, receipt->replay_material_size,
        replay_hex, sizeof(replay_hex))) return 0;
    written = snprintf(canonical, sizeof(canonical),
        "HHS158_RECEIPT|%d|%s|%s|%s|%s|%s|%s|%s|%llu|%llu|%u|%u|%s",
        (int)receipt->status, receipt->classification, receipt->definition_id, receipt->instance_id,
        receipt->transition_id, receipt->pre_state_root, receipt->post_state_root,
        receipt->opcode_trace_root, (unsigned long long)receipt->vm81_steps,
        (unsigned long long)receipt->witness_flags, receipt->lifecycle_state, receipt->committed, replay_hex);
    if (written < 0 || (size_t)written >= sizeof(canonical)) return 0;
    hhs158_hash72_bytes(canonical, (size_t)written, expected);
    return strcmp(expected, receipt->receipt_id) == 0;
}

static int test_binding_authority_and_receipt(void) {
    SecurityFixture fixture;
    HHS158Value value;
    HHS158Receipt *receipt = NULL;
    char before[HHS158_HASH216_LENGTH + 1u];
    char after[HHS158_HASH216_LENGTH + 1u];
    REQUIRE(make_fixture(&fixture, "binding-security", 64u,
        HHS158_CAP_BIND | HHS158_CAP_VALIDATE | HHS158_CAP_EXECUTE | HHS158_CAP_COMMIT | HHS158_CAP_SERIALIZE) == HHS158_OK);
    REQUIRE(fixed_value(hhs158_instance_state_root, fixture.instance, before));
    INIT(value);
    value.kind = HHS158_VALUE_RATIONAL;
    value.flags = HHS158_FLAG_AUTHORITATIVE | HHS158_FLAG_IMMUTABLE;
    value.canonical_payload = SPAN("1/3");
    REQUIRE(hhs158_instance_bind(fixture.instance, SPAN("x"), &value) == HHS158_CAPABILITY_REQUIRED);
    REQUIRE(hhs158_instance_bind_authorized(fixture.instance, fixture.capability, SPAN("x"), &value, &receipt) == HHS158_OK);
    REQUIRE(receipt != NULL && receipt->committed == 1u);
    REQUIRE(strcmp(receipt->classification, "HHS_P158_NFT_BINDING_COMMITTED") == 0);
    REQUIRE(canonical_receipt_matches(receipt));
    REQUIRE(fixed_value(hhs158_instance_state_root, fixture.instance, after));
    REQUIRE(strcmp(before, after) != 0);
    REQUIRE(strcmp(after, receipt->post_state_root) == 0);
    release_fixture(&fixture);
    return 1;
}

static int test_context_isolation(void) {
    SecurityFixture left;
    SecurityFixture right;
    HHS158InstanceConfig config;
    HHS158Instance *foreign_instance = NULL;
    HHS158Receipt *receipt = NULL;
    HHS158Value value;
    HHS158CompositionPolicy composition;
    HHS158Instance *composition_inputs[2];
    HHS158Instance *composite = NULL;
    HHS158ReplayOptions replay_options;
    HHS158ReplayResult replay_result;
    REQUIRE(make_fixture(&left, "context-left", 64u, HHS158_CAP_BIND | HHS158_CAP_EXECUTE) == HHS158_OK);
    REQUIRE(make_fixture(&right, "context-right", 64u, HHS158_CAP_BIND | HHS158_CAP_EXECUTE) == HHS158_OK);
    INIT(config);
    config.instance_nonce = SPAN("foreign-definition");
    config.max_vm81_steps = 100000u;
    config.max_recursion_depth = 72u;
    config.max_state_bytes = 16777216u;
    config.max_receipt_bytes = 1048576u;
    REQUIRE(hhs158_instance_create(right.context, left.definition, &config, &foreign_instance, &receipt) ==
        HHS158_CAPABILITY_SCOPE_VIOLATION);
    INIT(value);
    value.kind = HHS158_VALUE_RATIONAL;
    value.flags = HHS158_FLAG_AUTHORITATIVE;
    value.canonical_payload = SPAN("1/3");
    REQUIRE(hhs158_instance_bind_authorized(right.instance, left.capability, SPAN("x"), &value, &receipt) ==
        HHS158_CAPABILITY_SCOPE_VIOLATION);
    composition_inputs[0] = left.instance;
    composition_inputs[1] = right.instance;
    INIT(composition);
    composition.max_dependency_depth = 72u;
    REQUIRE(hhs158_instance_compose(left.context, composition_inputs, 2u, &composition, &composite, &receipt) ==
        HHS158_CAPABILITY_SCOPE_VIOLATION);
    INIT(replay_options);
    replay_options.verify_hash72 = 1u;
    replay_options.verify_hash216 = 1u;
    replay_options.verify_semantic_root = 1u;
    REQUIRE(hhs158_receipt_replay(right.context, left.instance_receipt, &replay_options, &replay_result) ==
        HHS158_CAPABILITY_SCOPE_VIOLATION);
    release_fixture(&right);
    release_fixture(&left);
    return 1;
}

static int test_kernel_audit_and_atomic_commit_failure(void) {
    SecurityFixture audit_fixture;
    SecurityFixture capacity_fixture;
    HHS158Receipt *binding_receipt = NULL;
    HHS158Operation operation;
    HHS158TransitionDescriptor descriptor;
    HHS158Transition *transition = NULL;
    HHS158ExecutionOptions options;
    HHS158ExecutionResult result;
    HHS158Receipt *receipt = NULL;
    char pre_root[HHS158_HASH216_LENGTH + 1u];
    char post_attempt[HHS158_HASH216_LENGTH + 1u];
    uint32_t lifecycle = UINT32_MAX;

    REQUIRE(make_fixture(&audit_fixture, "kernel-audit", 64u,
        HHS158_CAP_EXECUTE | HHS158_CAP_COMMIT) == HHS158_OK);
    REQUIRE(fixed_value(hhs158_instance_state_root, audit_fixture.instance, pre_root));
    INIT(operation);
    operation.opcode = HHS158_OP_BIND_EQ;
    operation.operands = SPAN("A,B");
    INIT(descriptor);
    descriptor.operations = &operation;
    descriptor.operation_count = 1u;
    descriptor.expected_pre_state_root = SPAN(pre_root);
    descriptor.max_vm81_steps = 1000u;
    descriptor.max_recursion_depth = 72u;
    descriptor.max_output_bytes = 1048576u;
    REQUIRE(hhs158_transition_create(audit_fixture.instance, audit_fixture.capability, &descriptor, &transition) == HHS158_OK);
    INIT(options);
    options.max_vm81_steps = 1000u;
    INIT(result);
    REQUIRE(hhs158_transition_execute(transition, &options, &result, &receipt) == HHS158_OK);
    REQUIRE(receipt != NULL);
    REQUIRE(result.vm81_steps >= 72u);
    REQUIRE((result.witness_flags & (W_TRANSPORT_CLOSED | W_ORIENTATION_CLOSED | W_CONSTRAINT_CLOSED | W_CONVERGED)) ==
        (W_TRANSPORT_CLOSED | W_ORIENTATION_CLOSED | W_CONSTRAINT_CLOSED | W_CONVERGED));
    REQUIRE(transition->executed == 1u);
    release_fixture(&audit_fixture);

    transition = NULL;
    receipt = NULL;
    binding_receipt = NULL;
    REQUIRE(make_fixture(&capacity_fixture, "receipt-exhaustion", 4u,
        HHS158_CAP_BIND | HHS158_CAP_EXECUTE | HHS158_CAP_COMMIT) == HHS158_OK);
    REQUIRE(bind_rational(&capacity_fixture, "x", "1/3", &binding_receipt) == HHS158_OK);
    REQUIRE(fixed_value(hhs158_instance_state_root, capacity_fixture.instance, pre_root));
    descriptor.expected_pre_state_root = SPAN(pre_root);
    REQUIRE(hhs158_transition_create(capacity_fixture.instance, capacity_fixture.capability, &descriptor, &transition) == HHS158_OK);
    INIT(options);
    options.atomic_execute_and_commit = 1u;
    options.max_vm81_steps = 1000u;
    INIT(result);
    REQUIRE(hhs158_transition_execute(transition, &options, &result, &receipt) == HHS158_MEMORY_BOUND);
    REQUIRE(receipt == NULL);
    REQUIRE(result.vm81_steps == 0u);
    REQUIRE(transition->executed == 0u);
    REQUIRE(transition->committed == 0u);
    REQUIRE(fixed_value(hhs158_instance_state_root, capacity_fixture.instance, post_attempt));
    REQUIRE(strcmp(pre_root, post_attempt) == 0);
    REQUIRE(hhs158_instance_lifecycle(capacity_fixture.instance, &lifecycle) == HHS158_OK);
    REQUIRE(lifecycle != HHS158_LIFECYCLE_COMMITTED);
    release_fixture(&capacity_fixture);
    return 1;
}

static int serialize_instance(HHS158Instance *instance, uint8_t **out_data, size_t *out_size) {
    HHS158SerializationOptions options;
    HHS158MutableByteSpan output = {0};
    uint8_t *buffer;
    INIT(options);
    options.format = HHS158_SERIALIZE_CANONICAL_JSON;
    options.preserve_unknown_fields = 1u;
    options.max_output_bytes = UINT64_C(1048576);
    if (hhs158_instance_serialize(instance, &options, &output) != HHS158_BUFFER_TOO_SMALL) return 0;
    buffer = (uint8_t *)malloc(output.size_written);
    if (!buffer) return 0;
    output.data = buffer;
    output.capacity = output.size_written;
    if (hhs158_instance_serialize(instance, &options, &output) != HHS158_OK) { free(buffer); return 0; }
    *out_data = buffer;
    *out_size = output.size_written;
    return 1;
}

static int test_large_binding_serialization(void) {
    SecurityFixture fixture;
    HHS158Value value;
    HHS158Receipt *receipt = NULL;
    uint8_t *serialized = NULL;
    size_t serialized_size = 0u;
    char payload[513];
    memset(payload, 'x', sizeof(payload) - 1u);
    payload[sizeof(payload) - 1u] = '\0';
    REQUIRE(make_fixture(&fixture, "large-binding", 64u, HHS158_CAP_BIND | HHS158_CAP_SERIALIZE) == HHS158_OK);
    INIT(value);
    value.kind = HHS158_VALUE_EXPRESSION;
    value.flags = HHS158_FLAG_AUTHORITATIVE | HHS158_FLAG_IMMUTABLE;
    value.canonical_payload = SPAN(payload);
    REQUIRE(hhs158_instance_bind_authorized(fixture.instance, fixture.capability, SPAN("large"), &value, &receipt) == HHS158_OK);
    REQUIRE(serialize_instance(fixture.instance, &serialized, &serialized_size));
    REQUIRE(serialized_size > 1024u);
    free(serialized);
    release_fixture(&fixture);
    return 1;
}

static int forge_binding_payload(const uint8_t *serialized, size_t serialized_size, uint8_t **out_data, size_t *out_size) {
    char *json = NULL;
    char *payload_marker;
    char *payload_end;
    char *hash_marker;
    char *hash_end;
    char *payload_hex = NULL;
    char *body = NULL;
    size_t body_size = 0u;
    char *rational;
    char new_hash[HHS158_HASH216_LENGTH + 1u];
    char *new_payload_hex = NULL;
    char *envelope = NULL;
    int written;
    json = (char *)malloc(serialized_size + 1u);
    if (!json) return 0;
    memcpy(json, serialized, serialized_size);
    json[serialized_size] = '\0';
    payload_marker = strstr(json, "\"payload_hex\":\"");
    hash_marker = strstr(json, "\"object_hash\":\"");
    if (!payload_marker || !hash_marker) goto fail;
    payload_marker += strlen("\"payload_hex\":\"");
    payload_end = strchr(payload_marker, '"');
    hash_marker += strlen("\"object_hash\":\"");
    hash_end = strchr(hash_marker, '"');
    if (!payload_end || !hash_end) goto fail;
    {
        size_t payload_hex_size = (size_t)(payload_end - payload_marker);
        payload_hex = (char *)malloc(payload_hex_size + 1u);
        if (!payload_hex) goto fail;
        memcpy(payload_hex, payload_marker, payload_hex_size);
        payload_hex[payload_hex_size] = '\0';
    }
    body = (char *)malloc(strlen(payload_hex) / 2u + 1u);
    if (!body) goto fail;
    if (hhs158_hex_decode(payload_hex, (uint8_t *)body, strlen(payload_hex) / 2u, &body_size) != HHS158_OK) goto fail;
    body[body_size] = '\0';
    rational = strstr(body, "312f33");
    if (!rational) goto fail;
    rational[1] = '2';
    hhs158_hash216_bytes(body, body_size, new_hash);
    new_payload_hex = (char *)malloc(body_size * 2u + 1u);
    if (!new_payload_hex || !hhs158_hex_encode((const uint8_t *)body, body_size, new_payload_hex, body_size * 2u + 1u)) goto fail;
    envelope = (char *)malloc(body_size * 2u + HHS158_HASH216_LENGTH + 128u);
    if (!envelope) goto fail;
    written = snprintf(envelope, body_size * 2u + HHS158_HASH216_LENGTH + 128u,
        "{\"schema\":\"HHS158_CANONICAL_V1\",\"format\":2,\"payload_hex\":\"%s\",\"object_hash\":\"%s\"}",
        new_payload_hex, new_hash);
    if (written < 0) goto fail;
    *out_data = (uint8_t *)envelope;
    *out_size = (size_t)written;
    free(json); free(payload_hex); free(body); free(new_payload_hex);
    return 1;
fail:
    free(json); free(payload_hex); free(body); free(new_payload_hex); free(envelope);
    return 0;
}

static int test_deserialization_requires_audited_history(void) {
    SecurityFixture fixture;
    HHS158Receipt *binding_receipt = NULL;
    uint8_t *serialized = NULL;
    size_t serialized_size = 0u;
    uint8_t *forged = NULL;
    size_t forged_size = 0u;
    HHS158DeserializationOptions options;
    HHS158Instance *copy = NULL;
    HHS158Receipt *receipt = NULL;
    REQUIRE(make_fixture(&fixture, "deserialize-audit", 64u, HHS158_CAP_BIND | HHS158_CAP_SERIALIZE) == HHS158_OK);
    REQUIRE(bind_rational(&fixture, "x", "1/3", &binding_receipt) == HHS158_OK);
    REQUIRE(serialize_instance(fixture.instance, &serialized, &serialized_size));
    REQUIRE(forge_binding_payload(serialized, serialized_size, &forged, &forged_size));
    INIT(options);
    options.format = HHS158_SERIALIZE_CANONICAL_JSON;
    options.preserve_unknown_fields = 1u;
    options.reject_authority_unknown_fields = 1u;
    REQUIRE(hhs158_instance_deserialize(fixture.context, (HHS158ByteSpan){forged, forged_size},
        &options, &copy, &receipt) == HHS158_HASH72_RECEIPT_MISMATCH);
    free(forged);
    free(serialized);
    release_fixture(&fixture);
    return 1;
}

static int test_deserialization_receipt_failure_is_atomic(void) {
    SecurityFixture fixture;
    HHS158Receipt *binding_receipt = NULL;
    uint8_t *serialized = NULL;
    size_t serialized_size = 0u;
    HHS158DeserializationOptions options;
    HHS158Instance *copy = NULL;
    HHS158Receipt *receipt = NULL;
    size_t instances_before;
    REQUIRE(make_fixture(&fixture, "deserialize-capacity", 3u, HHS158_CAP_BIND | HHS158_CAP_SERIALIZE) == HHS158_OK);
    REQUIRE(bind_rational(&fixture, "x", "1/3", &binding_receipt) == HHS158_OK);
    REQUIRE(serialize_instance(fixture.instance, &serialized, &serialized_size));
    instances_before = fixture.context->instance_count;
    INIT(options);
    options.format = HHS158_SERIALIZE_CANONICAL_JSON;
    options.preserve_unknown_fields = 1u;
    options.reject_authority_unknown_fields = 1u;
    REQUIRE(hhs158_instance_deserialize(fixture.context, (HHS158ByteSpan){serialized, serialized_size},
        &options, &copy, &receipt) == HHS158_MEMORY_BOUND);
    REQUIRE(fixture.context->instance_count == instances_before);
    free(serialized);
    release_fixture(&fixture);
    return 1;
}



static int test_terminal_mutations_require_receipts(void) {
    SecurityFixture fixture;
    HHS158Operation operation;
    HHS158TransitionDescriptor descriptor;
    HHS158Transition *transition = NULL;
    HHS158Receipt *receipt = NULL;
    uint32_t lifecycle = UINT32_MAX;
    char state_root[HHS158_HASH216_LENGTH + 1u];

    REQUIRE(make_fixture(&fixture, "terminal-abort", 2u,
        HHS158_CAP_EXECUTE | HHS158_CAP_COMMIT) == HHS158_OK);
    REQUIRE(fixed_value(hhs158_instance_state_root, fixture.instance, state_root));
    INIT(operation);
    operation.opcode = HHS158_OP_BIND_EQ;
    operation.operands = SPAN("A,B");
    INIT(descriptor);
    descriptor.operations = &operation;
    descriptor.operation_count = 1u;
    descriptor.expected_pre_state_root = SPAN(state_root);
    descriptor.max_vm81_steps = 1000u;
    descriptor.max_recursion_depth = 72u;
    descriptor.max_output_bytes = 1048576u;
    REQUIRE(hhs158_transition_create(fixture.instance, fixture.capability, &descriptor, &transition) == HHS158_OK);
    REQUIRE(hhs158_transition_abort(transition, 7u, &receipt) == HHS158_MEMORY_BOUND);
    REQUIRE(receipt == NULL);
    REQUIRE(transition->aborted == 0u);
    REQUIRE(hhs158_instance_retire(fixture.instance, fixture.capability, &receipt) == HHS158_MEMORY_BOUND);
    REQUIRE(receipt == NULL);
    REQUIRE(hhs158_instance_lifecycle(fixture.instance, &lifecycle) == HHS158_OK);
    REQUIRE(lifecycle != HHS158_LIFECYCLE_RETIRED);
    REQUIRE(hhs158_instance_quarantine(fixture.instance, 9u, &receipt) == HHS158_MEMORY_BOUND);
    REQUIRE(receipt == NULL);
    REQUIRE(hhs158_instance_lifecycle(fixture.instance, &lifecycle) == HHS158_OK);
    REQUIRE(lifecycle != HHS158_LIFECYCLE_QUARANTINED);
    release_fixture(&fixture);
    return 1;
}

static int test_opcode_capabilities_are_enforced(void) {
    SecurityFixture fixture;
    HHS158Operation operation;
    HHS158TransitionDescriptor descriptor;
    HHS158Transition *transition = NULL;
    char state_root[HHS158_HASH216_LENGTH + 1u];
    REQUIRE(make_fixture(&fixture, "opcode-capability", 64u, HHS158_CAP_EXECUTE) == HHS158_OK);
    REQUIRE(fixed_value(hhs158_instance_state_root, fixture.instance, state_root));
    INIT(operation);
    operation.opcode = HHS158_OP_PROJECT_CONTROL;
    operation.operands = SPAN("IEEE754_BINARY64_CONTROL");
    INIT(descriptor);
    descriptor.operations = &operation;
    descriptor.operation_count = 1u;
    descriptor.expected_pre_state_root = SPAN(state_root);
    descriptor.max_vm81_steps = 1000u;
    descriptor.max_recursion_depth = 72u;
    descriptor.max_output_bytes = 1048576u;
    REQUIRE(hhs158_transition_create(fixture.instance, fixture.capability, &descriptor, &transition) ==
        HHS158_CAPABILITY_SCOPE_VIOLATION);
    release_fixture(&fixture);
    return 1;
}

static int test_operand_values_reach_admission_gate(void) {
    SecurityFixture fixture;
    HHS158Operation operation;
    HHS158TransitionDescriptor descriptor;
    HHS158Transition *transition = NULL;
    HHS158ExecutionOptions options;
    HHS158ExecutionResult result;
    HHS158Receipt *receipt = NULL;
    HHS158Receipt *binding_receipt = NULL;
    char state_root[HHS158_HASH216_LENGTH + 1u];
    REQUIRE(make_fixture(&fixture, "operand-audit", 64u,
        HHS158_CAP_BIND | HHS158_CAP_EXECUTE | HHS158_CAP_COMMIT) == HHS158_OK);
    REQUIRE(fixed_value(hhs158_instance_state_root, fixture.instance, state_root));
    INIT(operation);
    operation.opcode = HHS158_OP_BIND_EQ;
    operation.operands = SPAN("1,2");
    INIT(descriptor);
    descriptor.operations = &operation;
    descriptor.operation_count = 1u;
    descriptor.expected_pre_state_root = SPAN(state_root);
    descriptor.max_vm81_steps = 1000u;
    descriptor.max_recursion_depth = 72u;
    descriptor.max_output_bytes = 1048576u;
    REQUIRE(hhs158_transition_create(fixture.instance, fixture.capability, &descriptor, &transition) ==
        HHS158_VM81_ADMISSION_REJECTED);
    operation.operands = SPAN("1,1");
    REQUIRE(hhs158_transition_create(fixture.instance, fixture.capability, &descriptor, &transition) == HHS158_OK);
    INIT(options);
    options.max_vm81_steps = 1000u;
    REQUIRE(hhs158_transition_execute(transition, &options, &result, &receipt) == HHS158_OK);
    REQUIRE(receipt != NULL && result.vm81_steps >= 72u);
    REQUIRE(bind_rational(&fixture, "left", "1/3", &binding_receipt) == HHS158_OK);
    REQUIRE(bind_rational(&fixture, "right", "1/2", &binding_receipt) == HHS158_OK);
    REQUIRE(fixed_value(hhs158_instance_state_root, fixture.instance, state_root));
    descriptor.expected_pre_state_root = SPAN(state_root);
    operation.operands = SPAN("left,right");
    transition = NULL;
    REQUIRE(hhs158_transition_create(fixture.instance, fixture.capability, &descriptor, &transition) ==
        HHS158_VM81_ADMISSION_REJECTED);
    release_fixture(&fixture);
    return 1;
}

static int test_dynamic_values_null_array_is_rejected(void) {
    SecurityFixture fixture;
    HHS158ExecutionInputs inputs;
    HHS158ValidationPolicy policy;
    HHS158ValidationReport report;
    REQUIRE(make_fixture(&fixture, "null-values", 64u, HHS158_CAP_VALIDATE) == HHS158_OK);
    INIT(inputs);
    inputs.values = NULL;
    inputs.value_count = 1u;
    inputs.parser_profile = SPAN("HARMONICODE");
    inputs.source_text = SPAN("x");
    INIT(policy);
    policy.max_recursion_depth = 72u;
    REQUIRE(hhs158_instance_validate_dynamic(fixture.instance, &inputs, &policy, &report) ==
        HHS158_INVALID_ARGUMENT);
    release_fixture(&fixture);
    return 1;
}

static int test_delta_null_payload_is_rejected(void) {
    HHS158Value projected;
    HHS158Value delta;
    HHS158Value normalized;
    INIT(projected);
    INIT(delta);
    INIT(normalized);
    projected.kind = HHS158_VALUE_RATIONAL;
    projected.flags = HHS158_FLAG_AUTHORITATIVE;
    projected.canonical_payload = SPAN("1/3");
    delta.kind = HHS158_VALUE_DELTA_VECTOR;
    delta.flags = HHS158_FLAG_AUTHORITATIVE;
    delta.canonical_payload.data = NULL;
    delta.canonical_payload.size = 8u;
    REQUIRE(hhs158_delta_normalize(&projected, &delta, &normalized) == HHS158_INVALID_ARGUMENT);
    return 1;
}

int main(void) {
    REQUIRE(test_binding_authority_and_receipt());
    REQUIRE(test_context_isolation());
    REQUIRE(test_kernel_audit_and_atomic_commit_failure());
    REQUIRE(test_large_binding_serialization());
    REQUIRE(test_deserialization_requires_audited_history());
    REQUIRE(test_deserialization_receipt_failure_is_atomic());
    REQUIRE(test_terminal_mutations_require_receipts());
    REQUIRE(test_opcode_capabilities_are_enforced());
    REQUIRE(test_operand_values_reach_admission_gate());
    REQUIRE(test_dynamic_values_null_array_is_rejected());
    REQUIRE(test_delta_null_payload_is_rejected());
    puts("{\"classification\":\"HHS_PASS_158_SECURITY_REGRESSIONS_VERIFIED\",\"cases\":11}");
    return 0;
}
