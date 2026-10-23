#ifndef HHS_PASS220_ORDERED4X4_RANK_I001_HANDOFF_V1_H
#define HHS_PASS220_ORDERED4X4_RANK_I001_HANDOFF_V1_H
#include "hhs_pass220_ordered4x4_i001_carrier_v1.h"
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define HHS220_RANK_I001_HANDOFF_VERSION UINT32_C(0x00010000)
/* Read-only, position-precise proof request. NOT a signed VM81 receipt. */
typedef struct HHS220RankI001HandoffV1 {
 uint32_t struct_size,version,unresolved_authority_mask;
 uint8_t candidate_only,carrier_and_rank_crosschecked;
 uint8_t ordered_s_v_roles_checked,all_162_positions_preserved;
 uint8_t deterministic_request_replay;
 uint8_t authenticated_rank,authenticated_native_action;
 uint8_t signed_parent_authenticated,mathematical_equality_proved;
 uint8_t signed_vm81_admitted,hash72_commit_authority;
 uint8_t hash216_commit_authority,canonical_vm81_mutation_authority;
 uint8_t reserved[2];
 uint16_t vm5184_address[2];
 uint8_t symbols[2],source_matrix_ids[2],tensor_left[2];
 uint8_t position_digits[2][HHS220_4X4_I001_CELLS];
 uint8_t source_sha256[32],parent_sha256[32],full_graph_sha256[32];
 uint8_t carrier_sha256[32],challenge_set_sha256[32];
 uint8_t binding_sha256[2][32],position_sha256[2][32],request_sha256[2][32];
 uint8_t handoff_sha256[32];
} HHS220RankI001HandoffV1;
/* Only a future trusted registered tensor/signed-state verifier may remove
 * authority blockers; this function never accepts claimed proof flags.
 * Output must not overlap any source, tensor or parent input.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_ordered4x4_rank_i001_handoff(
 const uint8_t *source,size_t source_bytes,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,
 HHS220RankI001HandoffV1 *out
);
#ifdef __cplusplus
}
#endif
#endif
