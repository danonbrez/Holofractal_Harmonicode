/*
 * Pass220 source-specific HNAN/Jordan mandatory 15-rule PRE-ADMISSION check.
 * Entirely reuses inherited native Pass219 1.63 ABI. This is not a generic
 * evaluator for == gates and never commits the canonical VM81 state.
 */
#include "hhs_pass219_lane5_hnan_global_constraint_1_63.h"
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define P220_V4_BYTES 527U
#define P220_V4_GATE_COUNT 40U
static const char P220_SOURCE_SHA256[] =
    "124900427b60ff688e3cff10f2178e76d121168273fcd3caec0782ca2a067344";

static int exact_source(const uint8_t *bytes, size_t n) {
    uint8_t digest[SHA256_DIGEST_LENGTH];
    char hex[SHA256_DIGEST_LENGTH*2U+1U];
    uint32_t depth=0U, count=0U, outers=0U;
    size_t i;
    static const char *required[] = {
        "(u^72==x*y)", "==x==-y*(", "(u^36==(y*x*w*z)/a^2)",
        "x*y+z*w", "1==z*w", "1==x*y"
    };
    if (n != P220_V4_BYTES || bytes[n-1U] != '\n' ||
        SHA256(bytes,n,digest) == NULL) return 0;
    for(i=0U;i<SHA256_DIGEST_LENGTH;i++)
        (void)snprintf(&hex[2U*i],3U,"%02x",(unsigned)digest[i]);
    if (strcmp(hex,P220_SOURCE_SHA256)!=0) return 0;
    for(i=0U;i<sizeof(required)/sizeof(required[0]);i++)
        if(strstr((const char *)bytes, required[i]) == NULL) return 0;
    for(i=0U;i<n;i++) {
        if(bytes[i]=='(') ++depth;
        else if(bytes[i]==')') {
            if(depth==0U)return 0;
            --depth;
        }
        if(bytes[i]=='=' && i+1U<n && bytes[i+1U]=='=') {
            if(depth==0U) {
                if ((outers==0U && i!=253U) ||
                    (outers==1U && i!=256U) || outers>=2U) return 0;
                ++outers;
            }
            ++count; ++i;
        }
    }
    return count==P220_V4_GATE_COUNT && depth==0U && outers==2U;
}
static int original_claim(uint32_t rule_id, HHSExactPass219HNANClaimV1 *claim,
                          HHSExactPass219HNANRuleV1 *rule) {
    memset(rule,0,sizeof(*rule));
    memset(claim,0,sizeof(*claim));
    if(hhs_exact_pass219_hnan_global_rule(rule_id,rule)!=HHS_EXACT_STATUS_OK)
        return 0;
    claim->struct_size=(uint32_t)sizeof(*claim);
    claim->version=HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION;
    claim->rule_id=rule->rule_id;
    claim->lhs_node=rule->lhs_node;
    claim->rhs_node=rule->rhs_node;
    claim->relation=rule->relation;
    claim->source_order_preserved=1U;
    claim->typed_identity_preserved=1U;
    return rule->directional==1U && rule->source_order_required==1U &&
           rule->typed_identity_required==1U &&
           rule->scalar_equality_authority==0U &&
           rule->commutation_authority==0U &&
           rule->cancellation_authority==0U;
}
static int check_relation(uint32_t id, const char *label) {
    HHSExactPass219HNANClaimV1 claim;
    HHSExactPass219HNANRuleV1 rule;
    HHSExactPass219HNANResolutionV1 res;
    uint32_t saved;
    if(!original_claim(id,&claim,&rule))return 0;
    memset(&res,0,sizeof(res));
    if(hhs_exact_pass219_hnan_resolve(&claim,&res)!=HHS_EXACT_STATUS_OK ||
        res.decision!=HHS_EXACT_HNAN_DECISION_VERIFIED ||
        res.exact_rule_match!=1U ||
        res.scalar_substitution_authority!=0U ||
        res.commutation_authority!=0U)return 0;
    printf("hnan_%s_original_order=VERIFIED\n",label);
    saved=claim.lhs_node; claim.lhs_node=claim.rhs_node; claim.rhs_node=saved;
    if(hhs_exact_pass219_hnan_resolve(&claim,&res)!=HHS_EXACT_STATUS_OK ||
        res.decision!=HHS_EXACT_HNAN_DECISION_REJECTED ||
        res.reason!=HHS_EXACT_HNAN_REASON_SOURCE_ORDER)return 0;
    printf("hnan_%s_reverse=REJECTED_SOURCE_ORDER\n",label);
    claim.lhs_node=rule.lhs_node;claim.rhs_node=rule.rhs_node;
    claim.commutation_requested=1U;
    if(hhs_exact_pass219_hnan_resolve(&claim,&res)!=HHS_EXACT_STATUS_OK ||
        res.decision!=HHS_EXACT_HNAN_DECISION_REJECTED ||
        res.reason!=HHS_EXACT_HNAN_REASON_COMMUTATION)return 0;
    printf("hnan_%s_commutation=REJECTED\n",label);
    claim.commutation_requested=0U;
    claim.equality_reversal_requested=1U;
    if(hhs_exact_pass219_hnan_resolve(&claim,&res)!=HHS_EXACT_STATUS_OK ||
        res.decision!=HHS_EXACT_HNAN_DECISION_REJECTED ||
        res.reason!=HHS_EXACT_HNAN_REASON_EQUALITY_REVERSAL)return 0;
    printf("hnan_%s_equality_reversal=REJECTED\n",label);
    return 1;
}
int main(int argc, char **argv) {
    uint8_t *source_bytes=NULL;
    size_t n=0U;
    FILE *fp;
    long len;
    HHSExactPass219HNANGlobalReceiptV1 graph;
    HHSExactPass219HNANAuthorityV1 authority;
    int ok=0;
    if(argc!=2)return 2;
    fp=fopen(argv[1],"rb");
    if(fp==NULL)return 2;
    if(fseek(fp,0L,SEEK_END)!=0 || (len=ftell(fp))<=0 ||
       fseek(fp,0L,SEEK_SET)!=0) {fclose(fp);return 2;}
    source_bytes=(uint8_t *)calloc((size_t)len+1U,1U);
    if(source_bytes==NULL){fclose(fp);return 2;}
    n=(size_t)len;
    if(fread(source_bytes,1U,n,fp)!=n){fclose(fp);goto cleanup;}
    fclose(fp);
    if(!exact_source(source_bytes,n)) {
        puts("V4_HNAN_SOURCE_IDENTITY_REJECTED");
        goto cleanup;
    }
    puts("v4_source_identity=VERIFIED");
    puts("v4_gate_occurrence_count=40");
    memset(&authority,0,sizeof(authority));
    if(hhs_exact_pass219_hnan_global_authority(&authority)!=HHS_EXACT_STATUS_OK ||
       authority.mandatory_rule_count!=15U ||
       authority.mandatory_rule_mask!=HHS_EXACT_PASS219_HNAN_GLOBAL_ALL_RULES ||
       authority.vm81_preflight_required!=1U ||
       authority.signed_environmental_preflight_required!=1U ||
       authority.canonical_vm81_mutation_authority!=0U ||
       authority.canonical_hash72_authority!=0U ||
       authority.canonical_hash216_authority!=0U)return 1;
    memset(&graph,0,sizeof(graph));
    if(hhs_exact_pass219_hnan_global_system_verify(&graph)!=HHS_EXACT_STATUS_OK ||
       graph.decision!=HHS_EXACT_HNAN_DECISION_VERIFIED ||
       graph.verified_rule_mask!=HHS_EXACT_PASS219_HNAN_GLOBAL_ALL_RULES ||
       graph.candidate_only!=1U ||
       graph.canonical_vm81_mutation_authority!=0U ||
       graph.canonical_hash72_authority!=0U ||
       graph.canonical_hash216_authority!=0U ||
       graph.xy_yx_distinct!=1U || graph.zw_wz_distinct!=1U ||
       graph.global_delta_denominator_preserved!=1U ||
       graph.delta_cancellation_forbidden!=1U)return 1;
    printf("hnan_15_rule_mask=0x%04X\n",graph.verified_rule_mask);
    printf("hnan_jordan_rank=%u\n",graph.rank_m01);
    printf("hnan_jordan_nullity=%u\n",graph.nullity_m01);
    printf("hnan_jordan_squared_nullity=%u\n",graph.nullity_m01_squared);
    if(!check_relation(12U,"xy_yx") || !check_relation(13U,"zw_wz"))goto cleanup;
    puts("40_boolean_truth_witnesses=UNRESOLVED");
    puts("vm81_signed_commit_performed=0");
    puts("canonical_hash72_hash216_transition_performed=0");
    puts("v4_hnan_native_preflight=PASS");
    ok=1;
cleanup:
    free(source_bytes);
    return ok?0:1;
}
