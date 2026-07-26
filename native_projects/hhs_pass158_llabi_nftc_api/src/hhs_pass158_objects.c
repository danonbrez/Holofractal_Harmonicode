#include "hhs_pass158_internal.h"

#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static HHS158Status copy_span_text(HHS158ByteSpan span, char *output, size_t capacity, int require_utf8) {
    if (!output || !capacity) return HHS158_INVALID_ARGUMENT;
    if (span.size >= capacity || (span.size && !span.data)) return HHS158_OUTPUT_BOUND;
    if (require_utf8 && !hhs158_utf8_valid(span)) return HHS158_INVALID_UTF8;
    if (span.size) memcpy(output, span.data, span.size);
    output[span.size] = '\0';
    return HHS158_OK;
}

static int context_valid(const HHS158Context *context) {
    return context && context->magic == HHS158_CONTEXT_MAGIC && !context->released;
}

static int definition_valid(const HHS158Definition *definition) {
    return definition && definition->magic == HHS158_DEFINITION_MAGIC && definition->context && context_valid(definition->context);
}

static int instance_valid(const HHS158Instance *instance) {
    return instance && instance->magic == HHS158_INSTANCE_MAGIC && !instance->released && instance->context && context_valid(instance->context);
}

static int value_contains_decimal(const HHS158Value *value) {
    size_t i;
    if (!value || !value->canonical_payload.data) return 0;
    for (i = 0; i < value->canonical_payload.size; ++i) {
        if (value->canonical_payload.data[i] == '.') return 1;
    }
    return 0;
}

static HHS158Status rational_payload_validate(const HHS158Value *value) {
    char text[HHS158_MAX_OPERAND_BYTES + 1u];
    char *slash;
    long long denominator;
    char *end;
    if (!value || value->canonical_payload.size == 0u || value->canonical_payload.size > HHS158_MAX_OPERAND_BYTES) return HHS158_TYPE_MISMATCH;
    if (value_contains_decimal(value)) return HHS158_EXACT_VALUE_LOSS;
    memcpy(text, value->canonical_payload.data, value->canonical_payload.size);
    text[value->canonical_payload.size] = '\0';
    slash = strchr(text, '/');
    if (!slash || strchr(slash + 1, '/')) return HHS158_TYPE_MISMATCH;
    *slash = '\0';
    if (!text[0] || !slash[1]) return HHS158_TYPE_MISMATCH;
    (void)strtoll(text, &end, 10);
    if (*end != '\0') return HHS158_TYPE_MISMATCH;
    denominator = strtoll(slash + 1, &end, 10);
    if (*end != '\0') return HHS158_TYPE_MISMATCH;
    if (denominator <= 0) return HHS158_TYPE_MISMATCH;
    return HHS158_OK;
}

static HHS158Status validate_bound_value(const HHS158Value *value) {
    if (!value || !hhs158_header_valid(&value->header, sizeof(*value))) return HHS158_STRUCT_SIZE_INVALID;
    if (value->kind > HHS158_VALUE_DELTA_VECTOR) return HHS158_TYPE_MISMATCH;
    if (value->canonical_payload.size > HHS158_MAX_OPERAND_BYTES) return HHS158_OUTPUT_BOUND;
    if (value->canonical_payload.size && !value->canonical_payload.data) return HHS158_INVALID_ARGUMENT;
    if ((value->flags & HHS158_FLAG_PROJECTION) != 0u || (value->flags & HHS158_FLAG_APPROXIMATE) != 0u) return HHS158_EXACT_VALUE_LOSS;
    if ((value->flags & HHS158_FLAG_AUTHORITATIVE) == 0u) return HHS158_TYPE_MISMATCH;
    if (value->kind == HHS158_VALUE_RATIONAL) return rational_payload_validate(value);
    if (value->kind == HHS158_VALUE_BIGINT && value_contains_decimal(value)) return HHS158_EXACT_VALUE_LOSS;
    if (value->kind == HHS158_VALUE_LIST && (value->flags & HHS158_FLAG_ORDERED) == 0u) return HHS158_LIST_TOPOLOGY_LOSS;
    if (value->kind == HHS158_VALUE_EXPRESSION) {
        if (hhs158_span_contains(value->canonical_payload, "O=Pi") || hhs158_span_contains(value->canonical_payload, "O==Pi") ||
            hhs158_span_contains(value->canonical_payload, "O=π") || hhs158_span_contains(value->canonical_payload, "O==π")) return HHS158_PHASE_IDENTITY_VIOLATION;
    }
    return HHS158_OK;
}

HHS158Status hhs158_context_create(const HHS158ContextConfig *config, HHS158Context **out_context) {
    HHS158Context *context;
    HHS158ContextConfig effective;
    if (!out_context) return HHS158_INVALID_ARGUMENT;
    *out_context = NULL;
    memset(&effective, 0, sizeof(effective));
    effective.header.struct_size = (uint32_t)sizeof(effective);
    effective.header.struct_version = HHS158_STRUCT_VERSION_1;
    effective.abi_major = HHS158_ABI_VERSION_MAJOR;
    effective.abi_minor = HHS158_ABI_VERSION_MINOR;
    effective.max_definitions = 64u;
    effective.max_instances = 64u;
    effective.max_receipts = 128u;
    effective.max_memory_bytes = UINT64_C(16777216);
    if (config) {
        if (!hhs158_header_valid(&config->header, sizeof(*config))) return HHS158_STRUCT_SIZE_INVALID;
        if (config->abi_major != HHS158_ABI_VERSION_MAJOR || config->abi_minor > HHS158_ABI_VERSION_MINOR) return HHS158_ABI_VERSION_UNSUPPORTED;
        effective = *config;
        if (!effective.max_definitions) effective.max_definitions = 64u;
        if (!effective.max_instances) effective.max_instances = 64u;
        if (!effective.max_receipts) effective.max_receipts = 128u;
        if (!effective.max_memory_bytes) effective.max_memory_bytes = UINT64_C(16777216);
    }
    if (effective.max_definitions > HHS158_MAX_CONTEXT_OBJECTS || effective.max_instances > HHS158_MAX_CONTEXT_OBJECTS ||
        effective.max_receipts > HHS158_MAX_CONTEXT_OBJECTS) return HHS158_MEMORY_BOUND;
    context = (HHS158Context *)calloc(1u, sizeof(*context));
    if (!context) return HHS158_MEMORY_BOUND;
    context->magic = HHS158_CONTEXT_MAGIC;
    context->config = effective;
    hhs_runtime_init(&context->runtime_template);
    *out_context = context;
    return HHS158_OK;
}

void hhs158_context_release(HHS158Context *context) {
    size_t i;
    if (!context || context->magic != HHS158_CONTEXT_MAGIC || context->released) return;
    context->released = 1u;
    for (i = 0; i < context->transition_count; ++i) free(context->transitions[i]);
    for (i = 0; i < context->capability_count; ++i) free(context->capabilities[i]);
    for (i = 0; i < context->receipt_count; ++i) free(context->receipts[i]);
    for (i = 0; i < context->instance_count; ++i) free(context->instances[i]);
    for (i = 0; i < context->definition_count; ++i) free(context->definitions[i]);
    context->magic = 0u;
    free(context);
}

HHS158Status hhs158_capability_open(HHS158Context *context, const HHS158CapabilityRequest *request, HHS158Capability **out_capability) {
    HHS158Capability *capability;
    char canonical[4096];
    size_t length = 0u;
    HHS158Status status;
    if (!out_capability) return HHS158_INVALID_ARGUMENT;
    *out_capability = NULL;
    if (!context_valid(context)) return HHS158_HANDLE_RELEASED;
    if (!request || !hhs158_header_valid(&request->header, sizeof(*request))) return HHS158_STRUCT_SIZE_INVALID;
    if (context->capability_count >= HHS158_MAX_CONTEXT_OBJECTS) return HHS158_MEMORY_BOUND;
    capability = (HHS158Capability *)calloc(1u, sizeof(*capability));
    if (!capability) return HHS158_MEMORY_BOUND;
    capability->magic = HHS158_CAPABILITY_MAGIC;
    capability->context = context;
    capability->operation_scope = request->operation_scope;
    capability->mutation_scope = request->mutation_scope;
    capability->max_vm81_steps = request->max_vm81_steps ? request->max_vm81_steps : UINT64_C(100000);
    capability->issued_at = request->issued_at;
    capability->expires_at = request->expires_at;
    status = copy_span_text(request->application_id, capability->application_id, sizeof(capability->application_id), 1);
    if (status != HHS158_OK) { free(capability); return status; }
    if (request->object_scope.size) status = copy_span_text(request->object_scope, capability->object_scope, sizeof(capability->object_scope), 1);
    else snprintf(capability->object_scope, sizeof(capability->object_scope), "%s", HHS158_SCOPE_WILDCARD);
    if (status != HHS158_OK) { free(capability); return status; }
    status = hhs158_append_text(canonical, sizeof(canonical), &length, "HHS158_CAPABILITY|");
    if (status == HHS158_OK) status = hhs158_append_span_hex(canonical, sizeof(canonical), &length, "issuer", request->issuer);
    if (status == HHS158_OK) status = hhs158_append_span_hex(canonical, sizeof(canonical), &length, "subject", request->subject);
    if (status == HHS158_OK) status = hhs158_append_span_hex(canonical, sizeof(canonical), &length, "application", request->application_id);
    if (status == HHS158_OK) status = hhs158_append_span_hex(canonical, sizeof(canonical), &length, "scope", request->object_scope);
    if (status != HHS158_OK) { free(capability); return status; }
    {
        char tail[256];
        int written = snprintf(tail, sizeof(tail), "ops:%llu|mutation:%llu|steps:%llu|issued:%llu|expires:%llu|",
            (unsigned long long)request->operation_scope, (unsigned long long)request->mutation_scope,
            (unsigned long long)capability->max_vm81_steps, (unsigned long long)request->issued_at,
            (unsigned long long)request->expires_at);
        if (written < 0 || (size_t)written >= sizeof(tail)) { free(capability); return HHS158_OUTPUT_BOUND; }
        status = hhs158_append_text(canonical, sizeof(canonical), &length, tail);
    }
    if (status != HHS158_OK) { free(capability); return status; }
    hhs158_hash216_bytes(canonical, length, capability->capability_id);
    context->capabilities[context->capability_count++] = capability;
    *out_capability = capability;
    return HHS158_OK;
}

HHS158Status hhs158_capability_revoke(HHS158Capability *capability, HHS158ByteSpan revocation_root) {
    HHS158Status status;
    if (!capability || capability->magic != HHS158_CAPABILITY_MAGIC || capability->released) return HHS158_HANDLE_RELEASED;
    status = copy_span_text(revocation_root, capability->revocation_root, sizeof(capability->revocation_root), 1);
    if (status != HHS158_OK) return status;
    capability->revoked = 1u;
    return HHS158_OK;
}

void hhs158_capability_release(HHS158Capability *capability) {
    if (!capability || capability->magic != HHS158_CAPABILITY_MAGIC) return;
    capability->released = 1u;
}

HHS158Status hhs158_definition_register(HHS158Context *context, const HHS158DefinitionDescriptor *descriptor,
    HHS158Definition **out_definition, HHS158Receipt **out_receipt) {
    HHS158Definition *definition;
    HHS158Receipt *receipt = NULL;
    HHS158Status status;
    size_t length = 0u;
    uint64_t elements = 1u;
    uint32_t i;
    if (!out_definition || !out_receipt) return HHS158_INVALID_ARGUMENT;
    *out_definition = NULL; *out_receipt = NULL;
    if (!context_valid(context)) return HHS158_HANDLE_RELEASED;
    if (!descriptor || !hhs158_header_valid(&descriptor->header, sizeof(*descriptor))) return HHS158_STRUCT_SIZE_INVALID;
    if (!descriptor->contract_id.size || !descriptor->canonical_name.size || !descriptor->object_class.size ||
        !descriptor->canonical_constraints.size || !descriptor->authority_root.size || !descriptor->ancestry.size) return HHS158_INVALID_ARGUMENT;
    if (descriptor->tensor_rank > HHS158_MAX_TENSOR_RANK || (descriptor->tensor_rank && !descriptor->tensor_shape)) return HHS158_TENSOR_SHAPE_MISMATCH;
    if (!hhs158_utf8_valid(descriptor->contract_id) || !hhs158_utf8_valid(descriptor->canonical_name) ||
        !hhs158_utf8_valid(descriptor->object_class) || !hhs158_utf8_valid(descriptor->authority_root) ||
        !hhs158_utf8_valid(descriptor->ancestry)) return HHS158_INVALID_UTF8;
    if (hhs158_span_contains(descriptor->canonical_constraints, "O=Pi") || hhs158_span_contains(descriptor->canonical_constraints, "O==Pi") ||
        hhs158_span_contains(descriptor->canonical_constraints, "O=π") || hhs158_span_contains(descriptor->canonical_constraints, "O==π")) return HHS158_PHASE_IDENTITY_VIOLATION;
    for (i = 0; i < descriptor->tensor_rank; ++i) {
        if (!descriptor->tensor_shape[i] || elements > UINT64_MAX / descriptor->tensor_shape[i]) return HHS158_TENSOR_SHAPE_MISMATCH;
        elements *= descriptor->tensor_shape[i];
    }
    if (context->definition_count >= context->config.max_definitions) return HHS158_MEMORY_BOUND;
    definition = (HHS158Definition *)calloc(1u, sizeof(*definition));
    if (!definition) return HHS158_MEMORY_BOUND;
    definition->magic = HHS158_DEFINITION_MAGIC;
    definition->context = context;
    definition->tensor_rank = descriptor->tensor_rank;
    definition->lifecycle = HHS158_LIFECYCLE_REGISTERED;
    for (i = 0; i < descriptor->tensor_rank; ++i) definition->tensor_shape[i] = descriptor->tensor_shape[i];
    status = copy_span_text(descriptor->canonical_name, definition->canonical_name, sizeof(definition->canonical_name), 1);
    if (status == HHS158_OK) status = copy_span_text(descriptor->object_class, definition->object_class, sizeof(definition->object_class), 1);
    if (status != HHS158_OK) { free(definition); return status; }
    status = hhs158_append_text(definition->canonical, sizeof(definition->canonical), &length, "HHS158_NFT_DEFINITION|");
    if (status == HHS158_OK) status = hhs158_append_span_hex(definition->canonical, sizeof(definition->canonical), &length, "domain", descriptor->contract_id);
    if (status == HHS158_OK) status = hhs158_append_span_hex(definition->canonical, sizeof(definition->canonical), &length, "schema", descriptor->schema_version);
    if (status == HHS158_OK) status = hhs158_append_span_hex(definition->canonical, sizeof(definition->canonical), &length, "name", descriptor->canonical_name);
    if (status == HHS158_OK) status = hhs158_append_span_hex(definition->canonical, sizeof(definition->canonical), &length, "class", descriptor->object_class);
    if (status == HHS158_OK) status = hhs158_append_span_hex(definition->canonical, sizeof(definition->canonical), &length, "constraints", descriptor->canonical_constraints);
    if (status == HHS158_OK) status = hhs158_append_span_hex(definition->canonical, sizeof(definition->canonical), &length, "symbols", descriptor->symbol_table);
    if (status == HHS158_OK) status = hhs158_append_span_hex(definition->canonical, sizeof(definition->canonical), &length, "numeric", descriptor->numeric_policy);
    if (status == HHS158_OK) status = hhs158_append_span_hex(definition->canonical, sizeof(definition->canonical), &length, "operators", descriptor->operator_policy);
    if (status == HHS158_OK) status = hhs158_append_span_hex(definition->canonical, sizeof(definition->canonical), &length, "authority", descriptor->authority_root);
    if (status == HHS158_OK) status = hhs158_append_span_hex(definition->canonical, sizeof(definition->canonical), &length, "ancestry", descriptor->ancestry);
    if (status != HHS158_OK) { free(definition); return status; }
    for (i = 0; i < descriptor->tensor_rank; ++i) {
        char shape[64];
        int written = snprintf(shape, sizeof(shape), "shape:%u:%llu|", i, (unsigned long long)descriptor->tensor_shape[i]);
        if (written < 0 || (size_t)written >= sizeof(shape)) { free(definition); return HHS158_OUTPUT_BOUND; }
        status = hhs158_append_text(definition->canonical, sizeof(definition->canonical), &length, shape);
        if (status != HHS158_OK) { free(definition); return status; }
    }
    definition->canonical_size = length;
    hhs158_hash216_bytes(definition->canonical, length, definition->canonical_hash);
    {
        char identity[HHS158_MAX_CANONICAL_BYTES];
        int written = snprintf(identity, sizeof(identity), "HHS158_DEFINITION_ID|%s|%s", HHS158_CONTRACT_ID, definition->canonical_hash);
        if (written < 0 || (size_t)written >= sizeof(identity)) { free(definition); return HHS158_OUTPUT_BOUND; }
        hhs158_hash216_bytes(identity, (size_t)written, definition->definition_id);
    }
    for (i = 0; i < context->definition_count; ++i) {
        if (strcmp(context->definitions[i]->definition_id, definition->definition_id) == 0) {
            HHS158Definition *existing = context->definitions[i];
            free(definition);
            status = hhs158_make_receipt(context, HHS158_OK, "HHS_P158_NFT_DEFINITION_REGISTERED", existing, NULL,
                NULL, NULL, existing->definition_id, NULL, existing->canonical, existing->canonical_size, 0u, 0u,
                HHS158_LIFECYCLE_REGISTERED, 1u, &receipt);
            if (status != HHS158_OK) return status;
            *out_definition = existing; *out_receipt = receipt;
            return HHS158_OK;
        }
    }
    context->definitions[context->definition_count++] = definition;
    status = hhs158_make_receipt(context, HHS158_OK, "HHS_P158_NFT_DEFINITION_REGISTERED", definition, NULL,
        NULL, NULL, definition->definition_id, NULL, definition->canonical, definition->canonical_size, 0u, 0u,
        HHS158_LIFECYCLE_REGISTERED, 1u, &receipt);
    if (status != HHS158_OK) return status;
    snprintf(definition->origin_receipt, sizeof(definition->origin_receipt), "%s", receipt->receipt_id);
    *out_definition = definition; *out_receipt = receipt;
    return HHS158_OK;
}

HHS158Status hhs158_definition_open(HHS158Context *context, HHS158ByteSpan definition_id, HHS158Definition **out_definition) {
    size_t i;
    if (!out_definition) return HHS158_INVALID_ARGUMENT;
    *out_definition = NULL;
    if (!context_valid(context)) return HHS158_HANDLE_RELEASED;
    if (definition_id.size != HHS158_HASH216_LENGTH || !definition_id.data) return HHS158_INVALID_ARGUMENT;
    for (i = 0; i < context->definition_count; ++i) {
        if (memcmp(context->definitions[i]->definition_id, definition_id.data, HHS158_HASH216_LENGTH) == 0) {
            *out_definition = context->definitions[i];
            return HHS158_OK;
        }
    }
    return HHS158_NOT_FOUND;
}

HHS158Status hhs158_definition_id(const HHS158Definition *definition, HHS158MutableByteSpan *output) {
    if (!definition_valid(definition) || definition->released) return HHS158_HANDLE_RELEASED;
    return hhs158_write_bytes((const uint8_t *)definition->definition_id, HHS158_HASH216_LENGTH, output);
}

void hhs158_definition_release(HHS158Definition *definition) {
    if (!definition || definition->magic != HHS158_DEFINITION_MAGIC) return;
    definition->released = 1u;
}

HHS158Status hhs158_instance_create(HHS158Context *context, HHS158Definition *definition, const HHS158InstanceConfig *config,
    HHS158Instance **out_instance, HHS158Receipt **out_receipt) {
    HHS158Instance *instance;
    HHS158Receipt *receipt = NULL;
    char identity[4096];
    char nonce_hex[513];
    int written;
    HHS158Status status;
    if (!out_instance || !out_receipt) return HHS158_INVALID_ARGUMENT;
    *out_instance = NULL; *out_receipt = NULL;
    if (!context_valid(context) || !definition_valid(definition)) return HHS158_HANDLE_RELEASED;
    if (!config || !hhs158_header_valid(&config->header, sizeof(*config))) return HHS158_STRUCT_SIZE_INVALID;
    if (!config->instance_nonce.size || config->instance_nonce.size > sizeof(instance->nonce) || !config->instance_nonce.data) return HHS158_INVALID_ARGUMENT;
    if (context->instance_count >= context->config.max_instances) return HHS158_MEMORY_BOUND;
    instance = (HHS158Instance *)calloc(1u, sizeof(*instance));
    if (!instance) return HHS158_MEMORY_BOUND;
    instance->magic = HHS158_INSTANCE_MAGIC;
    instance->context = context;
    instance->definition = definition;
    instance->nonce_size = config->instance_nonce.size;
    memcpy(instance->nonce, config->instance_nonce.data, instance->nonce_size);
    instance->max_vm81_steps = config->max_vm81_steps ? config->max_vm81_steps : UINT64_C(100000);
    instance->max_recursion_depth = config->max_recursion_depth ? config->max_recursion_depth : 72u;
    instance->max_state_bytes = config->max_state_bytes ? config->max_state_bytes : UINT64_C(16777216);
    instance->max_receipt_bytes = config->max_receipt_bytes ? config->max_receipt_bytes : UINT64_C(1048576);
    instance->projection_profile_mask = config->projection_profile_mask;
    instance->lifecycle = HHS158_LIFECYCLE_INSTANTIATED;
    if (!hhs158_hex_encode(instance->nonce, instance->nonce_size, nonce_hex, sizeof(nonce_hex))) { free(instance); return HHS158_OUTPUT_BOUND; }
    written = snprintf(identity, sizeof(identity), "HHS158_INSTANCE_ID|%s|%s|%s", definition->definition_id, definition->origin_receipt, nonce_hex);
    if (written < 0 || (size_t)written >= sizeof(identity)) { free(instance); return HHS158_OUTPUT_BOUND; }
    hhs158_hash216_bytes(identity, (size_t)written, instance->instance_id);
    written = snprintf(identity, sizeof(identity), "HHS158_STATE_ROOT|%s|EMPTY", instance->instance_id);
    if (written < 0 || (size_t)written >= sizeof(identity)) { free(instance); return HHS158_OUTPUT_BOUND; }
    hhs158_hash216_bytes(identity, (size_t)written, instance->current_state_root);
    context->instances[context->instance_count++] = instance;
    status = hhs158_make_receipt(context, HHS158_OK, "HHS_P158_NFT_INSTANCE_CONSTRUCTED", definition, instance,
        NULL, NULL, instance->current_state_root, NULL, identity, (size_t)written, 0u, 0u,
        HHS158_LIFECYCLE_INSTANTIATED, 1u, &receipt);
    if (status != HHS158_OK) return status;
    snprintf(instance->origin_receipt, sizeof(instance->origin_receipt), "%s", receipt->receipt_id);
    *out_instance = instance; *out_receipt = receipt;
    return HHS158_OK;
}

HHS158Status hhs158_instance_id(const HHS158Instance *instance, HHS158MutableByteSpan *output) {
    if (!instance_valid(instance)) return HHS158_HANDLE_RELEASED;
    return hhs158_write_bytes((const uint8_t *)instance->instance_id, HHS158_HASH216_LENGTH, output);
}

HHS158Status hhs158_instance_state_root(const HHS158Instance *instance, HHS158MutableByteSpan *output) {
    if (!instance_valid(instance)) return HHS158_HANDLE_RELEASED;
    return hhs158_write_bytes((const uint8_t *)instance->current_state_root, HHS158_HASH216_LENGTH, output);
}

HHS158Status hhs158_instance_lifecycle(const HHS158Instance *instance, uint32_t *out_lifecycle) {
    if (!out_lifecycle) return HHS158_INVALID_ARGUMENT;
    if (!instance_valid(instance)) return HHS158_HANDLE_RELEASED;
    *out_lifecycle = instance->lifecycle;
    return HHS158_OK;
}

HHS158Status hhs158_instance_bind(HHS158Instance *instance, HHS158ByteSpan symbol_name, const HHS158Value *value) {
    HHS158Status status;
    char symbol[HHS158_MAX_SYMBOL_BYTES];
    size_t i;
    if (!instance_valid(instance)) return HHS158_HANDLE_RELEASED;
    if (instance->lifecycle == HHS158_LIFECYCLE_RETIRED || instance->lifecycle == HHS158_LIFECYCLE_QUARANTINED) return HHS158_INVALID_STATE;
    status = copy_span_text(symbol_name, symbol, sizeof(symbol), 1);
    if (status != HHS158_OK) return status;
    if (!symbol[0]) return HHS158_INVALID_ARGUMENT;
    status = validate_bound_value(value);
    if (status != HHS158_OK) return status;
    for (i = 0; i < instance->binding_count; ++i) {
        HHS158BindingRecord *binding = &instance->bindings[i];
        if (strcmp(binding->symbol, symbol) == 0) {
            if (binding->kind == value->kind && binding->flags == (value->flags & ~HHS158_INTERNAL_OWNED_VALUE) &&
                binding->payload_size == value->canonical_payload.size &&
                memcmp(binding->payload, value->canonical_payload.data, binding->payload_size) == 0) return HHS158_OK;
            return HHS158_DUPLICATE_CONFLICTING_BINDING;
        }
    }
    if (instance->binding_count >= HHS158_MAX_BINDINGS) return HHS158_MEMORY_BOUND;
    {
        HHS158BindingRecord *binding = &instance->bindings[instance->binding_count++];
        snprintf(binding->symbol, sizeof(binding->symbol), "%s", symbol);
        binding->kind = value->kind;
        binding->flags = value->flags & ~HHS158_INTERNAL_OWNED_VALUE;
        binding->payload_size = value->canonical_payload.size;
        if (binding->payload_size) memcpy(binding->payload, value->canonical_payload.data, binding->payload_size);
    }
    instance->lifecycle = HHS158_LIFECYCLE_BOUND;
    return HHS158_OK;
}

HHS158Status hhs158_instance_validate_static(HHS158Instance *instance, const HHS158ValidationPolicy *policy,
    HHS158ValidationReport *out_report) {
    size_t i;
    uint64_t checked = 4u;
    HHS158Status status = HHS158_OK;
    if (!instance_valid(instance)) return HHS158_HANDLE_RELEASED;
    if (!policy || !hhs158_header_valid(&policy->header, sizeof(*policy)) || !out_report) return HHS158_STRUCT_SIZE_INVALID;
    if (policy->max_recursion_depth && policy->max_recursion_depth < 1u) status = HHS158_RECURSION_BOUND;
    for (i = 0; status == HHS158_OK && i < instance->binding_count; ++i) {
        HHS158Value view;
        memset(&view, 0, sizeof(view));
        view.header.struct_size = (uint32_t)sizeof(view);
        view.header.struct_version = HHS158_STRUCT_VERSION_1;
        view.kind = instance->bindings[i].kind;
        view.flags = instance->bindings[i].flags;
        view.canonical_payload.data = instance->bindings[i].payload;
        view.canonical_payload.size = instance->bindings[i].payload_size;
        status = validate_bound_value(&view);
        checked++;
    }
    hhs158_fill_validation_report(out_report, status, status == HHS158_OK ? HHS158_LIFECYCLE_VALIDATED : instance->lifecycle,
        checked, status == HHS158_OK ? "HHS_P158_ABI_APPLICATION_BINDING_VALIDATED" : hhs158_status_classification(status), instance->current_state_root);
    return status;
}

static size_t count_token(HHS158ByteSpan source, const char *token) {
    size_t count = 0u;
    size_t token_size = strlen(token);
    size_t i;
    if (!source.data || !token_size) return 0u;
    for (i = 0; i + token_size <= source.size; ++i) if (memcmp(source.data + i, token, token_size) == 0) count++;
    return count;
}

HHS158Status hhs158_instance_validate_dynamic(HHS158Instance *instance, const HHS158ExecutionInputs *inputs,
    const HHS158ValidationPolicy *policy, HHS158ValidationReport *out_report) {
    HHS158Status status;
    HHS158ValidationReport static_report;
    size_t i;
    if (!inputs || !hhs158_header_valid(&inputs->header, sizeof(*inputs))) return HHS158_STRUCT_SIZE_INVALID;
    status = hhs158_instance_validate_static(instance, policy, &static_report);
    if (status != HHS158_OK) { if (out_report) *out_report = static_report; return status; }
    if ((hhs158_span_equal_text(inputs->parser_profile, "C_EXPRESSION") || hhs158_span_equal_text(inputs->parser_profile, "JAVASCRIPT_EXPRESSION") ||
        hhs158_span_equal_text(inputs->parser_profile, "PYTHON_EXPRESSION")) && count_token(inputs->source_text, "==") > 1u) {
        status = HHS158_CONSTRAINT_CHAIN_COLLAPSED;
    }
    if (status == HHS158_OK && (hhs158_span_contains(inputs->source_text, "O==Pi") || hhs158_span_contains(inputs->source_text, "O=Pi") ||
        hhs158_span_contains(inputs->source_text, "O==π") || hhs158_span_contains(inputs->source_text, "O=π"))) status = HHS158_PHASE_IDENTITY_VIOLATION;
    for (i = 0; status == HHS158_OK && i < inputs->value_count; ++i) status = validate_bound_value(&inputs->values[i]);
    hhs158_fill_validation_report(out_report, status, status == HHS158_OK ? HHS158_LIFECYCLE_VALIDATED : instance->lifecycle,
        static_report.checked_constraints + inputs->value_count + 2u,
        status == HHS158_OK ? "HHS_P158_ABI_APPLICATION_BINDING_VALIDATED" : hhs158_status_classification(status), instance->current_state_root);
    return status;
}

HHS158Status hhs158_instance_retire(HHS158Instance *instance, HHS158Capability *capability, HHS158Receipt **out_receipt) {
    HHS158Status status;
    if (!out_receipt) return HHS158_INVALID_ARGUMENT;
    *out_receipt = NULL;
    if (!instance_valid(instance)) return HHS158_HANDLE_RELEASED;
    status = hhs158_capability_check(capability, instance, HHS158_CAP_COMMIT, HHS158_MUTATION_INSTANCE);
    if (status != HHS158_OK) return status;
    instance->lifecycle = HHS158_LIFECYCLE_RETIRED;
    return hhs158_make_receipt(instance->context, HHS158_OK, "HHS_P158_NFT_INSTANCE_RETIRED", instance->definition, instance,
        NULL, instance->current_state_root, instance->current_state_root, NULL, "RETIRE", 6u, 0u, 0u,
        HHS158_LIFECYCLE_RETIRED, 1u, out_receipt);
}

HHS158Status hhs158_instance_quarantine(HHS158Instance *instance, uint32_t reason_code, HHS158Receipt **out_receipt) {
    char material[64];
    int written;
    if (!out_receipt) return HHS158_INVALID_ARGUMENT;
    *out_receipt = NULL;
    if (!instance_valid(instance)) return HHS158_HANDLE_RELEASED;
    instance->lifecycle = HHS158_LIFECYCLE_QUARANTINED;
    written = snprintf(material, sizeof(material), "QUARANTINE:%u", reason_code);
    if (written < 0 || (size_t)written >= sizeof(material)) return HHS158_OUTPUT_BOUND;
    return hhs158_make_receipt(instance->context, HHS158_REJECTED, "HHS_P158_NFT_INTEGRATION_REQUEST_REJECTED", instance->definition, instance,
        NULL, instance->current_state_root, instance->current_state_root, NULL, material, (size_t)written, 0u, 0u,
        HHS158_LIFECYCLE_QUARANTINED, 0u, out_receipt);
}

void hhs158_instance_release(HHS158Instance *instance) {
    if (!instance || instance->magic != HHS158_INSTANCE_MAGIC) return;
    instance->released = 1u;
}
