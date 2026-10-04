#include "hhs_pass220_i077_vm81_exact_matrix_power_execution_1_0.h"

#include <stdio.h>
#include <string.h>

static int emit_execution(uint32_t node_id) {
    HHSExactPass220I077ExecutionV1 execution;
    HHSExactStatus status;

    memset(&execution, 0, sizeof(execution));
    status = hhs_exact_pass220_i077_execute(node_id, &execution);
    if (status != HHS_EXACT_STATUS_OK ||
        execution.decision != HHS_EXACT_PASS220_I077_VERIFIED)
        return 0;

    printf(
        "{"
        "\"node_id\":%u,"
        "\"decision\":%u,"
        "\"reason\":%u,"
        "\"source_node\":\"%s\","
        "\"shape\":[%u,%u],"
        "\"exponent_token\":\"%s\","
        "\"exponent_token_degree\":%u,"
        "\"cell_occurrence_count\":%u,"
        "\"source_identity_exact\":%u,"
        "\"ordered_topology_verified\":%u,"
        "\"exact_symbolic_node_executed\":%u,"
        "\"host_matrixpower_used\":%u,"
        "\"square_matrix_requirement_imported\":%u,"
        "\"numeric_exponent_evaluated\":%u,"
        "\"matrix_power_value_derived\":%u,"
        "\"exact_vm81_admission_verified\":%u,"
        "\"atomic_frame_commit_verified\":%u,"
        "\"hash72_receipt_verified\":%u,"
        "\"hash216_transition_identity_verified\":%u,"
        "\"deterministic_replay_verified\":%u,"
        "\"canonical_state_persisted\":%u,"
        "\"floating_point_authority\":%u,"
        "\"vm5184_address\":%u,"
        "\"vm81_steps\":%llu,"
        "\"replay_vm81_steps\":%llu,"
        "\"source_node_sha256\":\"%s\","
        "\"ordered_cells_sha256\":\"%s\","
        "\"change_hash72\":\"%s\","
        "\"receipt_hash72\":\"%s\","
        "\"replay_hash72\":\"%s\","
        "\"proof_hash216\":\"%s\","
        "\"transition_hash216\":\"%s\""
        "}",
        (unsigned int)execution.node_id,
        (unsigned int)execution.decision,
        (unsigned int)execution.reason,
        execution.source_node,
        (unsigned int)execution.rows,
        (unsigned int)execution.columns,
        execution.exponent_token,
        (unsigned int)execution.exponent_token_degree,
        (unsigned int)execution.cell_occurrence_count,
        (unsigned int)execution.source_identity_exact,
        (unsigned int)execution.ordered_topology_verified,
        (unsigned int)execution.exact_symbolic_node_executed,
        (unsigned int)execution.host_matrixpower_used,
        (unsigned int)execution.square_matrix_requirement_imported,
        (unsigned int)execution.numeric_exponent_evaluated,
        (unsigned int)execution.matrix_power_value_derived,
        (unsigned int)execution.exact_vm81_admission_verified,
        (unsigned int)execution.atomic_frame_commit_verified,
        (unsigned int)execution.hash72_receipt_verified,
        (unsigned int)execution.hash216_transition_identity_verified,
        (unsigned int)execution.deterministic_replay_verified,
        (unsigned int)execution.canonical_state_persisted,
        (unsigned int)execution.floating_point_authority,
        (unsigned int)execution.vm5184_address,
        (unsigned long long)execution.vm81_steps,
        (unsigned long long)execution.replay_vm81_steps,
        execution.source_node_sha256,
        execution.ordered_cells_sha256,
        execution.change_hash72,
        execution.receipt_hash72,
        execution.replay_hash72,
        execution.proof_hash216,
        execution.transition_hash216);
    return 1;
}

int main(void) {
    HHSExactPass220I077DescriptorV1 descriptor;
    HHSExactPass220I077ExecutionV1 invalid;
    HHSExactStatus status;

    memset(&descriptor, 0, sizeof(descriptor));
    status = hhs_exact_pass220_i077_descriptor(&descriptor);
    if (status != HHS_EXACT_STATUS_OK)
        return 1;

    memset(&invalid, 0, sizeof(invalid));
    status = hhs_exact_pass220_i077_execute(
        HHS_EXACT_PASS220_I077_NODE_COUNT, &invalid);
    if (status != HHS_EXACT_STATUS_RANGE_ERROR ||
        invalid.decision != HHS_EXACT_PASS220_I077_REJECTED ||
        invalid.reason != HHS_EXACT_PASS220_I077_REASON_NODE_ID)
        return 1;

    printf(
        "{"
        "\"schema\":\"HHS_PASS_220_I077_NATIVE_PROBE_V1\","
        "\"version\":%u,"
        "\"descriptor\":{"
        "\"node_count\":%u,"
        "\"rows\":%u,"
        "\"columns\":%u,"
        "\"native_symbolic_executor\":%u,"
        "\"rectangular_4x2_supported\":%u,"
        "\"vm81_transport_admission\":%u,"
        "\"hash72_execution_receipt\":%u,"
        "\"hash216_transition_identity\":%u,"
        "\"deterministic_replay\":%u,"
        "\"matrix_power_value_derivation\":%u,"
        "\"host_matrixpower_authority\":%u,"
        "\"host_square_matrix_requirement_authority\":%u,"
        "\"numeric_exponent_evaluation_authority\":%u,"
        "\"floating_point_authority\":%u,"
        "\"canonical_state_persistence_authority\":%u,"
        "\"canonical_vm81_mutation_authority\":%u,"
        "\"canonical_hash72_commit_authority\":%u,"
        "\"canonical_hash216_commit_authority\":%u,"
        "\"external_egress_authority\":%u"
        "},"
        "\"negative_node_rejected\":true,"
        "\"executions\":[",
        (unsigned int)descriptor.version,
        (unsigned int)descriptor.node_count,
        (unsigned int)descriptor.rows,
        (unsigned int)descriptor.columns,
        (unsigned int)descriptor.native_symbolic_executor,
        (unsigned int)descriptor.rectangular_4x2_supported,
        (unsigned int)descriptor.vm81_transport_admission,
        (unsigned int)descriptor.hash72_execution_receipt,
        (unsigned int)descriptor.hash216_transition_identity,
        (unsigned int)descriptor.deterministic_replay,
        (unsigned int)descriptor.matrix_power_value_derivation,
        (unsigned int)descriptor.host_matrixpower_authority,
        (unsigned int)descriptor.host_square_matrix_requirement_authority,
        (unsigned int)descriptor.numeric_exponent_evaluation_authority,
        (unsigned int)descriptor.floating_point_authority,
        (unsigned int)descriptor.canonical_state_persistence_authority,
        (unsigned int)descriptor.canonical_vm81_mutation_authority,
        (unsigned int)descriptor.canonical_hash72_commit_authority,
        (unsigned int)descriptor.canonical_hash216_commit_authority,
        (unsigned int)descriptor.external_egress_authority);

    if (!emit_execution(HHS_EXACT_PASS220_I077_NODE_M_WZ_X2))
        return 1;
    printf(",");
    if (!emit_execution(HHS_EXACT_PASS220_I077_NODE_M_XY_X4))
        return 1;
    printf("]}\n");
    return 0;
}
