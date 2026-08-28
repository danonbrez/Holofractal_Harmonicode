#include "hhs_pass219_pass159_vm81_proof_bridge_1_21_2.h"

#include <stdio.h>
#include <string.h>

static void dump_failure(
    HHSExactStatus exact_status,
    const HHSExactPass219Pass159ProofV1 *proof
) {
    fprintf(stderr,
        "exact=%d pass159=%d stages=0x%08x source=%u frontend=%u vmir=%u "
        "interpret=%u replay=%u receipt_ok=%u replay_receipt_ok=%u "
        "steps=%llu replay_steps=%llu h72=%u replay_h72=%u semeq=%u "
        "compare=%u fallback=%u committed=%u replay_committed=%u "
        "pipeline=%u vm81=%u proven=%u effectful=%u observed=%u replay_exec=%u "
        "step_auth=%u candidate=%u canonical=%u required=%u\n",
        (int)exact_status,
        (int)proof->pass159_status,
        proof->completed_stage_mask,
        proof->source_exact,
        proof->frontend_chain_complete,
        proof->vmir_complete,
        proof->interpret_ok,
        proof->replay_ok,
        proof->receipt_status_ok,
        proof->replay_receipt_status_ok,
        (unsigned long long)proof->vm81_steps,
        (unsigned long long)proof->replay_vm81_steps,
        proof->receipt_hash72_valid,
        proof->replay_hash72_valid,
        proof->semantic_root_equal,
        proof->interpreter_compiler_match,
        proof->fallback_used,
        proof->committed,
        proof->replay_committed,
        proof->source_pipeline_verified,
        proof->vm81_execution_verified,
        proof->native_shared_invariant_proven,
        proof->pass159_vmir_effectful,
        proof->pass159_vm81_execution_observed,
        proof->pass159_replay_reexecuted,
        proof->pass159_step_counter_authoritative,
        proof->candidate_binding_supported,
        proof->canonical_vm81_proof_observed,
        proof->candidate_vm81_proof_required);
}

int main(void) {
    HHSExactPass219Pass159ProofV1 proof;
    uint8_t native_source[HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH];
    size_t native_length = 0U;
    HHSExactStatus status;

    memset(&proof, 0, sizeof(proof));
    status = hhs_exact_pass219_pass159_prove_monolithic(&proof);
    if (status != HHS_EXACT_STATUS_OK) {
        dump_failure(status, &proof);
        return 1;
    }
    if (proof.struct_size != sizeof(proof) ||
        proof.version != hhs_exact_pass219_pass159_proof_version())
        return 2;
    if (proof.pass159_status != 0 ||
        (proof.completed_stage_mask & HHS_EXACT_PASS219_PASS159_SOURCE_PIPELINE_REQUIRED) !=
            HHS_EXACT_PASS219_PASS159_SOURCE_PIPELINE_REQUIRED ||
        (proof.completed_stage_mask & HHS_EXACT_PASS219_STAGE_VM81_PROOF) != 0U)
        return 3;
    if (proof.source_exact != 1U ||
        proof.frontend_chain_complete != 1U ||
        proof.vmir_complete != 1U ||
        proof.interpret_ok != 1U ||
        proof.replay_ok != 1U ||
        proof.source_pipeline_verified != 1U)
        return 4;
    if (proof.receipt_status_ok != 1U ||
        proof.replay_receipt_status_ok != 1U ||
        proof.receipt_hash72_valid != 1U ||
        proof.replay_hash72_valid != 1U ||
        proof.semantic_root_equal != 1U)
        return 5;
    if (proof.vm81_steps == 0U || proof.replay_vm81_steps == 0U ||
        proof.interpreter_compiler_match != 1U || proof.fallback_used != 0U)
        return 6;
    if (proof.committed != 0U || proof.replay_committed != 0U ||
        proof.vm81_mutation_authority != 0U || proof.hash72_commit_authority != 0U ||
        proof.floating_point_authority != 0U)
        return 7;

    /* Current Pass159 receipt/replay is foundation evidence, not VM81 proof. */
    if (proof.vm81_execution_verified != 0U ||
        proof.native_shared_invariant_proven != 0U ||
        proof.pass159_vmir_effectful != 0U ||
        proof.pass159_vm81_execution_observed != 0U ||
        proof.pass159_replay_reexecuted != 0U ||
        proof.pass159_step_counter_authoritative != 0U ||
        proof.candidate_binding_supported != 0U ||
        proof.canonical_vm81_proof_observed != 0U ||
        proof.candidate_vm81_proof_required != 1U)
        return 8;

    if (hhs_exact_pass219_monolithic_native_source(
            native_source, sizeof(native_source), &native_length) != HHS_EXACT_STATUS_OK ||
        native_length != sizeof(native_source) ||
        memcmp(native_source, proof.source_bytes, sizeof(native_source)) != 0)
        return 9;

    if (proof.source_hash216[HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN] != '\0' ||
        proof.ast_hash216[HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN] != '\0' ||
        proof.constraint_graph_hash216[HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN] != '\0' ||
        proof.vmir_hash216[HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN] != '\0' ||
        proof.receipt_hash216[HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN] != '\0' ||
        proof.replay_hash216[HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN] != '\0')
        return 10;

    puts("PASS219_PASS159_SOURCE_PIPELINE_1_21_2_OK_VM81_PROOF_REQUIRED");
    return 0;
}
