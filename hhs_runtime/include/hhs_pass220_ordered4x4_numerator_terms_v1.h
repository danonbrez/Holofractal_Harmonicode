#ifndef HHS_PASS220_ORDERED4X4_NUMERATOR_TERMS_V1_H
#define HHS_PASS220_ORDERED4X4_NUMERATOR_TERMS_V1_H
#include "hhs_pass220_ordered4x4_neg4_1_0.h"
#include <stdint.h>
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
#define HHS220_ORDERED4X4_NUMERATOR_TERMS 64U
#define HHS220_ORDERED4X4_NUMERATOR_OUTPUTS 16U
typedef struct HHS220Ordered4x4ProductTermV1 {
 uint8_t output_row;
 uint8_t reduction_position;
 uint8_t output_column;
 uint8_t left_source_matrix;
 uint8_t right_source_matrix;
 uint8_t left_source_row;
 uint8_t left_source_col;
 uint8_t right_source_row;
 uint8_t right_source_col;
 int8_t left_literal_token;
 int8_t right_literal_token;
 uint8_t left_outer_negate;
 uint8_t right_outer_negate;
 uint8_t reserved[3];
 uint8_t left_operand_root[32];
 uint8_t right_operand_root[32];
 uint8_t ordered_product_root[32];
} HHS220Ordered4x4ProductTermV1;
typedef struct HHS220Ordered4x4NumeratorTermsV1 {
 uint32_t struct_size;
 uint32_t version;
 uint32_t source_matrix_rows;
 uint32_t source_matrix_columns;
 uint32_t term_count;
 uint32_t ordered_sum_count;
 uint8_t original_source_verified;
 uint8_t ordered_left_right_preserved;
 uint8_t ordered_reduction_k_preserved;
 uint8_t source_leaf_address_verified;
 uint8_t matrix_operator_value_derived;
 uint8_t host_scalar_arithmetic_used;
 uint8_t commutation_proved;
 uint8_t equality_proved;
 uint8_t signed_vm81_admission;
 uint8_t canonical_hash72_commit_authority;
 uint8_t canonical_hash216_commit_authority;
 uint8_t reserved[5];
 uint8_t source_sha256[32];
 uint8_t numerator_expression_root[32];
 HHS220Ordered4x4ProductTermV1 terms[HHS220_ORDERED4X4_NUMERATOR_TERMS];
 uint8_t ordered_cell_sum_roots[HHS220_ORDERED4X4_NUMERATOR_OUTPUTS][32];
} HHS220Ordered4x4NumeratorTermsV1;
/* Enumerate the exactly ordered expression product terms of the two negated
 * source matrices, without evaluating/cancelling signs or coefficient values.
 * Diagnostic roots are not native Hash72/Hash216 receipt material. */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_ordered4x4_numerator_terms(
 const uint8_t *source, size_t source_bytes,
 HHS220Ordered4x4NumeratorTermsV1 *out_terms);
#ifdef __cplusplus
}
#endif
#endif
