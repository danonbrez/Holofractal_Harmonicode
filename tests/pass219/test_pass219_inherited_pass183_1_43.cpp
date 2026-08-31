#include <assert.h>
#include "hhs_pass219_inherited_pass183_1_43.hpp"
int main(){
 using hhs::rna::InheritedPass183ProbabilityHydrationAuthority;
 static_assert(!InheritedPass183ProbabilityHydrationAuthority::candidate_authority());
 static_assert(!InheritedPass183ProbabilityHydrationAuthority::mutation_authority());
 static_assert(!InheritedPass183ProbabilityHydrationAuthority::hash72_clock_authority());
 static_assert(!InheritedPass183ProbabilityHydrationAuthority::vm81_mutation_authority());
 static_assert(!InheritedPass183ProbabilityHydrationAuthority::hash216_precommit_authority());
 static_assert(InheritedPass183ProbabilityHydrationAuthority::hash216_archival_only());
 static_assert(!InheritedPass183ProbabilityHydrationAuthority::legacy_native_hash_witness_canonical());
 static_assert(InheritedPass183ProbabilityHydrationAuthority::singleton_vm81_authority_remains_inherited());
 assert(hhs_exact_pass219_inherited_pass183_version()!=0U);
 return 0;
}
