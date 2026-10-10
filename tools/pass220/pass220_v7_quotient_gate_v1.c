/* HHS Pass220 V7: native ordered matrix quotient INTENT checker.
 * Source-specific / exact byte matching; 15 native HNAN rules and rule 12/13
 * checks; Pass169 registered operator spellings. Fail-closed until a genuine
 * canonical environment-bound quotient execution provider exists.
 * Source numbers 5184/72^2 do NOT identify the matrix with scalar 1.
 */
#include "hhs_pass220_v7_quotient_gate_v1.h"
#include "hhs_pass219_lane5_hnan_global_constraint_1_63.h"
#include <openssl/sha.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const uint8_t SOURCE[]=
    "(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))\n";

const char *hhs220_v7_mode_name(uint32_t mode){
    switch(mode){
        case HHS220_V7_MODE_UNDECLARED:return "UNDECLARED";
        case HHS220_V7_ELEMENTWISE_SCALAR_QUOTIENT:return "ELEMENTWISE_SCALAR_QUOTIENT";
        case HHS220_V7_RIGHT_MATRIX_SOLVE:return "RIGHT_MATRIX_SOLVE";
        case HHS220_V7_LEFT_MATRIX_SOLVE:return "LEFT_MATRIX_SOLVE";
        case HHS220_V7_SCALAR_DENOMINATOR:return "SCALAR_DENOMINATOR";
        case HHS220_V7_DECLARED_FRACTAL_NESTING:return "DECLARED_FRACTAL_NESTING";
        default:return "UNKNOWN_MODE";
    }
}
static void reject(HHS220V7QuotientResult *r,uint32_t reason){
    r->decision=HHS220_V7_REJECT;
    r->reason=reason;
}
static int native_order_relation(uint32_t rule_id){
    HHSExactPass219HNANRuleV1 rule;
    HHSExactPass219HNANClaimV1 claim;
    HHSExactPass219HNANResolutionV1 result;
    memset(&rule,0,sizeof(rule));
    memset(&claim,0,sizeof(claim));
    memset(&result,0,sizeof(result));
    if(hhs_exact_pass219_hnan_global_rule(rule_id,&rule)!=HHS_EXACT_STATUS_OK ||
       rule.source_order_required!=1U || rule.typed_identity_required!=1U ||
       rule.scalar_equality_authority!=0U || rule.commutation_authority!=0U ||
       rule.cancellation_authority!=0U)return 0;
    claim.struct_size=(uint32_t)sizeof(claim);
    claim.version=HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION;
    claim.rule_id=rule.rule_id;
    claim.lhs_node=rule.lhs_node;
    claim.rhs_node=rule.rhs_node;
    claim.relation=rule.relation;
    claim.source_order_preserved=1U;
    claim.typed_identity_preserved=1U;
    if(hhs_exact_pass219_hnan_resolve(&claim,&result)!=HHS_EXACT_STATUS_OK ||
       result.decision!=HHS_EXACT_HNAN_DECISION_VERIFIED)return 0;
    claim.commutation_requested=1U;
    if(hhs_exact_pass219_hnan_resolve(&claim,&result)!=HHS_EXACT_STATUS_OK ||
       result.decision!=HHS_EXACT_HNAN_DECISION_REJECTED ||
       result.reason!=HHS_EXACT_HNAN_REASON_COMMUTATION)return 0;
    claim.commutation_requested=0U;
    claim.scalar_substitution_requested=1U;
    if(hhs_exact_pass219_hnan_resolve(&claim,&result)!=HHS_EXACT_STATUS_OK ||
       result.decision!=HHS_EXACT_HNAN_DECISION_REJECTED ||
       result.reason!=HHS_EXACT_HNAN_REASON_SCALARIZATION)return 0;
    claim.scalar_substitution_requested=0U;
    claim.equality_reversal_requested=1U;
    if(hhs_exact_pass219_hnan_resolve(&claim,&result)!=HHS_EXACT_STATUS_OK ||
       result.decision!=HHS_EXACT_HNAN_DECISION_REJECTED ||
       result.reason!=HHS_EXACT_HNAN_REASON_EQUALITY_REVERSAL)return 0;
    return 1;
}
int hhs220_v7_quotient_preflight(const HHS220V7QuotientInput *input,
                                HHS220V7QuotientResult *out){
    HHSExactPass219HNANGlobalReceiptV1 native;
    if(out==NULL)return 0;
    memset(out,0,sizeof(*out));
    out->struct_size=(uint32_t)sizeof(*out);
    out->version=HHS220_V7_QUOTIENT_VERSION;
    reject(out,HHS220_V7_INVALID_CALL);
    if(input==NULL || input->struct_size!=sizeof(*input) ||
       input->version!=HHS220_V7_QUOTIENT_VERSION ||
       input->source==NULL)return 0;
    out->declared_mode=input->declared_mode;
    if(input->source_bytes!=sizeof(SOURCE)-1U ||
       memcmp(input->source,SOURCE,sizeof(SOURCE)-1U)!=0){
        reject(out,HHS220_V7_SOURCE_MISMATCH);return 1;
    }
    out->source_exact=1U;
    if(SHA256(input->source,input->source_bytes,out->source_sha256)==NULL){
        reject(out,HHS220_V7_SOURCE_MISMATCH);return 1;
    }
    if(input->declared_mode>HHS220_V7_DECLARED_FRACTAL_NESTING){
        reject(out,HHS220_V7_UNKNOWN_MODE);return 1;
    }
    if(input->claim_vm81_commit || input->claim_hash72_commit ||
       input->claim_hash216_commit){
        reject(out,HHS220_V7_FABRICATED_COMMIT);return 1;
    }
    if(input->scalarize_ordered_carriers || input->commute_phase_products ||
       input->cancel_global_denominator || input->reverse_ordered_equality){
        reject(out,HHS220_V7_FORBIDDEN_TRANSFORMATION);return 1;
    }
    memset(&native,0,sizeof(native));
    if(hhs_exact_pass219_hnan_global_system_verify(&native)!=HHS_EXACT_STATUS_OK ||
       native.decision!=HHS_EXACT_HNAN_DECISION_VERIFIED ||
       native.verified_rule_mask!=HHS220_V7_HNAN_ALL_RULES ||
       native.candidate_only!=1U ||
       native.global_delta_denominator_preserved!=1U ||
       native.delta_cancellation_forbidden!=1U ||
       native.xy_yx_distinct!=1U || native.zw_wz_distinct!=1U ||
       native.canonical_vm81_mutation_authority!=0U ||
       native.canonical_hash72_authority!=0U ||
       native.canonical_hash216_authority!=0U){
        reject(out,HHS220_V7_HNAN_AUTHORITY_FAILED);return 1;
    }
    out->hnan_15_rule_graph_verified=1U;
    out->native_hnan_rule_mask=native.verified_rule_mask;
    if(!native_order_relation(12U) || !native_order_relation(13U)){
        reject(out,HHS220_V7_HNAN_AUTHORITY_FAILED);return 1;
    }
    out->xy_yx_order_verified=1U;
    out->zw_wz_order_verified=1U;
    if(input->declared_mode==HHS220_V7_MODE_UNDECLARED){
        /* Unspecified spelling is NOT evidence of ambiguous tensor values.
         * Let the inherited native typed VMIR choose a legal unique branch.
         */
        out->native_type_dispatch_required=1U;
        out->decision=HHS220_V7_INHERIT_NATIVE_DISPATCH;
        out->reason=HHS220_V7_NATIVE_TYPE_DISPATCH_REQUIRED;
        return 1;
    }
    out->typed_mode_lexically_registered=1U;
    /* No caller-provided Boolean or hash can stand in for the missing
     * source-specific Pass169/VM81 quotient provider. The only decision is
     * UNRESOLVED_PROVIDER, which grants no canonical state authority.
     */
    out->decision=HHS220_V7_UNRESOLVED_PROVIDER;
    out->reason=HHS220_V7_NATIVE_QUOTIENT_PROVIDER_MISSING;
    return 1;
}

#ifdef HHS220_V7_CLI
static int load_file(const char *path,uint8_t **bytes,size_t *length){
    FILE *f=fopen(path,"rb");
    long count;
    if(f==NULL)return 0;
    if(fseek(f,0,SEEK_END)!=0 || (count=ftell(f))<1L ||
       fseek(f,0,SEEK_SET)!=0){fclose(f);return 0;}
    if(count>1048576L){fclose(f);return 0;}
    *bytes=(uint8_t *)malloc((size_t)count);
    if(*bytes==NULL){fclose(f);return 0;}
    *length=(size_t)count;
    if(fread(*bytes,1,*length,f)!=*length){fclose(f);free(*bytes);*bytes=NULL;return 0;}
    fclose(f);
    return 1;
}
int main(int argc,char **argv){
    HHS220V7QuotientInput in;
    HHS220V7QuotientResult out;
    uint8_t *source=NULL;
    size_t n=0U;
    unsigned long mode;
    char *end=NULL;
    if(argc<3 || argc>4 || !load_file(argv[1],&source,&n))return 2;
    mode=strtoul(argv[2],&end,10);
    if(end==argv[2] || *end!='\0' || mode>UINT32_MAX){free(source);return 2;}
    memset(&in,0,sizeof(in));
    in.struct_size=(uint32_t)sizeof(in);
    in.version=HHS220_V7_QUOTIENT_VERSION;
    in.source=source;
    in.source_bytes=n;
    in.declared_mode=(uint32_t)mode;
    if(argc==4){
        if(strcmp(argv[3],"--commute")==0)in.commute_phase_products=1U;
        else if(strcmp(argv[3],"--scalarize")==0)in.scalarize_ordered_carriers=1U;
        else if(strcmp(argv[3],"--cancel-delta")==0)in.cancel_global_denominator=1U;
        else if(strcmp(argv[3],"--reverse-equality")==0)in.reverse_ordered_equality=1U;
        else if(strcmp(argv[3],"--claim-commit")==0)in.claim_vm81_commit=1U;
        else {free(source);return 2;}
    }
    if(!hhs220_v7_quotient_preflight(&in,&out)){free(source);return 2;}
    printf("v7_source_exact=%u\n",(unsigned)out.source_exact);
    printf("v7_mode=%s\n",hhs220_v7_mode_name(out.declared_mode));
    printf("hnan_15_rule_mask=0x%04X\n",out.native_hnan_rule_mask);
    printf("v7_hnan_order_verified=%u\n",(unsigned)(out.xy_yx_order_verified &&
                                                out.zw_wz_order_verified));
    printf("v7_decision=%s\n",out.decision==HHS220_V7_INHERIT_NATIVE_DISPATCH?
                               "INHERIT_NATIVE_DISPATCH":
                               (out.decision==HHS220_V7_UNRESOLVED_PROVIDER?
                               "UNRESOLVED_PROVIDER":"REJECT"));
    printf("v7_reason=%u\n",out.reason);
    printf("v7_native_type_dispatch_required=%u\n",
           (unsigned)out.native_type_dispatch_required);
    puts("native_v7_matrix_inverse_proved=0");
    puts("native_v7_global_environment_verified=0");
    puts("canonical_vm81_admission=0");
    puts("canonical_hash72_hash216_commit=0");
    free(source);
    return out.decision==HHS220_V7_UNRESOLVED_PROVIDER ||
           out.decision==HHS220_V7_INHERIT_NATIVE_DISPATCH?0:3;
}
#endif
