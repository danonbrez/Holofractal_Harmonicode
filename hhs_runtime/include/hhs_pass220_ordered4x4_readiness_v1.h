#ifndef HHS_PASS220_ORDERED4X4_READINESS_V1_H
#define HHS_PASS220_ORDERED4X4_READINESS_V1_H
#include "hhs_pass220_ordered4x4_rank_challenge_v1.h"
#include <stdint.h>
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif

#define HHS220_4X4_PREFLIGHT_SOURCE              UINT32_C(0x0001)
#define HHS220_4X4_PREFLIGHT_HASH216_INDEX       UINT32_C(0x0002)
#define HHS220_4X4_PREFLIGHT_TYPED_GRAPH         UINT32_C(0x0004)
#define HHS220_4X4_PREFLIGHT_ADDRESS_PHASE       UINT32_C(0x0008)
#define HHS220_4X4_PREFLIGHT_GRAPH_REPLAY        UINT32_C(0x0010)
#define HHS220_4X4_PREFLIGHT_RANK_CHALLENGE      UINT32_C(0x0020)
#define HHS220_4X4_PREFLIGHT_ALL                 UINT32_C(0x003F)

#define HHS220_4X4_BLOCK_SIGNED_PARENT           UINT32_C(0x0001)
#define HHS220_4X4_BLOCK_AUTHENTICATED_RANK       UINT32_C(0x0002)
#define HHS220_4X4_BLOCK_FULL_PHASE_ACTION       UINT32_C(0x0004)
#define HHS220_4X4_BLOCK_MATRIX_VALUES           UINT32_C(0x0008)
#define HHS220_4X4_BLOCK_QUOTIENT_VALUE          UINT32_C(0x0010)
#define HHS220_4X4_BLOCK_NEGATIVE_FOUR_VALUE     UINT32_C(0x0020)
#define HHS220_4X4_BLOCK_EQUALITY_PROOF          UINT32_C(0x0040)
#define HHS220_4X4_BLOCK_SIGNED_VM81_ADMISSION   UINT32_C(0x0080)
#define HHS220_4X4_BLOCK_ALL                     UINT32_C(0x00FF)

typedef enum HHS220Ordered4x4ReadinessDecisionV1 {
 HHS220_4X4_READINESS_INVALID=0,
 HHS220_4X4_READINESS_BLOCKED=1,
 HHS220_4X4_READINESS_READY=2
} HHS220Ordered4x4ReadinessDecisionV1;

typedef struct HHS220Ordered4x4ReadinessV1 {
 uint32_t struct_size;
 uint32_t version;
 uint32_t decision;
 uint32_t preflight_verified_mask;
 uint32_t required_preflight_mask;
 uint32_t missing_authority_mask;
 uint32_t required_authority_mask;
 uint32_t challenge_count;
 uint8_t candidate_only;
 uint8_t phase_address_is_not_full_tensor_phase;
 uint8_t structural_hash216_is_not_signed_parent;
 uint8_t declared_rank_is_not_authenticated_rank;
 uint8_t result_is_not_math_equality;
 uint8_t deterministic_report_replay_verified;
 uint8_t signed_vm81_admission_executed;
 uint8_t hash72_commit_authority;
 uint8_t hash216_commit_authority;
 uint8_t canonical_vm81_mutation_authority;
 uint8_t reserved[2];
 uint8_t source_sha256[32];
 uint8_t parent_reference_sha256[32];
 uint8_t proof_challenge_set_sha256[32];
 uint8_t full_graph_sha256[32];
 uint8_t report_identity_sha256[32];
} HHS220Ordered4x4ReadinessV1;

/* Observational read-only, externally callable. It does not accept caller
 * asserted "verified" bits, ranks, signed receipts or alleged matrix values.
 * A valid source candidate returns STATUS_OK with decision BLOCKED.
 * A malformed candidate fails closed with zero verified preflight bits.
 * READY must never be produced until a future trusted native verifier
 * implements every missing proof; this version has no such verifier.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_ordered4x4_readiness(
 const uint8_t *source,size_t source_size,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,
 HHS220Ordered4x4ReadinessV1 *out_readiness
);
#ifdef __cplusplus
}
#endif
#endif
