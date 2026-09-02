#include "hhs_pass219_global_canonical_defaults_1_0.hpp"
#include <cassert>
int main(){
 using hhs::rna::CumulativePassGlobalDefaults; using hhs::rna::GlobalCanonicalDefaults;
 static_assert(GlobalCanonicalDefaults::numbered_passes_are_additive());
 static_assert(GlobalCanonicalDefaults::successful_implementations_must_remain_reachable());
 static_assert(!GlobalCanonicalDefaults::standalone_passes_allowed());
 static_assert(!GlobalCanonicalDefaults::isolated_native_project_is_canonical_substitute());
 static_assert(GlobalCanonicalDefaults::cross_cutting_defaults_are_mandatory());
 static_assert(GlobalCanonicalDefaults::retroactive_repair_forward_required());
 static_assert(!GlobalCanonicalDefaults::grandfather_bypass_allowed());
 static_assert(GlobalCanonicalDefaults::explicit_upgrade_or_deprecation_required());
 static_assert(GlobalCanonicalDefaults::global_latency_policy_required());
 using P218=CumulativePassGlobalDefaults<218>;
 using P200C=CumulativePassGlobalDefaults<200,HHS_EXACT_PASS219_BINDING_VARIANT_C>;
 using P186=CumulativePassGlobalDefaults<186>;
 using P185=CumulativePassGlobalDefaults<185>;
 using P184=CumulativePassGlobalDefaults<184>;
 using P183=CumulativePassGlobalDefaults<183>;
 using P182=CumulativePassGlobalDefaults<182>;
 using P181=CumulativePassGlobalDefaults<181>;
 using P180=CumulativePassGlobalDefaults<180>;
 using P179=CumulativePassGlobalDefaults<179>;
 using P178=CumulativePassGlobalDefaults<178>;
 using P177=CumulativePassGlobalDefaults<177>;
 static_assert(P218::global_defaults_required&&P200C::global_defaults_required&&P186::global_defaults_required);
 static_assert(P185::global_defaults_required&&P184::global_defaults_required&&P183::global_defaults_required&&P182::global_defaults_required&&P181::global_defaults_required&&P180::global_defaults_required&&P179::global_defaults_required&&P178::global_defaults_required&&P177::global_defaults_required);
 static_assert(P177::repair_forward_on_gap&&!P177::standalone_application&&!P177::optional_cross_cutting_defaults);
 assert(GlobalCanonicalDefaults::wired_floor_pass()==177U);
 assert(GlobalCanonicalDefaults::registered_binding_count()==44U);
 assert(GlobalCanonicalDefaults::validate_latency_policy()==HHS_EXACT_STATUS_OK);
 assert(GlobalCanonicalDefaults::validate()==HHS_EXACT_STATUS_OK);
 return 0;
}
