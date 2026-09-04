#include "hhs_pass219_i162_pass169_vm81_exact_symbolic_execution_1_23.h"
#include "hhs_pass219_pass159_global_witness_provenance_1_21_10.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int read_source(
    const char *path,
    uint8_t *out,
    size_t capacity,
    size_t *out_size
) {
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
    if (length < 0L ||
        (unsigned long)length > (unsigned long)capacity ||
        fseek(file, 0L, SEEK_SET) != 0) {
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

static void hex32(const uint8_t bytes[32], char out[65]) {
    static const char HEX[] = "0123456789abcdef";
    size_t i;
    for (i = 0U; i < 32U; ++i) {
        out[i * 2U] = HEX[(bytes[i] >> 4U) & 0x0fU];
        out[i * 2U + 1U] = HEX[bytes[i] & 0x0fU];
    }
    out[64] = '\0';
}

int main(int argc, char **argv) {
    uint8_t source[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SOURCE_BYTES];
    size_t source_size = 0U;
    HHSExactPass219Pass159GlobalWitnessProvenanceV1 provenance;
    HHSExactPass219I162ExecutionV1 execution;
    HHSExactPass219Pass169BindingResultV1 binding;
    HHSExactStatus status;
    char environment_root[65];
    FILE *out;

    if (argc != 3) {
        fprintf(stderr, "usage: %s <combined-source> <out-json>\n", argv[0]);
        return 2;
    }
    if (!read_source(argv[1], source, sizeof(source), &source_size) ||
        source_size != sizeof(source)) {
        fprintf(stderr, "failed to read exact combined source\n");
        return 1;
    }

    memset(&provenance, 0, sizeof(provenance));
    status = hhs_exact_pass219_pass159_global_witness_produce(
        source, source_size, &provenance);
    if (status != HHS_EXACT_STATUS_OK)
        return 1;

    memset(&execution, 0, sizeof(execution));
    status = hhs_exact_pass219_i162_execute(&provenance, &execution);
    if (status != HHS_EXACT_STATUS_OK ||
        execution.decision != HHS_EXACT_PASS219_I162_VERIFIED)
        return 1;

    memset(&binding, 0, sizeof(binding));
    status = hhs_exact_pass219_pass169_bind_authority(&provenance, &binding);
    if (status != HHS_EXACT_STATUS_OK ||
        binding.decision != HHS_EXACT_PASS219_PASS169_BINDING_PROPAGATE)
        return 1;

    hex32(execution.canonical_global_symbol_environment_root, environment_root);
    out = fopen(argv[2], "wb");
    if (out == NULL)
        return 1;

    fprintf(out,
        "{\n"
        "  \"schema\": \"HHS_PASS219_I162_PASS169_VM81_EXACT_SYMBOLIC_PROBE_V1\",\n"
        "  \"result\": \"PASS\",\n"
        "  \"edge_proved_mask\": %u,\n"
        "  \"typed_join_count\": 10,\n"
        "  \"typed_join_proved\": 10,\n"
        "  \"gate_true_mask\": %u,\n"
        "  \"boolean_gate_count\": 5,\n"
        "  \"boolean_gates_true\": 5,\n"
        "  \"P\": %u,\n"
        "  \"p\": %u,\n"
        "  \"q\": %u,\n"
        "  \"delta\": %u,\n"
        "  \"vm5184_address\": %u,\n"
        "  \"vm81_steps\": %llu,\n"
        "  \"replay_vm81_steps\": %llu,\n"
        "  \"typed_scalar_zero_verified\": true,\n"
        "  \"typed_renewed_unit_verified\": true,\n"
        "  \"ordinary_scalar_boundary_equality_claimed\": false,\n"
        "  \"compatibility_ab_transport_only\": true,\n"
        "  \"source_ab_definitionally_p2\": false,\n"
        "  \"exact_vm81_admission_verified\": true,\n"
        "  \"atomic_commit_verified\": true,\n"
        "  \"hash72_receipt_verified\": true,\n"
        "  \"hash216_proof_identity_verified\": true,\n"
        "  \"deterministic_replay_verified\": true,\n"
        "  \"source_reconstruction_verified\": true,\n"
        "  \"pass169_authority_verified\": true,\n"
        "  \"whole_equation_propagated\": true,\n"
        "  \"floating_point_authority\": false,\n"
        "  \"hash216_persistence_authority\": false,\n"
        "  \"canonical_global_symbol_environment_root\": \"%s\",\n"
        "  \"proof_hash216\": \"%s\",\n"
        "  \"transition_hash216\": \"%s\",\n"
        "  \"receipt_hash72\": \"%s\",\n"
        "  \"replay_hash72\": \"%s\"\n"
        "}\n",
        (unsigned int)execution.edge_proved_mask,
        (unsigned int)execution.gate_true_mask,
        (unsigned int)execution.P,
        (unsigned int)execution.p,
        (unsigned int)execution.q,
        (unsigned int)execution.delta,
        (unsigned int)execution.vm5184_address,
        (unsigned long long)execution.vm81_steps,
        (unsigned long long)execution.replay_vm81_steps,
        environment_root,
        execution.proof_hash216,
        execution.transition_hash216,
        execution.receipt_hash72,
        execution.replay_hash72);

    if (fclose(out) != 0)
        return 1;
    return 0;
}
