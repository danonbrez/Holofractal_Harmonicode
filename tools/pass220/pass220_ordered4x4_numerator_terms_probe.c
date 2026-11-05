/* Test exact 64 ordered tensor product terms; DO NOT evaluate matrix values. */
#include "hhs_runtime_exact_abi.h"
#include <openssl/sha.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#define CHECK(x,msg) do {if(!(x)){fprintf(stderr,"FAIL:%s\n",msg);return 1;}}while(0)
static uint8_t source[HHS220_ORDERED4X4_SOURCE_BYTES+1U];
static HHS220Ordered4x4NumeratorTermsV1 a,b,failed;

static int reversed_root_is_distinct(const HHS220Ordered4x4ProductTermV1 *term,
                                    const uint8_t source_sha[32]) {
 static const char DOMAIN[]="HHS-P220-4X4-ORDERED-NUMERATOR-MATRIXTIMES-TERM-V1";
 uint8_t material[sizeof(DOMAIN)-1U+32U+3U+64U],reversed[32];
 size_t n=0U;
 memcpy(material+n,DOMAIN,sizeof(DOMAIN)-1U);n+=sizeof(DOMAIN)-1U;
 memcpy(material+n,source_sha,32U);n+=32U;
 material[n++]=term->output_row;
 material[n++]=term->reduction_position;
 material[n++]=term->output_column;
 /* Explicit reversed witness is NOT the canonical ordered product root. */
 memcpy(material+n,term->right_operand_root,32U);n+=32U;
 memcpy(material+n,term->left_operand_root,32U);n+=32U;
 if(n!=sizeof(material)||SHA256(material,n,reversed)==NULL) return 0;
 return memcmp(reversed,term->ordered_product_root,32U)!=0;
}

int main(void) {
 FILE *file=fopen("contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode","rb");
 size_t length,i,j,k,index;
 CHECK(file!=NULL,"source file exists");
 length=fread(source,1U,sizeof(source),file);
 CHECK(!ferror(file) && fclose(file)==0 && length==HHS220_ORDERED4X4_SOURCE_BYTES,"exact source length");
 CHECK(hhs_exact_pass220_ordered4x4_numerator_terms(source,length,&a)==HHS_EXACT_STATUS_OK,"64 term native expansion");
 CHECK(hhs_exact_pass220_ordered4x4_numerator_terms(source,length,&b)==HHS_EXACT_STATUS_OK,"deterministic expansion");
 CHECK(memcmp(&a,&b,sizeof(a))==0,"full native term witness replay");
 CHECK(a.source_matrix_rows==4U && a.source_matrix_columns==4U,"native 4x4 shape");
 CHECK(a.term_count==64U && a.ordered_sum_count==16U,"64 terms and 16 sums");
 CHECK(a.original_source_verified==1U && a.ordered_left_right_preserved==1U &&
       a.ordered_reduction_k_preserved==1U && a.source_leaf_address_verified==1U,
       "ordered source topology verified");
 CHECK(a.matrix_operator_value_derived==0U && a.host_scalar_arithmetic_used==0U &&
       a.commutation_proved==0U && a.equality_proved==0U,
       "no scalar or algebraic authority");
 CHECK(a.signed_vm81_admission==0U && a.canonical_hash72_commit_authority==0U &&
       a.canonical_hash216_commit_authority==0U,"no receipt authority");
 for(i=0U;i<4U;++i) for(j=0U;j<4U;++j) for(k=0U;k<4U;++k) {
  const HHS220Ordered4x4ProductTermV1 *term;
  index=16U*i+4U*j+k;
  term=&a.terms[index];
  CHECK(term->output_row==i && term->output_column==j && term->reduction_position==k,
        "ordered row column reduction index");
  CHECK(term->left_source_matrix==0U && term->right_source_matrix==1U,
        "operand matrices never swapped");
  CHECK(term->left_source_row==i && term->left_source_col==k &&
        term->right_source_row==k && term->right_source_col==j,
        "source occurrence addresses");
  CHECK(term->left_outer_negate==1U && term->right_outer_negate==1U,
        "two original -List wrappers retained");
  CHECK(reversed_root_is_distinct(term,a.source_sha256),"noncommutative reversal distinct");
  CHECK(memcmp(term->left_operand_root,term->right_operand_root,32U)!=0,
        "operand address provenance distinct");
 }
 CHECK(a.terms[0].left_literal_token==1 && a.terms[0].right_literal_token==-1,
       "first exact signed literal tokens retained");
 CHECK(a.terms[63].left_literal_token==1 && a.terms[63].right_literal_token==-1,
       "last exact signed literal tokens retained");
 CHECK(memcmp(a.ordered_cell_sum_roots[0],a.ordered_cell_sum_roots[1],32U)!=0,
       "distinct addressed output sums");
 CHECK(memcmp(a.numerator_expression_root,a.ordered_cell_sum_roots[0],32U)!=0,
       "full numerator differs from one output cell");
 source[0]^=1U;
 CHECK(hhs_exact_pass220_ordered4x4_numerator_terms(source,length,&failed)!=HHS_EXACT_STATUS_OK,
       "one byte source mutation fails closed");
 CHECK(failed.original_source_verified==0U && failed.canonical_hash216_commit_authority==0U,
       "tamper cannot grant authority");
 source[0]^=1U;
 CHECK(hhs_exact_pass220_ordered4x4_numerator_terms(source,length-1U,&failed)!=HHS_EXACT_STATUS_OK,
       "truncated source rejected");
 CHECK(hhs_exact_pass220_ordered4x4_numerator_terms(NULL,length,&failed)!=HHS_EXACT_STATUS_OK,
       "null source rejected");
 CHECK(hhs_exact_pass220_ordered4x4_numerator_terms(source,length,NULL)!=HHS_EXACT_STATUS_OK,
       "null destination rejected");
 puts("{\"schema\":\"HHS_PASS220_ORDERED4X4_64_SOURCE_TERMS_V1\","
      "\"native_ordered_product_terms\":64,\"ordered_cell_sum_nodes\":16,"
      "\"source_address_preserved\":true,\"operand_reversal_distinguished\":true,"
      "\"deterministic_replay\":true,\"matrix_values_computed\":false,"
      "\"equality_proved\":false,\"vm81_admission\":false,"
      "\"hash72_commit\":false,\"hash216_commit\":false}");
 return 0;
}
