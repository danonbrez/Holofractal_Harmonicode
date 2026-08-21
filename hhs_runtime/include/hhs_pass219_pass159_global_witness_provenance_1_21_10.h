#ifndef HHS_PASS219_PASS159_GLOBAL_WITNESS_PROVENANCE_1_21_10_H
#define HHS_PASS219_PASS159_GLOBAL_WITNESS_PROVENANCE_1_21_10_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_VERSION_MINOR 21U
#define HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_VERSION_PATCH 10U
#define HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SOURCE_BYTES 632U
#define HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SHA256_BYTES 32U
#define HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_GATE_COUNT 5U
#define HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN 216U
#define HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_STRLEN 217U

typedef struct HHSExactPass219Pass159GlobalWitnessProvenanceV1 {
    uint32_t struct_size;
    uint32_t version;
    int32_t pass159_status;
    uint32_t source_length;
    uint8_t combined_source_sha256[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SHA256_BYTES];
    uint32_t gate_count;
    uint32_t gate_offsets[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_GATE_COUNT];

    char source_hash216[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_STRLEN];
    char tokens_hash216[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_STRLEN];
    char cst_hash216[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_STRLEN];
    char ast_hash216[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_STRLEN];
    char type_environment_hash216[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_STRLEN];
    char constraint_graph_hash216[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_STRLEN];
    char hir_hash216[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_STRLEN];
    char vmir_hash216[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_STRLEN];

    uint8_t global_symbol_environment_root[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SHA256_BYTES];

    uint8_t source_identity_exact;
    uint8_t gate_occurrence_provenance_exact;
    uint8_t frontend_chain_complete;
    uint8_t source_root_lineage_exact;
    uint8_t pass159_whole_expression_provenance_verified;
    uint8_t boolean_gate_results_available;
    uint8_t membrane_input_ready;
    uint8_t pass169_whole_expression_authority_required;
    uint8_t canonical_monolithic_proof;
    uint8_t floating_point_authority;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t persistence_mutation_authority;
    uint8_t reserved0[3];
} HHSExactPass219Pass159GlobalWitnessProvenanceV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_pass159_global_witness_version(void);

/*
 * Produce deterministic whole-expression provenance from the exact 632-byte
 * combined Harmonicode source using the inherited Pass159 front-end pipeline.
 *
 * This function does not evaluate the five Boolean gates and does not grant
 * Pass169, VM81, Hash72, persistence, or canonical-proof authority. A valid
 * result therefore keeps boolean_gate_results_available and membrane_input_ready
 * false even when the complete Pass159 provenance chain is verified.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_pass159_global_witness_produce(
    const uint8_t *source_bytes,
    size_t source_length,
    HHSExactPass219Pass159GlobalWitnessProvenanceV1 *out_provenance
);

#ifdef __cplusplus
}
#endif

#endif
