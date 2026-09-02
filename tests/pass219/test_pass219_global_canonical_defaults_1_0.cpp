#include <assert.h>
#include "hhs_runtime_exact_abi.h"
#include "hhs_pass219_global_canonical_defaults_1_0.hpp"
int main(){
 using hhs::rna::CumulativePassGlobalDefaults; using hhs::rna::GlobalCanonicalDefaults;
 static_assert(GlobalCanonicalDefaults::numbered_passes_are_additive());
 static_assert(GlobalCanonicalDefaults::successful_implementations_must_remain_reachable());
 static_assert(!GlobalCanonicalDefaults::standalone_passes_allowed());
 static_assert(!GlobalCanonicalDefaults::isolated_native_project_is_canonical_substitute());
 static_assert(GlobalCanonicalDefaults::cross_cutting_defaults_are_mandatory());
 static_assert(GlobalCanonicalDefaults::retroactive_repair_forward_required());
 using P184=CumulativePassGlobalDefaults<184>; using P183=CumulativePassGlobalDefaults<183>; using P182=CumulativePassGlobalDefaults<182>; using P181=CumulativePassGlobalDefaults<181>; using P180=CumulativePassGlobalDefaults<180>;
 static_assert(P184::global_defaults_required&&P183::global_defaults_required&&P182::global_defaults_required&&P181::global_defaults_required&&P180::global_defaults_required);
 static_assert(P180::repair_forward_on_gap&&!P180::standalone_application&&!P180::optional_cross_cutting_defaults);
 assert(GlobalCanonicalDefaults::validate()==HHS_EXACT_STATUS_OK); return 0;
}
