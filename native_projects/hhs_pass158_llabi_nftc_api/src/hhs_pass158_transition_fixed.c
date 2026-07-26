#define hhs158_transition_execute hhs158_transition_execute_legacy
#define hhs158_transition_commit hhs158_transition_commit_legacy
#include "hhs_pass158_transition.c"
#undef hhs158_transition_execute
#undef hhs158_transition_commit

HHS158Status hhs158_transition_commit(HHS158Transition *transition, HHS158Receipt **out_commit_receipt) {
    HHS158Status status;
    if (!out_commit_receipt) return HHS158_INVALID_ARGUMENT;
    *out_commit_receipt = NULL;
    if (!transition_valid(transition)) return HHS158_HANDLE_RELEASED;
    if (!transition->executed || transition->committed || transition->aborted) return HHS158_INVALID_STATE;
    status = hhs158_capability_check(transition->capability, transition->instance, HHS158_CAP_COMMIT, HHS158_MUTATION_INSTANCE);
    if (status != HHS158_OK) return status;
    if (strcmp(transition->instance->current_state_root, transition->pre_state_root) != 0) return HHS158_STATE_ROOT_CONFLICT;
    snprintf(transition->instance->current_state_root, sizeof(transition->instance->current_state_root), "%s", transition->candidate_state_root);
    transition->instance->lifecycle = HHS158_LIFECYCLE_COMMITTED;
    transition->instance->version++;
    transition->committed = 1u;
    status = hhs158_make_receipt(transition->context, HHS158_OK, "HHS_P158_HASH72_EXECUTION_RECEIPT_CLOSED",
        transition->instance->definition, transition->instance, transition->transition_id,
        transition->pre_state_root, transition->candidate_state_root, transition->opcode_trace_root,
        transition->replay_material, transition->replay_material_size, transition->operation_count,
        W_IDENTITY_GATE_PASS | W_CONSTRAINT_FIRED, HHS158_LIFECYCLE_COMMITTED, 1u, out_commit_receipt);
    if (status == HHS158_OK) snprintf(transition->instance->last_transition_receipt,
        sizeof(transition->instance->last_transition_receipt), "%s", (*out_commit_receipt)->receipt_id);
    return status;
}

HHS158Status hhs158_transition_execute(HHS158Transition *transition, const HHS158ExecutionOptions *options,
    HHS158ExecutionResult *out_result, HHS158Receipt **out_receipt) {
    HHS158ExecutionOptions execution_only;
    HHS158Status status;
    uint32_t atomic = 0u;
    if (!out_result || !out_receipt) return HHS158_INVALID_ARGUMENT;
    if (options) {
        if (!hhs158_header_valid(&options->header, sizeof(*options))) return HHS158_STRUCT_SIZE_INVALID;
        execution_only = *options;
        atomic = options->atomic_execute_and_commit;
        execution_only.atomic_execute_and_commit = 0u;
        status = hhs158_transition_execute_legacy(transition, &execution_only, out_result, out_receipt);
    } else {
        status = hhs158_transition_execute_legacy(transition, NULL, out_result, out_receipt);
    }
    if (status != HHS158_OK || !atomic) return status;
    {
        HHS158Receipt *commit_receipt = NULL;
        status = hhs158_transition_commit(transition, &commit_receipt);
        if (status != HHS158_OK) return status;
        *out_receipt = commit_receipt;
        out_result->lifecycle_state = HHS158_LIFECYCLE_COMMITTED;
        snprintf(out_result->classification, sizeof(out_result->classification), "%s", "HHS_VM81_TRANSITION_COMMITTED");
        snprintf(out_result->post_state_root, sizeof(out_result->post_state_root), "%s", transition->candidate_state_root);
    }
    return HHS158_OK;
}
