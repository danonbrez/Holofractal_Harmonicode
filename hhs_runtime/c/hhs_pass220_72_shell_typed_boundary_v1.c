#include "hhs_pass220_72_shell_typed_boundary_v1.h"
#include "hhs_pass220_72_shell_exact_residue_v1.h"
#include <string.h>
HHS72ShellProofStatus hhs_pass220_72_shell_typed_boundary(
 const uint8_t *source, size_t size, HHS72ShellProofResult *out) {
 HHS72ShellResult lowered;
 char numerator[160], denominator[160];
 static const char expected_n[]="775710873160901421359061468620360862729920180854006643986760192036";
 static const char expected_d[]="3110094060648844770831880556173301180945943326884396380767822265625";
 HHS72ShellStatus st;
 if(out==NULL) return HHS_72_SHELL_PROOF_INVALID;
 memset(out,0,sizeof(*out));
 out->required_gates=4U;
 st=hhs_pass220_72_shell_lower(source,size,&lowered);
 if(st!=HHS_72_SHELL_STRUCTURAL_ONLY) {
   out->decision=HHS_72_SHELL_PROOF_INVALID;
   return out->decision;
 }
 if(!hhs_pass220_72_shell_exact_residue(numerator,sizeof(numerator),denominator,sizeof(denominator)) || strcmp(numerator,expected_n)!=0 || strcmp(denominator,expected_d)!=0) {
   out->decision=HHS_72_SHELL_PROOF_INVALID;
   return out->decision;
 }
 out->exact_residue_verified=1U;
 memcpy(out->source_sha256,lowered.source_sha256,32);
 /* Current source is valid but native ordered semantics are unresolved.
    No byte-level or scalar-projection evidence is promoted to proof. */
 out->decision=HHS_72_SHELL_PROOF_UNRESOLVED;
 return out->decision;
}
