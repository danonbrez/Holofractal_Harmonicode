#include "hhs_pass158_internal.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int hhs158_header_valid(const HHS158StructHeader *header, size_t minimum_size) {
    if (!header) return 0;
    if (header->struct_version != HHS158_STRUCT_VERSION_1) return 0;
    if ((size_t)header->struct_size < minimum_size) return 0;
    return 1;
}

int hhs158_utf8_valid(HHS158ByteSpan span) {
    size_t i = 0;
    if (span.size && !span.data) return 0;
    while (i < span.size) {
        uint8_t c = span.data[i++];
        uint32_t codepoint;
        size_t remaining;
        if (c <= 0x7fu) {
            if (c == 0u) return 0;
            continue;
        }
        if ((c & 0xe0u) == 0xc0u) { codepoint = c & 0x1fu; remaining = 1u; if (codepoint < 2u) return 0; }
        else if ((c & 0xf0u) == 0xe0u) { codepoint = c & 0x0fu; remaining = 2u; }
        else if ((c & 0xf8u) == 0xf0u) { codepoint = c & 0x07u; remaining = 3u; }
        else return 0;
        if (i + remaining > span.size) return 0;
        while (remaining--) {
            uint8_t tail = span.data[i++];
            if ((tail & 0xc0u) != 0x80u) return 0;
            codepoint = (codepoint << 6u) | (uint32_t)(tail & 0x3fu);
        }
        if (codepoint > 0x10ffffu) return 0;
        if (codepoint >= 0xd800u && codepoint <= 0xdfffu) return 0;
        if (codepoint == 0xfffeu || codepoint == 0xffffu) return 0;
    }
    return 1;
}

int hhs158_span_equal_text(HHS158ByteSpan span, const char *text) {
    size_t length;
    if (!text) return 0;
    length = strlen(text);
    return span.size == length && (!length || (span.data && memcmp(span.data, text, length) == 0));
}

int hhs158_span_contains(HHS158ByteSpan span, const char *needle) {
    size_t needle_length;
    size_t i;
    if (!needle) return 0;
    needle_length = strlen(needle);
    if (!needle_length) return 1;
    if (!span.data || span.size < needle_length) return 0;
    for (i = 0; i + needle_length <= span.size; ++i) {
        if (memcmp(span.data + i, needle, needle_length) == 0) return 1;
    }
    return 0;
}

HHS158Status hhs158_write_bytes(const uint8_t *data, size_t size, HHS158MutableByteSpan *output) {
    if (!output) return HHS158_INVALID_ARGUMENT;
    output->size_written = size;
    if (size && !data) return HHS158_INVALID_ARGUMENT;
    if (!output->data || output->capacity < size) return HHS158_BUFFER_TOO_SMALL;
    if (size) memcpy(output->data, data, size);
    return HHS158_OK;
}

HHS158Status hhs158_value_set(HHS158Value *value, uint32_t kind, uint32_t flags, const uint8_t *data, size_t size) {
    uint8_t *copy;
    if (!value || (size && !data)) return HHS158_INVALID_ARGUMENT;
    memset(value, 0, sizeof(*value));
    value->header.struct_size = (uint32_t)sizeof(*value);
    value->header.struct_version = HHS158_STRUCT_VERSION_1;
    value->kind = kind;
    value->flags = flags;
    if (!size) return HHS158_OK;
    copy = (uint8_t *)malloc(size);
    if (!copy) return HHS158_MEMORY_BOUND;
    memcpy(copy, data, size);
    value->canonical_payload.data = copy;
    value->canonical_payload.size = size;
    value->flags |= HHS158_INTERNAL_OWNED_VALUE;
    return HHS158_OK;
}

void hhs158_value_release(HHS158Value *value) {
    if (!value) return;
    if ((value->flags & HHS158_INTERNAL_OWNED_VALUE) && value->canonical_payload.data) {
        free((void *)value->canonical_payload.data);
    }
    memset(value, 0, sizeof(*value));
}

void hhs158_hash216_bytes(const void *data, size_t size, char output[HHS158_HASH216_LENGTH + 1u]) {
    HHS158NativeHash216 hash;
    memset(&hash, 0, sizeof(hash));
    hhs_hash216_compute(data, size, &hash);
    memcpy(output, hash.value, HHS158_HASH216_LENGTH + 1u);
}

void hhs158_hash72_bytes(const void *data, size_t size, char output[HHS158_HASH72_LENGTH + 1u]) {
    uint8_t cells[HHS158_HASH72_LENGTH];
    const uint8_t *bytes = (const uint8_t *)data;
    size_t i;
    memset(cells, 0, sizeof(cells));
    for (i = 0; i < size; ++i) {
        size_t slot = i % HHS158_HASH72_LENGTH;
        cells[slot] = (uint8_t)((cells[slot] + bytes[i] + (uint8_t)(i % 72u)) % 72u);
    }
    hhs_hash72_project(cells, output);
}

size_t hhs158_hex_encode(const uint8_t *data, size_t size, char *output, size_t capacity) {
    static const char HEX[] = "0123456789abcdef";
    size_t i;
    if (!output || capacity < size * 2u + 1u || (size && !data)) return 0;
    for (i = 0; i < size; ++i) {
        output[i * 2u] = HEX[(data[i] >> 4u) & 0x0fu];
        output[i * 2u + 1u] = HEX[data[i] & 0x0fu];
    }
    output[size * 2u] = '\0';
    return size * 2u;
}

static int hhs158_hex_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

HHS158Status hhs158_hex_decode(const char *text, uint8_t *output, size_t capacity, size_t *out_size) {
    size_t length;
    size_t i;
    if (!text || !out_size) return HHS158_INVALID_ARGUMENT;
    length = strlen(text);
    if ((length & 1u) != 0u) return HHS158_SERIALIZATION_INVALID;
    *out_size = length / 2u;
    if (!output || capacity < *out_size) return HHS158_BUFFER_TOO_SMALL;
    for (i = 0; i < *out_size; ++i) {
        int high = hhs158_hex_value(text[i * 2u]);
        int low = hhs158_hex_value(text[i * 2u + 1u]);
        if (high < 0 || low < 0) return HHS158_SERIALIZATION_INVALID;
        output[i] = (uint8_t)((high << 4) | low);
    }
    return HHS158_OK;
}

HHS158Status hhs158_append_text(char *buffer, size_t capacity, size_t *length, const char *text) {
    size_t add;
    if (!buffer || !length || !text) return HHS158_INVALID_ARGUMENT;
    add = strlen(text);
    if (*length > capacity || add > capacity - *length - 1u) return HHS158_OUTPUT_BOUND;
    memcpy(buffer + *length, text, add);
    *length += add;
    buffer[*length] = '\0';
    return HHS158_OK;
}

HHS158Status hhs158_append_span_hex(char *buffer, size_t capacity, size_t *length, const char *tag, HHS158ByteSpan span) {
    char header[96];
    char *hex;
    int written;
    HHS158Status status;
    if (span.size && !span.data) return HHS158_INVALID_ARGUMENT;
    written = snprintf(header, sizeof(header), "%s:%lu:", tag, (unsigned long)span.size);
    if (written < 0 || (size_t)written >= sizeof(header)) return HHS158_OUTPUT_BOUND;
    status = hhs158_append_text(buffer, capacity, length, header);
    if (status != HHS158_OK) return status;
    hex = (char *)malloc(span.size * 2u + 1u);
    if (!hex) return HHS158_MEMORY_BOUND;
    if (!hhs158_hex_encode(span.data, span.size, hex, span.size * 2u + 1u)) {
        free(hex);
        return HHS158_OUTPUT_BOUND;
    }
    status = hhs158_append_text(buffer, capacity, length, hex);
    free(hex);
    if (status != HHS158_OK) return status;
    return hhs158_append_text(buffer, capacity, length, "|");
}

static int hhs158_context_accepts_receipt(HHS158Context *context) {
    return context && context->magic == HHS158_CONTEXT_MAGIC && !context->released &&
        context->receipt_count < context->config.max_receipts &&
        context->receipt_count < HHS158_MAX_CONTEXT_OBJECTS;
}

HHS158Status hhs158_make_receipt(
    HHS158Context *context,
    HHS158Status status,
    const char *classification,
    const HHS158Definition *definition,
    const HHS158Instance *instance,
    const char *transition_id,
    const char *pre_root,
    const char *post_root,
    const char *trace_root,
    const char *replay_material,
    size_t replay_material_size,
    uint64_t vm81_steps,
    uint64_t witness_flags,
    uint32_t lifecycle_state,
    uint32_t committed,
    HHS158Receipt **out_receipt
) {
    HHS158Receipt *receipt;
    char canonical[HHS158_MAX_CANONICAL_BYTES];
    char replay_hex[HHS158_MAX_CANONICAL_BYTES];
    int written;
    if (!out_receipt) return HHS158_INVALID_ARGUMENT;
    *out_receipt = NULL;
    if (!hhs158_context_accepts_receipt(context)) return HHS158_MEMORY_BOUND;
    if (replay_material_size >= sizeof(replay_hex) / 2u) return HHS158_OUTPUT_BOUND;
    if (replay_material_size && !replay_material) return HHS158_INVALID_ARGUMENT;
    if (!hhs158_hex_encode((const uint8_t *)replay_material, replay_material_size, replay_hex, sizeof(replay_hex))) {
        return HHS158_OUTPUT_BOUND;
    }
    receipt = (HHS158Receipt *)calloc(1u, sizeof(*receipt));
    if (!receipt) return HHS158_MEMORY_BOUND;
    receipt->magic = HHS158_RECEIPT_MAGIC;
    receipt->context = context;
    receipt->status = status;
    receipt->vm81_steps = vm81_steps;
    receipt->witness_flags = witness_flags;
    receipt->lifecycle_state = lifecycle_state;
    receipt->committed = committed;
    snprintf(receipt->classification, sizeof(receipt->classification), "%s", classification ? classification : hhs158_status_classification(status));
    if (definition) snprintf(receipt->definition_id, sizeof(receipt->definition_id), "%s", definition->definition_id);
    if (instance) snprintf(receipt->instance_id, sizeof(receipt->instance_id), "%s", instance->instance_id);
    if (transition_id) snprintf(receipt->transition_id, sizeof(receipt->transition_id), "%s", transition_id);
    if (pre_root) snprintf(receipt->pre_state_root, sizeof(receipt->pre_state_root), "%s", pre_root);
    if (post_root) snprintf(receipt->post_state_root, sizeof(receipt->post_state_root), "%s", post_root);
    if (trace_root) snprintf(receipt->opcode_trace_root, sizeof(receipt->opcode_trace_root), "%s", trace_root);
    if (replay_material_size) {
        memcpy(receipt->replay_material, replay_material, replay_material_size);
        receipt->replay_material[replay_material_size] = '\0';
        receipt->replay_material_size = replay_material_size;
    }
    written = snprintf(canonical, sizeof(canonical),
        "HHS158_RECEIPT|%d|%s|%s|%s|%s|%s|%s|%s|%llu|%llu|%u|%u|%s",
        (int)status, receipt->classification, receipt->definition_id, receipt->instance_id,
        receipt->transition_id, receipt->pre_state_root, receipt->post_state_root,
        receipt->opcode_trace_root, (unsigned long long)vm81_steps,
        (unsigned long long)witness_flags, lifecycle_state, committed, replay_hex);
    if (written < 0 || (size_t)written >= sizeof(canonical)) {
        free(receipt);
        return HHS158_OUTPUT_BOUND;
    }
    hhs158_hash216_bytes(canonical, (size_t)written, receipt->object_root);
    hhs158_hash72_bytes(canonical, (size_t)written, receipt->receipt_id);
    context->receipts[context->receipt_count++] = receipt;
    *out_receipt = receipt;
    return HHS158_OK;
}

HHS158Status hhs158_capability_check(
    const HHS158Capability *capability,
    const HHS158Instance *instance,
    uint64_t operation,
    uint64_t mutation
) {
    uint64_t now;
    if (!capability) return HHS158_CAPABILITY_REQUIRED;
    if (capability->magic != HHS158_CAPABILITY_MAGIC || capability->released) return HHS158_HANDLE_RELEASED;
    if (capability->revoked) return HHS158_CAPABILITY_REVOKED;
    if (!capability->context || capability->context->released) return HHS158_HANDLE_RELEASED;
    now = capability->context->config.deterministic_epoch_seconds;
    if (capability->expires_at && now >= capability->expires_at) return HHS158_CAPABILITY_EXPIRED;
    if ((capability->operation_scope & operation) != operation) return HHS158_CAPABILITY_SCOPE_VIOLATION;
    if ((capability->mutation_scope & mutation) != mutation) return HHS158_CAPABILITY_SCOPE_VIOLATION;
    if (instance && strcmp(capability->object_scope, HHS158_SCOPE_WILDCARD) != 0 &&
        strcmp(capability->object_scope, instance->instance_id) != 0) return HHS158_CAPABILITY_SCOPE_VIOLATION;
    return HHS158_OK;
}

void hhs158_fill_validation_report(
    HHS158ValidationReport *report,
    HHS158Status status,
    uint32_t lifecycle,
    uint64_t checked,
    const char *classification,
    const char *state_root
) {
    if (!report) return;
    memset(report, 0, sizeof(*report));
    report->header.struct_size = (uint32_t)sizeof(*report);
    report->header.struct_version = HHS158_STRUCT_VERSION_1;
    report->status = status;
    report->lifecycle_state = lifecycle;
    report->checked_constraints = checked;
    snprintf(report->classification, sizeof(report->classification), "%s", classification ? classification : hhs158_status_classification(status));
    if (state_root) snprintf(report->state_root, sizeof(report->state_root), "%s", state_root);
}
