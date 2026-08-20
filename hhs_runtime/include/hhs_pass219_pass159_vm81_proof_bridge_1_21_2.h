#ifndef HHS_PASS219_PASS159_VM81_PROOF_BRIDGE_1_21_2_H
#define HHS_PASS219_PASS159_VM81_PROOF_BRIDGE_1_21_2_H

#include "hhs_pass219_monolithic_constraint_abi_1_20.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_PASS159_PROOF_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_PASS159_PROOF_VERSION_MINOR 21U
#define HHS_EXACT_PASS219_PASS159_PROOF_VERSION_PATCH 2U

#define HHS_EXACT_PASS219_PASS159_PROOF_HASH216_STRLEN \
    HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN
#define HHS_EXACT_PASS219_PASS159_PROOF_HASH72_STRLEN HHS_EXACT_HASH72_STRLEN

typedef struct HHSExactPass219Pass159ProofV1 {
    uint32_t struct_size;
    uint32_t version;
    int32_t pass159_status;
    uint32_t completed_stage_mask;

    uint8_t source_bytes[HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH];

    char source_hash216[HHS_EXACT_PASS219_PASS159_PROOF_HASH216_STRLEN];
    char ast_hash216[HHS_EXACT_PASS219_PASS159_PROOF_HASH216_STRLEN];
    char constraint_graph_hash216[HHS_EXACT_PASS219_PASS159_PROOF_HASH216_STRLEN];
    char vmir_hash216[HHS_EXACT_PASS219_PASS159_PROOF_HASH216_STRLEN];
    char receipt_hash216[HHS_EXACT_PASS219_PASS159_PROOF_HASH216_STRLEN];
    char replay_hash216[HHS_EXACT_PASS219_PASS159_PROOF_HASH216_STRLEN];
    char semantic_root_hash216[HHS_EXACT_PASS219_PASS159_PROOF_HASH216_STRLEN];
    char replay_semantic_root_hash216[HHS_EXACT_PASS219_PASS159_PROOF_HASH216_STRLEN];

    char receipt_hash72[HHS_EXACT_PASS219_PASS159_PROOF_HASH72_STRLEN];
    char replay_hash72[HHS_EXACT_PASS219_PASS159_PROOF_HASH72_STRLEN];

    uint64_t vm81_steps;
    uint64_t replay_vm81_steps;

    uint32_t source_exact;
    uint32_t frontend_chain_complete;
    uint32_t vmir_complete;
    uint32_t interpret_ok;
    uint32_t replay_ok;
    uint32_t receipt_status_ok;
    uint32_t replay_receipt_status_ok;
    uint32_t receipt_hash72_valid;
    uint32_t replay_hash72_valid;
    uint32_t semantic_root_equal;
    uint32_t interpreter_compiler_match;
    uint32_t fallback_used;
    uint32_t committed;
    uint32_t replay_committed;
    uint32_t vm81_execution_verified;
    uint32_t native_shared_invariant_proven;
    uint32_t floating_point_authority;
    uint32_t vm81_mutation_authority;
    uint32_t hash72_commit_authority;
} HHSExactPass219Pass159ProofV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_pass159_proof_version(void);

/*
 * Executes the exact native 1.20 verbatim HARMONICODE source through the
 * inherited Pass159 source -> AST -> constraint graph -> HIR -> VMIR ->
 * interpreter/replay path. The bridge is read-only: it uses EXECUTE_AND_HOLD,
 * rejects fallback, requires a non-zero VM81 step witness, requires replay
 * semantic-root equality, and never claims VM81 mutation or Hash72 commit
 * authority of its own.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_pass159_prove_monolithic(
    HHSExactPass219Pass159ProofV1 *out_proof
);

#ifdef __cplusplus
}
#endif

#endif
