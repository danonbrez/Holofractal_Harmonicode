#include "hhs_pass219_exact_vm81_candidate_adapter_1_21_3.h"

#include <stdio.h>
#include <string.h>

static int hash72_valid(const char value[HHS_EXACT_HASH72_STRLEN]) {
    size_t i;
    if (value == NULL || value[HHS_EXACT_HASH72_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i) {
        if (strchr(HHS_EXACT_HASH72_ALPHABET, value[i]) == NULL)
            return 0;
    }
    return 1;
}

static HHSExactVM81Frame build_candidate(void) {
    HHSExactVM81Frame frame;
    uint32_t i;
    memset(&frame, 0, sizeof(frame));
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        frame.words[i] = UINT64_C(0x0102030405060708) ^
                         ((uint64_t)(i + 1U) * UINT64_C(0x9E3779B97F4A7C15));
    return frame;
}

int main(void) {
    HHSExactPass219VM81ProgramV1 program;
    HHSExactPass219VM81ExecutionV1 execution;
    HHSExactPass219VM81ReplayV1 replay;
    HHSExactVM81Frame candidate = build_candidate();
    HHSExactPass219MonolithicDescriptorV1 descriptor;
    HHSExactStatus status;
    uint32_t i;

    memset(&program, 0, sizeof(program));
    status = hhs_exact_pass219_vm81_lower_monolithic_structure(&program);
    if (status != HHS_EXACT_STATUS_OK)
        return 1;

    if (program.struct_size != sizeof(program) ||
        program.version != hhs_exact_pass219_vm81_adapter_version() ||
        program.instruction_count != HHS_EXACT_PASS219_VM81_PROGRAM_THREADS ||
        program.source_structure_thread_count !=
            HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS ||
        program.derived_thread_count != HHS_EXACT_PASS219_VM81_DERIVED_THREADS)
        return 2;

    if (program.source_structure_complete != 1U ||
        program.effectful_lowering_complete != 1U ||
        program.source_semantics_complete != 0U ||
        program.full_symbolic_identity_required != 1U ||
        program.semantic_family_coverage_mask != HHS_EXACT_PASS219_FAMILY_REQUIRED ||
        program.equality_edge_coverage_mask !=
            HHS_EXACT_PASS219_MONOLITHIC_ALL_EDGE_MASK)
        return 3;

    if (hhs_exact_pass219_monolithic_descriptor(&descriptor) != HHS_EXACT_STATUS_OK ||
        memcmp(program.source_sha256,
               descriptor.native_source_sha256,
               HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES) != 0)
        return 4;

    for (i = 0U; i < HHS_EXACT_PASS219_VM81_SYMBOL_COUNT; ++i) {
        if (program.symbol_cell81[i] != i)
            return 5;
    }
    if (program.x_cell81 != HHS_EXACT_PASS219_VM81_SYMBOL_X ||
        program.y_cell81 != HHS_EXACT_PASS219_VM81_SYMBOL_Y ||
        program.z_cell81 != HHS_EXACT_PASS219_VM81_SYMBOL_Z ||
        program.w_cell81 != HHS_EXACT_PASS219_VM81_SYMBOL_W)
        return 6;

    for (i = 0U; i < HHS_EXACT_PASS219_VM81_PROGRAM_THREADS; ++i) {
        if (program.instructions[i].struct_size != sizeof(program.instructions[i]) ||
            program.instructions[i].version != hhs_exact_pass219_vm81_adapter_version())
            return 7;
    }
    for (i = 0U; i < HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS; ++i) {
        if (program.instructions[i].opcode != HHS_EXACT_PASS219_VM81_OP_CONSTRAIN)
            return 8;
    }
    if (program.instructions[57].opcode != HHS_EXACT_PASS219_VM81_OP_MULXY ||
        program.instructions[58].opcode != HHS_EXACT_PASS219_VM81_OP_MULYX ||
        program.instructions[59].opcode != HHS_EXACT_PASS219_VM81_OP_QGU ||
        program.instructions[60].opcode != HHS_EXACT_PASS219_VM81_OP_SWEEP81 ||
        program.instructions[61].opcode != HHS_EXACT_PASS219_VM81_OP_CLOSE81 ||
        program.instructions[62].opcode != HHS_EXACT_PASS219_VM81_OP_GATE_IDENTITY ||
        program.instructions[63].opcode != HHS_EXACT_PASS219_VM81_OP_HALT)
        return 9;

    memset(&execution, 0, sizeof(execution));
    status = hhs_exact_pass219_vm81_execute_candidate(
        &program, &candidate, &execution);
    if (status != HHS_EXACT_STATUS_OK)
        return 10;

    if (execution.struct_size != sizeof(execution) ||
        execution.version != hhs_exact_pass219_vm81_adapter_version() ||
        memcmp(&execution.before_frame, &candidate, sizeof(candidate)) != 0 ||
        memcmp(&execution.after_frame, &candidate, sizeof(candidate)) == 0)
        return 11;

    if (!hash72_valid(execution.previous_hash72) ||
        !hash72_valid(execution.state_hash72) ||
        !hash72_valid(execution.receipt_hash72) ||
        execution.steps_executed == 0U ||
        execution.steps_executed > HHS_EXACT_PASS219_VM81_MAX_EXECUTION_STEPS ||
        execution.halted != 1U ||
        execution.source_identity_valid != 1U ||
        execution.candidate_frame_bound != 1U ||
        execution.exact_kernel_execution_observed != 1U)
        return 12;

    if (execution.source_structure_complete != 1U ||
        execution.effectful_lowering_complete != 1U ||
        execution.source_semantics_complete != 0U ||
        execution.full_symbolic_identity_required != 1U ||
        execution.full_symbolic_identity_gate_supported != 0U ||
        execution.canonical_monolithic_proof != 0U)
        return 13;

    if (execution.floating_point_authority != 0U ||
        execution.vm81_mutation_authority != 0U ||
        execution.hash72_commit_authority != 0U)
        return 14;

    memset(&replay, 0, sizeof(replay));
    status = hhs_exact_pass219_vm81_replay_candidate(
        &program, &candidate, &execution, &replay);
    if (status != HHS_EXACT_STATUS_OK || replay.replay_verified != 1U)
        return 15;
    if (replay.frame_equal != 1U ||
        replay.previous_hash72_equal != 1U ||
        replay.state_hash72_equal != 1U ||
        replay.receipt_hash72_equal != 1U ||
        replay.witness_equal != 1U ||
        replay.steps_equal != 1U ||
        replay.phase_surface_equal != 1U ||
        replay.source_identity_equal != 1U ||
        replay.coverage_equal != 1U ||
        replay.authority_boundary_equal != 1U)
        return 16;

    {
        HHSExactPass219VM81ProgramV1 tampered = program;
        tampered.source_sha256[0] ^= 1U;
        if (hhs_exact_pass219_vm81_execute_candidate(
                &tampered, &candidate, &execution) !=
            HHS_EXACT_STATUS_INVARIANT_FAILURE)
            return 17;
    }

    {
        HHSExactPass219VM81ProgramV1 duplicate_cell = program;
        duplicate_cell.symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_Y] =
            duplicate_cell.symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_X];
        duplicate_cell.y_cell81 = duplicate_cell.x_cell81;
        if (hhs_exact_pass219_vm81_execute_candidate(
                &duplicate_cell, &candidate, &execution) !=
            HHS_EXACT_STATUS_INVARIANT_FAILURE)
            return 18;
    }

    {
        HHSExactPass219VM81ProgramV1 forged_semantics = program;
        forged_semantics.source_semantics_complete = 1U;
        if (hhs_exact_pass219_vm81_execute_candidate(
                &forged_semantics, &candidate, &execution) !=
            HHS_EXACT_STATUS_INVARIANT_FAILURE)
            return 19;
    }

    {
        HHSExactPass219VM81ExecutionV1 forged_expected = replay.replay;
        HHSExactPass219VM81ReplayV1 negative_replay;
        forged_expected.after_frame.words[40] ^= UINT64_C(1);
        memset(&negative_replay, 0, sizeof(negative_replay));
        if (hhs_exact_pass219_vm81_replay_candidate(
                &program, &candidate, &forged_expected, &negative_replay) !=
                HHS_EXACT_STATUS_INVARIANT_FAILURE ||
            negative_replay.replay_verified != 0U ||
            negative_replay.frame_equal != 0U)
            return 20;
    }

    puts("PASS219_EXACT_VM81_CANDIDATE_ADAPTER_1_21_3_OK_PROOF_STILL_FAIL_CLOSED");
    return 0;
}
