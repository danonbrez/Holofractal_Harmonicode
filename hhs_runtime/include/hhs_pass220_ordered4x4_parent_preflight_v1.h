#ifndef HHS_PASS220_ORDERED4X4_PARENT_PREFLIGHT_V1_H
#define HHS_PASS220_ORDERED4X4_PARENT_PREFLIGHT_V1_H

#include "hhs_pass220_ordered4x4_typed_bindings_v1.h"
#include "hhs_pass219_vm81_pqc_firewall_1_30.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct HHS220Ordered4x4ParentPreflightV1 {
 uint32_t struct_size;
 uint32_t version;
 uint8_t inherited_hash216_structure_verified;
 uint8_t all_216_indexes_verified;
 uint8_t s_parent_matches_verified_reference;
 uint8_t v_parent_matches_verified_reference;
 uint8_t bound_graph_executed;
 uint8_t deterministic_bound_graph_replay_verified;
 uint8_t parent_signed_authenticity_verified;
 uint8_t vm81_environment_signed_admission;
 uint8_t tensor_equality_proved;
 uint8_t hash72_commit_authority;
 uint8_t hash216_commit_authority;
 uint8_t canonical_vm81_mutation_authority;
 uint8_t reserved[4];
 uint8_t parent_transition_identity_sha256[32];
 uint8_t bound_result_root_sha256[32];
} HHS220Ordered4x4ParentPreflightV1;

/*
 * Pure, read-only verifier for a COMPLETE inherited Hash216 transition
 * reference. A reconstructible reference is NOT proof of signed origin.
 *
 * No trusted parent is manufactured by this API. Inputs must come from caller.
 * No VM81 state is mutated, no PQC signature is checked or signed, and no
 * Hash72/Hash216 commitment is ever issued here.
 */
HHS_EXACT_API HHSExactStatus
hhs_exact_pass220_ordered4x4_parent_preflight(
 const uint8_t *source, size_t source_size,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent_reference,
 HHS220Ordered4x4ParentPreflightV1 *out_preflight
);

#ifdef __cplusplus
}
#endif
#endif
