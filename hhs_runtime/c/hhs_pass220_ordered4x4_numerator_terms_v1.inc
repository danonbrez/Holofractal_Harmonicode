/* Native noncommutative ordered entry expansion for the numerator MatrixTimes.
 * Matrix negations are outer operator nodes, NOT scalar sign cancellation.
 * This is a 4x4×4x4 native source-addressed expression graph, not a value.
 */
#include "../include/hhs_pass220_ordered4x4_numerator_terms_v1.h"
#include <openssl/sha.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static int hhs220_numerator_leaf_root(
 const uint8_t source_sha[32], uint8_t matrix_id,
 uint8_t row, uint8_t column, int8_t original_literal,
 uint8_t result[32]
) {
 static const char DOMAIN[]="HHS-P220-4X4-NUMERATOR-ADDRESSED-LEAF-V1";
 uint8_t data[sizeof(DOMAIN)-1U+32U+6U];
 size_t cursor=0U;
 memcpy(data+cursor,DOMAIN,sizeof(DOMAIN)-1U);
 cursor+=sizeof(DOMAIN)-1U;
 memcpy(data+cursor,source_sha,32U);
 cursor+=32U;
 data[cursor++]=matrix_id;
 data[cursor++]=row;
 data[cursor++]=column;
 data[cursor++]=(uint8_t)original_literal; /* exact signed *token*, not arithmetic */
 data[cursor++]=1U; /* outer -List node retained */
 data[cursor++]=1U; /* ordered source occurrence semantics */
 return cursor==sizeof(data) && SHA256(data,sizeof(data),result)!=NULL;
}

static int hhs220_numerator_product_root(
 const uint8_t source_sha[32], uint8_t i,uint8_t k,uint8_t j,
 const uint8_t left_root[32],const uint8_t right_root[32],
 uint8_t result[32]
) {
 static const char DOMAIN[]="HHS-P220-4X4-ORDERED-NUMERATOR-MATRIXTIMES-TERM-V1";
 uint8_t data[sizeof(DOMAIN)-1U+32U+3U+64U];
 size_t cursor=0U;
 memcpy(data+cursor,DOMAIN,sizeof(DOMAIN)-1U);
 cursor+=sizeof(DOMAIN)-1U;
 memcpy(data+cursor,source_sha,32U);
 cursor+=32U;
 data[cursor++]=i;
 data[cursor++]=k;
 data[cursor++]=j;
 memcpy(data+cursor,left_root,32U);
 cursor+=32U;
 memcpy(data+cursor,right_root,32U);
 cursor+=32U;
 return cursor==sizeof(data) && SHA256(data,sizeof(data),result)!=NULL;
}

static int hhs220_numerator_sum_root(
 const uint8_t source_sha[32],uint8_t i,uint8_t j,
 const HHS220Ordered4x4ProductTermV1 *terms,
 uint8_t result[32]
) {
 static const char DOMAIN[]="HHS-P220-4X4-ORDERED-FOUR-TERM-SUM-V1";
 uint8_t data[sizeof(DOMAIN)-1U+32U+2U+128U];
 size_t cursor=0U,k;
 memcpy(data+cursor,DOMAIN,sizeof(DOMAIN)-1U);
 cursor+=sizeof(DOMAIN)-1U;
 memcpy(data+cursor,source_sha,32U);
 cursor+=32U;
 data[cursor++]=i;
 data[cursor++]=j;
 for(k=0U;k<4U;++k) {
  if(terms[k].output_row!=i || terms[k].output_column!=j ||
     terms[k].reduction_position!=k)
   return 0;
  memcpy(data+cursor,terms[k].ordered_product_root,32U);
  cursor+=32U;
 }
 return cursor==sizeof(data) && SHA256(data,sizeof(data),result)!=NULL;
}

HHSExactStatus hhs_exact_pass220_ordered4x4_numerator_terms(
 const uint8_t *source, size_t source_bytes,
 HHS220Ordered4x4NumeratorTermsV1 *out_terms
) {
 static const char MATRIX_DOMAIN[]="HHS-P220-4X4-ORDERED-NUMERATOR-CELL-ARRAY-V1";
 HHSExactVM81Frame candidate;
 HHS220Ordered4x4HIRWitnessV1 origin;
 uint8_t matrix_material[sizeof(MATRIX_DOMAIN)-1U+32U+512U];
 size_t cursor=0U,i,j,k,index;
 HHSExactStatus status;
 if(out_terms==NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 memset(out_terms,0,sizeof(*out_terms));
 out_terms->struct_size=(uint32_t)sizeof(*out_terms);
 out_terms->version=UINT32_C(0x00010000);
 if(source==NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 status=hhs_exact_pass220_ordered4x4_lower(source,source_bytes,&candidate,&origin);
 if(status!=HHS_EXACT_STATUS_OK) return status;
 if(origin.source_identity_verified!=1U ||
    origin.ordered_topology_verified!=1U ||
    origin.literal_cells!=64U ||
    origin.numerator_negative_operand_count!=2U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 memcpy(out_terms->source_sha256,origin.source_sha256,32U);
 for(i=0U;i<4U;++i) {
  for(j=0U;j<4U;++j) {
   for(k=0U;k<4U;++k) {
    HHS220Ordered4x4ProductTermV1 *term;
    index=16U*i+4U*j+k;
    term=&out_terms->terms[index];
    term->output_row=(uint8_t)i;
    term->output_column=(uint8_t)j;
    term->reduction_position=(uint8_t)k;
    term->left_source_matrix=0U;
    term->right_source_matrix=1U;
    term->left_source_row=(uint8_t)i;
    term->left_source_col=(uint8_t)k;
    term->right_source_row=(uint8_t)k;
    term->right_source_col=(uint8_t)j;
    term->left_literal_token=HHS220_ORDERED4X4_CELLS[0][4U*i+k];
    term->right_literal_token=HHS220_ORDERED4X4_CELLS[1][4U*k+j];
    term->left_outer_negate=1U;
    term->right_outer_negate=1U;
    if(!hhs220_numerator_leaf_root(
          origin.source_sha256,0U,(uint8_t)i,(uint8_t)k,
          term->left_literal_token,term->left_operand_root) ||
       !hhs220_numerator_leaf_root(
          origin.source_sha256,1U,(uint8_t)k,(uint8_t)j,
          term->right_literal_token,term->right_operand_root) ||
       !hhs220_numerator_product_root(
          origin.source_sha256,(uint8_t)i,(uint8_t)k,(uint8_t)j,
          term->left_operand_root,term->right_operand_root,
          term->ordered_product_root))
     return HHS_EXACT_STATUS_INVARIANT_FAILURE;
   }
   if(!hhs220_numerator_sum_root(
      origin.source_sha256,(uint8_t)i,(uint8_t)j,
      &out_terms->terms[16U*i+4U*j],
      out_terms->ordered_cell_sum_roots[4U*i+j]))
    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
  }
 }
 memcpy(matrix_material+cursor,MATRIX_DOMAIN,sizeof(MATRIX_DOMAIN)-1U);
 cursor+=sizeof(MATRIX_DOMAIN)-1U;
 memcpy(matrix_material+cursor,origin.source_sha256,32U);
 cursor+=32U;
 for(index=0U;index<16U;++index) {
  memcpy(matrix_material+cursor,out_terms->ordered_cell_sum_roots[index],32U);
  cursor+=32U;
 }
 if(cursor!=sizeof(matrix_material) ||
    SHA256(matrix_material,sizeof(matrix_material),
      out_terms->numerator_expression_root)==NULL)
   return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 out_terms->source_matrix_rows=4U;
 out_terms->source_matrix_columns=4U;
 out_terms->term_count=HHS220_ORDERED4X4_NUMERATOR_TERMS;
 out_terms->ordered_sum_count=HHS220_ORDERED4X4_NUMERATOR_OUTPUTS;
 out_terms->original_source_verified=1U;
 out_terms->ordered_left_right_preserved=1U;
 out_terms->ordered_reduction_k_preserved=1U;
 out_terms->source_leaf_address_verified=1U;
 /* Do not grant value, sign-cancellation, commutation, equality, or VM81 authority. */
 return HHS_EXACT_STATUS_OK;
}
