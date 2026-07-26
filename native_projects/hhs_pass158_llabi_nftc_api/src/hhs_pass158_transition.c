#include "hhs_pass158_internal.h"

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

static HHS158Status operation_semantic_gate(const HHS158Operation *operation) {
    if (!operation || !hhs158_header_valid(&operation->header, sizeof(*operation))) return HHS158_STRUCT_SIZE_INVALID;
    if (!hhs158_opcode_is_public(operation->opcode)) return HHS158_PRIVATE_OPCODE;
    if (operation->operands.size > HHS158_MAX_OPERAND_BYTES || (operation->operands.size && !operation->operands.data)) return HHS158_OUTPUT_BOUND;
    if ((operation->opcode == HHS158_OP_BIND_EQ || operation->opcode == HHS158_OP_BIND_NEQ) &&
        hhs158_span_contains(operation->operands, "==") && hhs158_span_contains(operation->operands, "==")) {
        size_t i;
        size_t count = 0u;
        for (i = 0; i + 1u < operation->operands.size; ++i) {
            if (operation->operands.data[i] == '=' && operation->operands.data[i + 1u] == '=') count++;
        }
        if (count > 1u) return HHS158_CONSTRAINT_CHAIN_COLLAPSED;
    }
    if (operation->opcode == HHS158_OP_LIST_ORDERED && operation->operands.size > 0u &&
        operation->operands.data[0] == '{') return HHS158_LIST_TOPOLOGY_LOSS;
    if (hhs158_span_contains(operation->operands, "O=Pi") || hhs158_span_contains(operation->operands, "O==Pi") ||
        hhs158_span_contains(operation->operands, "O=π") || hhs158_span_contains(operation->operands, "O==π")) return HHS158_PHASE_IDENTITY_VIOLATION;
    return HHS158_OK;
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
        status = operation_semantic_gate(&descriptor->operations[i]);
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
        status = hhs158_capability_check(transition->capability, transition->instance, HHS158_CAP_COMMIT, HHS158_MUTATION_INSTANCE);
        if (status != HHS158_OK) return status;
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
        memset(&tensor, 0, sizeof(tensor));
        tensor.xy = (int64_t)transition->operations[i].opcode;
        tensor.yx = (int64_t)transition->operations[i].opcode;
        tensor.transport = (int64_t)(transition->operations[i].operand_size + 1u);
        tensor.orientation = 0;
        tensor.constraint = (int64_t)(transition->operations[i].opcode % 3u);
        hhs_runtime_step(&runtime, &tensor);
    }
    while (!runtime.converged && runtime.step < limit) {
        HHSTensorState audit_tensor;
        memset(&audit_tensor, 0, sizeof(audit_tensor));
        audit_tensor.constraint = -runtime.flux.constraint_flux;
        audit_tensor.orientation = -runtime.flux.orientation_flux;
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
        if (status != HHS158_OK) return status;
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
    if (!out_abort_receipt) return HHS158_INVALID_ARGUMENT;
    *out_abort_receipt = NULL;
    if (!transition_valid(transition)) return HHS158_HANDLE_RELEASED;
    if (transition->committed || transition->aborted) return HHS158_INVALID_STATE;
    transition->aborted = 1u;
    written = snprintf(material, sizeof(material), "%s|ABORT:%u", transition->replay_material, reason_code);
    if (written < 0 || (size_t)written >= sizeof(material)) return HHS158_OUTPUT_BOUND;
    return hhs158_make_receipt(transition->context, HHS158_REJECTED, "HHS_P158_NFT_INTEGRATION_REQUEST_REJECTED",
        transition->instance->definition, transition->instance, transition->transition_id,
        transition->pre_state_root, transition->pre_state_root, transition->opcode_trace_root,
        material, (size_t)written, 0u, 0u, HHS158_LIFECYCLE_REJECTED, 0u, out_abort_receipt);
}

void hhs158_transition_release(HHS158Transition *transition) {
    if (!transition || transition->magic != HHS158_TRANSITION_MAGIC) return;
    transition->released = 1u;
}
