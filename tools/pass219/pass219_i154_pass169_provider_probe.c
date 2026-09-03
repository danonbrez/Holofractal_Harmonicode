#include "hhs_pass219_pass169_gate_authority_binding_1_21_11.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef HHS_I154_TEST_FIXTURE_PROVIDER
#define HHS_I154_TEST_FIXTURE_PROVIDER 0
#endif

#if HHS_I154_TEST_FIXTURE_PROVIDER
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

static const char *decision_name(uint32_t decision) {
    if (decision == HHS_EXACT_PASS219_PASS169_BINDING_PROPAGATE)
        return "PROPAGATE";
    if (decision == HHS_EXACT_PASS219_PASS169_BINDING_REJECT)
        return "REJECT";
    return "UNRESOLVED";
}

static const char *classification_name(
    const HHSExactPass219Pass169BindingResultV1 *result
) {
#if HHS_I154_TEST_FIXTURE_PROVIDER
    (void)result;
    return "TEST_FIXTURE_PROVIDER_DIAGNOSTIC_ONLY";
#else
    if (result->runtime_provider_available == 0U)
        return "BLOCKED_PROVIDER_UNAVAILABLE";
    if (result->reason_mask ==
        HHS_EXACT_PASS219_PASS169_BINDING_REASON_FULL_SYMBOLIC_UNRESOLVED)
        return "BLOCKED_FULL_SYMBOLIC_RESIDUAL";
    if (result->pass169_authority_verified == 0U)
        return "BLOCKED_PASS169_AUTHORITY_NOT_VERIFIED";
    return "BLOCKED_I154_LOCAL_SNAPSHOT_BINDING_EXTENSION_MISSING";
#endif
}

int main(int argc, char **argv) {
    uint8_t source[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SOURCE_BYTES];
    size_t source_size = 0U;
    HHSExactPass219Pass159GlobalWitnessProvenanceV1 provenance;
    HHSExactPass219Pass169BindingDescriptorV1 descriptor;
    HHSExactPass219Pass169BindingResultV1 result;
    HHSExactStatus status;
    FILE *out;

    if (argc != 3) {
        fprintf(stderr, "usage: %s <combined-source> <output-json>\n", argv[0]);
        return 2;
    }

    if (!read_source(argv[1], source, sizeof(source), &source_size) ||
        source_size != sizeof(source)) {
        fprintf(stderr, "I154 provider probe: exact 632-byte source required\n");
        return 1;
    }

    memset(&provenance, 0, sizeof(provenance));
    status = hhs_exact_pass219_pass159_global_witness_produce(
        source, source_size, &provenance
    );
    if (status != HHS_EXACT_STATUS_OK) {
        fprintf(stderr, "I154 provider probe: Pass159 provenance failed\n");
        return 1;
    }

    memset(&descriptor, 0, sizeof(descriptor));
    status = hhs_exact_pass219_pass169_binding_descriptor(&descriptor);
    if (status != HHS_EXACT_STATUS_OK) {
        fprintf(stderr, "I154 provider probe: binding descriptor failed\n");
        return 1;
    }

#if HHS_I154_TEST_FIXTURE_PROVIDER
    hhs_i12111_test_provider_set_mode(0U);
#endif

    memset(&result, 0, sizeof(result));
    status = hhs_exact_pass219_pass169_bind_authority(&provenance, &result);
    if (status != HHS_EXACT_STATUS_OK &&
        result.decision != HHS_EXACT_PASS219_PASS169_BINDING_REJECT) {
        fprintf(stderr, "I154 provider probe: binding call failed\n");
        return 1;
    }

    out = fopen(argv[2], "wb");
    if (out == NULL) {
        fprintf(stderr, "I154 provider probe: cannot open output\n");
        return 1;
    }

    fprintf(out,
        "{\n"
        "  \"schema\": \"HHS_PASS219_I154_PASS169_PROVIDER_PROBE_V1\",\n"
        "  \"pass\": 219,\n"
        "  \"iteration\": \"I154\",\n"
        "  \"provider_origin\": \"%s\",\n"
        "  \"classification\": \"%s\",\n"
        "  \"runtime_provider_available\": %s,\n"
        "  \"binding_decision\": \"%s\",\n"
        "  \"binding_reason_mask\": %u,\n"
        "  \"pass159_provenance_exact\": %s,\n"
        "  \"pass169_authority_verified\": %s,\n"
        "  \"boolean_gate_results_available\": %s,\n"
        "  \"membrane_input_ready\": %s,\n"
        "  \"canonical_monolithic_proof\": %s,\n"
        "  \"whole_equation_propagated\": %s,\n"
        "  \"test_fixture_is_authority\": false,\n"
        "  \"i12111_legacy_binding_complete\": %s,\n"
        "  \"i154_local_snapshot_binding_available\": false,\n"
        "  \"i154_gate_vector_export_available\": false,\n"
        "  \"i154_planner_input_ready\": false,\n"
        "  \"floating_point_authority\": false,\n"
        "  \"vm81_mutation_authority\": false,\n"
        "  \"hash72_commit_authority\": false,\n"
        "  \"persistence_mutation_authority\": false,\n"
        "  \"result\": \"PASS\"\n"
        "}\n",
#if HHS_I154_TEST_FIXTURE_PROVIDER
        "TEST_FIXTURE_PASS169_VM81_PROVIDER",
#else
        "REPOSITORY_PRODUCTION_PASS169_VM81_PROVIDER",
#endif
        classification_name(&result),
        result.runtime_provider_available ? "true" : "false",
        decision_name(result.decision),
        result.reason_mask,
        result.pass159_provenance_exact ? "true" : "false",
        result.pass169_authority_verified ? "true" : "false",
        result.boolean_gate_results_available ? "true" : "false",
        result.membrane_input_ready ? "true" : "false",
        result.canonical_monolithic_proof ? "true" : "false",
        result.whole_equation_propagated ? "true" : "false",
        (result.runtime_provider_available &&
         result.pass169_authority_verified &&
         result.boolean_gate_results_available &&
         result.membrane_input_ready &&
         result.canonical_monolithic_proof) ? "true" : "false"
    );

    if (fclose(out) != 0)
        return 1;

    return 0;
}
