#include "hhs_pass219_i168_pass169_general_runtime_binding_1_25.h"

#include "hhs_pass219_pass159_global_witness_provenance_1_21_10.h"
#include "hhs_pass219_i162_pass169_vm81_exact_symbolic_execution_1_23.h"
#include "hhs_pass219_i163_pass169_reverse_crossarch_1_24.h"

#include <string.h>

static uint32_t hhs219_i168_version_word(void) {
    return (HHS_EXACT_PASS219_I168_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_I168_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_I168_VERSION_PATCH;
}

static int hhs219_i168_hash_present(const char *value, size_t length) {
    size_t i;
    if (value == NULL || value[length] != '\0')
        return 0;
    for (i = 0U; i < length; ++i) {
        if (value[i] == '\0')
            return 0;
    }
    return 1;
}

static void hhs219_i168_copy_hash216(
    char out[HHS_EXACT_PASS219_I168_HASH216_STRLEN],
    const char in[HHS_EXACT_PASS219_I168_HASH216_STRLEN]
) {
    memcpy(out, in, HHS_EXACT_PASS219_I168_HASH216_STRLEN);
}

static void hhs219_i168_copy_hash72(
    char out[HHS_EXACT_PASS219_I168_HASH72_STRLEN],
    const char in[HHS_EXACT_PASS219_I168_HASH72_STRLEN]
) {
    memcpy(out, in, HHS_EXACT_PASS219_I168_HASH72_STRLEN);
}

uint32_t hhs_exact_pass219_i168_version(void) {
    return hhs219_i168_version_word();
}

HHSExactStatus hhs_exact_pass219_i168_bind_canonical(
    const uint8_t *source_bytes,
    size_t source_length,
    HHSExactPass219I168RuntimeBindingV1 *out_binding
) {
    HHSExactPass219Pass159GlobalWitnessProvenanceV1 provenance;
    HHSExactPass219I162ExecutionV1 forward;
    HHSExactPass219I163ReverseExecutionV1 reverse;
    HHSExactStatus status;
    uint16_t mask = 0U;

    if (source_bytes == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = hhs219_i168_version_word();
    out_binding->decision = HHS_EXACT_PASS219_I168_UNRESOLVED;
    out_binding->reason = HHS_EXACT_PASS219_I168_REASON_SOURCE_PROVENANCE;
    out_binding->required_operation_mask = HHS_EXACT_PASS219_I168_ALL_OPS;
    out_binding->floating_point_authority = 0U;
    out_binding->hash216_persistence_authority = 0U;
    out_binding->fallback_used = 0U;

    if (source_length != HHS_EXACT_PASS219_I168_SOURCE_BYTES) {
        out_binding->decision = HHS_EXACT_PASS219_I168_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    memset(&provenance, 0, sizeof(provenance));
    status = hhs_exact_pass219_pass159_global_witness_produce(
        source_bytes, source_length, &provenance);
    if (status != HHS_EXACT_STATUS_OK ||
        provenance.pass159_status != 0 ||
        provenance.source_length != HHS_EXACT_PASS219_I168_SOURCE_BYTES ||
        provenance.source_identity_exact != 1U ||
        provenance.gate_occurrence_provenance_exact != 1U ||
        provenance.frontend_chain_complete != 1U ||
        provenance.source_root_lineage_exact != 1U ||
        provenance.pass159_whole_expression_provenance_verified != 1U ||
        provenance.floating_point_authority != 0U ||
        provenance.vm81_mutation_authority != 0U ||
        provenance.hash72_commit_authority != 0U ||
        provenance.persistence_mutation_authority != 0U) {
        out_binding->decision = HHS_EXACT_PASS219_I168_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_binding->source_identity_exact = 1U;
    out_binding->pass159_frontend_chain_complete = 1U;
    hhs219_i168_copy_hash216(out_binding->source_hash216, provenance.source_hash216);
    hhs219_i168_copy_hash216(out_binding->tokens_hash216, provenance.tokens_hash216);
    hhs219_i168_copy_hash216(out_binding->ast_hash216, provenance.ast_hash216);
    hhs219_i168_copy_hash216(
        out_binding->type_environment_hash216,
        provenance.type_environment_hash216);
    hhs219_i168_copy_hash216(
        out_binding->constraint_graph_hash216,
        provenance.constraint_graph_hash216);
    hhs219_i168_copy_hash216(out_binding->normalized_ir_hash216, provenance.hir_hash216);
    hhs219_i168_copy_hash216(out_binding->vmir_hash216, provenance.vmir_hash216);

    if (!hhs219_i168_hash_present(out_binding->tokens_hash216, HHS_EXACT_PASS219_I168_HASH216_LEN) ||
        !hhs219_i168_hash_present(out_binding->ast_hash216, HHS_EXACT_PASS219_I168_HASH216_LEN) ||
        !hhs219_i168_hash_present(out_binding->type_environment_hash216, HHS_EXACT_PASS219_I168_HASH216_LEN) ||
        !hhs219_i168_hash_present(out_binding->constraint_graph_hash216, HHS_EXACT_PASS219_I168_HASH216_LEN) ||
        !hhs219_i168_hash_present(out_binding->normalized_ir_hash216, HHS_EXACT_PASS219_I168_HASH216_LEN) ||
        !hhs219_i168_hash_present(out_binding->vmir_hash216, HHS_EXACT_PASS219_I168_HASH216_LEN)) {
        out_binding->reason = HHS_EXACT_PASS219_I168_REASON_PASS159_FRONTEND;
        out_binding->decision = HHS_EXACT_PASS219_I168_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    mask |= HHS_EXACT_PASS219_I168_OP_TOKENS;
    mask |= HHS_EXACT_PASS219_I168_OP_AST;
    mask |= HHS_EXACT_PASS219_I168_OP_CONSTRAINTS;
    mask |= HHS_EXACT_PASS219_I168_OP_TYPECHECK;
    mask |= HHS_EXACT_PASS219_I168_OP_NORMALIZE;

    memset(&forward, 0, sizeof(forward));
    out_binding->reason = HHS_EXACT_PASS219_I168_REASON_TYPED_PROOF;
    status = hhs_exact_pass219_i162_execute(&provenance, &forward);
    if (status != HHS_EXACT_STATUS_OK ||
        forward.decision != HHS_EXACT_PASS219_I162_VERIFIED ||
        forward.edge_proved_mask != HHS_EXACT_PASS219_I162_ALL_EDGE_MASK ||
        forward.gate_true_mask != HHS_EXACT_PASS219_I162_ALL_GATE_MASK ||
        forward.all_ten_typed_joins_verified != 1U ||
        forward.typed_scalar_zero_verified != 1U ||
        forward.typed_renewed_unit_verified != 1U ||
        forward.ordinary_scalar_boundary_equality_claimed != 0U ||
        forward.source_reconstruction_verified != 1U ||
        forward.floating_point_authority != 0U ||
        forward.hash216_persistence_authority != 0U) {
        out_binding->decision = HHS_EXACT_PASS219_I168_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_binding->typed_proof_verified = 1U;
    hhs219_i168_copy_hash216(out_binding->proof_hash216, forward.proof_hash216);
    hhs219_i168_copy_hash216(out_binding->transition_hash216, forward.transition_hash216);
    hhs219_i168_copy_hash72(out_binding->receipt_hash72, forward.receipt_hash72);
    hhs219_i168_copy_hash72(out_binding->replay_hash72, forward.replay_hash72);
    out_binding->vm5184_address = forward.vm5184_address;
    out_binding->forward_vm81_steps = forward.vm81_steps;
    out_binding->replay_vm81_steps = forward.replay_vm81_steps;
    mask |= HHS_EXACT_PASS219_I168_OP_PROVE;
    mask |= HHS_EXACT_PASS219_I168_OP_EVALUATE_CANDIDATE;

    out_binding->reason = HHS_EXACT_PASS219_I168_REASON_VM81_ADMISSION_COMMIT;
    if (forward.exact_vm81_admission_verified != 1U ||
        forward.atomic_commit_verified != 1U) {
        out_binding->decision = HHS_EXACT_PASS219_I168_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_binding->exact_vm81_admission_verified = 1U;
    out_binding->atomic_commit_verified = 1U;
    mask |= HHS_EXACT_PASS219_I168_OP_ADMIT;
    mask |= HHS_EXACT_PASS219_I168_OP_COMMIT;

    out_binding->reason = HHS_EXACT_PASS219_I168_REASON_RECEIPT_REPLAY;
    if (forward.hash72_receipt_verified != 1U ||
        forward.hash216_proof_identity_verified != 1U ||
        forward.deterministic_replay_verified != 1U ||
        !hhs219_i168_hash_present(out_binding->proof_hash216, HHS_EXACT_PASS219_I168_HASH216_LEN) ||
        !hhs219_i168_hash_present(out_binding->transition_hash216, HHS_EXACT_PASS219_I168_HASH216_LEN) ||
        !hhs219_i168_hash_present(out_binding->receipt_hash72, HHS_EXACT_PASS219_I168_HASH72_LEN) ||
        !hhs219_i168_hash_present(out_binding->replay_hash72, HHS_EXACT_PASS219_I168_HASH72_LEN)) {
        out_binding->decision = HHS_EXACT_PASS219_I168_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_binding->hash72_receipts_verified = 1U;
    out_binding->hash216_identities_verified = 1U;
    out_binding->deterministic_replay_verified = 1U;
    mask |= HHS_EXACT_PASS219_I168_OP_RECEIPT;
    mask |= HHS_EXACT_PASS219_I168_OP_REPLAY;

    memset(&reverse, 0, sizeof(reverse));
    out_binding->reason = HHS_EXACT_PASS219_I168_REASON_REVERSE;
    status = hhs_exact_pass219_i163_verify_reverse(
        source_bytes, source_length, &reverse);
    if (status != HHS_EXACT_STATUS_OK ||
        reverse.decision != HHS_EXACT_PASS219_I163_VERIFIED ||
        reverse.source_provenance_exact != 1U ||
        reverse.forward_commit_verified != 1U ||
        reverse.reverse_runtime_verified != 1U ||
        reverse.reverse_transition_receipt_verified != 1U ||
        reverse.reverse_transition_deterministic != 1U ||
        reverse.vm81_snapshot_reverse_verified != 1U ||
        reverse.prior_committed_state_restored != 1U ||
        reverse.interpreter_compiler_match != 1U ||
        reverse.hash72_ring_reverse_verified != 1U ||
        reverse.hash72_ring_restored_prior_state != 1U ||
        reverse.deterministic_repeat_verified != 1U ||
        reverse.floating_point_authority != 0U ||
        reverse.canonical_mutation_authority != 0U ||
        reverse.hash216_persistence_authority != 0U ||
        reverse.pass169_terminal_contract_claimed != 0U) {
        out_binding->decision = HHS_EXACT_PASS219_I168_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (strcmp(forward.transition_hash216, reverse.vm81_hash216_identity) != 0 ||
        strcmp(forward.receipt_hash72, reverse.vm81_receipt_hash72) != 0) {
        out_binding->reason = HHS_EXACT_PASS219_I168_REASON_AUTHORITY;
        out_binding->decision = HHS_EXACT_PASS219_I168_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_binding->interpreter_compiler_match = 1U;
    out_binding->reverse_restores_prior_state_verified = 1U;
    out_binding->reverse_vm81_steps = reverse.reverse_vm81_steps;
    hhs219_i168_copy_hash216(out_binding->reverse_hash216, reverse.reverse_receipt_hash216);
    hhs219_i168_copy_hash72(out_binding->reverse_hash72, reverse.reverse_receipt_hash72);
    mask |= HHS_EXACT_PASS219_I168_OP_REVERSE;

    out_binding->reason = HHS_EXACT_PASS219_I168_REASON_AUTHORITY;
    out_binding->live_runtime_abi_verified = 1U;
    out_binding->canonical_computation_through_runtime_abi = 1U;
    out_binding->single_vm81_commit_authority = 1U;
    out_binding->operation_verified_mask = mask;

    if (mask != HHS_EXACT_PASS219_I168_ALL_OPS ||
        out_binding->source_identity_exact != 1U ||
        out_binding->pass159_frontend_chain_complete != 1U ||
        out_binding->typed_proof_verified != 1U ||
        out_binding->interpreter_compiler_match != 1U ||
        out_binding->exact_vm81_admission_verified != 1U ||
        out_binding->atomic_commit_verified != 1U ||
        out_binding->hash72_receipts_verified != 1U ||
        out_binding->hash216_identities_verified != 1U ||
        out_binding->deterministic_replay_verified != 1U ||
        out_binding->reverse_restores_prior_state_verified != 1U ||
        out_binding->live_runtime_abi_verified != 1U ||
        out_binding->canonical_computation_through_runtime_abi != 1U ||
        out_binding->single_vm81_commit_authority != 1U ||
        out_binding->fallback_used != 0U ||
        out_binding->floating_point_authority != 0U ||
        out_binding->hash216_persistence_authority != 0U) {
        out_binding->decision = HHS_EXACT_PASS219_I168_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_binding->reason = HHS_EXACT_PASS219_I168_REASON_NONE;
    out_binding->decision = HHS_EXACT_PASS219_I168_VERIFIED;
    return HHS_EXACT_STATUS_OK;
}
