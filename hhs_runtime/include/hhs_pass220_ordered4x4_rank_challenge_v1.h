#ifndef HHS_PASS220_ORDERED4X4_RANK_CHALLENGE_V1_H
#define HHS_PASS220_ORDERED4X4_RANK_CHALLENGE_V1_H
#include "hhs_pass220_ordered4x4_full_graph_v1.h"
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

#define HHS220_4X4_RANK_OBLIGATIONS 2U
#define HHS220_4X4_RANK_REQUIRED_FLAGS UINT32_C(0x0000007F)
#define HHS220_4X4_RANK_PROOF_BINDING_VERSION UINT32_C(0x00010000)

/*
 * The seven mandatory proof requirements are obligations, not claims:
 * 1. canonical 5184-character object/type/VM81 address correspondence;
 * 2. inherited registered tensor definition and exact rank/shape provenance;
 * 3. kernel-verified ordered x/y/z/w phase action and source-matrix operand side;
 * 4. authorized MatrixTimes input/output contracts (not scalar broadcast);
 * 5. canonical source/Hash216 ancestry and lineage;
 * 6. native ordered quotient/invertibility and (-4) power compatibility;
 * 7. complete source equality proof under singleton signed VM81 admission.
 */
typedef struct HHS220Ordered4x4RankObligationV1 {
 uint32_t struct_size;
 uint32_t version;
 uint32_t required_flags;
 uint16_t vm5184_address;
 uint8_t symbol;
 uint8_t source_matrix_id;
 uint8_t tensor_left_operand;
 uint8_t source_matrix_rows;
 uint8_t source_matrix_columns;
 uint8_t rank_proved;
 uint8_t phase_action_proved;
 uint8_t definition_source_authenticated;
 uint8_t signed_vm81_state_authenticated;
 uint8_t matrix_action_value_authorized;
 uint8_t reserved[2];
 uint8_t binding_root_sha256[32];
 uint8_t native_phase_address_root_sha256[32];
 uint8_t ordered_matrix_action_root_sha256[32];
 uint8_t challenge_root_sha256[32];
} HHS220Ordered4x4RankObligationV1;

typedef struct HHS220Ordered4x4RankChallengeV1 {
 uint32_t struct_size;
 uint32_t version;
 uint32_t challenge_count;
 uint32_t required_flags;
 uint8_t complete_expression_source_verified;
 uint8_t hash216_parent_index_structure_verified;
 uint8_t full_native_graph_constructed;
 uint8_t native_phase_addresses_verified;
 uint8_t complete_proof_challenges_derived;
 uint8_t deterministic_challenges_replayed;
 uint8_t registered_rank_witness_verified;
 uint8_t native_action_semantics_verified;
 uint8_t mathematical_equality_proved;
 uint8_t signed_vm81_admission_executed;
 uint8_t hash72_commit_authority;
 uint8_t hash216_commit_authority;
 uint8_t canonical_vm81_mutation_authority;
 uint8_t reserved[3];
 HHS220Ordered4x4RankObligationV1 obligations[HHS220_4X4_RANK_OBLIGATIONS];
 uint8_t source_sha256[32];
 uint8_t parent_reference_sha256[32];
 uint8_t full_graph_root_sha256[32];
 uint8_t challenge_set_root_sha256[32];
} HHS220Ordered4x4RankChallengeV1;

/* Read-only preparation for an inherited verifier (e.g., registered Pass158
 * tensor-definition/shape + VM81 authenticated object and phase action).
 * No response/proof is accepted by this API. In particular, callers MUST NOT
 * turn a presented 5184 string, shape metadata, or digest into rank authority.
 */
HHS_EXACT_API HHSExactStatus
hhs_exact_pass220_ordered4x4_rank_challenge(
 const uint8_t *source, size_t source_bytes,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,
 HHS220Ordered4x4RankChallengeV1 *out_challenge
);
#ifdef __cplusplus
}
#endif
#endif
