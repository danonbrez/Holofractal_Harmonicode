#include <assert.h>
#include "hhs_runtime_exact_abi.h"
int main(void){
 HHSExactPass219GlobalCanonicalDefaultPolicyV1 p; HHSExactPass219CumulativeBindingKeyV1 k;
 assert(hhs_exact_pass219_global_canonical_defaults_validate()==HHS_EXACT_STATUS_OK);
 assert(hhs_exact_pass219_global_canonical_defaults_policy(&p)==HHS_EXACT_STATUS_OK);
 assert(p.numbered_passes_are_additive==1U&&p.successful_implementations_must_remain_reachable==1U);
 assert(p.standalone_passes_allowed==0U&&p.isolated_native_project_is_canonical_substitute==0U);
 assert(p.cross_cutting_defaults_are_mandatory==1U&&p.retroactive_repair_forward_required==1U);
 assert(p.grandfather_bypass_allowed==0U&&p.explicit_upgrade_or_deprecation_required==1U);
 assert(p.wired_ceiling_pass==218U&&p.wired_floor_pass==181U&&p.registered_binding_count==40U);
 assert(hhs_exact_pass219_global_canonical_defaults_binding_at(0U,&k)==HHS_EXACT_STATUS_OK&&k.pass_number==218U);
 assert(hhs_exact_pass219_global_canonical_defaults_binding_at(34U,&k)==HHS_EXACT_STATUS_OK&&k.pass_number==186U);
 assert(hhs_exact_pass219_global_canonical_defaults_binding_at(35U,&k)==HHS_EXACT_STATUS_OK&&k.pass_number==185U);
 assert(hhs_exact_pass219_global_canonical_defaults_binding_at(36U,&k)==HHS_EXACT_STATUS_OK&&k.pass_number==184U);
 assert(hhs_exact_pass219_global_canonical_defaults_binding_at(37U,&k)==HHS_EXACT_STATUS_OK&&k.pass_number==183U);
 assert(hhs_exact_pass219_global_canonical_defaults_binding_at(38U,&k)==HHS_EXACT_STATUS_OK&&k.pass_number==182U);
 assert(hhs_exact_pass219_global_canonical_defaults_binding_at(39U,&k)==HHS_EXACT_STATUS_OK&&k.pass_number==181U);
 assert(hhs_exact_pass219_global_canonical_defaults_binding_at(40U,&k)==HHS_EXACT_STATUS_RANGE_ERROR);
 return 0;
}
