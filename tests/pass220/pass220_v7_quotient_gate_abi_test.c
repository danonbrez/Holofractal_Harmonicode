/* Native ABI regression, including adversarial fake proof flags.
 * Compiled against the actual inherited HNAN shared Runtime, no stubs.
 */
#include "hhs_pass220_v7_quotient_gate_v1.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static const uint8_t SOURCE[]=
    "(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))\n";
static int mode_test(HHS220V7QuotientInput *in,HHS220V7QuotientResult *out,
                     uint32_t mode,uint32_t decision,uint32_t reason){
    in->declared_mode=mode;
    if(hhs220_v7_quotient_preflight(in,out)!=1 ||
       out->decision!=decision || out->reason!=reason ||
       out->canonical_vm81_admission_verified!=0U ||
       out->hash72_commit_authority!=0U ||
       out->hash216_commit_authority!=0U ||
       out->canonical_persistence_mutated!=0U ||
       out->matrix_inverse_verified!=0U ||
       out->global_environment_verified!=0U)return 0;
    return 1;
}
int main(void){
    HHS220V7QuotientInput in;
    HHS220V7QuotientResult out;
    uint8_t mutation[sizeof(SOURCE)-1U];
    uint32_t mode;
    memset(&in,0,sizeof(in));
    in.struct_size=(uint32_t)sizeof(in);
    in.version=HHS220_V7_QUOTIENT_VERSION;
    in.source=SOURCE;
    in.source_bytes=sizeof(SOURCE)-1U;
    if(in.source_bytes!=HHS220_V7_SOURCE_BYTES)return 1;
    if(!mode_test(&in,&out,HHS220_V7_MODE_UNDECLARED,HHS220_V7_REJECT,
                  HHS220_V7_MODE_NOT_DECLARED) ||
       out.hnan_15_rule_graph_verified!=1U ||
       out.xy_yx_order_verified!=1U || out.zw_wz_order_verified!=1U ||
       out.native_hnan_rule_mask!=HHS220_V7_HNAN_ALL_RULES)return 1;
    puts("v7_undeclared_matrix_quotient=REJECTED");
    for(mode=1U;mode<=5U;mode++){
        if(!mode_test(&in,&out,mode,HHS220_V7_UNRESOLVED_PROVIDER,
                      HHS220_V7_NATIVE_QUOTIENT_PROVIDER_MISSING) ||
           out.typed_mode_lexically_registered!=1U ||
           out.native_quotient_provider_available!=0U)return 1;
    }
    puts("v7_five_pass169_modes=REGISTERED_PROVIDER_REQUIRED");
    if(!mode_test(&in,&out,6U,HHS220_V7_REJECT,HHS220_V7_UNKNOWN_MODE))return 1;
    in.declared_mode=HHS220_V7_DECLARED_FRACTAL_NESTING;
    in.commute_phase_products=1U;
    if(!mode_test(&in,&out,in.declared_mode,HHS220_V7_REJECT,
                  HHS220_V7_FORBIDDEN_TRANSFORMATION))return 1;
    in.commute_phase_products=0U;in.scalarize_ordered_carriers=1U;
    if(!mode_test(&in,&out,in.declared_mode,HHS220_V7_REJECT,
                  HHS220_V7_FORBIDDEN_TRANSFORMATION))return 1;
    in.scalarize_ordered_carriers=0U;in.cancel_global_denominator=1U;
    if(!mode_test(&in,&out,in.declared_mode,HHS220_V7_REJECT,
                  HHS220_V7_FORBIDDEN_TRANSFORMATION))return 1;
    in.cancel_global_denominator=0U;in.reverse_ordered_equality=1U;
    if(!mode_test(&in,&out,in.declared_mode,HHS220_V7_REJECT,
                  HHS220_V7_FORBIDDEN_TRANSFORMATION))return 1;
    in.reverse_ordered_equality=0U;
    in.claim_hash72_commit=1U;
    if(!mode_test(&in,&out,in.declared_mode,HHS220_V7_REJECT,
                  HHS220_V7_FABRICATED_COMMIT))return 1;
    in.claim_hash72_commit=0U;in.claim_vm81_commit=1U;
    if(!mode_test(&in,&out,in.declared_mode,HHS220_V7_REJECT,
                  HHS220_V7_FABRICATED_COMMIT))return 1;
    in.claim_vm81_commit=0U;in.claim_hash216_commit=1U;
    if(!mode_test(&in,&out,in.declared_mode,HHS220_V7_REJECT,
                  HHS220_V7_FABRICATED_COMMIT))return 1;
    in.claim_hash216_commit=0U;
    memcpy(mutation,SOURCE,sizeof(mutation));
    mutation[10]='x';  /* swaps the initial yx into xx, same length */
    in.source=mutation;
    if(!mode_test(&in,&out,in.declared_mode,HHS220_V7_REJECT,
                  HHS220_V7_SOURCE_MISMATCH))return 1;
    in.source=SOURCE;
    in.source_bytes--;
    if(!mode_test(&in,&out,in.declared_mode,HHS220_V7_REJECT,
                  HHS220_V7_SOURCE_MISMATCH))return 1;
    in.source_bytes++;
    in.version=0U;
    if(hhs220_v7_quotient_preflight(&in,&out)!=0 ||
       out.reason!=HHS220_V7_INVALID_CALL)return 1;
    puts("v7_negative_phase_source_and_fake_commits=REJECTED");
    puts("v7_canonical_vm81_admission=0");
    puts("v7_native_quotient_intent_abi=PASS");
    return 0;
}
