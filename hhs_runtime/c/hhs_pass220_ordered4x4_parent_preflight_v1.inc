/* Pure inherited Hash216 index/reference verifier for native 4x4 bindings.
 * A reconstructible reference is never a signed predecessor certificate.
 */
#include "../include/hhs_pass220_ordered4x4_parent_preflight_v1.h"
#include <openssl/crypto.h>
#include <openssl/sha.h>
#include <stdint.h>
#include <string.h>

HHSExactStatus hhs_exact_pass220_ordered4x4_parent_preflight(
 const uint8_t *source,size_t source_size,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent_reference,
 HHS220Ordered4x4ParentPreflightV1 *out_preflight
) {
 HHS220Ordered4x4BoundExecutionV1 bound;
 HHSExactStatus status;
 if (out_preflight==NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 memset(out_preflight,0,sizeof(*out_preflight));
 out_preflight->struct_size=(uint32_t)sizeof(*out_preflight);
 out_preflight->version=UINT32_C(0x00010000);
 if (source==NULL || s==NULL || v==NULL || parent_reference==NULL ||
     s->predecessor_hash216==NULL || v->predecessor_hash216==NULL)
  return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 if (s->predecessor_bytes!=HHS220_ORDERED4X4_PARENT_GLYPHS ||
     v->predecessor_bytes!=HHS220_ORDERED4X4_PARENT_GLYPHS)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 /* This verifier reconstructs all 216 SHA-256 token indexes from inherited
  * Hash72 lanes and verifies the complete source-bound transition structure.
  * It does not authenticate a caller's claim that those lanes were signed. */
 status=hhs_exact_pass219_vm81_pqc_hash216_reference_verify(parent_reference);
 if (status!=HHS_EXACT_STATUS_OK) return status;
 out_preflight->inherited_hash216_structure_verified=1U;
 out_preflight->all_216_indexes_verified=1U;
 if (CRYPTO_memcmp(s->predecessor_hash216,
         parent_reference->transition_identity216,
         HHS220_ORDERED4X4_PARENT_GLYPHS)!=0 ||
     CRYPTO_memcmp(v->predecessor_hash216,
         parent_reference->transition_identity216,
         HHS220_ORDERED4X4_PARENT_GLYPHS)!=0)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 out_preflight->s_parent_matches_verified_reference=1U;
 out_preflight->v_parent_matches_verified_reference=1U;
 if (SHA256((const uint8_t *)parent_reference->transition_identity216,
            HHS220_ORDERED4X4_PARENT_GLYPHS,
            out_preflight->parent_transition_identity_sha256)==NULL)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 status=hhs_exact_pass220_ordered4x4_execute_bound(
  source,source_size,s,v,&bound);
 if (status!=HHS_EXACT_STATUS_OK ||
     bound.source_identity_verified!=1U ||
     bound.ordered_type_graph_executed!=1U ||
     bound.deterministic_bound_graph_replay_verified!=1U ||
     bound.native_binding_authenticity_verified!=0U ||
     bound.equation_equality_proved!=0U ||
     bound.vm81_admission_executed!=0U ||
     bound.hash72_commit_authority!=0U ||
     bound.hash216_commit_authority!=0U ||
     bound.canonical_vm81_mutation_authority!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 out_preflight->bound_graph_executed=1U;
 out_preflight->deterministic_bound_graph_replay_verified=1U;
 memcpy(out_preflight->bound_result_root_sha256,bound.result_root_sha256,32U);
 return HHS_EXACT_STATUS_OK;
}
