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

/*
 * Pass159's current repository implementation completes the source/front-end
 * pipeline through VMIR, interpreter receipt, replay receipt, and
 * interpreter/compiler semantic-root equivalence.  It does NOT currently
 * execute candidate state in the canonical VM81 kernel: its VMIR execution is
 * a foundation artifact with a fixed EXACT_PROGRAM marker and a fixed reported
 * step count.  Therefore VM81_PROOF is deliberately excluded here.
 */
#define HHS_EXACT_PASS219_PASS159_SOURCE_PIPELINE_REQUIRED \
    (HHS_EXACT_PASS219_STAGE_REQUIRED & ~HHS_EXACT_PASS219_STAGE_VM81_PROOF)

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

    /* I121.2 repair-forward truth classification. */
    uint32_t source_pipeline_verified;
    uint32_t pass159_vmir_effectful;
    uint32_t pass159_vm81_execution_observed;
    uint32_t pass159_replay_reexecuted;
    uint32_t pass159_step_counter_authoritative;
    uint32_t candidate_binding_supported;
    uint32_t canonical_vm81_proof_observed;
    uint32_t candidate_vm81_proof_required;
} HHSExactPass219Pass159ProofV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_pass159_proof_version(void);

/*
 * Verify the exact native 1.20 verbatim HARMONICODE source through the
 * inherited Pass159 source -> AST -> constraint graph -> HIR -> VMIR ->
 * interpreter/replay foundation pipeline.
 *
 * IMPORTANT: this function is a source-pipeline verifier, not a VM81 semantic
 * proof.  The repository census shows the current Pass159 interpreter hashes a
 * fixed VMIR artifact, reports a fixed step count, and replay re-wraps the
 * receipt rather than re-executing candidate state.  Consequently this bridge
 * MUST leave vm81_execution_verified and native_shared_invariant_proven false.
 * A separate exact candidate-bound VM81 adapter is required for those claims.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_pass159_prove_monolithic(
    HHSExactPass219Pass159ProofV1 *out_proof
);

#ifdef __cplusplus
}
#endif

#endif
