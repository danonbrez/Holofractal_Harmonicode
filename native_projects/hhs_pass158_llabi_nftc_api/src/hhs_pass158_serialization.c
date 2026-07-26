#include "hhs_pass158_internal.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int context_valid(const HHS158Context *context) {
    return context && context->magic == HHS158_CONTEXT_MAGIC && !context->released;
}

static int instance_valid(const HHS158Instance *instance) {
    return instance && instance->magic == HHS158_INSTANCE_MAGIC && !instance->released && context_valid(instance->context);
}

static int receipt_valid(const HHS158Receipt *receipt) {
    return receipt && receipt->magic == HHS158_RECEIPT_MAGIC && !receipt->released && context_valid(receipt->context);
}

static HHS158Definition *find_definition(HHS158Context *context, const char *definition_id) {
    size_t i;
    for (i = 0; i < context->definition_count; ++i) {
        if (strcmp(context->definitions[i]->definition_id, definition_id) == 0) return context->definitions[i];
    }
    return NULL;
}

static HHS158Status append_binding_body(char *body, size_t capacity, size_t *length, const HHS158BindingRecord *binding) {
    char symbol_hex[HHS158_MAX_SYMBOL_BYTES * 2u + 1u];
    char payload_hex[HHS158_MAX_OPERAND_BYTES * 2u + 1u];
    char header[HHS158_MAX_OPERAND_BYTES * 2u + HHS158_MAX_SYMBOL_BYTES * 2u + 128u];
    int written;
    HHS158Status status;
    if (!hhs158_hex_encode((const uint8_t *)binding->symbol, strlen(binding->symbol), symbol_hex, sizeof(symbol_hex))) return HHS158_OUTPUT_BOUND;
    if (!hhs158_hex_encode(binding->payload, binding->payload_size, payload_hex, sizeof(payload_hex))) return HHS158_OUTPUT_BOUND;
    written = snprintf(header, sizeof(header), "%s,%u,%u,%lu,%s;", symbol_hex, binding->kind, binding->flags,
        (unsigned long)binding->payload_size, payload_hex);
    if (written < 0 || (size_t)written >= sizeof(header)) return HHS158_OUTPUT_BOUND;
    status = hhs158_append_text(body, capacity, length, header);
    return status;
}

HHS158Status hhs158_instance_serialize(HHS158Instance *instance, const HHS158SerializationOptions *options,
    HHS158MutableByteSpan *output) {
    char body[HHS158_MAX_CANONICAL_BYTES];
    char body_hex[HHS158_MAX_CANONICAL_BYTES * 2u + 1u];
    char nonce_hex[513];
    char object_hash[HHS158_HASH216_LENGTH + 1u];
    char envelope[HHS158_MAX_CANONICAL_BYTES * 2u + 1024u];
    size_t length = 0u;
    size_t i;
    HHS158Status status;
    int written;
    if (!instance_valid(instance)) return HHS158_HANDLE_RELEASED;
    if (!options || !hhs158_header_valid(&options->header, sizeof(*options))) return HHS158_STRUCT_SIZE_INVALID;
    if (options->format < HHS158_SERIALIZE_CANONICAL_BINARY || options->format > HHS158_SERIALIZE_TRANSITION_PACKAGE) return HHS158_TYPE_MISMATCH;
    if (!hhs158_hex_encode(instance->nonce, instance->nonce_size, nonce_hex, sizeof(nonce_hex))) return HHS158_OUTPUT_BOUND;
    written = snprintf(body, sizeof(body), "HHS158V1|%s|%s|%s|%s|%u|%llu|%lu|",
        instance->definition->definition_id, instance->instance_id, instance->current_state_root, nonce_hex,
        instance->lifecycle, (unsigned long long)instance->version, (unsigned long)instance->binding_count);
    if (written < 0 || (size_t)written >= sizeof(body)) return HHS158_OUTPUT_BOUND;
    length = (size_t)written;
    for (i = 0; i < instance->binding_count; ++i) {
        status = append_binding_body(body, sizeof(body), &length, &instance->bindings[i]);
        if (status != HHS158_OK) return status;
    }
    hhs158_hash216_bytes(body, length, object_hash);
    if (!hhs158_hex_encode((const uint8_t *)body, length, body_hex, sizeof(body_hex))) return HHS158_OUTPUT_BOUND;
    written = snprintf(envelope, sizeof(envelope),
        "{\"schema\":\"HHS158_CANONICAL_V1\",\"format\":%u,\"payload_hex\":\"%s\",\"object_hash\":\"%s\"}",
        options->format, body_hex, object_hash);
    if (written < 0 || (size_t)written >= sizeof(envelope)) return HHS158_OUTPUT_BOUND;
    if (options->max_output_bytes && (uint64_t)written > options->max_output_bytes) return HHS158_OUTPUT_BOUND;
    return hhs158_write_bytes((const uint8_t *)envelope, (size_t)written, output);
}

static HHS158Status extract_json_string(const char *json, const char *field, char *output, size_t capacity) {
    char marker[128];
    const char *start;
    const char *end;
    int written = snprintf(marker, sizeof(marker), "\"%s\":\"", field);
    size_t size;
    if (written < 0 || (size_t)written >= sizeof(marker)) return HHS158_SERIALIZATION_INVALID;
    start = strstr(json, marker);
    if (!start) return HHS158_SERIALIZATION_INVALID;
    start += strlen(marker);
    end = strchr(start, '"');
    if (!end) return HHS158_SERIALIZATION_INVALID;
    size = (size_t)(end - start);
    if (size >= capacity) return HHS158_OUTPUT_BOUND;
    memcpy(output, start, size);
    output[size] = '\0';
    return HHS158_OK;
}

static char *next_field(char **cursor) {
    char *start;
    char *separator;
    if (!cursor || !*cursor) return NULL;
    start = *cursor;
    separator = strchr(start, '|');
    if (!separator) { *cursor = NULL; return start; }
    *separator = '\0';
    *cursor = separator + 1;
    return start;
}

static HHS158Status parse_bindings(char *text, HHS158Instance *instance, size_t expected_count) {
    size_t count = 0u;
    char *cursor = text;
    while (cursor && *cursor) {
        char *entry = cursor;
        char *end = strchr(entry, ';');
        char *parts[5];
        size_t part_count = 0u;
        char *part_cursor;
        size_t decoded;
        HHS158Status status;
        unsigned long kind;
        unsigned long flags;
        unsigned long payload_size;
        if (!end) return HHS158_SERIALIZATION_INVALID;
        *end = '\0';
        cursor = end + 1;
        part_cursor = entry;
        while (part_count < 5u) {
            char *comma = strchr(part_cursor, ',');
            parts[part_count++] = part_cursor;
            if (!comma) break;
            *comma = '\0';
            part_cursor = comma + 1;
        }
        if (part_count != 5u || count >= HHS158_MAX_BINDINGS) return HHS158_SERIALIZATION_INVALID;
        status = hhs158_hex_decode(parts[0], (uint8_t *)instance->bindings[count].symbol,
            sizeof(instance->bindings[count].symbol) - 1u, &decoded);
        if (status != HHS158_OK) return status;
        instance->bindings[count].symbol[decoded] = '\0';
        kind = strtoul(parts[1], NULL, 10);
        flags = strtoul(parts[2], NULL, 10);
        payload_size = strtoul(parts[3], NULL, 10);
        if (kind > HHS158_VALUE_DELTA_VECTOR || payload_size > HHS158_MAX_OPERAND_BYTES) return HHS158_SERIALIZATION_INVALID;
        status = hhs158_hex_decode(parts[4], instance->bindings[count].payload, sizeof(instance->bindings[count].payload), &decoded);
        if (status != HHS158_OK || decoded != payload_size) return HHS158_SERIALIZATION_INVALID;
        instance->bindings[count].kind = (uint32_t)kind;
        instance->bindings[count].flags = (uint32_t)flags;
        instance->bindings[count].payload_size = decoded;
        count++;
    }
    if (count != expected_count) return HHS158_SERIALIZATION_INVALID;
    instance->binding_count = count;
    return HHS158_OK;
}

static int binding_receipt_matches(const HHS158Receipt *receipt, const HHS158Instance *instance,
    const HHS158BindingRecord *binding, const char *pre_state_root) {
    char payload_hex[HHS158_MAX_OPERAND_BYTES * 2u + 1u];
    char expected[HHS158_MAX_CANONICAL_BYTES];
    int written;
    if (!receipt || !instance || !binding || !pre_state_root) return 0;
    if (!hhs158_hex_encode(binding->payload, binding->payload_size, payload_hex, sizeof(payload_hex))) return 0;
    written = snprintf(expected, sizeof(expected), "HHS158_BIND|%s|%s|%s|%u|%u|%s",
        instance->instance_id, pre_state_root, binding->symbol, binding->kind, binding->flags, payload_hex);
    if (written < 0 || (size_t)written >= sizeof(expected)) return 0;
    return receipt->replay_material_size == (size_t)written &&
        memcmp(receipt->replay_material, expected, (size_t)written) == 0;
}

static int audited_history_reaches(HHS158Context *context, HHS158Instance *instance, const char *target_root) {
    char current_root[HHS158_HASH216_LENGTH + 1u];
    char material[HHS158_HASH216_LENGTH + 64u];
    size_t binding_index = 0u;
    size_t receipt_index;
    int written;
    written = snprintf(material, sizeof(material), "HHS158_STATE_ROOT|%s|EMPTY", instance->instance_id);
    if (written < 0 || (size_t)written >= sizeof(material)) return 0;
    hhs158_hash216_bytes(material, (size_t)written, current_root);
    if (strcmp(current_root, target_root) == 0 && instance->binding_count == 0u) return 1;
    for (receipt_index = 0; receipt_index < context->receipt_count; ++receipt_index) {
        HHS158Receipt *receipt = context->receipts[receipt_index];
        HHS158ReplayOptions options;
        HHS158ReplayResult replay;
        if (!receipt || receipt->released || !receipt->committed) continue;
        if (strcmp(receipt->instance_id, instance->instance_id) != 0) continue;
        if (strcmp(receipt->pre_state_root, current_root) != 0) continue;
        memset(&options, 0, sizeof(options));
        options.header.struct_size = (uint32_t)sizeof(options);
        options.header.struct_version = HHS158_STRUCT_VERSION_1;
        options.verify_hash72 = 1u;
        options.verify_hash216 = 1u;
        options.verify_semantic_root = 1u;
        if (hhs158_receipt_replay(context, receipt, &options, &replay) != HHS158_OK || !replay.matched) return 0;
        if (strcmp(receipt->classification, "HHS_P158_NFT_BINDING_COMMITTED") == 0) {
            if (binding_index >= instance->binding_count ||
                !binding_receipt_matches(receipt, instance, &instance->bindings[binding_index], current_root)) return 0;
            binding_index++;
        }
        snprintf(current_root, sizeof(current_root), "%s", receipt->post_state_root);
        if (strcmp(current_root, target_root) == 0 && binding_index == instance->binding_count) return 1;
    }
    return 0;
}

HHS158Status hhs158_instance_deserialize(HHS158Context *context, HHS158ByteSpan serialized_object,
    const HHS158DeserializationOptions *options, HHS158Instance **out_instance, HHS158Receipt **out_receipt) {
    char *json;
    char payload_hex[HHS158_MAX_CANONICAL_BYTES * 2u + 1u];
    char expected_hash[HHS158_HASH216_LENGTH + 1u];
    char actual_hash[HHS158_HASH216_LENGTH + 1u];
    char body[HHS158_MAX_CANONICAL_BYTES];
    size_t body_size;
    char *cursor;
    char *prefix;
    char *definition_id;
    char *instance_id;
    char *state_root;
    char *nonce_hex;
    char *lifecycle_text;
    char *version_text;
    char *binding_count_text;
    HHS158Definition *definition;
    HHS158Instance *instance;
    HHS158Status status;
    size_t nonce_size;
    size_t binding_count;
    char identity[4096];
    int written;
    if (!out_instance || !out_receipt) return HHS158_INVALID_ARGUMENT;
    *out_instance = NULL; *out_receipt = NULL;
    if (!context_valid(context)) return HHS158_HANDLE_RELEASED;
    if (!options || !hhs158_header_valid(&options->header, sizeof(*options))) return HHS158_STRUCT_SIZE_INVALID;
    if (!serialized_object.data || !serialized_object.size || serialized_object.size > HHS158_MAX_CANONICAL_BYTES * 2u + 1024u) return HHS158_SERIALIZATION_INVALID;
    json = (char *)malloc(serialized_object.size + 1u);
    if (!json) return HHS158_MEMORY_BOUND;
    memcpy(json, serialized_object.data, serialized_object.size);
    json[serialized_object.size] = '\0';
    status = extract_json_string(json, "payload_hex", payload_hex, sizeof(payload_hex));
    if (status == HHS158_OK) status = extract_json_string(json, "object_hash", expected_hash, sizeof(expected_hash));
    if (status != HHS158_OK) { free(json); return status; }
    status = hhs158_hex_decode(payload_hex, (uint8_t *)body, sizeof(body) - 1u, &body_size);
    if (status != HHS158_OK) { free(json); return status; }
    body[body_size] = '\0';
    hhs158_hash216_bytes(body, body_size, actual_hash);
    if (strcmp(actual_hash, expected_hash) != 0) { free(json); return HHS158_HASH216_IDENTITY_MISMATCH; }
    cursor = body;
    prefix = next_field(&cursor);
    definition_id = next_field(&cursor);
    instance_id = next_field(&cursor);
    state_root = next_field(&cursor);
    nonce_hex = next_field(&cursor);
    lifecycle_text = next_field(&cursor);
    version_text = next_field(&cursor);
    binding_count_text = next_field(&cursor);
    if (!prefix || !definition_id || !instance_id || !state_root || !nonce_hex || !lifecycle_text || !version_text || !binding_count_text || !cursor ||
        strcmp(prefix, "HHS158V1") != 0 || strlen(definition_id) != HHS158_HASH216_LENGTH || strlen(instance_id) != HHS158_HASH216_LENGTH ||
        strlen(state_root) != HHS158_HASH216_LENGTH) { free(json); return HHS158_SERIALIZATION_INVALID; }
    definition = find_definition(context, definition_id);
    if (!definition) { free(json); return HHS158_NOT_FOUND; }
    if (context->instance_count >= context->config.max_instances) { free(json); return HHS158_MEMORY_BOUND; }
    instance = (HHS158Instance *)calloc(1u, sizeof(*instance));
    if (!instance) { free(json); return HHS158_MEMORY_BOUND; }
    instance->magic = HHS158_INSTANCE_MAGIC;
    instance->context = context;
    instance->definition = definition;
    status = hhs158_hex_decode(nonce_hex, instance->nonce, sizeof(instance->nonce), &nonce_size);
    if (status != HHS158_OK || !nonce_size) { free(instance); free(json); return HHS158_SERIALIZATION_INVALID; }
    instance->nonce_size = nonce_size;
    written = snprintf(identity, sizeof(identity), "HHS158_INSTANCE_ID|%s|%s|%s", definition->definition_id, definition->origin_receipt, nonce_hex);
    if (written < 0 || (size_t)written >= sizeof(identity)) { free(instance); free(json); return HHS158_OUTPUT_BOUND; }
    hhs158_hash216_bytes(identity, (size_t)written, actual_hash);
    if (strcmp(actual_hash, instance_id) != 0) { free(instance); free(json); return HHS158_HASH216_IDENTITY_MISMATCH; }
    snprintf(instance->instance_id, sizeof(instance->instance_id), "%s", instance_id);
    binding_count = (size_t)strtoul(binding_count_text, NULL, 10);
    if (binding_count > HHS158_MAX_BINDINGS) { free(instance); free(json); return HHS158_SERIALIZATION_INVALID; }
    status = parse_bindings(cursor, instance, binding_count);
    if (status != HHS158_OK) { free(instance); free(json); return status; }
    if (!audited_history_reaches(context, instance, state_root)) {
        free(instance); free(json); return HHS158_HASH72_RECEIPT_MISMATCH;
    }
    snprintf(instance->current_state_root, sizeof(instance->current_state_root), "%s", state_root);
    instance->version = strtoull(version_text, NULL, 10);
    instance->lifecycle = binding_count ? HHS158_LIFECYCLE_BOUND : HHS158_LIFECYCLE_INSTANTIATED;
    instance->max_vm81_steps = UINT64_C(100000);
    instance->max_recursion_depth = 72u;
    instance->max_state_bytes = UINT64_C(16777216);
    instance->max_receipt_bytes = UINT64_C(1048576);
    status = hhs158_make_receipt(context, HHS158_OK, "HHS_P158_NFT_INSTANCE_DESERIALIZED_UNPRIVILEGED",
        definition, instance, NULL, state_root, state_root, NULL, body, body_size, 0u, 0u,
        instance->lifecycle, 0u, out_receipt);
    if (status != HHS158_OK) { free(instance); free(json); return status; }
    context->instances[context->instance_count++] = instance;
    free(json);
    *out_instance = instance;
    return HHS158_OK;
}

HHS158Status hhs158_instance_compose(HHS158Context *context, HHS158Instance *const *instances, size_t instance_count,
    const HHS158CompositionPolicy *policy, HHS158Instance **out_composite, HHS158Receipt **out_receipt) {
    char constraints[8192];
    size_t length = 0u;
    size_t i;
    size_t j;
    HHS158Status status;
    HHS158DefinitionDescriptor descriptor;
    HHS158Definition *definition;
    HHS158Receipt *definition_receipt;
    HHS158InstanceConfig config;
    uint64_t shape[2];
    char nonce[HHS158_HASH216_LENGTH + 1u];
    static const uint8_t CONTRACT[] = HHS158_CONTRACT_ID;
    static const uint8_t VERSION[] = HHS158_CONTRACT_VERSION;
    static const uint8_t NAME[] = "COMPOSITE_NON_FUNGIBLE_TENSOR_CONSTRAINT";
    static const uint8_t CLASS[] = "NON_FUNGIBLE_TENSOR_CONSTRAINT";
    static const uint8_t NUMERIC[] = "EXACT_SYMBOLIC";
    static const uint8_t OPERATORS[] = "HHS_TYPED_OPERATORS";
    static const uint8_t AUTHORITY[] = "PASS_158_INHERITED_ROOT";
    static const uint8_t ANCESTRY[] = "P154|P155|P156|P156.1|P157|P158";
    if (!out_composite || !out_receipt) return HHS158_INVALID_ARGUMENT;
    *out_composite = NULL; *out_receipt = NULL;
    if (!context_valid(context)) return HHS158_HANDLE_RELEASED;
    if (!policy || !hhs158_header_valid(&policy->header, sizeof(*policy))) return HHS158_STRUCT_SIZE_INVALID;
    if (!instances || instance_count < 2u || instance_count > 16u) return HHS158_INVALID_ARGUMENT;
    status = hhs158_append_text(constraints, sizeof(constraints), &length, "COMPOSE[");
    for (i = 0; status == HHS158_OK && i < instance_count; ++i) {
        if (!instance_valid(instances[i])) return HHS158_HANDLE_RELEASED;
        for (j = i + 1u; j < instance_count; ++j) {
            if (instances[i] == instances[j] && !policy->allow_declared_cycles) return HHS158_DEPENDENCY_CYCLE_UNBOUNDED;
        }
        if (i) status = hhs158_append_text(constraints, sizeof(constraints), &length, ",");
        if (status == HHS158_OK) status = hhs158_append_text(constraints, sizeof(constraints), &length, instances[i]->instance_id);
    }
    if (status == HHS158_OK) status = hhs158_append_text(constraints, sizeof(constraints), &length, "]");
    if (status != HHS158_OK) return status;
    memset(&descriptor, 0, sizeof(descriptor));
    descriptor.header.struct_size = (uint32_t)sizeof(descriptor);
    descriptor.header.struct_version = HHS158_STRUCT_VERSION_1;
    descriptor.contract_id.data = CONTRACT; descriptor.contract_id.size = sizeof(CONTRACT) - 1u;
    descriptor.schema_version.data = VERSION; descriptor.schema_version.size = sizeof(VERSION) - 1u;
    descriptor.canonical_name.data = NAME; descriptor.canonical_name.size = sizeof(NAME) - 1u;
    descriptor.object_class.data = CLASS; descriptor.object_class.size = sizeof(CLASS) - 1u;
    descriptor.canonical_constraints.data = (const uint8_t *)constraints; descriptor.canonical_constraints.size = length;
    descriptor.numeric_policy.data = NUMERIC; descriptor.numeric_policy.size = sizeof(NUMERIC) - 1u;
    descriptor.operator_policy.data = OPERATORS; descriptor.operator_policy.size = sizeof(OPERATORS) - 1u;
    descriptor.authority_root.data = AUTHORITY; descriptor.authority_root.size = sizeof(AUTHORITY) - 1u;
    descriptor.ancestry.data = ANCESTRY; descriptor.ancestry.size = sizeof(ANCESTRY) - 1u;
    shape[0] = (uint64_t)instance_count; shape[1] = 1u;
    descriptor.tensor_rank = 2u; descriptor.tensor_shape = shape;
    status = hhs158_definition_register(context, &descriptor, &definition, &definition_receipt);
    if (status != HHS158_OK) return status;
    hhs158_hash216_bytes(constraints, length, nonce);
    memset(&config, 0, sizeof(config));
    config.header.struct_size = (uint32_t)sizeof(config);
    config.header.struct_version = HHS158_STRUCT_VERSION_1;
    config.instance_nonce.data = (const uint8_t *)nonce;
    config.instance_nonce.size = HHS158_HASH216_LENGTH;
    config.max_vm81_steps = UINT64_C(100000);
    config.max_recursion_depth = policy->max_dependency_depth ? policy->max_dependency_depth : 72u;
    config.max_state_bytes = UINT64_C(16777216);
    config.max_receipt_bytes = UINT64_C(1048576);
    (void)definition_receipt;
    return hhs158_instance_create(context, definition, &config, out_composite, out_receipt);
}

HHS158Status hhs158_receipt_serialize(HHS158Receipt *receipt, HHS158MutableByteSpan *output) {
    char json[HHS158_MAX_CANONICAL_BYTES * 2u + 2048u];
    char replay_hex[HHS158_MAX_CANONICAL_BYTES * 2u + 1u];
    int written;
    if (!receipt_valid(receipt)) return HHS158_HANDLE_RELEASED;
    if (!hhs158_hex_encode((const uint8_t *)receipt->replay_material, receipt->replay_material_size, replay_hex, sizeof(replay_hex))) return HHS158_OUTPUT_BOUND;
    written = snprintf(json, sizeof(json),
        "{\"schema\":\"HHS158_EXECUTION_RECEIPT_V1\",\"receipt_id\":\"%s\",\"object_root\":\"%s\","
        "\"transition_id\":\"%s\",\"definition_id\":\"%s\",\"instance_id\":\"%s\","
        "\"pre_state_root\":\"%s\",\"post_state_root\":\"%s\",\"opcode_trace_root\":\"%s\","
        "\"status\":%d,\"classification\":\"%s\",\"vm81_steps\":%llu,\"witness_flags\":%llu,"
        "\"lifecycle_state\":%u,\"committed\":%u,\"replay_material_hex\":\"%s\"}",
        receipt->receipt_id, receipt->object_root, receipt->transition_id, receipt->definition_id, receipt->instance_id,
        receipt->pre_state_root, receipt->post_state_root, receipt->opcode_trace_root, (int)receipt->status,
        receipt->classification, (unsigned long long)receipt->vm81_steps, (unsigned long long)receipt->witness_flags,
        receipt->lifecycle_state, receipt->committed, replay_hex);
    if (written < 0 || (size_t)written >= sizeof(json)) return HHS158_OUTPUT_BOUND;
    return hhs158_write_bytes((const uint8_t *)json, (size_t)written, output);
}

HHS158Status hhs158_receipt_hash72(const HHS158Receipt *receipt, HHS158MutableByteSpan *output) {
    if (!receipt_valid(receipt)) return HHS158_HANDLE_RELEASED;
    return hhs158_write_bytes((const uint8_t *)receipt->receipt_id, HHS158_HASH72_LENGTH, output);
}

HHS158Status hhs158_receipt_hash216(const HHS158Receipt *receipt, HHS158MutableByteSpan *output) {
    if (!receipt_valid(receipt)) return HHS158_HANDLE_RELEASED;
    return hhs158_write_bytes((const uint8_t *)receipt->object_root, HHS158_HASH216_LENGTH, output);
}

HHS158Status hhs158_receipt_replay(HHS158Context *context, HHS158Receipt *receipt, const HHS158ReplayOptions *options,
    HHS158ReplayResult *out_result) {
    char canonical[HHS158_MAX_CANONICAL_BYTES];
    char replay_hex[HHS158_MAX_CANONICAL_BYTES * 2u + 1u];
    char object_root[HHS158_HASH216_LENGTH + 1u];
    char receipt_id[HHS158_HASH72_LENGTH + 1u];
    char reconstructed[HHS158_HASH216_LENGTH + 1u];
    int written;
    int match = 1;
    if (!out_result) return HHS158_INVALID_ARGUMENT;
    if (!context_valid(context) || !receipt_valid(receipt)) return HHS158_HANDLE_RELEASED;
    if (!options || !hhs158_header_valid(&options->header, sizeof(*options))) return HHS158_STRUCT_SIZE_INVALID;
    if (!hhs158_hex_encode((const uint8_t *)receipt->replay_material, receipt->replay_material_size, replay_hex, sizeof(replay_hex))) return HHS158_OUTPUT_BOUND;
    written = snprintf(canonical, sizeof(canonical),
        "HHS158_RECEIPT|%d|%s|%s|%s|%s|%s|%s|%s|%llu|%llu|%u|%u|%s",
        (int)receipt->status, receipt->classification, receipt->definition_id, receipt->instance_id,
        receipt->transition_id, receipt->pre_state_root, receipt->post_state_root,
        receipt->opcode_trace_root, (unsigned long long)receipt->vm81_steps,
        (unsigned long long)receipt->witness_flags, receipt->lifecycle_state, receipt->committed, replay_hex);
    if (written < 0 || (size_t)written >= sizeof(canonical)) return HHS158_OUTPUT_BOUND;
    hhs158_hash216_bytes(canonical, (size_t)written, object_root);
    hhs158_hash72_bytes(canonical, (size_t)written, receipt_id);
    if (options->verify_hash216 && strcmp(object_root, receipt->object_root) != 0) match = 0;
    if (options->verify_hash72 && strcmp(receipt_id, receipt->receipt_id) != 0) match = 0;
    if (receipt->committed && receipt->transition_id[0]) {
        hhs158_hash216_bytes(receipt->replay_material, receipt->replay_material_size, reconstructed);
        if (options->verify_semantic_root && strcmp(reconstructed, receipt->post_state_root) != 0) match = 0;
    } else snprintf(reconstructed, sizeof(reconstructed), "%s", receipt->post_state_root);
    memset(out_result, 0, sizeof(*out_result));
    out_result->header.struct_size = (uint32_t)sizeof(*out_result);
    out_result->header.struct_version = HHS158_STRUCT_VERSION_1;
    out_result->status = match ? HHS158_OK : HHS158_REPLAY_MISMATCH;
    out_result->matched = match ? 1u : 0u;
    out_result->lifecycle_state = match ? HHS158_LIFECYCLE_REPLAYED : HHS158_LIFECYCLE_REJECTED;
    snprintf(out_result->classification, sizeof(out_result->classification), "%s",
        match ? "HHS_P158_NFT_TRANSITION_REPLAY_VERIFIED" : "REPLAY_MISMATCH");
    snprintf(out_result->reconstructed_state_root, sizeof(out_result->reconstructed_state_root), "%s", reconstructed);
    return out_result->status;
}

void hhs158_receipt_release(HHS158Receipt *receipt) {
    if (!receipt || receipt->magic != HHS158_RECEIPT_MAGIC) return;
    receipt->released = 1u;
}
