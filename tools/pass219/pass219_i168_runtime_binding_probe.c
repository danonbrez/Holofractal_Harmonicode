#include "hhs_pass219_i168_pass169_general_runtime_binding_1_25.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int read_source(const char *path, uint8_t *out, size_t capacity, size_t *out_size) {
    FILE *file;
    long length;
    size_t size;
    if (path == NULL || out == NULL || out_size == NULL)
        return 0;
    file = fopen(path, "rb");
    if (file == NULL)
        return 0;
    if (fseek(file, 0L, SEEK_END) != 0) {
        fclose(file);
        return 0;
    }
    length = ftell(file);
    if (length < 0L || (size_t)length > capacity || fseek(file, 0L, SEEK_SET) != 0) {
        fclose(file);
        return 0;
    }
    size = fread(out, 1U, (size_t)length, file);
    if (size != (size_t)length || ferror(file)) {
        fclose(file);
        return 0;
    }
    fclose(file);
    *out_size = size;
    return 1;
}

int main(int argc, char **argv) {
    uint8_t source[HHS_EXACT_PASS219_I168_SOURCE_BYTES];
    size_t source_size = 0U;
    HHSExactPass219I168RuntimeBindingV1 binding;
    HHSExactStatus status;

    if (argc != 2) {
        fprintf(stderr, "usage: %s <canonical-pass169-source>\n", argv[0]);
        return 2;
    }
    if (!read_source(argv[1], source, sizeof(source), &source_size) || source_size != sizeof(source)) {
        fprintf(stderr, "failed to read exact 632-byte Pass169 source\n");
        return 1;
    }

    memset(&binding, 0, sizeof(binding));
    status = hhs_exact_pass219_i168_bind_canonical(source, source_size, &binding);
    if (status != HHS_EXACT_STATUS_OK || binding.decision != HHS_EXACT_PASS219_I168_VERIFIED)
        return 1;

    printf(
        "{"
        "\"schema\":\"HHS_PASS219_I168_NATIVE_RUNTIME_BINDING_PROBE_V1\","
        "\"status\":%u,"
        "\"decision\":%u,"
        "\"operation_verified_mask\":%u,"
        "\"required_operation_mask\":%u,"
        "\"source_identity_exact\":%u,"
        "\"pass159_frontend_chain_complete\":%u,"
        "\"typed_proof_verified\":%u,"
        "\"interpreter_compiler_match\":%u,"
        "\"exact_vm81_admission_verified\":%u,"
        "\"atomic_commit_verified\":%u,"
        "\"hash72_receipts_verified\":%u,"
        "\"hash216_identities_verified\":%u,"
        "\"deterministic_replay_verified\":%u,"
        "\"reverse_restores_prior_state_verified\":%u,"
        "\"live_runtime_abi_verified\":%u,"
        "\"canonical_computation_through_runtime_abi\":%u,"
        "\"single_vm81_commit_authority\":%u,"
        "\"fallback_used\":%u,"
        "\"floating_point_authority\":%u,"
        "\"hash216_persistence_authority\":%u,"
        "\"vm5184_address\":%u,"
        "\"forward_vm81_steps\":%llu,"
        "\"replay_vm81_steps\":%llu,"
        "\"reverse_vm81_steps\":%llu,"
        "\"source_hash216\":\"%s\","
        "\"tokens_hash216\":\"%s\","
        "\"ast_hash216\":\"%s\","
        "\"constraint_graph_hash216\":\"%s\","
        "\"normalized_ir_hash216\":\"%s\","
        "\"vmir_hash216\":\"%s\","
        "\"proof_hash216\":\"%s\","
        "\"transition_hash216\":\"%s\","
        "\"reverse_hash216\":\"%s\","
        "\"receipt_hash72\":\"%s\","
        "\"replay_hash72\":\"%s\","
        "\"reverse_hash72\":\"%s\""
        "}\n",
        (unsigned int)status,
        (unsigned int)binding.decision,
        (unsigned int)binding.operation_verified_mask,
        (unsigned int)binding.required_operation_mask,
        (unsigned int)binding.source_identity_exact,
        (unsigned int)binding.pass159_frontend_chain_complete,
        (unsigned int)binding.typed_proof_verified,
        (unsigned int)binding.interpreter_compiler_match,
        (unsigned int)binding.exact_vm81_admission_verified,
        (unsigned int)binding.atomic_commit_verified,
        (unsigned int)binding.hash72_receipts_verified,
        (unsigned int)binding.hash216_identities_verified,
        (unsigned int)binding.deterministic_replay_verified,
        (unsigned int)binding.reverse_restores_prior_state_verified,
        (unsigned int)binding.live_runtime_abi_verified,
        (unsigned int)binding.canonical_computation_through_runtime_abi,
        (unsigned int)binding.single_vm81_commit_authority,
        (unsigned int)binding.fallback_used,
        (unsigned int)binding.floating_point_authority,
        (unsigned int)binding.hash216_persistence_authority,
        (unsigned int)binding.vm5184_address,
        (unsigned long long)binding.forward_vm81_steps,
        (unsigned long long)binding.replay_vm81_steps,
        (unsigned long long)binding.reverse_vm81_steps,
        binding.source_hash216,
        binding.tokens_hash216,
        binding.ast_hash216,
        binding.constraint_graph_hash216,
        binding.normalized_ir_hash216,
        binding.vmir_hash216,
        binding.proof_hash216,
        binding.transition_hash216,
        binding.reverse_hash216,
        binding.receipt_hash72,
        binding.replay_hash72,
        binding.reverse_hash72);
    return 0;
}
