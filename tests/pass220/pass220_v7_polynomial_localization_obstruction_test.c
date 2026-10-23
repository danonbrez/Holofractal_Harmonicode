/* Exhaustive native API negative and exact degree/source tests.
 * Tests the *auxiliary Z< x,y,z,w > obstruction*, not native VM81 proof.
 */
#include "hhs_pass220_v7_polynomial_localization_obstruction_v1.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static const uint8_t SOURCE[]=
    "(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))\n";
static int expectation(const HHS220V7QuotientInput *in,uint32_t wanted){
    HHS220V7AugmentResult result;
    int status=hhs220_v7_aux_polynomial_obstruction(in,&result);
    size_t k;
    if(status!=1 || result.decision!=wanted ||
       result.native_rational_localization_proved!=0U ||
       result.native_hhs_matrix_quotient_admitted!=0U ||
       result.signed_vm81_admission_verified!=0U ||
       result.canonical_hash72_hash216_transition_verified!=0U)return 0;
    if(wanted==HHS220_V7_AUGMENT_POLYNOMIAL_OBSTRUCTION_PROVED){
        uint32_t expected_degree[9]={2U,1U,2U,2U,1U,2U,2U,1U,2U};
        uint32_t expected_terms[9]={1U,2U,1U,2U,8U,2U,1U,2U,1U};
        if(result.hnan_verified_mask!=HHS220_V7_HNAN_ALL_RULES ||
           !result.all_nine_augmentation_zero ||
           !result.right_finite_polynomial_target_obstructed ||
           !result.left_finite_polynomial_target_obstructed)return 0;
        for(k=0U;k<9U;k++){
            if(result.minimum_word_degree[k]!=expected_degree[k] ||
               result.ordered_term_occurrences[k]!=expected_terms[k])return 0;
        }
    }
    return 1;
}
int main(void){
    HHS220V7QuotientInput in;
    HHS220V7AugmentResult out;
    uint8_t modified[sizeof(SOURCE)-1U];
    memset(&in,0,sizeof(in));
    in.struct_size=(uint32_t)sizeof(in);
    in.version=HHS220_V7_QUOTIENT_VERSION;
    in.source=SOURCE;in.source_bytes=sizeof(SOURCE)-1U;
    in.declared_mode=HHS220_V7_RIGHT_MATRIX_SOLVE;
    if(!expectation(&in,HHS220_V7_AUGMENT_POLYNOMIAL_OBSTRUCTION_PROVED))return 1;
    in.declared_mode=HHS220_V7_LEFT_MATRIX_SOLVE;
    if(!expectation(&in,HHS220_V7_AUGMENT_POLYNOMIAL_OBSTRUCTION_PROVED))return 1;
    puts("v7_auxiliary_left_right_polynomial_obstruction=PROVED");
    for(in.declared_mode=HHS220_V7_MODE_UNDECLARED;
        in.declared_mode<=HHS220_V7_DECLARED_FRACTAL_NESTING;
        in.declared_mode++){
        if(in.declared_mode==HHS220_V7_RIGHT_MATRIX_SOLVE ||
           in.declared_mode==HHS220_V7_LEFT_MATRIX_SOLVE)continue;
        if(hhs220_v7_aux_polynomial_obstruction(&in,&out)!=0 ||
           out.decision!=HHS220_V7_AUGMENT_INVALID)return 1;
    }
    in.declared_mode=HHS220_V7_RIGHT_MATRIX_SOLVE;
    in.commute_phase_products=1U;
    if(!expectation(&in,HHS220_V7_AUGMENT_SOURCE_REJECTED))return 1;
    in.commute_phase_products=0U;in.scalarize_ordered_carriers=1U;
    if(!expectation(&in,HHS220_V7_AUGMENT_SOURCE_REJECTED))return 1;
    in.scalarize_ordered_carriers=0U;in.cancel_global_denominator=1U;
    if(!expectation(&in,HHS220_V7_AUGMENT_SOURCE_REJECTED))return 1;
    in.cancel_global_denominator=0U;in.claim_hash216_commit=1U;
    if(!expectation(&in,HHS220_V7_AUGMENT_SOURCE_REJECTED))return 1;
    in.claim_hash216_commit=0U;in.claim_vm81_commit=1U;
    if(!expectation(&in,HHS220_V7_AUGMENT_SOURCE_REJECTED))return 1;
    in.claim_vm81_commit=0U;
    memcpy(modified,SOURCE,sizeof(modified));
    modified[10]='x';
    in.source=modified;
    if(!expectation(&in,HHS220_V7_AUGMENT_SOURCE_REJECTED))return 1;
    in.source=SOURCE;in.source_bytes--;
    if(!expectation(&in,HHS220_V7_AUGMENT_SOURCE_REJECTED))return 1;
    in.source_bytes++;
    in.version=0U;
    if(hhs220_v7_aux_polynomial_obstruction(&in,&out)!=0 ||
       out.decision!=HHS220_V7_AUGMENT_INVALID)return 1;
    puts("v7_native_augmentation_source_and_authority_rejections=PASS");
    puts("v7_hhs_exact_rational_localization_authority=UNRESOLVED");
    puts("v7_native_auxiliary_augmentation_abi=PASS");
    return 0;
}
