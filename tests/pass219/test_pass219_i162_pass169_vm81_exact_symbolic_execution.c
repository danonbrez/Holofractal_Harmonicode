#include "hhs_pass219_i162_pass169_vm81_exact_symbolic_execution_1_23.h"
#include "hhs_pass219_pass159_global_witness_provenance_1_21_10.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int require(int condition, const char *message) {
    if (!condition) {
        fprintf(stderr, "FAIL: %s\n", message);
        return 0;
    }
    return 1;
}

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

int main(int argc, char **argv) {
    uint8_t source[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SOURCE_BYTES];
    size_t source_size = 0U;
    HHSExactPass219Pass159GlobalWitnessProvenanceV1 provenance;
    HHSExactPass219Pass159GlobalWitnessProvenanceV1 tampered;
    HHSExactPass219I162DescriptorV1 descriptor;
    HHSExactPass219I162ExecutionV1 execution;
    HHSExactPass219I162ExecutionV1 rejected;
    HHSExactPass219Pass169AuthorityProofV1 direct_proof;
    HHSExactPass219Pass169BindingResultV1 binding;
    HHSExactStatus status;
    size_t gate;

    if (argc != 2) {
        fprintf(stderr, "usage: %s <combined-source>\n", argv[0]);
        return 2;
    }

    if (!read_source(argv[1], source, sizeof(source), &source_size) ||
        !require(source_size == sizeof(source), "exact 632-byte combined source"))
        return 1;

    memset(&provenance, 0, sizeof(provenance));
    status = hhs_exact_pass219_pass159_global_witness_produce(
        source, source_size, &provenance);
    if (!require(status == HHS_EXACT_STATUS_OK, "Pass159 provenance producer") ||
        !require(provenance.pass159_whole_expression_provenance_verified == 1U,
                 "Pass159 whole-expression provenance"))
        return 1;

    memset(&descriptor, 0, sizeof(descriptor));
    status = hhs_exact_pass219_i162_descriptor(&descriptor);
    if (!require(status == HHS_EXACT_STATUS_OK, "I162 descriptor") ||
        !require(descriptor.edge_count == 10U, "ten source joins") ||
        !require(descriptor.gate_count == 5U, "five Boolean gates") ||
        !require(descriptor.required_edge_mask ==
                     HHS_EXACT_PASS219_I162_ALL_EDGE_MASK,
                 "all-edge mask") ||
        !require(descriptor.required_gate_mask ==
                     HHS_EXACT_PASS219_I162_ALL_GATE_MASK,
                 "all-gate mask") ||
        !require(descriptor.native_symbolic_verifier == 1U,
                 "native symbolic verifier") ||
        !require(descriptor.i161_typed_closure_preserved == 1U,
                 "I161 typed closure preserved") ||
        !require(descriptor.compatibility_ab_transport_only == 1U,
                 "compatibility A/B transport only") ||
        !require(descriptor.source_ab_definitionally_p2 == 0U,
                 "source A/B not P2 definitions") ||
        !require(descriptor.full_symbolic_uqcel_v1_promoted == 0U,
                 "legacy full-symbolic UQCEL not silently promoted") ||
        !require(descriptor.floating_point_authority == 0U,
                 "no floating-point authority") ||
        !require(descriptor.hash216_persistence_authority == 0U,
                 "no Hash216 persistence authority"))
        return 1;

    memset(&execution, 0, sizeof(execution));
    status = hhs_exact_pass219_i162_execute(&provenance, &execution);
    if (!require(status == HHS_EXACT_STATUS_OK, "I162 native execution") ||
        !require(execution.decision == HHS_EXACT_PASS219_I162_VERIFIED,
                 "I162 verified") ||
        !require(execution.edge_proved_mask ==
                     HHS_EXACT_PASS219_I162_ALL_EDGE_MASK,
                 "10/10 typed joins proved") ||
        !require(execution.gate_true_mask ==
                     HHS_EXACT_PASS219_I162_ALL_GATE_MASK,
                 "5/5 Boolean gates true") ||
        !require(execution.typed_scalar_zero_verified == 1U,
                 "typed scalar-zero closure") ||
        !require(execution.typed_renewed_unit_verified == 1U,
                 "typed renewed-unit closure") ||
        !require(execution.ordinary_scalar_boundary_equality_claimed == 0U,
                 "no ordinary scalar A=B") ||
        !require(execution.compatibility_ab_transport_only == 1U,
                 "VM81 A/B compatibility transport only") ||
        !require(execution.source_ab_definitionally_p2 == 0U,
                 "source boundaries remain non-P2 definitions") ||
        !require(execution.exact_vm81_admission_verified == 1U,
                 "VM81 admission verified") ||
        !require(execution.atomic_commit_verified == 1U,
                 "atomic commit verified") ||
        !require(execution.hash72_receipt_verified == 1U,
                 "Hash72 receipt verified") ||
        !require(execution.hash216_proof_identity_verified == 1U,
                 "Hash216 proof identity verified") ||
        !require(execution.deterministic_replay_verified == 1U,
                 "deterministic replay verified") ||
        !require(execution.source_reconstruction_verified == 1U,
                 "source reconstruction lineage verified") ||
        !require(execution.vm81_steps == 1U &&
                     execution.replay_vm81_steps == 1U,
                 "bounded VM81/replay steps") ||
        !require(strcmp(execution.receipt_hash72,
                        execution.replay_hash72) == 0,
                 "replay receipt identical") ||
        !require(strcmp(execution.proof_hash216,
                        execution.transition_hash216) != 0,
                 "proof and transition Hash216 identities distinct"))
        return 1;

    memset(&direct_proof, 0, sizeof(direct_proof));
    status = hhs_pass169_verify_combined_gate_authority_i162_1_23(
        &provenance, &direct_proof);
    if (!require(status == HHS_EXACT_STATUS_OK,
                 "I162 direct Pass169 provider") ||
        !require(direct_proof.whole_expression_constraint_graph_verified == 1U,
                 "whole constraint graph verified") ||
        !require(direct_proof.exact_vm81_admission_verified == 1U,
                 "proof VM81 admission") ||
        !require(direct_proof.atomic_commit_verified == 1U,
                 "proof atomic commit") ||
        !require(direct_proof.hash72_receipt_verified == 1U,
                 "proof Hash72 receipt") ||
        !require(direct_proof.hash216_proof_identity_verified == 1U,
                 "proof Hash216 identity") ||
        !require(direct_proof.deterministic_replay_verified == 1U,
                 "proof deterministic replay") ||
        !require(direct_proof.source_reconstruction_verified == 1U,
                 "proof source reconstruction") ||
        !require(direct_proof.shared_environment_revalidated == 1U,
                 "shared environment revalidated") ||
        !require(direct_proof.canonical_monolithic_proof == 1U,
                 "canonical monolithic proof") ||
        !require(direct_proof.floating_point_authority == 0U,
                 "provider no floating authority") ||
        !require(direct_proof.gate_count == 5U,
                 "provider gate count"))
        return 1;

    for (gate = 0U; gate < direct_proof.gate_count; ++gate) {
        if (!require(direct_proof.gates[gate].boolean_result == 1U,
                     "every provider gate true") ||
            !require(direct_proof.gates[gate].source_offset ==
                         provenance.gate_offsets[gate],
                     "gate source offset preserved"))
            return 1;
    }

    memset(&binding, 0, sizeof(binding));
    status = hhs_exact_pass219_pass169_bind_authority(&provenance, &binding);
    if (!require(status == HHS_EXACT_STATUS_OK,
                 "I121.11 binder with I162 provider") ||
        !require(binding.decision ==
                     HHS_EXACT_PASS219_PASS169_BINDING_PROPAGATE,
                 "binder propagates") ||
        !require(binding.reason_mask ==
                     HHS_EXACT_PASS219_PASS169_BINDING_REASON_NONE,
                 "binder no rejection reason") ||
        !require(binding.runtime_provider_available == 1U,
                 "runtime provider available") ||
        !require(binding.pass159_provenance_exact == 1U,
                 "Pass159 provenance exact") ||
        !require(binding.pass169_authority_verified == 1U,
                 "Pass169 authority verified") ||
        !require(binding.boolean_gate_results_available == 1U,
                 "Boolean gate results available") ||
        !require(binding.membrane_input_ready == 1U,
                 "membrane input ready") ||
        !require(binding.canonical_monolithic_proof == 1U,
                 "binder canonical monolithic proof") ||
        !require(binding.whole_equation_propagated == 1U,
                 "whole equation propagated") ||
        !require(binding.membrane_result.all_nested_boolean_gates_true == 1U,
                 "global membrane all gates true") ||
        !require(binding.membrane_result.whole_equation_propagated == 1U,
                 "global membrane propagated") ||
        !require(binding.vm81_mutation_authority == 0U &&
                     binding.hash72_commit_authority == 0U &&
                     binding.persistence_mutation_authority == 0U,
                 "read-only binder gains no mutation authority"))
        return 1;

    tampered = provenance;
    tampered.gate_offsets[4] += 1U;
    memset(&rejected, 0, sizeof(rejected));
    status = hhs_exact_pass219_i162_execute(&tampered, &rejected);
    if (!require(status == HHS_EXACT_STATUS_INVARIANT_FAILURE,
                 "tampered provenance fails closed") ||
        !require(rejected.decision == HHS_EXACT_PASS219_I162_REJECTED,
                 "tampered provenance rejected") ||
        !require(rejected.reason == HHS_EXACT_PASS219_I162_REASON_PROVENANCE,
                 "tampered provenance reason"))
        return 1;

    printf("PASS219 I162 Pass169 VM81 exact symbolic execution: PASS\n");
    return 0;
}
