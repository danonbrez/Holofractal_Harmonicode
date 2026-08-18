#include "hhs_pass219_inherited_pass212_1_16.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void copy_text(char *target, size_t size, const char *value) {
    assert(strlen(value) + 1U == size);
    memcpy(target, value, size);
}

static HHSExactPass212RecoveryWitnessV1 witness(void) {
    HHSExactPass212RecoveryWitnessV1 v;
    memset(&v, 0, sizeof(v));
    v.struct_size = (uint32_t)sizeof(v);
    v.version = hhs_exact_pass219_inherited_pass212_version();
    v.runtime_verified = 1U;
    v.full_hydration_bits = 50388480U; v.full_hydration_bytes = 6298560U;
    v.local_leaf_bits = 5184U; v.local_leaf_bytes = 648U; v.full_leaf_count = 9720U;
    v.hydration_lanes = 40U; v.g243_controls = 243U; v.affine_seed_bits = 19440U; v.affine_seed_bytes = 2430U;
    v.pure_affine_payload_bytes = 2473U; v.pure_affine_protected_bytes = 3769U;
    v.sparse_exception_count = 4096U; v.sparse_payload_bytes = 10665U;
    v.raw_data_shards = 9720U; v.raw_parity_shards = 80U; v.raw_protected_bytes = 6350400U;
    v.data_shards_per_stripe = 243U; v.parity_shards_per_stripe = 2U;
    v.recoverable_erasures_per_stripe = 2U; v.physical_erasures_verified_per_stripe = 2U;
    v.strict_claim_boundary_preserved = 1U; v.arbitrary_raw_state_exact = 1U;
    v.physical_recovery_requires_surviving_bytes = 1U; v.three_missing_same_stripe_fail_closed = 1U;
    v.corrupted_material_fail_closed = 1U; v.no_float_canonical_authority = 1U;
    v.required_operation_count = 7U; v.pass213_recovery_admission_consumes_pass212 = 1U;
    v.branch_validation_run = 31015011012ULL; v.main_validation_run = 31015122160ULL;
    copy_text(v.validated_branch_head,sizeof(v.validated_branch_head),"adc6737d12a371625413c63068de5a898fed0c0f");
    copy_text(v.main_merge_head,sizeof(v.main_merge_head),"3fc3ec4596062a1f7e37de19165cfe0e6ed88483");
    copy_text(v.contract_git_blob,sizeof(v.contract_git_blob),"12f2c577e02f4436ee776366a1994ece5a765fca");
    copy_text(v.restart_git_blob,sizeof(v.restart_git_blob),"c2f2ef336de57a2897397e01e820c69e724fa1cc");
    copy_text(v.runtime_git_blob,sizeof(v.runtime_git_blob),"2688cf46e2f3084589d4ad961d53e89c33b40a7c");
    copy_text(v.api_git_blob,sizeof(v.api_git_blob),"0699e1c720f88f47d1d8e4562cb9a73f6a3c0372");
    copy_text(v.evidence_git_blob,sizeof(v.evidence_git_blob),"c27a29e5268bba4361741ed304c31fa293a9e0ae");
    copy_text(v.validation_script_git_blob,sizeof(v.validation_script_git_blob),"923303154fa4703b897aad59c0b1b0411a52a276");
    copy_text(v.pass213_recovery_admission_git_blob,sizeof(v.pass213_recovery_admission_git_blob),"df7ee51a72991a10bdb25e1342d17cd26a826b9c");
    copy_text(v.affine_state_hash216,sizeof(v.affine_state_hash216),"19c67438fd7d21eb20817d188f7906212a2507f9783acd82e2176d6fc6c97faa");
    copy_text(v.affine_full_root216,sizeof(v.affine_full_root216),"4b4e820cfcec05442e3b2db385dedbfbd17ad5de4c88fcd6fe67c3112df8be2c");
    copy_text(v.sparse_state_hash216,sizeof(v.sparse_state_hash216),"5fd2c170d5500932fdd04d1ea520d2240175f032cd9540ad383acf4d23bd8dfa");
    copy_text(v.sparse_full_root216,sizeof(v.sparse_full_root216),"0ded0d6c6572cb11484c7eff3ce7c9cf5d62a5f1de3cc3a2e3769fcdde58ef3c");
    copy_text(v.raw_state_hash216,sizeof(v.raw_state_hash216),"6da86f4b17915b107dada49a36b3b9374cccc7855fbbd793798996cbe1890cec");
    copy_text(v.raw_full_root216,sizeof(v.raw_full_root216),"d5753f8b8146a8beae63091652d9a8a0c51dbd9a179476257b83b4d22d2b687f");
    return v;
}

int main(void) {
    HHSExactPass212RecoveryWitnessV1 input = witness();
    HHSExactPass219InheritedPass212BindingV1 output;
    assert(hhs_exact_pass219_bind_pass212_full_hydration_recovery(&input,&output) == HHS_EXACT_STATUS_OK);
    assert(output.pass_number == 212U && output.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(output.full_hydration_authority_bound == 1U && output.physical_erasure_recovery_bound == 1U);
    assert(output.pass213_recovery_successor_bound == 1U && output.pass219_new_canonical_mutation_authority == 0U);
    assert(output.cxx_mutation_authority == 0U && output.vm81_mutation_authority == 0U);
    input = witness(); input.pass219_new_canonical_mutation_authority = 1U;
    assert(hhs_exact_pass219_bind_pass212_full_hydration_recovery(&input,&output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.recoverable_erasures_per_stripe = 3U;
    assert(hhs_exact_pass219_bind_pass212_full_hydration_recovery(&input,&output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.no_float_canonical_authority = 0U;
    assert(hhs_exact_pass219_bind_pass212_full_hydration_recovery(&input,&output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.raw_state_hash216[0] = '0';
    assert(hhs_exact_pass219_bind_pass212_full_hydration_recovery(&input,&output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    puts("PASS219_INHERITED_PASS212_1_16_C_OK");
    return 0;
}
