/*
 * HHS Pass220 V7 native HNAN + exact Z-free-word diagnostic.
 * Canonical HHS tensor semantics remain external/authoritative.
 * This checker does NOT invert 3x3 matrices or authorize VM81 commits.
 */
#include "hhs_pass219_lane5_hnan_global_constraint_1_63.h"
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char SOURCE[]="(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))\n";
static const char *const CELLS[9]={
    "yx","y+w","wx","-xy-wz","x+y-z-w+xy+yx-zw-wz","-zw-yx","xy","x-z","zw"
};
static const char *const BASIS[9]={"x","y","z","w","xy","yx","zw","wz","wx"};
enum { X=0,Y=1,Z=2,W=3,XY=4,YX=5,ZW=6,WZ=7,WX=8,WORD_COUNT=9 };
typedef struct WordVector { int32_t coefficient[WORD_COUNT]; } WordVector;
static const WordVector EXPECTED_COLS[3]={
    {{0,0,0,0,0, 1,0,-1,0}},
    {{2,2,-2,0,1,1,-1,-1,0}},
    {{0,0,0,0,0,-1,0,0,1}}
};
static const WordVector EXPECTED_ROWS[3]={
    {{0,1,0,1,0,1,0,0,1}},
    {{1,1,-1,-1,0,0,-2,-2,0}},
    {{1,0,-1,0,1,0,1,0,0}}
};

static int exact_source_file(const char *path) {
    FILE *fp=fopen(path,"rb");
    unsigned char buff[256];
    size_t n;
    if(fp==NULL)return 0;
    n=fread(buff,1U,sizeof(buff),fp);
    if(ferror(fp) || !feof(fp)){fclose(fp);return 0;}
    fclose(fp);
    return n==sizeof(SOURCE)-1U && memcmp(buff,SOURCE,n)==0;
}
static int parse_word_cell(const char *source,WordVector *out) {
    size_t i=0U,j;
    if(*source=='\0')return 0;
    memset(out,0,sizeof(*out));
    while(source[i]!='\0'){
        int sign=1,slot=-1;
        size_t length=0U;
        if(source[i]=='+' || source[i]=='-'){
            sign=source[i]=='-'?-1:1; ++i;
        }
        j=i;
        while(source[i]=='x' || source[i]=='y' ||
              source[i]=='z' || source[i]=='w')++i;
        length=i-j;
        if(length==0U || length>2U)return 0;
        for(size_t k=0U;k<WORD_COUNT;k++){
            if(strlen(BASIS[k])==length &&
               memcmp(source+j,BASIS[k],length)==0){
                slot=(int)k; break;
            }
        }
        if(slot<0 || (source[i]!='\0' && source[i]!='+' &&
                       source[i]!='-'))return 0;
        out->coefficient[slot]+=(int32_t)sign;
    }
    return 1;
}
static int check_ordered_HNAN(void) {
    HHSExactPass219HNANGlobalReceiptV1 all;
    uint32_t rules[2]={12U,13U};
    memset(&all,0,sizeof(all));
    if(hhs_exact_pass219_hnan_global_system_verify(&all)!=HHS_EXACT_STATUS_OK ||
       all.decision!=HHS_EXACT_HNAN_DECISION_VERIFIED ||
       all.verified_rule_mask!=HHS_EXACT_PASS219_HNAN_GLOBAL_ALL_RULES ||
       all.xy_yx_distinct!=1U || all.zw_wz_distinct!=1U ||
       all.candidate_only!=1U ||
       all.global_delta_denominator_preserved!=1U ||
       all.delta_cancellation_forbidden!=1U ||
       all.canonical_vm81_mutation_authority!=0U ||
       all.canonical_hash72_authority!=0U ||
       all.canonical_hash216_authority!=0U)return 0;
    for(size_t i=0U;i<2U;i++){
        HHSExactPass219HNANRuleV1 rule;
        HHSExactPass219HNANClaimV1 claim;
        HHSExactPass219HNANResolutionV1 decision;
        memset(&rule,0,sizeof(rule));
        memset(&claim,0,sizeof(claim));
        memset(&decision,0,sizeof(decision));
        if(hhs_exact_pass219_hnan_global_rule(rules[i],&rule)!=HHS_EXACT_STATUS_OK ||
           rule.commutation_authority!=0U || rule.scalar_equality_authority!=0U ||
           rule.source_order_required!=1U ||
           rule.typed_identity_required!=1U)return 0;
        claim.struct_size=(uint32_t)sizeof(claim);
        claim.version=HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION;
        claim.rule_id=rule.rule_id;
        claim.lhs_node=rule.lhs_node;
        claim.rhs_node=rule.rhs_node;
        claim.relation=rule.relation;
        claim.source_order_preserved=1U;
        claim.typed_identity_preserved=1U;
        if(hhs_exact_pass219_hnan_resolve(&claim,&decision)!=HHS_EXACT_STATUS_OK ||
           decision.decision!=HHS_EXACT_HNAN_DECISION_VERIFIED)return 0;
        claim.commutation_requested=1U;
        if(hhs_exact_pass219_hnan_resolve(&claim,&decision)!=HHS_EXACT_STATUS_OK ||
           decision.decision!=HHS_EXACT_HNAN_DECISION_REJECTED ||
           decision.reason!=HHS_EXACT_HNAN_REASON_COMMUTATION)return 0;
        claim.commutation_requested=0U;
        claim.scalar_substitution_requested=1U;
        if(hhs_exact_pass219_hnan_resolve(&claim,&decision)!=HHS_EXACT_STATUS_OK ||
           decision.decision!=HHS_EXACT_HNAN_DECISION_REJECTED ||
           decision.reason!=HHS_EXACT_HNAN_REASON_SCALARIZATION)return 0;
    }
    printf("hnan_15_rule_mask=0x%04X\n",all.verified_rule_mask);
    puts("hnan_xy_yx_commutation=REJECTED");
    puts("hnan_zw_wz_commutation=REJECTED");
    return 1;
}
int main(int argc,char **argv){
    WordVector cell[9],row[3],col[3];
    unsigned char digest[SHA256_DIGEST_LENGTH];
    const char *cursor=SOURCE;
    size_t i,j;
    if(argc!=2 || !exact_source_file(argv[1])){
        fputs("V7_FREE_WORD_SOURCE_REJECTED\n",stderr);return 1;
    }
    if(SHA256((const unsigned char *)SOURCE,sizeof(SOURCE)-1U,digest)==NULL)return 1;
    printf("source_sha256=");
    for(i=0U;i<SHA256_DIGEST_LENGTH;i++)printf("%02x",(unsigned)digest[i]);
    putchar('\n');
    memset(row,0,sizeof(row));
    memset(col,0,sizeof(col));
    for(i=0U;i<9U;i++){
        const char *found=strstr(cursor,CELLS[i]);
        if(found==NULL || !parse_word_cell(CELLS[i],&cell[i]))return 1;
        printf("free_word_site_%zu_offset=%zu\n",i,(size_t)(found-SOURCE));
        cursor=found+strlen(CELLS[i]);
        for(j=0U;j<WORD_COUNT;j++){
            row[i/3U].coefficient[j]+=cell[i].coefficient[j];
            col[i%3U].coefficient[j]+=cell[i].coefficient[j];
        }
    }
    for(i=0U;i<3U;i++){
        if(memcmp(&row[i],&EXPECTED_ROWS[i],sizeof(WordVector))!=0 ||
           memcmp(&col[i],&EXPECTED_COLS[i],sizeof(WordVector))!=0)return 1;
    }
    if(cell[4].coefficient[XY]!=1 || cell[4].coefficient[YX]!=1 ||
       cell[4].coefficient[ZW]!=-1 || cell[4].coefficient[WZ]!=-1)return 1;
    puts("free_word_center_ordered_channels=VERIFIED");
    puts("free_word_column0=yx-wz");
    puts("free_word_column2=wx-yx");
    puts("free_word_row_column_diagnostics=VERIFIED");
    if(!check_ordered_HNAN())return 1;
    puts("native_free_word_HHS_operator_equivalence=NOT_ASSERTED");
    puts("native_matrix_quotient_admissibility=UNRESOLVED");
    puts("vm81_signed_admission_performed=0");
    puts("hash72_hash216_canonical_commit=0");
    puts("v7_hnan_free_word_diagnostic=PASS");
    return 0;
}
