#include "hhs_pass219_pass169_runtime_provider_1_21_13.h"
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
    if (length < 0L || (unsigned long)length > (unsigned long)capacity ||
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
    HHSExactPass219Pass169RuntimeProviderDescriptorV1 provider;
    HHSExactPass219Pass169BindingDescriptorV1 binder_descriptor;
    HHSExactPass219Pass169BindingResultV1 result;
    HHSExactPass219Pass169AuthorityProofV1 direct_proof;
    HHSExactStatus status;

    if (argc != 2) {
        fprintf(stderr, "usage: %s <combined-source>\n", argv[0]);
        return 2;
    }

    if (!read_source(argv[1], source, sizeof(source), &source_size) ||
        !require(source_size == sizeof(source), "exact 632-byte combined source"))
        return 1;

    memset(&provenance, 0, sizeof(provenance));
    status = hhs_exact_pass219_pass159_global_witness_produce(
        source, source_size, &provenance
    );
    if (!require(status == HHS_EXACT_STATUS_OK, "Pass159 provenance producer") ||
        !require(provenance.pass159_whole_expression_provenance_verified == 1U,
                 "whole-expression provenance verified"))
        return 1;

    memset(&provider, 0, sizeof(provider));
    status = hhs_exact_pass219_pass169_runtime_provider_descriptor(&provider);
    if (!require(status == HHS_EXACT_STATUS_OK, "provider descriptor") ||
        !require(provider.production_provider_implementation_present == 1U,
                 "production provider implementation present") ||
        !require(provider.non_test_provider == 1U, "non-test provider") ||
        !require(provider.pass159_provenance_required == 1U,
                 "Pass159 provenance required") ||
        !require(provider.full_symbolic_uqcel_probe_required == 1U,
                 "full-symbolic probe required") ||
        !require(provider.full_symbolic_uqcel_supported == 0U,
                 "full-symbolic UQCEL still unresolved") ||
        !require(provider.local_p_snapshot_binding_supported == 0U,
                 "local P binding not fabricated") ||
        !require(provider.canonical_gate_vector_export_supported == 0U,
                 "canonical gate export not fabricated") ||
        !require(provider.canonical_authority_available == 0U,
                 "canonical authority unavailable") ||
        !require(provider.test_fixture_authority == 0U,
                 "provider is not test-fixture authority") ||
        !require(provider.floating_point_authority == 0U,
                 "no floating-point authority"))
        return 1;

    memset(&direct_proof, 0, sizeof(direct_proof));
    status = hhs_pass169_verify_combined_gate_authority_1_21_11(
        &provenance, &direct_proof
    );
    if (!require(status == HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN,
                 "provider returns unsupported full-symbolic domain") ||
        !require(direct_proof.struct_size == sizeof(direct_proof),
                 "provider emits bounded proof shell") ||
        !require(memcmp(direct_proof.combined_source_sha256,
                        provenance.combined_source_sha256,
                        sizeof(direct_proof.combined_source_sha256)) == 0,
                 "provider preserves combined source identity") ||
        !require(strcmp(direct_proof.source_hash216, provenance.source_hash216) == 0,
                 "provider preserves source Hash216") ||
        !require(strcmp(direct_proof.constraint_graph_hash216,
                        provenance.constraint_graph_hash216) == 0,
                 "provider preserves graph Hash216") ||
        !require(direct_proof.canonical_monolithic_proof == 0U,
                 "direct provider does not claim canonical proof") ||
        !require(direct_proof.exact_vm81_admission_verified == 0U,
                 "direct provider does not claim VM81 admission"))
        return 1;

    memset(&binder_descriptor, 0, sizeof(binder_descriptor));
    status = hhs_exact_pass219_pass169_binding_descriptor(&binder_descriptor);
    if (!require(status == HHS_EXACT_STATUS_OK, "binder descriptor") ||
        !require(binder_descriptor.linked_runtime_provider_available == 1U,
                 "I121.11 sees linked production provider") ||
        !require(binder_descriptor.test_fixture_is_authority == 0U,
                 "I121.11 fixture authority remains false"))
        return 1;

    memset(&result, 0, sizeof(result));
    status = hhs_exact_pass219_pass169_bind_authority(&provenance, &result);
    if (!require(status == HHS_EXACT_STATUS_OK,
                 "unresolved full-symbolic state is valid fail-closed result") ||
        !require(result.decision ==
                     HHS_EXACT_PASS219_PASS169_BINDING_UNRESOLVED,
                 "binder remains unresolved") ||
        !require(result.reason_mask ==
                     HHS_EXACT_PASS219_PASS169_BINDING_REASON_FULL_SYMBOLIC_UNRESOLVED,
                 "binder reports exact full-symbolic reason") ||
        !require(result.runtime_provider_available == 1U,
                 "provider absence blocker cleared") ||
        !require(result.pass159_provenance_exact == 1U,
                 "Pass159 provenance remains exact") ||
        !require(result.pass169_authority_verified == 0U,
                 "Pass169 truth not manufactured") ||
        !require(result.boolean_gate_results_available == 0U,
                 "Boolean gate truth unavailable") ||
        !require(result.membrane_input_ready == 0U,
                 "membrane input remains blocked") ||
        !require(result.canonical_monolithic_proof == 0U,
                 "canonical monolithic proof remains false") ||
        !require(result.whole_equation_propagated == 0U,
                 "whole equation cannot propagate") ||
        !require(result.vm81_mutation_authority == 0U &&
                 result.hash72_commit_authority == 0U &&
                 result.persistence_mutation_authority == 0U,
                 "binder gains no mutation authority"))
        return 1;

    printf("PASS219 I155 production provider residual closure: PASS\n");
    return 0;
}
