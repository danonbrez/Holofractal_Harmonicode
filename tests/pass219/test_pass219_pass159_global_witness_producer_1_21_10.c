#include "hhs_pass219_pass159_global_witness_provenance_1_21_10.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const uint8_t EXPECTED_SHA256[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SHA256_BYTES] = {
    0x33U, 0x15U, 0x64U, 0x1cU, 0x8dU, 0x6aU, 0xa9U, 0xfcU,
    0x4fU, 0x39U, 0x18U, 0xecU, 0xcdU, 0xa8U, 0xe3U, 0xa4U,
    0x0cU, 0x84U, 0x45U, 0xccU, 0x41U, 0x7aU, 0x65U, 0xe5U,
    0xdeU, 0xa6U, 0x83U, 0xf6U, 0x80U, 0x20U, 0xcfU, 0x53U
};

static const uint32_t EXPECTED_OFFSETS[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_GATE_COUNT] = {
    96U, 240U, 266U, 274U, 285U
};

static int read_file(const char *path, uint8_t **out, size_t *out_size) {
    FILE *fp;
    long size;
    uint8_t *buffer;
    if (path == NULL || out == NULL || out_size == NULL)
        return 0;
    fp = fopen(path, "rb");
    if (fp == NULL)
        return 0;
    if (fseek(fp, 0L, SEEK_END) != 0) {
        fclose(fp);
        return 0;
    }
    size = ftell(fp);
    if (size < 0 || fseek(fp, 0L, SEEK_SET) != 0) {
        fclose(fp);
        return 0;
    }
    buffer = (uint8_t *)malloc((size_t)size);
    if (buffer == NULL) {
        fclose(fp);
        return 0;
    }
    if (fread(buffer, 1U, (size_t)size, fp) != (size_t)size) {
        free(buffer);
        fclose(fp);
        return 0;
    }
    fclose(fp);
    *out = buffer;
    *out_size = (size_t)size;
    return 1;
}

static int nonzero_root(const uint8_t *root, size_t size) {
    size_t i;
    uint8_t aggregate = 0U;
    for (i = 0U; i < size; ++i)
        aggregate = (uint8_t)(aggregate | root[i]);
    return aggregate != 0U;
}

static int hash216_present(const char *value) {
    size_t i;
    if (value[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN; ++i) {
        if (value[i] == '\0')
            return 0;
    }
    return 1;
}

static int provenance_valid(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *value
) {
    const char *hashes[8];
    size_t i;
    if (value == NULL)
        return 0;
    if (value->struct_size != sizeof(*value) ||
        value->version != hhs_exact_pass219_pass159_global_witness_version() ||
        value->source_length != HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SOURCE_BYTES ||
        memcmp(value->combined_source_sha256, EXPECTED_SHA256, sizeof(EXPECTED_SHA256)) != 0 ||
        value->gate_count != HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_GATE_COUNT ||
        memcmp(value->gate_offsets, EXPECTED_OFFSETS, sizeof(EXPECTED_OFFSETS)) != 0)
        return 0;

    hashes[0] = value->source_hash216;
    hashes[1] = value->tokens_hash216;
    hashes[2] = value->cst_hash216;
    hashes[3] = value->ast_hash216;
    hashes[4] = value->type_environment_hash216;
    hashes[5] = value->constraint_graph_hash216;
    hashes[6] = value->hir_hash216;
    hashes[7] = value->vmir_hash216;
    for (i = 0U; i < 8U; ++i) {
        if (!hash216_present(hashes[i]))
            return 0;
    }

    if (!nonzero_root(value->global_symbol_environment_root,
                      sizeof(value->global_symbol_environment_root)))
        return 0;

    return value->source_identity_exact == 1U &&
           value->gate_occurrence_provenance_exact == 1U &&
           value->frontend_chain_complete == 1U &&
           value->source_root_lineage_exact == 1U &&
           value->pass159_whole_expression_provenance_verified == 1U &&
           value->boolean_gate_results_available == 0U &&
           value->membrane_input_ready == 0U &&
           value->pass169_whole_expression_authority_required == 1U &&
           value->canonical_monolithic_proof == 0U &&
           value->floating_point_authority == 0U &&
           value->vm81_mutation_authority == 0U &&
           value->hash72_commit_authority == 0U &&
           value->persistence_mutation_authority == 0U;
}

int main(void) {
    const char *path =
        "contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode";
    uint8_t *source = NULL;
    uint8_t *mutated = NULL;
    size_t source_size = 0U;
    HHSExactPass219Pass159GlobalWitnessProvenanceV1 first;
    HHSExactPass219Pass159GlobalWitnessProvenanceV1 second;
    HHSExactPass219Pass159GlobalWitnessProvenanceV1 rejected;
    HHSExactStatus status;
    int ok = 0;

    if (!read_file(path, &source, &source_size) ||
        source_size != HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SOURCE_BYTES)
        goto cleanup;

    status = hhs_exact_pass219_pass159_global_witness_produce(
        source, source_size, &first);
    if (status != HHS_EXACT_STATUS_OK || !provenance_valid(&first))
        goto cleanup;

    status = hhs_exact_pass219_pass159_global_witness_produce(
        source, source_size, &second);
    if (status != HHS_EXACT_STATUS_OK || !provenance_valid(&second))
        goto cleanup;
    if (memcmp(&first, &second, sizeof(first)) != 0)
        goto cleanup;

    if (hhs_exact_pass219_pass159_global_witness_produce(
            source,
            source_size - 1U,
            &rejected) != HHS_EXACT_STATUS_RANGE_ERROR)
        goto cleanup;

    mutated = (uint8_t *)malloc(source_size);
    if (mutated == NULL)
        goto cleanup;
    memcpy(mutated, source, source_size);
    mutated[0] ^= 1U;
    status = hhs_exact_pass219_pass159_global_witness_produce(
        mutated, source_size, &rejected);
    if (status != HHS_EXACT_STATUS_INVARIANT_FAILURE ||
        rejected.pass159_whole_expression_provenance_verified != 0U ||
        rejected.boolean_gate_results_available != 0U ||
        rejected.membrane_input_ready != 0U ||
        rejected.pass169_whole_expression_authority_required != 1U ||
        rejected.canonical_monolithic_proof != 0U ||
        rejected.vm81_mutation_authority != 0U ||
        rejected.hash72_commit_authority != 0U)
        goto cleanup;

    ok = 1;

cleanup:
    free(mutated);
    free(source);
    if (!ok) {
        fputs("PASS219 I121.10 Pass159 whole-expression witness provenance: FAIL\n", stderr);
        return 1;
    }
    puts("PASS219 I121.10 Pass159 whole-expression witness provenance: PASS");
    return 0;
}
