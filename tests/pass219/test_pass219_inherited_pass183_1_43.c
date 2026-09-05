#include <assert.h>
#include <string.h>
#include "hhs_runtime_exact_abi.h"

int main(void){
 HHSExactPass183ProbabilityHydrationWitnessV1 w;
 HHSExactPass219InheritedPass183BindingV1 b;
 memset(&w,0,sizeof(w));
 w.struct_size=(uint32_t)sizeof(w);
 w.version=hhs_exact_pass219_inherited_pass183_version();
 w.historical_contract_preserved=1U;
 w.historical_implementation_preserved=1U;
 w.historical_ci_green=1U;
 w.exact_probability_runtime_bound=1U;
 w.factorial72_reciprocal_bound=1U;
 w.membrane_boundary_bound=1U;
 w.typed_zero_bypass_bound=1U;
 w.global_modulus_bound=1U;
 w.singleton_vm81_bound=1U;
 w.canonical_hash72_after_vm81_bound=1U;
 w.hash216_archive_after_hash72_bound=1U;
 w.deterministic_replay_bound=1U;
 w.runtime_os_gui_bound=1U;
 w.legacy_native_hash_witness_noncanonical=1U;
 w.pass184_successor_preserved=1U;
 memcpy(w.implementation_commit,"4a2797ffcf75e29b616ca37b3183ea3521e03a39",41U);
 memcpy(w.historical_green_head,"3ae56827b27500c2c8187126d5825a901d4feb40",41U);
 memcpy(w.frozen_i142_commit,"33004d347337cf8c57f9772609806e49503c1bd0",41U);
 memcpy(w.i142_validation_receipt_blob,"7677afce5fcbfecc4ef276a8be9d3efcee95e4ab",41U);
 assert(hhs_exact_pass219_bind_pass183_probability_hydration(&w,&b)==HHS_EXACT_STATUS_OK);
 assert(b.pass_number==183U);
 assert(b.exact_probability_runtime_bound==1U);
 assert(b.singleton_vm81_bound==1U);
 assert(b.canonical_hash72_receipt_bound==1U);
 assert(b.hash216_archival_only_bound==1U);
 assert(b.legacy_native_hash_witness_noncanonical==1U);
 assert(b.native_hash72_authority==0U);
 assert(b.native_hash216_authority==0U);
 assert(b.hash216_precommit_authority==0U);
 assert(b.independent_vm81_authority==0U);
 assert(b.floating_point_canonical_authority==0U);
 assert(strcmp(hhs_p183_native_receipt_mode(),"LEGACY_LOCAL_WITNESS_NONCANONICAL")==0);
 return 0;
}
