#include "hhs_pass219_pass169_gate_authority_binding_1_21_11.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef HHS_I12111_EXPECT_PROVIDER
#define HHS_I12111_EXPECT_PROVIDER 0
#endif

#if HHS_I12111_EXPECT_PROVIDER
void hhs_i12111_test_provider_set_mode(uint32_t mode);
#endif

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

static int require(int condition, const char *message) {
    if (!condition) {
        fprintf(stderr, "FAIL: %s\n", message);
        return 0;
    }
    return 1;
}

int main(int argc, char **argv) {
    uint8_t source[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SOURCE_BYTES];
    size_t source_size = 0U;
    HHSExactPass219Pass159GlobalWitnessProvenanceV1 provenance;
    HHSExactPass219Pass169BindingDescriptorV1 descriptor;
    HHSExactPass219Pass169BindingResultV1 result;
    HHSExactStatus status;

    if (argc != 2) {
        fprintf(stderr, "usage: %s <combined-source>\n", argv[0]);
        return 2;
    }
    if (!read_source(argv[1], source, sizeof(source), &source_size) ||
        !require(source_size == sizeof(source), "exact 632-byte source"))
        return 1;

    memset(&provenance, 0, sizeof(provenance));
    status = hhs_exact_pass219_pass159_global_witness_produce(
        source, source_size, &provenance);
    if (!require(status == HHS_EXACT_STATUS_OK, "I121.10 provenance producer") ||
        !require(provenance.pass159_whole_expression_provenance_verified == 1U,
                 "whole-expression provenance verified") ||
        !require(provenance.boolean_gate_results_available == 0U,
                 "I121.10 does not manufacture gate truth") ||
        !require(provenance.membrane_input_ready == 0U,
                 "I121.10 does not mark membrane ready"))
        return 1;

    memset(&descriptor, 0, sizeof(descriptor));
    status = hhs_exact_pass219_pass169_binding_descriptor(&descriptor);
    if (!require(status == HHS_EXACT_STATUS_OK, "binding descriptor") ||
        !require(descriptor.pass169_contract_anchor_is_authorization_only == 1U,
                 "Pass169 contract-only census preserved") ||
        !require(descriptor.linked_runtime_provider_required == 1U,
                 "linked provider required") ||
        !require(descriptor.test_fixture_is_authority == 0U,
                 "test fixture is never authority") ||
        !require(descriptor.pass159_can_substitute_for_pass169 == 0U,
                 "Pass159 cannot substitute") ||
        !require(descriptor.candidate_vm81_can_substitute_for_pass169 == 0U,
                 "candidate VM81 cannot substitute") ||
        !require(descriptor.canonical_monolithic_proof == 0U,
                 "descriptor cannot claim canonical proof") ||
        !require(descriptor.vm81_mutation_authority == 0U &&
                 descriptor.hash72_commit_authority == 0U &&
                 descriptor.persistence_mutation_authority == 0U,
                 "binder descriptor has no mutation authority"))
        return 1;

#if !HHS_I12111_EXPECT_PROVIDER
    if (!require(descriptor.linked_runtime_provider_available == 0U,
                 "production provider absent"))
        return 1;
    memset(&result, 0, sizeof(result));
    status = hhs_exact_pass219_pass169_bind_authority(&provenance, &result);
    if (!require(status == HHS_EXACT_STATUS_OK, "provider absence is valid unresolved state") ||
        !require(result.decision == HHS_EXACT_PASS219_PASS169_BINDING_UNRESOLVED,
                 "provider absence stays unresolved") ||
        !require(result.reason_mask == HHS_EXACT_PASS219_PASS169_BINDING_REASON_PROVIDER_UNAVAILABLE,
                 "provider unavailable reason") ||
        !require(result.runtime_provider_available == 0U,
                 "runtime provider unavailable") ||
        !require(result.pass159_provenance_exact == 1U,
                 "I121.10 provenance retained") ||
        !require(result.pass169_authority_verified == 0U,
                 "Pass169 authority not verified") ||
        !require(result.boolean_gate_results_available == 0U,
                 "Boolean gate results unavailable") ||
        !require(result.membrane_input_ready == 0U,
                 "membrane input not ready") ||
        !require(result.canonical_monolithic_proof == 0U,
                 "canonical proof unavailable") ||
        !require(result.whole_equation_propagated == 0U,
                 "whole equation not propagated") ||
        !require(result.vm81_mutation_authority == 0U &&
                 result.hash72_commit_authority == 0U &&
                 result.persistence_mutation_authority == 0U,
                 "binder result has no mutation authority"))
        return 1;
    printf("PASS219 I121.11 Pass169 binding no-provider fail-closed: PASS\n");
#else
    if (!require(descriptor.linked_runtime_provider_available == 1U,
                 "test-only linked provider visible"))
        return 1;

    hhs_i12111_test_provider_set_mode(0U);
    memset(&result, 0, sizeof(result));
    status = hhs_exact_pass219_pass169_bind_authority(&provenance, &result);
    if (!require(status == HHS_EXACT_STATUS_OK, "test provider all-true binding") ||
        !require(result.decision == HHS_EXACT_PASS219_PASS169_BINDING_PROPAGATE,
                 "all true authoritative packet propagates") ||
        !require(result.pass169_authority_verified == 1U,
                 "test packet exercises verified-authority branch") ||
        !require(result.boolean_gate_results_available == 1U,
                 "gate results available") ||
        !require(result.membrane_input_ready == 1U,
                 "membrane input ready") ||
        !require(result.canonical_monolithic_proof == 1U,
                 "provider proof packet classification retained") ||
        !require(result.whole_equation_propagated == 1U,
                 "whole equation propagated") ||
        !require(result.membrane_result.decision == HHS_EXACT_PASS219_GLOBAL_MEMBRANE_PROPAGATE,
                 "I121.9 propagate decision") ||
        !require(result.test_fixture_authority_claimed == 0U,
                 "binder never claims fixture authority") ||
        !require(result.vm81_mutation_authority == 0U &&
                 result.hash72_commit_authority == 0U &&
                 result.persistence_mutation_authority == 0U,
                 "binder itself has no mutation authority"))
        return 1;

    hhs_i12111_test_provider_set_mode(1U);
    memset(&result, 0, sizeof(result));
    status = hhs_exact_pass219_pass169_bind_authority(&provenance, &result);
    if (!require(status == HHS_EXACT_STATUS_OK, "false-gate proof packet is structurally valid") ||
        !require(result.decision == HHS_EXACT_PASS219_PASS169_BINDING_REJECT,
                 "false gate rejects") ||
        !require(result.reason_mask == HHS_EXACT_PASS219_PASS169_BINDING_REASON_MEMBRANE_REJECTED,
                 "membrane rejection reason") ||
        !require(result.pass169_authority_verified == 1U,
                 "authoritative rejection packet remains verified") ||
        !require(result.membrane_input_ready == 1U,
                 "complete rejected input was ready") ||
        !require(result.whole_equation_propagated == 0U,
                 "false gate blocks propagation") ||
        !require((result.membrane_result.reason_mask &
                  HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_BOOLEAN_GATE_FALSE) != 0U,
                 "I121.9 reports Boolean gate false"))
        return 1;

    hhs_i12111_test_provider_set_mode(2U);
    memset(&result, 0, sizeof(result));
    status = hhs_exact_pass219_pass169_bind_authority(&provenance, &result);
    if (!require(status == HHS_EXACT_STATUS_INVARIANT_FAILURE,
                 "tampered VMIR identity fails binding") ||
        !require(result.decision == HHS_EXACT_PASS219_PASS169_BINDING_REJECT,
                 "tampered VMIR rejects") ||
        !require(result.reason_mask ==
                     HHS_EXACT_PASS219_PASS169_BINDING_REASON_PIPELINE_IDENTITY_MISMATCH,
                 "pipeline mismatch reason") ||
        !require(result.pass169_authority_verified == 0U &&
                 result.membrane_input_ready == 0U,
                 "tampered identity never reaches membrane"))
        return 1;

    hhs_i12111_test_provider_set_mode(3U);
    memset(&result, 0, sizeof(result));
    status = hhs_exact_pass219_pass169_bind_authority(&provenance, &result);
    if (!require(status == HHS_EXACT_STATUS_INVARIANT_FAILURE,
                 "missing receipt authority fails binding") ||
        !require(result.decision == HHS_EXACT_PASS219_PASS169_BINDING_REJECT,
                 "missing receipt authority rejects") ||
        !require(result.reason_mask ==
                     HHS_EXACT_PASS219_PASS169_BINDING_REASON_AUTHORITY_EVIDENCE_INCOMPLETE,
                 "authority evidence incomplete reason") ||
        !require(result.pass169_authority_verified == 0U &&
                 result.membrane_input_ready == 0U,
                 "incomplete authority never reaches membrane"))
        return 1;

    printf("PASS219 I121.11 Pass169 binding test-provider plumbing: PASS\n");
#endif

    return 0;
}
