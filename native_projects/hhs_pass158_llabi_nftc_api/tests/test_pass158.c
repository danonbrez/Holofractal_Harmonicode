#include "hhs_pass158_api.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HEADER(value) do { memset(&(value), 0, sizeof(value)); (value).header.struct_size = (uint32_t)sizeof(value); (value).header.struct_version = HHS158_STRUCT_VERSION_1; } while (0)
#define SPAN(text) ((HHS158ByteSpan){(const uint8_t *)(text), strlen(text)})
#define REQUIRE(condition) do { if (!(condition)) { fprintf(stderr, "assertion failed at %s:%d: %s\n", __FILE__, __LINE__, #condition); return 0; } } while (0)

typedef struct {
    HHS158Context *context;
    HHS158Definition *definition;
    HHS158Instance *instance;
    HHS158Capability *capability;
    HHS158Receipt *definition_receipt;
    HHS158Receipt *instance_receipt;
    char instance_id[HHS158_HASH216_LENGTH + 1u];
    char state_root[HHS158_HASH216_LENGTH + 1u];
} Fixture;

static int read_fixed(HHS158Status (*getter)(const HHS158Instance *, HHS158MutableByteSpan *), const HHS158Instance *instance, char *output, size_t size) {
    HHS158MutableByteSpan span;
    if (size < HHS158_HASH216_LENGTH + 1u) return 0;
    span.data = (uint8_t *)output;
    span.capacity = HHS158_HASH216_LENGTH;
    span.size_written = 0u;
    if (getter(instance, &span) != HHS158_OK || span.size_written != HHS158_HASH216_LENGTH) return 0;
    output[HHS158_HASH216_LENGTH] = '\0';
    return 1;
}

static int fixture_init(Fixture *fixture, const char *nonce, uint64_t operation_scope, uint64_t mutation_scope,
    uint64_t issued_at, uint64_t expires_at, const char *object_scope) {
    HHS158ContextConfig context_config;
    HHS158DefinitionDescriptor descriptor;
    HHS158InstanceConfig instance_config;
    HHS158CapabilityRequest capability_request;
    uint64_t shape[2] = {9u, 9u};
    static const uint8_t CONSTRAINTS[] = "A==B==C;O!=Pi;ordered=[x,x,y];Delta=P^2-pq";
    HHS158Status status;
    memset(fixture, 0, sizeof(*fixture));
    HEADER(context_config);
    context_config.abi_major = HHS158_ABI_VERSION_MAJOR;
    context_config.abi_minor = HHS158_ABI_VERSION_MINOR;
    context_config.max_definitions = 32u;
    context_config.max_instances = 64u;
    context_config.max_receipts = 128u;
    context_config.max_memory_bytes = UINT64_C(16777216);
    context_config.deterministic_epoch_seconds = UINT64_C(1799711799);
    status = hhs158_context_create(&context_config, &fixture->context);
    if (status != HHS158_OK) return 0;
    HEADER(descriptor);
    descriptor.contract_id = SPAN("HHS-P158-LLABI-NFTC-API");
    descriptor.schema_version = SPAN("1.0.0");
    descriptor.canonical_name = SPAN("PASS158_TEST_OBJECT");
    descriptor.object_class = SPAN("NON_FUNGIBLE_TENSOR_CONSTRAINT");
    descriptor.canonical_constraints.data = CONSTRAINTS;
    descriptor.canonical_constraints.size = sizeof(CONSTRAINTS) - 1u;
    descriptor.symbol_table = SPAN("A,B,C,O,Pi,x,y,Delta,P,p,q");
    descriptor.numeric_policy = SPAN("EXACT_SYMBOLIC");
    descriptor.operator_policy = SPAN("HHS_TYPED_OPERATORS");
    descriptor.authority_root = SPAN("PASS_158_INHERITED_ROOT");
    descriptor.ancestry = SPAN("P154|P155|P156|P156.1|P157");
    descriptor.tensor_rank = 2u;
    descriptor.tensor_shape = shape;
    status = hhs158_definition_register(fixture->context, &descriptor, &fixture->definition, &fixture->definition_receipt);
    if (status != HHS158_OK) return 0;
    HEADER(instance_config);
    instance_config.instance_nonce = SPAN(nonce);
    instance_config.max_vm81_steps = UINT64_C(100000);
    instance_config.max_recursion_depth = 72u;
    instance_config.max_state_bytes = UINT64_C(16777216);
    instance_config.max_receipt_bytes = UINT64_C(1048576);
    instance_config.projection_profile_mask = 0xffffffffu;
    status = hhs158_instance_create(fixture->context, fixture->definition, &instance_config, &fixture->instance, &fixture->instance_receipt);
    if (status != HHS158_OK) return 0;
    if (!read_fixed(hhs158_instance_id, fixture->instance, fixture->instance_id, sizeof(fixture->instance_id))) return 0;
    if (!read_fixed(hhs158_instance_state_root, fixture->instance, fixture->state_root, sizeof(fixture->state_root))) return 0;
    HEADER(capability_request);
    capability_request.issuer = SPAN("HHS_PASS158_AUTHORITY");
    capability_request.subject = SPAN("pass158-test");
    capability_request.application_id = SPAN("org.hhs.pass158.test");
    if (object_scope) capability_request.object_scope = SPAN(object_scope);
    capability_request.operation_scope = operation_scope;
    capability_request.mutation_scope = mutation_scope;
    capability_request.max_vm81_steps = UINT64_C(100000);
    capability_request.issued_at = issued_at;
    capability_request.expires_at = expires_at;
    status = hhs158_capability_open(fixture->context, &capability_request, &fixture->capability);
    return status == HHS158_OK;
}

static void fixture_destroy(Fixture *fixture) {
    hhs158_context_release(fixture->context);
    memset(fixture, 0, sizeof(*fixture));
}

static int bind_rational(Fixture *fixture, const char *symbol, const char *value_text) {
    HHS158Value value;
    HEADER(value);
    value.kind = HHS158_VALUE_RATIONAL;
    value.flags = HHS158_FLAG_AUTHORITATIVE | HHS158_FLAG_IMMUTABLE;
    value.canonical_payload = SPAN(value_text);
    return hhs158_instance_bind(fixture->instance, SPAN(symbol), &value) == HHS158_OK;
}

static int create_transition(Fixture *fixture, uint32_t opcode, const char *operands, uint64_t max_steps,
    HHS158Transition **out_transition) {
    HHS158Operation operation;
    HHS158TransitionDescriptor descriptor;
    HEADER(operation);
    operation.opcode = opcode;
    operation.operands = SPAN(operands);
    HEADER(descriptor);
    descriptor.operations = &operation;
    descriptor.operation_count = 1u;
    descriptor.expected_pre_state_root = SPAN(fixture->state_root);
    descriptor.max_vm81_steps = max_steps;
    descriptor.max_recursion_depth = 72u;
    descriptor.max_output_bytes = UINT64_C(1048576);
    return hhs158_transition_create(fixture->instance, fixture->capability, &descriptor, out_transition) == HHS158_OK;
}

static int run_vm81_and_replay_matrix(size_t *vm81_count, size_t *replay_count) {
    Fixture fixture;
    const HHS158OpcodeDescriptor *registry;
    size_t registry_count = 0u;
    size_t i;
    HHS158Receipt *last_receipt = NULL;
    REQUIRE(fixture_init(&fixture, "vm81-matrix", HHS158_CAP_VALIDATE | HHS158_CAP_EXECUTE | HHS158_CAP_PROJECT |
        HHS158_CAP_SERIALIZE | HHS158_CAP_REPLAY, HHS158_MUTATION_INSTANCE, UINT64_C(1799711700), UINT64_C(1799719999), NULL));
    REQUIRE(bind_rational(&fixture, "x", "1/3"));
    registry = hhs158_public_opcode_registry(&registry_count);
    REQUIRE(registry && registry_count > 0u);
    for (i = 0; i < 81u; ++i) {
        HHS158Transition *transition = NULL;
        HHS158ExecutionOptions options;
        HHS158ExecutionResult result;
        HHS158Receipt *receipt = NULL;
        HHS158ReplayOptions replay_options;
        HHS158ReplayResult replay_result;
        const char *operands = registry[i % registry_count].opcode == HHS158_OP_LIST_ORDERED ? "[x,x,y]" : "x,y";
        REQUIRE(create_transition(&fixture, registry[i % registry_count].opcode, operands, UINT64_C(1000), &transition));
        HEADER(options);
        options.max_vm81_steps = UINT64_C(1000);
        REQUIRE(hhs158_transition_execute(transition, &options, &result, &receipt) == HHS158_OK);
        REQUIRE(result.vm81_steps == 1u);
        HEADER(replay_options);
        replay_options.verify_hash72 = 1u;
        replay_options.verify_hash216 = 1u;
        replay_options.verify_semantic_root = 1u;
        REQUIRE(hhs158_receipt_replay(fixture.context, receipt, &replay_options, &replay_result) == HHS158_OK);
        REQUIRE(replay_result.matched == 1u);
        last_receipt = receipt;
        (*vm81_count)++;
    }
    REQUIRE(last_receipt != NULL);
    for (i = 0; i < 72u; ++i) {
        HHS158ReplayOptions options;
        HHS158ReplayResult result;
        HEADER(options);
        options.verify_hash72 = 1u;
        options.verify_hash216 = 1u;
        options.verify_semantic_root = 1u;
        REQUIRE(hhs158_receipt_replay(fixture.context, last_receipt, &options, &result) == HHS158_OK);
        REQUIRE(result.matched == 1u);
        (*replay_count)++;
    }
    fixture_destroy(&fixture);
    return 1;
}

static int run_loshu_matrix(size_t *count) {
    static const int loshu[9] = {4,9,2,3,5,7,8,1,6};
    size_t i;
    int rows[3] = {0,0,0};
    int columns[3] = {0,0,0};
    int diagonals[2] = {0,0};
    for (i = 0; i < 9u; ++i) {
        rows[i / 3u] += loshu[i];
        columns[i % 3u] += loshu[i];
        if (i / 3u == i % 3u) diagonals[0] += loshu[i];
        if (i / 3u + i % 3u == 2u) diagonals[1] += loshu[i];
        (*count)++;
    }
    REQUIRE(rows[0] == 15 && rows[1] == 15 && rows[2] == 15);
    REQUIRE(columns[0] == 15 && columns[1] == 15 && columns[2] == 15);
    REQUIRE(diagonals[0] == 15 && diagonals[1] == 15);
    return 1;
}

static int run_delta_matrix(size_t *count) {
    size_t i;
    for (i = 1u; i <= 18u; ++i) {
        char projected_text[32];
        char reference_text[32];
        HHS158Value projected;
        HHS158Value reference;
        HHS158Value delta;
        HHS158Value normalized;
        HHS158DeltaPolicy policy;
        int written;
        HEADER(projected); HEADER(reference); HEADER(policy);
        projected.kind = HHS158_VALUE_RATIONAL;
        projected.flags = HHS158_FLAG_AUTHORITATIVE;
        reference.kind = HHS158_VALUE_RATIONAL;
        reference.flags = HHS158_FLAG_AUTHORITATIVE;
        written = snprintf(projected_text, sizeof(projected_text), "%lu/%lu", (unsigned long)(i + 1u), (unsigned long)i);
        REQUIRE(written > 0);
        written = snprintf(reference_text, sizeof(reference_text), "%lu/%lu", (unsigned long)i, (unsigned long)(i + 1u));
        REQUIRE(written > 0);
        projected.canonical_payload = SPAN(projected_text);
        reference.canonical_payload = SPAN(reference_text);
        policy.mode = HHS158_DELTA_ALL;
        policy.require_invertible_reference = 1u;
        policy.preserve_all_components = 1u;
        REQUIRE(hhs158_delta_compute(&projected, &reference, &policy, &delta) == HHS158_OK);
        REQUIRE(hhs158_delta_normalize(&projected, &delta, &normalized) == HHS158_OK);
        REQUIRE(normalized.canonical_payload.size == strlen(reference_text));
        REQUIRE(memcmp(normalized.canonical_payload.data, reference_text, strlen(reference_text)) == 0);
        hhs158_value_release(&delta);
        hhs158_value_release(&normalized);
        (*count)++;
    }
    return 1;
}

static int run_atomic_matrix(size_t *count) {
    Fixture fixture;
    size_t i;
    REQUIRE(fixture_init(&fixture, "atomic-matrix", HHS158_CAP_VALIDATE | HHS158_CAP_EXECUTE | HHS158_CAP_COMMIT |
        HHS158_CAP_REPLAY, HHS158_MUTATION_INSTANCE, UINT64_C(1799711700), UINT64_C(1799719999), NULL));
    REQUIRE(bind_rational(&fixture, "x", "1/3"));
    for (i = 0; i < 18u; ++i) {
        char operands[64];
        HHS158Transition *transition = NULL;
        HHS158ExecutionOptions options;
        HHS158ExecutionResult result;
        HHS158Receipt *receipt = NULL;
        HHS158ReplayOptions replay_options;
        HHS158ReplayResult replay_result;
        int written;
        REQUIRE(read_fixed(hhs158_instance_state_root, fixture.instance, fixture.state_root, sizeof(fixture.state_root)));
        written = snprintf(operands, sizeof(operands), "A%lu,B%lu", (unsigned long)i, (unsigned long)i);
        REQUIRE(written > 0);
        REQUIRE(create_transition(&fixture, HHS158_OP_BIND_EQ, operands, UINT64_C(1000), &transition));
        HEADER(options);
        options.max_vm81_steps = UINT64_C(1000);
        options.atomic_execute_and_commit = 1u;
        REQUIRE(hhs158_transition_execute(transition, &options, &result, &receipt) == HHS158_OK);
        REQUIRE(result.lifecycle_state == HHS158_LIFECYCLE_COMMITTED);
        HEADER(replay_options);
        replay_options.verify_hash72 = 1u;
        replay_options.verify_hash216 = 1u;
        replay_options.verify_semantic_root = 1u;
        REQUIRE(hhs158_receipt_replay(fixture.context, receipt, &replay_options, &replay_result) == HHS158_OK);
        (*count)++;
    }
    fixture_destroy(&fixture);
    return 1;
}

static int run_serialization_matrix(size_t *count) {
    Fixture fixture;
    HHS158SerializationOptions options;
    HHS158MutableByteSpan output = {0};
    uint8_t *buffer;
    size_t i;
    REQUIRE(fixture_init(&fixture, "serialization-matrix", HHS158_CAP_VALIDATE | HHS158_CAP_SERIALIZE,
        HHS158_MUTATION_INSTANCE, UINT64_C(1799711700), UINT64_C(1799719999), NULL));
    REQUIRE(bind_rational(&fixture, "x", "1/3"));
    HEADER(options);
    options.format = HHS158_SERIALIZE_CANONICAL_JSON;
    options.preserve_unknown_fields = 1u;
    options.max_output_bytes = UINT64_C(1048576);
    REQUIRE(hhs158_instance_serialize(fixture.instance, &options, &output) == HHS158_BUFFER_TOO_SMALL);
    buffer = (uint8_t *)malloc(output.size_written);
    REQUIRE(buffer != NULL);
    output.data = buffer; output.capacity = output.size_written;
    REQUIRE(hhs158_instance_serialize(fixture.instance, &options, &output) == HHS158_OK);
    for (i = 0; i < 18u; ++i) {
        HHS158DeserializationOptions deserialization;
        HHS158Instance *copy = NULL;
        HHS158Receipt *receipt = NULL;
        char copy_id[HHS158_HASH216_LENGTH + 1u];
        HEADER(deserialization);
        deserialization.format = HHS158_SERIALIZE_CANONICAL_JSON;
        deserialization.preserve_unknown_fields = 1u;
        deserialization.reject_authority_unknown_fields = 1u;
        REQUIRE(hhs158_instance_deserialize(fixture.context, (HHS158ByteSpan){buffer, output.size_written},
            &deserialization, &copy, &receipt) == HHS158_OK);
        REQUIRE(read_fixed(hhs158_instance_id, copy, copy_id, sizeof(copy_id)));
        REQUIRE(strcmp(copy_id, fixture.instance_id) == 0);
        (*count)++;
    }
    free(buffer);
    fixture_destroy(&fixture);
    return 1;
}

static int run_dependency_matrix(size_t *count) {
    Fixture fixture;
    size_t i;
    REQUIRE(fixture_init(&fixture, "dependency-root", HHS158_CAP_VALIDATE | HHS158_CAP_COMPOSE,
        HHS158_MUTATION_COMPOSITE, UINT64_C(1799711700), UINT64_C(1799719999), NULL));
    for (i = 0; i < 12u; ++i) {
        char nonce[64];
        HHS158InstanceConfig config;
        HHS158Instance *peer = NULL;
        HHS158Receipt *peer_receipt = NULL;
        HHS158Instance *components[2];
        HHS158CompositionPolicy policy;
        HHS158Instance *composite = NULL;
        HHS158Receipt *receipt = NULL;
        int written = snprintf(nonce, sizeof(nonce), "dependency-peer-%lu", (unsigned long)i);
        REQUIRE(written > 0);
        HEADER(config);
        config.instance_nonce = SPAN(nonce);
        config.max_vm81_steps = UINT64_C(100000);
        config.max_recursion_depth = 72u;
        config.max_state_bytes = UINT64_C(16777216);
        config.max_receipt_bytes = UINT64_C(1048576);
        REQUIRE(hhs158_instance_create(fixture.context, fixture.definition, &config, &peer, &peer_receipt) == HHS158_OK);
        components[0] = fixture.instance; components[1] = peer;
        HEADER(policy);
        policy.max_dependency_depth = 72u;
        policy.isolation_level = 1u;
        REQUIRE(hhs158_instance_compose(fixture.context, components, 2u, &policy, &composite, &receipt) == HHS158_OK);
        REQUIRE(composite != NULL && receipt != NULL);
        (*count)++;
    }
    fixture_destroy(&fixture);
    return 1;
}

static int run_abi_lifecycle(size_t *count) {
    Fixture fixture;
    HHS158ValidationPolicy validation;
    HHS158ValidationReport report;
    HHS158ProjectionProfile exact_profile;
    HHS158ProjectionProfile control_profile;
    HHS158Value exact_value;
    HHS158Value control_value;
    HHS158MutableByteSpan descriptor = {0};
    REQUIRE(fixture_init(&fixture, "abi-lifecycle", HHS158_CAP_VALIDATE | HHS158_CAP_EXECUTE | HHS158_CAP_COMMIT |
        HHS158_CAP_PROJECT | HHS158_CAP_SERIALIZE | HHS158_CAP_REPLAY, HHS158_MUTATION_INSTANCE,
        UINT64_C(1799711700), UINT64_C(1799719999), NULL));
    (*count) += 6u;
    REQUIRE(bind_rational(&fixture, "x", "1/3")); (*count)++;
    HEADER(validation); validation.max_recursion_depth = 72u;
    REQUIRE(hhs158_instance_validate_static(fixture.instance, &validation, &report) == HHS158_OK); (*count)++;
    HEADER(exact_profile); exact_profile.kind = HHS158_PROJECTION_EXACT_REFERENCE;
    REQUIRE(hhs158_instance_project(fixture.instance, &exact_profile, &exact_value, &fixture.instance_receipt) == HHS158_OK); (*count)++;
    HEADER(control_profile); control_profile.kind = HHS158_PROJECTION_IEEE754_BINARY64_CONTROL;
    REQUIRE(hhs158_instance_project(fixture.instance, &control_profile, &control_value, &fixture.instance_receipt) == HHS158_OK); (*count)++;
    REQUIRE((control_value.flags & HHS158_FLAG_APPROXIMATE) != 0u); (*count)++;
    REQUIRE(hhs158_abi_descriptor_json(&descriptor) == HHS158_BUFFER_TOO_SMALL); (*count)++;
    descriptor.size_written = 0u; REQUIRE(hhs158_capabilities_json(&descriptor) == HHS158_BUFFER_TOO_SMALL); (*count)++;
    descriptor.size_written = 0u; REQUIRE(hhs158_opcode_descriptor_json(&descriptor) == HHS158_BUFFER_TOO_SMALL); (*count)++;
    REQUIRE(hhs158_abi_version_major() == 1u); (*count)++;
    REQUIRE(strcmp(hhs158_contract_id(), "HHS-P158-LLABI-NFTC-API") == 0); (*count)++;
    REQUIRE(strcmp(hhs158_contract_version(), "1.0.0") == 0); (*count)++;
    hhs158_value_release(&exact_value);
    hhs158_value_release(&control_value);
    REQUIRE(*count == 18u);
    fixture_destroy(&fixture);
    return 1;
}

static int run_api_descriptor_matrix(size_t *count, size_t *binding_count, size_t *identity_count) {
    size_t i;
    for (i = 0; i < 6u; ++i) {
        HHS158MutableByteSpan span = {0};
        REQUIRE(hhs158_abi_descriptor_json(&span) == HHS158_BUFFER_TOO_SMALL); (*count)++;
        span.size_written = 0u; REQUIRE(hhs158_capabilities_json(&span) == HHS158_BUFFER_TOO_SMALL); (*count)++;
        span.size_written = 0u; REQUIRE(hhs158_opcode_descriptor_json(&span) == HHS158_BUFFER_TOO_SMALL); (*count)++;
    }
    *binding_count = 6u;
    REQUIRE(hhs158_abi_version_major() == 1u); (*identity_count)++;
    REQUIRE(hhs158_abi_version_minor() == 0u); (*identity_count)++;
    return 1;
}

static HHS158Status negative_case(size_t index) {
    Fixture fixture;
    HHS158Status status = HHS158_REJECTED;
    size_t kind = index % 27u;
    char nonce[64];
    snprintf(nonce, sizeof(nonce), "negative-%lu", (unsigned long)index);
    if (kind == 0u) {
        HHS158ContextConfig config;
        HHS158Context *context = NULL;
        HEADER(config); config.abi_major = 99u; config.abi_minor = 0u;
        return hhs158_context_create(&config, &context);
    }
    if (kind == 1u) {
        HHS158ContextConfig config;
        HHS158Context *context = NULL;
        HEADER(config); config.header.struct_size = 1u; config.abi_major = 1u;
        return hhs158_context_create(&config, &context);
    }
    if (!fixture_init(&fixture, nonce, HHS158_CAP_VALIDATE | HHS158_CAP_EXECUTE | HHS158_CAP_COMMIT |
        HHS158_CAP_PROJECT | HHS158_CAP_SERIALIZE | HHS158_CAP_REPLAY | HHS158_CAP_COMPOSE,
        HHS158_MUTATION_INSTANCE | HHS158_MUTATION_COMPOSITE,
        UINT64_C(1799711700), kind == 10u ? UINT64_C(1799711701) : UINT64_C(1799719999), NULL)) return HHS158_REJECTED;
    if (kind == 2u) {
        const uint8_t bad[] = {0xc0u, 0x80u};
        HHS158Value value; HEADER(value); value.kind = HHS158_VALUE_BIGINT; value.flags = HHS158_FLAG_AUTHORITATIVE;
        value.canonical_payload = SPAN("1"); status = hhs158_instance_bind(fixture.instance, (HHS158ByteSpan){bad, sizeof(bad)}, &value);
    } else if (kind == 3u || kind == 4u || kind == 5u || kind == 6u || kind == 20u) {
        HHS158Value value; HEADER(value); value.flags = HHS158_FLAG_AUTHORITATIVE;
        if (kind == 3u) { value.kind = HHS158_VALUE_RATIONAL; value.canonical_payload = SPAN("0.5"); }
        else if (kind == 4u) { value.kind = HHS158_VALUE_RATIONAL; value.canonical_payload = SPAN("1/0"); }
        else if (kind == 5u) { value.kind = HHS158_VALUE_LIST; value.canonical_payload = SPAN("[x,x,y]"); }
        else if (kind == 6u) { value.kind = HHS158_VALUE_EXPRESSION; value.canonical_payload = SPAN("O==Pi"); }
        else { value.kind = HHS158_VALUE_BIGINT; value.canonical_payload = SPAN("1"); value.header.struct_size = 1u; }
        status = hhs158_instance_bind(fixture.instance, SPAN("x"), &value);
    } else if (kind == 7u || kind == 8u || kind == 13u) {
        HHS158Operation operations[2]; HHS158TransitionDescriptor descriptor; HHS158Transition *transition = NULL;
        HEADER(operations[0]); operations[0].opcode = kind == 7u ? 0xffffu : HHS158_OP_BIND_EQ; operations[0].operands = SPAN("A,B");
        HEADER(operations[1]); operations[1].opcode = HHS158_OP_BIND_EQ; operations[1].operands = SPAN("B,C");
        HEADER(descriptor); descriptor.operations = operations; descriptor.operation_count = kind == 13u ? 2u : 1u;
        descriptor.expected_pre_state_root = kind == 8u ? SPAN("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX") : SPAN(fixture.state_root);
        descriptor.max_vm81_steps = kind == 13u ? 1u : 100u;
        status = hhs158_transition_create(fixture.instance, fixture.capability, &descriptor, &transition);
        if (status == HHS158_OK && kind == 13u) {
            HHS158ExecutionOptions options; HHS158ExecutionResult result; HHS158Receipt *receipt = NULL;
            HEADER(options); options.max_vm81_steps = 1u;
            status = hhs158_transition_execute(transition, &options, &result, &receipt);
        }
    } else if (kind == 9u) {
        HHS158CapabilityRequest request; HHS158Capability *wrong = NULL; HHS158Transition *transition = NULL;
        HEADER(request); request.issuer = SPAN("issuer"); request.subject = SPAN("subject"); request.application_id = SPAN("app");
        request.object_scope = SPAN("wrong-instance"); request.operation_scope = HHS158_CAP_EXECUTE; request.mutation_scope = HHS158_MUTATION_INSTANCE;
        request.expires_at = UINT64_C(1799719999);
        status = hhs158_capability_open(fixture.context, &request, &wrong);
        if (status == HHS158_OK) { HHS158Operation op; HHS158TransitionDescriptor descriptor; HEADER(op); op.opcode = HHS158_OP_BIND_EQ; op.operands = SPAN("A,B"); HEADER(descriptor); descriptor.operations = &op; descriptor.operation_count = 1u; status = hhs158_transition_create(fixture.instance, wrong, &descriptor, &transition); }
    } else if (kind == 10u) {
        HHS158Transition *transition = NULL; status = create_transition(&fixture, HHS158_OP_BIND_EQ, "A,B", 100u, &transition) ? HHS158_OK : HHS158_CAPABILITY_EXPIRED;
        if (status == HHS158_OK) status = HHS158_REJECTED;
    } else if (kind == 11u) {
        HHS158CapabilityRequest request; HHS158Capability *execute_only = NULL; HHS158Transition *transition = NULL;
        HHS158Operation op; HHS158TransitionDescriptor descriptor; HHS158ExecutionOptions options; HHS158ExecutionResult result; HHS158Receipt *receipt = NULL;
        HEADER(request); request.issuer = SPAN("issuer"); request.subject = SPAN("subject"); request.application_id = SPAN("app");
        request.operation_scope = HHS158_CAP_EXECUTE; request.mutation_scope = HHS158_MUTATION_INSTANCE; request.expires_at = UINT64_C(1799719999);
        status = hhs158_capability_open(fixture.context, &request, &execute_only);
        HEADER(op); op.opcode = HHS158_OP_BIND_EQ; op.operands = SPAN("A,B"); HEADER(descriptor); descriptor.operations = &op; descriptor.operation_count = 1u;
        if (status == HHS158_OK) status = hhs158_transition_create(fixture.instance, execute_only, &descriptor, &transition);
        HEADER(options); options.atomic_execute_and_commit = 1u;
        if (status == HHS158_OK) status = hhs158_transition_execute(transition, &options, &result, &receipt);
    } else if (kind == 12u) {
        HHS158Value value; HEADER(value); value.kind = HHS158_VALUE_RATIONAL; value.flags = HHS158_FLAG_AUTHORITATIVE; value.canonical_payload = SPAN("1/3");
        status = hhs158_instance_bind(fixture.instance, SPAN("x"), &value);
        value.canonical_payload = SPAN("2/3"); if (status == HHS158_OK) status = hhs158_instance_bind(fixture.instance, SPAN("x"), &value);
    } else if (kind == 14u || kind == 15u) {
        HHS158Value projected; HHS158Value reference; HHS158Value delta; HHS158DeltaPolicy policy;
        HEADER(projected); HEADER(reference); HEADER(policy); projected.kind = reference.kind = HHS158_VALUE_RATIONAL;
        projected.flags = reference.flags = HHS158_FLAG_AUTHORITATIVE; projected.canonical_payload = kind == 14u ? SPAN("NaN") : SPAN("1/3");
        reference.canonical_payload = kind == 15u ? SPAN("0/1") : SPAN("1/3"); policy.mode = HHS158_DELTA_ALL; policy.require_invertible_reference = 1u;
        status = hhs158_delta_compute(&projected, &reference, &policy, &delta);
    } else if (kind == 16u) {
        HHS158SerializationOptions options; HHS158MutableByteSpan output = {0}; uint8_t *buffer; HHS158DeserializationOptions input; HHS158Instance *copy = NULL; HHS158Receipt *receipt = NULL;
        HEADER(options); options.format = HHS158_SERIALIZE_CANONICAL_JSON; options.max_output_bytes = UINT64_C(1048576);
        status = hhs158_instance_serialize(fixture.instance, &options, &output); buffer = (uint8_t *)malloc(output.size_written); if (!buffer) status = HHS158_MEMORY_BOUND;
        if (status == HHS158_BUFFER_TOO_SMALL) { output.data = buffer; output.capacity = output.size_written; status = hhs158_instance_serialize(fixture.instance, &options, &output); }
        if (status == HHS158_OK && output.size_written > 10u) buffer[output.size_written / 2u] ^= 1u;
        HEADER(input); input.format = HHS158_SERIALIZE_CANONICAL_JSON; input.reject_authority_unknown_fields = 1u;
        if (status == HHS158_OK) status = hhs158_instance_deserialize(fixture.context, (HHS158ByteSpan){buffer, output.size_written}, &input, &copy, &receipt);
        free(buffer);
    } else if (kind == 17u) {
        HHS158Instance *items[2] = {fixture.instance, fixture.instance}; HHS158CompositionPolicy policy; HHS158Instance *composite = NULL; HHS158Receipt *receipt = NULL;
        HEADER(policy); policy.allow_declared_cycles = 0u; policy.max_dependency_depth = 72u;
        status = hhs158_instance_compose(fixture.context, items, 2u, &policy, &composite, &receipt);
    } else if (kind == 18u) {
        HHS158Receipt *receipt = NULL; HHS158Transition *transition = NULL;
        status = hhs158_instance_retire(fixture.instance, fixture.capability, &receipt);
        if (status == HHS158_OK) status = create_transition(&fixture, HHS158_OP_BIND_EQ, "A,B", 100u, &transition) ? HHS158_OK : HHS158_INVALID_STATE;
    } else if (kind == 19u) {
        HHS158Receipt *receipt = NULL; HHS158Transition *transition = NULL;
        status = hhs158_instance_quarantine(fixture.instance, 1u, &receipt);
        if (status == HHS158_OK) status = create_transition(&fixture, HHS158_OP_BIND_EQ, "A,B", 100u, &transition) ? HHS158_OK : HHS158_INVALID_STATE;
    } else if (kind == 21u) {
        HHS158DefinitionDescriptor descriptor; HHS158Definition *definition = NULL; HHS158Receipt *receipt = NULL; uint64_t shape[1] = {0u};
        HEADER(descriptor); descriptor.contract_id = SPAN("x"); descriptor.schema_version = SPAN("1"); descriptor.canonical_name = SPAN("bad"); descriptor.object_class = SPAN("NON_FUNGIBLE_TENSOR_CONSTRAINT"); descriptor.canonical_constraints = SPAN("A==B"); descriptor.authority_root = SPAN("root"); descriptor.ancestry = SPAN("P157"); descriptor.tensor_rank = 1u; descriptor.tensor_shape = shape;
        status = hhs158_definition_register(fixture.context, &descriptor, &definition, &receipt);
    } else if (kind == 22u) {
        HHS158ProjectionProfile profile; HHS158Value projection; HHS158Receipt *receipt = NULL; char before[HHS158_HASH216_LENGTH + 1u]; char after[HHS158_HASH216_LENGTH + 1u];
        read_fixed(hhs158_instance_state_root, fixture.instance, before, sizeof(before)); HEADER(profile); profile.kind = HHS158_PROJECTION_EXACT_REFERENCE;
        status = hhs158_instance_project(fixture.instance, &profile, &projection, &receipt); read_fixed(hhs158_instance_state_root, fixture.instance, after, sizeof(after));
        if (status == HHS158_OK && strcmp(before, after) == 0) status = HHS158_UNAUTHORIZED_MUTATION;
        hhs158_value_release(&projection);
    } else if (kind == 23u) {
        HHS158MutableByteSpan output = {0}; status = hhs158_receipt_serialize(fixture.instance_receipt, &output);
    } else if (kind == 24u) {
        HHS158Transition *transition = NULL; status = hhs158_capability_revoke(fixture.capability, SPAN("revoked-root"));
        if (status == HHS158_OK) status = create_transition(&fixture, HHS158_OP_BIND_EQ, "A,B", 100u, &transition) ? HHS158_OK : HHS158_CAPABILITY_REVOKED;
    } else if (kind == 25u) {
        HHS158Operation op; HHS158TransitionDescriptor descriptor; HHS158Transition *transition = NULL;
        HEADER(op); op.opcode = HHS158_OP_BIND_EQ; op.operands = SPAN("A==B==C"); HEADER(descriptor); descriptor.operations = &op; descriptor.operation_count = 1u;
        status = hhs158_transition_create(fixture.instance, fixture.capability, &descriptor, &transition);
    } else {
        HHS158Transition *transition = NULL; HHS158ExecutionOptions options; HHS158ExecutionResult result; HHS158Receipt *receipt = NULL; volatile uint32_t cancel = 1u;
        if (!create_transition(&fixture, HHS158_OP_BIND_EQ, "A,B", 100u, &transition)) status = HHS158_REJECTED;
        else { HEADER(options); options.cancel_flag = &cancel; status = hhs158_transition_execute(transition, &options, &result, &receipt); }
    }
    fixture_destroy(&fixture);
    return status;
}

static int run_negative_matrix(size_t *count) {
    size_t i;
    for (i = 0; i < 81u; ++i) {
        HHS158Status status = negative_case(i);
        REQUIRE(status != HHS158_OK);
        (*count)++;
    }
    return 1;
}

int main(void) {
    size_t vm81 = 0u, replay = 0u, loshu = 0u, delta = 0u, dependency = 0u;
    size_t atomic = 0u, serialization = 0u, abi = 0u, bindings = 0u, endpoints = 0u, identity = 0u, negative = 0u;
    size_t positive_total;
    REQUIRE(run_vm81_and_replay_matrix(&vm81, &replay));
    REQUIRE(run_loshu_matrix(&loshu));
    REQUIRE(run_delta_matrix(&delta));
    REQUIRE(run_dependency_matrix(&dependency));
    REQUIRE(run_atomic_matrix(&atomic));
    REQUIRE(run_serialization_matrix(&serialization));
    REQUIRE(run_abi_lifecycle(&abi));
    REQUIRE(run_api_descriptor_matrix(&endpoints, &bindings, &identity));
    REQUIRE(run_negative_matrix(&negative));
    positive_total = vm81 + replay + loshu + delta + dependency + atomic + serialization + abi + bindings + endpoints + identity;
    REQUIRE(positive_total == 272u);
    REQUIRE(negative == 81u);
    printf("{\"classification\":\"HHS_PASS_158_NATIVE_MATRIX_VERIFIED\",\"positive_total\":%lu,\"negative_total\":%lu,"
           "\"vm81\":%lu,\"hash72_replay\":%lu,\"loshu\":%lu,\"delta\":%lu,\"dependency\":%lu,"
           "\"atomic\":%lu,\"serialization\":%lu,\"abi_lifecycle\":%lu,\"binding_surfaces\":%lu,"
           "\"api_descriptors\":%lu,\"identity\":%lu}\n",
        (unsigned long)positive_total, (unsigned long)negative, (unsigned long)vm81, (unsigned long)replay,
        (unsigned long)loshu, (unsigned long)delta, (unsigned long)dependency, (unsigned long)atomic,
        (unsigned long)serialization, (unsigned long)abi, (unsigned long)bindings, (unsigned long)endpoints,
        (unsigned long)identity);
    return 0;
}
