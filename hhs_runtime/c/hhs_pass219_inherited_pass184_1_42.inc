#include "../include/hhs_pass219_inherited_pass184_1_42.h"
#include <string.h>
static const char P184_I142_HISTORICAL_BRANCH_HEAD[] = "8fc42ee8364bd79cd711c0b0e60808b24a19a20d";
static const char P184_I142_PASS185_VALIDATED_HEAD[] = "ee21cebede955354c0a0050dc3b267f166ef9cfe";
static uint32_t p184_i142_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS184_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS184_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS184_VERSION_PATCH;
}
static int p184_i142_git(const char value[HHS_EXACT_PASS184_I142_GIT_SHA_STRLEN], const char *expected) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS184_I142_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS184_I142_GIT_SHA_LEN) == 0;
}
uint32_t hhs_exact_pass219_inherited_pass184_version(void) { return p184_i142_version_word(); }
HHSExactStatus hhs_exact_pass219_bind_pass184_portable_runtime(
    const HHSExactPass184PortableRuntimeWitnessV1 *witness,
    HHSExactPass219InheritedPass184BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p184_i142_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (witness->historical_contract_preserved != 1U || witness->historical_nucleus_preserved != 1U ||
        witness->current_runtime_os_target_bound != 1U || witness->deterministic_profile_closure_verified != 1U ||
        witness->deterministic_package_manifest_verified != 1U || witness->listener_health_supervision_verified != 1U ||
        witness->foreground_service_authority_verified != 1U || witness->cli_api_gui_bound != 1U ||
        witness->hash72_completion_receipt_bound != 1U || witness->hash216_archival_identity_bound != 1U ||
        witness->pass185_successor_preserved != 1U || witness->independent_vm81_authority != 0U ||
        witness->independent_hash72_clock != 0U || witness->package_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!p184_i142_git(witness->historical_branch_head,P184_I142_HISTORICAL_BRANCH_HEAD) ||
        !p184_i142_git(witness->pass185_validated_head,P184_I142_PASS185_VALIDATED_HEAD))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    memset(out_binding,0,sizeof(*out_binding));
    out_binding->struct_size=(uint32_t)sizeof(*out_binding);
    out_binding->version=p184_i142_version_word();
    out_binding->pass_number=HHS_EXACT_PASS219_INHERITED_PASS184_NUMBER;
    out_binding->classification=HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->portable_package_bound=1U; out_binding->supervised_service_bound=1U;
    out_binding->current_runtime_os_target_bound=1U; out_binding->hash72_hash216_evidence_bound=1U;
    out_binding->pass185_successor_bound=1U; out_binding->no_new_authority_bound=1U;
    memcpy(out_binding->historical_branch_head,P184_I142_HISTORICAL_BRANCH_HEAD,HHS_EXACT_PASS184_I142_GIT_SHA_STRLEN);
    memcpy(out_binding->pass185_validated_head,P184_I142_PASS185_VALIDATED_HEAD,HHS_EXACT_PASS184_I142_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
