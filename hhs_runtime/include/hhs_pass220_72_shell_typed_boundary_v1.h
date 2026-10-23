#ifndef HHS_PASS220_72_SHELL_TYPED_BOUNDARY_V1_H
#define HHS_PASS220_72_SHELL_TYPED_BOUNDARY_V1_H
#include "hhs_pass220_72_shell_source_bound_v1.h"
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef enum {
 HHS_72_SHELL_PROOF_UNRESOLVED=0,
 HHS_72_SHELL_PROOF_INVALID=1,
 HHS_72_SHELL_PROOF_VERIFIED=2
} HHS72ShellProofStatus;
typedef struct {
 HHS72ShellProofStatus decision;
 uint32_t required_gates;
 uint32_t proven_gates;
 uint8_t source_sha256[32];
 uint8_t exact_residue_verified;
 uint8_t native_proof_admitted;
 uint8_t vm81_admitted;
} HHS72ShellProofResult;
/* Structural checkpoint only. This function cannot promote an opaque
   ordered chain to proof or mint VM81/Hash72/Hash216 authority. */
HHS72ShellProofStatus hhs_pass220_72_shell_typed_boundary(
 const uint8_t *source, size_t size, HHS72ShellProofResult *out);
#ifdef __cplusplus
}
#endif
#endif
