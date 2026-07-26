#include "hhs_pass158_internal.h"
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int transition_valid(const HHS158Transition *transition) {
    return transition && transition->magic == HHS158_TRANSITION_MAGIC && !transition->released &&
        transition->context && transition->context->magic == HHS158_CONTEXT_MAGIC && !transition->context->released &&
        transition->instance && transition->instance->magic == HHS158_INSTANCE_MAGIC && !transition->instance->released;
}

static uint64_t minimum_nonzero(uint64_t left, uint64_t right) {
    if (!left) return right;
    if (!right) return left;
    return left < right ? left : right;
}

static HHS158Status append_operation_material(HHS158Transition *transition, const HHS158Operation *operation, size_t index) {
    char header[96];
    char hex[HHS158_MAX_OPERAND_BYTES * 2u + 1u];
    int written;
    HHS158Status status;
    written = snprintf(header, sizeof(header), "op:%lu:%u:%u:%lu:", (unsigned long)index, operation->opcode,
        operation->flags, (unsigned long)operation->operands.size);
    if (written < 0 || (size_t)written >= sizeof(header)) return HHS158_OUTPUT_BOUND;
    status = hhs158_append_text(transition->replay_material, sizeof(transition->replay_material), &transition->replay_material_size, header);
    if (status != HHS158_OK) return status;
    if (!hhs158_hex_encode(operation->operands.data, operation->operands.size, hex, sizeof(hex))) return HHS158_OUTPUT_BOUND;
    status = hhs158_append_text(transition->replay_material, sizeof(transition->replay_material), &transition->replay_material_size, hex);
    if (status != HHS158_OK) return status;
    return hhs158_append_text(transition->replay_material, sizeof(transition->replay_material), &transition->replay_material_size, "|");
}

typedef struct {
    uint8_t data[HHS158_MAX_OPERAND_BYTES + 1u];
    size_t size;
} HHS158ParsedOperand;

static const HHS158OpcodeDescriptor *opcode_descriptor(uint32_t opcode) {
    const HHS158OpcodeDescriptor *registry;
    size_t count = 0u;
    size_t i;
    registry = hhs158_public_opcode_registry(&count);
    for (i = 0u; i < count; ++i) if (registry[i].opcode == opcode) return &registry[i];
    return NULL;
}

static int hash72_index(char symbol) {
    static const char alphabet[] = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";
    const char *position = strchr(alphabet, symbol);
    return position ? (int)(position - alphabet) : 0;
}

static void trim_operand(HHS158ParsedOperand *operand) {
    size_t begin = 0u;
    size_t end = operand->size;
    while (begin < end && isspace((unsigned char)operand->data[begin])) begin++;
    while (end > begin && isspace((unsigned char)operand->data[end - 1u])) end--;
    if (begin) memmove(operand->data, operand->data + begin, end - begin);
    operand->size = end - begin;
    operand->data[operand->size] = '\0';
}

static int append_decoded_byte(HHS158ParsedOperand *operand, uint8_t byte) {
    if (operand->size >= HHS158_MAX_OPERAND_BYTES) return 0;
    operand->data[operand->size++] = byte;
    operand->data[operand->size] = '\0';
    return 1;
}

static int parse_json_string(const uint8_t **cursor, const uint8_t *end, HHS158ParsedOperand *operand) {
    const uint8_t *p = *cursor;
    if (p >= end || *p != '"') return 0;
    p++;
    while (p < end) {
        uint8_t byte = *p++;
        if (byte == '"') { *cursor = p; return 1; }
        if (byte == '\\') {
            if (p >= end) return 0;
            byte = *p++;
            switch (byte) {
                case '"': case '\\': case '/': break;
                case 'b': byte = '\b'; break;
                case 'f': byte = '\f'; break;
                case 'n': byte = '\n'; break;
                case 'r': byte = '\r'; break;
                case 't': byte = '\t'; break;
                default: return 0;
            }
        }
        if (!append_decoded_byte(operand, byte)) return 0;
    }
    return 0;
}

static int parse_two_operands(HHS158ByteSpan source, HHS158ParsedOperand operands[2]) {
    const uint8_t *cursor;
    const uint8_t *end;
    size_t count = 0u;
    if (!source.data || source.size == 0u) return 0;
    memset(operands, 0, sizeof(HHS158ParsedOperand) * 2u);
    cursor = source.data;
    end = source.data + source.size;
    while (cursor < end && isspace((unsigned char)*cursor)) cursor++;
    if (cursor < end && *cursor == '[') {
        cursor++;
        while (cursor < end) {
            while (cursor < end && isspace((unsigned char)*cursor)) cursor++;
            if (cursor < end && *cursor == ']') { cursor++; break; }
            if (count >= 2u || !parse_json_string(&cursor, end, &operands[count])) return 0;
            trim_operand(&operands[count]);
            count++;
            while (cursor < end && isspace((unsigned char)*cursor)) cursor++;
            if (cursor < end && *cursor == ',') { cursor++; continue; }
            if (cursor < end && *cursor == ']') { cursor++; break; }
            return 0;
        }
        while (cursor < end && isspace((unsigned char)*cursor)) cursor++;
        return count == 2u && cursor == end;
    }
    while (count < 2u) {
        const uint8_t *start = cursor;
        const uint8_t *separator = NULL;
        while (cursor < end) {
            if (*cursor == ',' && count == 0u) { separator = cursor; break; }
            cursor++;
        }
        if (count == 0u) {
            if (!separator) return 0;
            if ((size_t)(separator - start) > HHS158_MAX_OPERAND_BYTES) return 0;
            memcpy(operands[0].data, start, (size_t)(separator - start));
            operands[0].size = (size_t)(separator - start);
            operands[0].data[operands[0].size] = '\0';
            trim_operand(&operands[0]);
            cursor = separator + 1u;
            count = 1u;
        } else {
            if ((size_t)(end - start) > HHS158_MAX_OPERAND_BYTES) return 0;
            memcpy(operands[1].data, start, (size_t)(end - start));
            operands[1].size = (size_t)(end - start);
            operands[1].data[operands[1].size] = '\0';
            trim_operand(&operands[1]);
            count = 2u;
        }
    }
    return operands[0].size > 0u && operands[1].size > 0u;
}

static const HHS158BindingRecord *find_binding(const HHS158Instance *instance, const HHS158ParsedOperand *operand) {
    size_t i;
    for (i = 0u; i < instance->binding_count; ++i) {
        size_t symbol_size = strlen(instance->bindings[i].symbol);
        if (symbol_size == operand->size && memcmp(instance->bindings[i].symbol, operand->data, operand->size) == 0)
            return &instance->bindings[i];
    }
    return NULL;
}

static int exact_numeric_operand(const HHS158ParsedOperand *operand) {
    size_t i = 0u;
    size_t digits = 0u;
    size_t slash_count = 0u;
    if (!operand->size) return 0;
    if (operand->data[i] == '+' || operand->data[i] == '-') i++;
    for (; i < operand->size; ++i) {
        if (operand->data[i] >= '0' && operand->data[i] <= '9') { digits++; continue; }
        if (operand->data[i] == '/' && digits && slash_count == 0u && i + 1u < operand->size) {
            slash_count++;
            digits = 0u;
            continue;
        }
        return 0;
    }
    return digits > 0u;
}

static int operand_equality_known(const HHS158Instance *instance, const HHS158ParsedOperand operands[2], int *equal) {
    const HHS158BindingRecord *left_binding = find_binding(instance, &operands[0]);
    const HHS158BindingRecord *right_binding = find_binding(instance, &operands[1]);
    const uint8_t *left = operands[0].data;
    const uint8_t *right = operands[1].data;
    size_t left_size = operands[0].size;
    size_t right_size = operands[1].size;
    int left_concrete = exact_numeric_operand(&operands[0]);
    int right_concrete = exact_numeric_operand(&operands[1]);
    if (operands[0].size == operands[1].size && memcmp(operands[0].data, operands[1].data, operands[0].size) == 0) {
        *equal = 1;
        return 1;
    }
    if (left_binding) {
        left = left_binding->payload;
        left_size = left_binding->payload_size;
        left_concrete = 1;
    }
    if (right_binding) {
        right = right_binding->payload;
        right_size = right_binding->payload_size;
        right_concrete = 1;
    }
    if (!left_concrete || !right_concrete) return 0;
    *equal = left_size == right_size && memcmp(left, right, left_size) == 0;
    return 1;
}

static HHS158Status operation_semantic_gate(const HHS158Instance *instance, const HHS158Operation *operation) {
    if (!operation || !hhs158_header_valid(&operation->header, sizeof(*operation))) return HHS158_STRUCT_SIZE_INVALID;
    if (!hhs158_opcode_is_public(operation->opcode)) return HHS158_PRIVATE_OPCODE;
    if (operation->operands.size > HHS158_MAX_OPERAND_BYTES || (operation->operands.size && !operation->operands.data)) return HHS158_OUTPUT_BOUND;
    if ((operation->opcode == HHS158_OP_BIND_EQ || operation->opcode == HHS158_OP_BIND_NEQ) &&
        hhs158_span_contains(operation->operands, "==")) {
        size_t i;
        size_t count = 0u;
        for (i = 0; i + 1u < operation->operands.size; ++i) {
            if (operation->operands.data[i] == '=' && operation->operands.data[i + 1u] == '=') count++;
        }
        if (count > 1u) return HHS158_CONSTRAINT_CHAIN_COLLAPSED;
    }
    if (operation->opcode == HHS158_OP_BIND_EQ || operation->opcode == HHS158_OP_BIND_NEQ) {
        HHS158ParsedOperand operands[2];
        int equal = 0;
        int known;
        if (!parse_two_operands(operation->operands, operands)) return HHS158_INVALID_ARGUMENT;
        known = operand_equality_known(instance, operands, &equal);
        if (known && ((operation->opcode == HHS158_OP_BIND_EQ && !equal) ||
            (operation->opcode == HHS158_OP_BIND_NEQ && equal))) return HHS158_VM81_ADMISSION_REJECTED;
    }
    if (operation->opcode == HHS158_OP_LIST_ORDERED && operation->operands.size > 0u &&
        operation->operands.data[0] == '{') return HHS158_LIST_TOPOLOGY_LOSS;
    if (hhs158_span_contains(operation->operands, "O=Pi") || hhs158_span_contains(operation->operands, "O==Pi") ||
        hhs158_span_contains(operation->operands, "O=π") || hhs158_span_contains(operation->operands, "O==π")) return HHS158_PHASE_IDENTITY_VIOLATION;
    return HHS158_OK;
}

static void operation_tensor(const HHS158Transition *transition, size_t index, HHSTensorState *tensor) {
    char hash72[HHS158_HASH72_LENGTH + 1u];
    size_t offset = (index * 9u) % HHS158_HASH72_LENGTH;
    hhs158_hash72_bytes(transition->replay_material, transition->replay_material_size, hash72);
    memset(tensor, 0, sizeof(*tensor));
    tensor->xy = (int64_t)transition->operations[index].opcode + hash72_index(hash72[offset]) + 1;
    tensor->yx = (int64_t)transition->operations[index].opcode + hash72_index(hash72[(offset + 1u) % HHS158_HASH72_LENGTH]) + 1;
    tensor->transport = (int64_t)hash72_index(hash72[(offset + 2u) % HHS158_HASH72_LENGTH]) + 1;
    tensor->orientation = (int64_t)hash72_index(hash72[(offset + 3u) % HHS158_HASH72_LENGTH]) -
        (int64_t)hash72_index(hash72[(offset + 4u) % HHS158_HASH72_LENGTH]);
    tensor->constraint = (int64_t)(hash72_index(hash72[(offset + 5u) % HHS158_HASH72_LENGTH]) % 3) - 1;
}

static void closure_tensor(const HHS158Transition *transition, const HHSRuntimeState *runtime, HHSTensorState *tensor) {
    char hash72[HHS158_HASH72_LENGTH + 1u];
    hhs158_hash72_bytes(transition->replay_material, transition->replay_material_size, hash72);
    memset(tensor, 0, sizeof(*tensor));
    tensor->xy = (int64_t)hash72_index(hash72[6]) + 1;
    tensor->yx = (int64_t)hash72_index(hash72[7]) + 1;
    tensor->transport = (int64_t)hash72_index(hash72[8]) + 1;
    tensor->constraint = -runtime->flux.constraint_flux;
    tensor->orientation = -runtime->flux.orientation_flux;
}

HHS158Status hhs158_transition_create(HHS158Instance *instance, HHS158Capability *capability,
    const HHS158TransitionDescriptor *descriptor, HHS158Transition **out_transition) {
    HHS158Transition *transition;
    HHS158Status status;
    size_t i;
    uint64_t mutation = HHS158_MUTATION_INSTANCE;
    if (!out_transition) return HHS158_INVALID_ARGUMENT;
    *out_transition = NULL;
    if (!instance || instance->magic != HHS158_INSTANCE_MAGIC || instance->released) return HHS158_HANDLE_RELEASED;
    if (!descriptor || !hhs158_header_valid(&descriptor->header, sizeof(*descriptor))) return HHS158_STRUCT_SIZE_INVALID;
    if (!descriptor->operations || descriptor->operation_count == 0u || descriptor->operation_count > HHS158_MAX_OPERATIONS) return HHS158_INVALID_ARGUMENT;
    if (instance->lifecycle == HHS158_LIFECYCLE_RETIRED || instance->lifecycle == HHS158_LIFECYCLE_QUARANTINED) return HHS158_INVALID_STATE;
    status = hhs158_capability_check(capability, instance, HHS158_CAP_EXECUTE, mutation);
    if (status != HHS158_OK) return status;
    for (i = 0u; i < descriptor->operation_count; ++i) {
        const HHS158OpcodeDescriptor *opcode = opcode_descriptor(descriptor->operations[i].opcode);
        if (!opcode) return HHS158_PRIVATE_OPCODE;
        status = hhs158_capability_check(capability, instance, opcode->required_capability, mutation);
        if (status != HHS158_OK) return status;
        status = operation_semantic_gate(instance, &descriptor->operations[i]);
        if (status != HHS158_OK) return status;
    }
    if (descriptor->expected_pre_state_root.size) {
        if (descriptor->expected_pre_state_root.size != HHS158_HASH216_LENGTH || !descriptor->expected_pre_state_root.data) return HHS158_INVALID_ARGUMENT;
        if (memcmp(descriptor->expected_pre_state_root.data, instance->current_state_root, HHS158_HASH216_LENGTH) != 0) return HHS158_STATE_ROOT_CONFLICT;
    }
    if (instance->context->transition_count >= HHS158_MAX_CONTEXT_OBJECTS) return HHS158_MEMORY_BOUND;
    transition = (HHS158Transition *)calloc(1u, sizeof(*transition));
    if (!transition) return HHS158_MEMORY_BOUND;
    transition->magic = HHS158_TRANSITION_MAGIC;
    transition->context = instance->context;
    transition->instance = instance;
    transition->capability = capability;
    transition->operation_count = descriptor->operation_count;
    transition->max_vm81_steps = descriptor->max_vm81_steps ? descriptor->max_vm81_steps : instance->max_vm81_steps;
    transition->max_recursion_depth = descriptor->max_recursion_depth ? descriptor->max_recursion_depth : instance->max_recursion_depth;
    transition->max_output_bytes = descriptor->max_output_bytes ? descriptor->max_output_bytes : instance->max_receipt_bytes;
    transition->commit_policy = descriptor->commit_policy;
    transition->flags = descriptor->flags;
    snprintf(transition->pre_state_root, sizeof(transition->pre_state_root), "%s", instance->current_state_root);
    status = hhs158_append_text(transition->replay_material, sizeof(transition->replay_material), &transition->replay_material_size, "HHS158_TRANSITION|");
    if (status == HHS158_OK) status = hhs158_append_text(transition->replay_material, sizeof(transition->replay_material), &transition->replay_material_size, transition->pre_state_root);
    if (status == HHS158_OK) status = hhs158_append_text(transition->replay_material, sizeof(transition->replay_material), &transition->replay_material_size, "|bindings:");
    for (i = 0; status == HHS158_OK && i < instance->binding_count; ++i) {
        char header[256];
        char hex[HHS158_MAX_OPERAND_BYTES * 2u + 1u];
        int written = snprintf(header, sizeof(header), "%s:%u:%u:%lu:", instance->bindings[i].symbol,
            instance->bindings[i].kind, instance->bindings[i].flags, (unsigned long)instance->bindings[i].payload_size);
        if (written < 0 || (size_t)written >= sizeof(header)) status = HHS158_OUTPUT_BOUND;
        else status = hhs158_append_text(transition->replay_material, sizeof(transition->replay_material), &transition->replay_material_size, header);
        if (status == HHS158_OK && !hhs158_hex_encode(instance->bindings[i].payload, instance->bindings[i].payload_size, hex, sizeof(hex))) status = HHS158_OUTPUT_BOUND;
        if (status == HHS158_OK) status = hhs158_append_text(transition->replay_material, sizeof(transition->replay_material), &transition->replay_material_size, hex);
        if (status == HHS158_OK) status = hhs158_append_text(transition->replay_material, sizeof(transition->replay_material), &transition->replay_material_size, ";");
    }
    if (status == HHS158_OK) status = hhs158_append_text(transition->replay_material, sizeof(transition->replay_material), &transition->replay_material_size, "|operations:");
    for (i = 0; status == HHS158_OK && i < descriptor->operation_count; ++i) {
        status = operation_semantic_gate(instance, &descriptor->operations[i]);
        if (status != HHS158_OK) break;
        transition->operations[i].opcode = descriptor->operations[i].opcode;
        transition->operations[i].flags = descriptor->operations[i].flags;
        transition->operations[i].operand_size = descriptor->operations[i].operands.size;
        if (transition->operations[i].operand_size) memcpy(transition->operations[i].operands, descriptor->operations[i].operands.data, transition->operations[i].operand_size);
        status = append_operation_material(transition, &descriptor->operations[i], i);
    }
    if (status != HHS158_OK) { free(transition); return status; }
    hhs158_hash216_bytes(transition->replay_material, transition->replay_material_size, transition->candidate_state_root);
    {
        char trace[HHS158_MAX_CANONICAL_BYTES];
        int written = snprintf(trace, sizeof(trace), "HHS158_OPCODE_TRACE|%s|%lu", transition->candidate_state_root, (unsigned long)transition->operation_count);
        if (written < 0 || (size_t)written >= sizeof(trace)) { free(transition); return HHS158_OUTPUT_BOUND; }
        hhs158_hash216_bytes(trace, (size_t)written, transition->opcode_trace_root);
        written = snprintf(trace, sizeof(trace), "HHS158_TRANSITION_ID|%s|%s|%s", transition->pre_state_root,
            transition->candidate_state_root, capability->capability_id);
        if (written < 0 || (size_t)written >= sizeof(trace)) { free(transition); return HHS158_OUTPUT_BOUND; }
        hhs158_hash216_bytes(trace, (size_t)written, transition->transition_id);
    }
    instance->context->transitions[instance->context->transition_count++] = transition;
    *out_transition = transition;
    return HHS158_OK;
}

static void fill_execution_result(HHS158ExecutionResult *result, HHS158Status status, uint32_t lifecycle,
    uint64_t steps, uint64_t flags, const char *classification, const HHS158Transition *transition) {
    if (!result) return;
    memset(result, 0, sizeof(*result));
    result->header.struct_size = (uint32_t)sizeof(*result);
    result->header.struct_version = HHS158_STRUCT_VERSION_1;
    result->status = status;
    result->lifecycle_state = lifecycle;
    result->vm81_steps = steps;
    result->witness_flags = flags;
    snprintf(result->classification, sizeof(result->classification), "%s", classification);
    snprintf(result->pre_state_root, sizeof(result->pre_state_root), "%s", transition->pre_state_root);
    snprintf(result->post_state_root, sizeof(result->post_state_root), "%s", transition->candidate_state_root);
    snprintf(result->opcode_trace_root, sizeof(result->opcode_trace_root), "%s", transition->opcode_trace_root);
}

HHS158Status hhs158_transition_execute(HHS158Transition *transition, const HHS158ExecutionOptions *options,
    HHS158ExecutionResult *out_result, HHS158Receipt **out_receipt) {
    HHSRuntimeState runtime;
    HHSReceipt runtime_receipt;
    HHS158Receipt *execution_receipt = NULL;
    HHS158Status status;
    uint64_t limit;
    size_t i;
    uint32_t atomic_commit = 0u;
    if (!out_result || !out_receipt) return HHS158_INVALID_ARGUMENT;
    *out_receipt = NULL;
    if (!transition_valid(transition)) return HHS158_HANDLE_RELEASED;
    if (transition->executed || transition->aborted) return HHS158_INVALID_STATE;
    if (options) {
        if (!hhs158_header_valid(&options->header, sizeof(*options))) return HHS158_STRUCT_SIZE_INVALID;
        atomic_commit = options->atomic_execute_and_commit;
    }
    status = hhs158_capability_check(transition->capability, transition->instance, HHS158_CAP_EXECUTE, HHS158_MUTATION_INSTANCE);
    if (status != HHS158_OK) return status;
    if (atomic_commit) {
        uint64_t configured_remaining;
        size_t storage_remaining;
        status = hhs158_capability_check(transition->capability, transition->instance, HHS158_CAP_COMMIT, HHS158_MUTATION_INSTANCE);
        if (status != HHS158_OK) return status;
        configured_remaining = transition->context->config.max_receipts > transition->context->receipt_count
            ? transition->context->config.max_receipts - transition->context->receipt_count : 0u;
        storage_remaining = HHS158_MAX_CONTEXT_OBJECTS > transition->context->receipt_count
            ? HHS158_MAX_CONTEXT_OBJECTS - transition->context->receipt_count : 0u;
        if (configured_remaining < 2u || storage_remaining < 2u) return HHS158_MEMORY_BOUND;
    }
    limit = minimum_nonzero(transition->max_vm81_steps, transition->capability->max_vm81_steps);
    limit = minimum_nonzero(limit, transition->instance->max_vm81_steps);
    if (options) limit = minimum_nonzero(limit, options->max_vm81_steps);
    if (limit < transition->operation_count) {
        fill_execution_result(out_result, HHS158_VM81_RESOURCE_BOUNDED, HHS158_LIFECYCLE_HELD, 0u, 0u,
            "VM81_RESOURCE_BOUNDED", transition);
        status = hhs158_make_receipt(transition->context, HHS158_VM81_RESOURCE_BOUNDED, "VM81_RESOURCE_BOUNDED",
            transition->instance->definition, transition->instance, transition->transition_id,
            transition->pre_state_root, transition->pre_state_root, transition->opcode_trace_root,
            transition->replay_material, transition->replay_material_size, 0u, 0u, HHS158_LIFECYCLE_HELD, 0u, out_receipt);
        return status == HHS158_OK ? HHS158_VM81_RESOURCE_BOUNDED : status;
    }
    runtime = transition->context->runtime_template;
    hhs_receipt_reset(&runtime_receipt);
    for (i = 0; i < transition->operation_count; ++i) {
        HHSTensorState tensor;
        if (options && options->cancel_flag && *options->cancel_flag) {
            fill_execution_result(out_result, HHS158_CANCELLED, HHS158_LIFECYCLE_HELD, runtime.step, runtime.witness_flags,
                "CANCELLED", transition);
            status = hhs158_make_receipt(transition->context, HHS158_CANCELLED, "CANCELLED",
                transition->instance->definition, transition->instance, transition->transition_id,
                transition->pre_state_root, transition->pre_state_root, transition->opcode_trace_root,
                transition->replay_material, transition->replay_material_size, runtime.step, runtime.witness_flags,
                HHS158_LIFECYCLE_HELD, 0u, out_receipt);
            return status == HHS158_OK ? HHS158_CANCELLED : status;
        }
        operation_tensor(transition, i, &tensor);
        hhs_runtime_step(&runtime, &tensor);
    }
    while (!runtime.converged && runtime.step < limit) {
        HHSTensorState audit_tensor;
        closure_tensor(transition, &runtime, &audit_tensor);
        hhs_runtime_step(&runtime, &audit_tensor);
    }
    if (!runtime.converged || (runtime.witness_flags & (W_TRANSPORT_CLOSED | W_ORIENTATION_CLOSED | W_CONSTRAINT_CLOSED | W_CONVERGED)) !=
        (W_TRANSPORT_CLOSED | W_ORIENTATION_CLOSED | W_CONSTRAINT_CLOSED | W_CONVERGED)) {
        fill_execution_result(out_result, HHS158_VM81_ADMISSION_REJECTED, HHS158_LIFECYCLE_HELD,
            runtime.step, runtime.witness_flags, "VM81_ADMISSION_REJECTED", transition);
        status = hhs158_make_receipt(transition->context, HHS158_VM81_ADMISSION_REJECTED, "VM81_ADMISSION_REJECTED",
            transition->instance->definition, transition->instance, transition->transition_id,
            transition->pre_state_root, transition->pre_state_root, transition->opcode_trace_root,
            transition->replay_material, transition->replay_material_size, runtime.step, runtime.witness_flags,
            HHS158_LIFECYCLE_HELD, 0u, out_receipt);
        return status == HHS158_OK ? HHS158_VM81_ADMISSION_REJECTED : status;
    }
    hhs_receipt_commit(&runtime, &runtime_receipt);
    if (runtime_receipt.closure_delta != 1 || strcmp(runtime_receipt.current_receipt, runtime.receipt_hash72) != 0) {
        return HHS158_HASH72_RECEIPT_MISMATCH;
    }
    status = hhs158_make_receipt(transition->context, HHS158_OK, "HHS_P158_VM81_NFT_TRANSITION_AUTHORIZED",
        transition->instance->definition, transition->instance, transition->transition_id,
        transition->pre_state_root, transition->candidate_state_root, transition->opcode_trace_root,
        transition->replay_material, transition->replay_material_size, runtime.step, runtime.witness_flags,
        HHS158_LIFECYCLE_AUTHORIZED, 0u, &execution_receipt);
    if (status != HHS158_OK) return status;
    transition->audit_vm81_steps = runtime.step;
    transition->audit_witness_flags = runtime.witness_flags;
    transition->executed = 1u;
    fill_execution_result(out_result, HHS158_OK, HHS158_LIFECYCLE_AUTHORIZED, runtime.step, runtime.witness_flags,
        "HHS_P158_VM81_NFT_TRANSITION_AUTHORIZED", transition);
    *out_receipt = execution_receipt;
    if (atomic_commit) {
        HHS158Receipt *commit_receipt = NULL;
        status = hhs158_transition_commit(transition, &commit_receipt);
        if (status != HHS158_OK) {
            *out_receipt = execution_receipt;
            return status;
        }
        *out_receipt = commit_receipt;
        out_result->lifecycle_state = HHS158_LIFECYCLE_COMMITTED;
        snprintf(out_result->classification, sizeof(out_result->classification), "%s", "HHS_VM81_TRANSITION_COMMITTED");
    }
    return HHS158_OK;
}

HHS158Status hhs158_transition_commit(HHS158Transition *transition, HHS158Receipt **out_commit_receipt) {
    HHS158Status status;
    if (!out_commit_receipt) return HHS158_INVALID_ARGUMENT;
    *out_commit_receipt = NULL;
    if (!transition_valid(transition)) return HHS158_HANDLE_RELEASED;
    if (!transition->executed || transition->committed || transition->aborted) return HHS158_INVALID_STATE;
    status = hhs158_capability_check(transition->capability, transition->instance, HHS158_CAP_COMMIT, HHS158_MUTATION_INSTANCE);
    if (status != HHS158_OK) return status;
    if (strcmp(transition->instance->current_state_root, transition->pre_state_root) != 0) return HHS158_STATE_ROOT_CONFLICT;
    status = hhs158_make_receipt(transition->context, HHS158_OK, "HHS_P158_HASH72_EXECUTION_RECEIPT_CLOSED",
        transition->instance->definition, transition->instance, transition->transition_id,
        transition->pre_state_root, transition->candidate_state_root, transition->opcode_trace_root,
        transition->replay_material, transition->replay_material_size, transition->audit_vm81_steps,
        transition->audit_witness_flags, HHS158_LIFECYCLE_COMMITTED, 1u, out_commit_receipt);
    if (status != HHS158_OK) return status;
    snprintf(transition->instance->current_state_root, sizeof(transition->instance->current_state_root), "%s", transition->candidate_state_root);
    transition->instance->lifecycle = HHS158_LIFECYCLE_COMMITTED;
    transition->instance->version++;
    transition->committed = 1u;
    snprintf(transition->instance->last_transition_receipt,
        sizeof(transition->instance->last_transition_receipt), "%s", (*out_commit_receipt)->receipt_id);
    return HHS158_OK;
}

HHS158Status hhs158_transition_abort(HHS158Transition *transition, uint32_t reason_code, HHS158Receipt **out_abort_receipt) {
    char material[HHS158_MAX_CANONICAL_BYTES];
    int written;
    HHS158Status status;
    if (!out_abort_receipt) return HHS158_INVALID_ARGUMENT;
    *out_abort_receipt = NULL;
    if (!transition_valid(transition)) return HHS158_HANDLE_RELEASED;
    if (transition->committed || transition->aborted) return HHS158_INVALID_STATE;
    written = snprintf(material, sizeof(material), "%s|ABORT:%u", transition->replay_material, reason_code);
    if (written < 0 || (size_t)written >= sizeof(material)) return HHS158_OUTPUT_BOUND;
    status = hhs158_make_receipt(transition->context, HHS158_REJECTED, "HHS_P158_NFT_INTEGRATION_REQUEST_REJECTED",
        transition->instance->definition, transition->instance, transition->transition_id,
        transition->pre_state_root, transition->pre_state_root, transition->opcode_trace_root,
        material, (size_t)written, 0u, 0u, HHS158_LIFECYCLE_REJECTED, 0u, out_abort_receipt);
    if (status != HHS158_OK) return status;
    transition->aborted = 1u;
    return HHS158_OK;
}

void hhs158_transition_release(HHS158Transition *transition) {
    if (!transition || transition->magic != HHS158_TRANSITION_MAGIC) return;
    transition->released = 1u;
}
