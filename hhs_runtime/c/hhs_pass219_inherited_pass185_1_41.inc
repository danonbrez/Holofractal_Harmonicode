#include "../include/hhs_pass219_inherited_pass185_1_41.h"
#include <string.h>
static const char P185_I141_VALIDATED_HEAD[] = "ee21cebede955354c0a0050dc3b267f166ef9cfe";
static const char P185_I141_CUMULATIVE_RECEIPT_BLOB[] = "9b9bbc53254795e766ebe5982b9d2e918e0847d5";
static uint32_t p185_i141_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS185_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS185_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS185_VERSION_PATCH;
}
static int p185_i141_git(const char value[HHS_EXACT_PASS185_I141_GIT_SHA_STRLEN], const char *expected) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS185_I141_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS185_I141_GIT_SHA_LEN) == 0;
}
uint32_t hhs_exact_pass219_inherited_pass185_version(void) { return p185_i141_version_word(); }
HHSExactStatus hhs_exact_pass219_bind_pass185_cumulative_closure(
    const HHSExactPass185CumulativeClosureWitnessV1 *witness,
    HHSExactPass219InheritedPass185BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p185_i141_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (witness->contract_preserved != 1U || witness->phase7_matrix_verified != 1U ||
        witness->cumulative_local_closure_verified != 1U ||
        witness->exact_production_entrypoint_verified != 1U ||
        witness->browser_trace_verified != 1U || witness->zero_local_gaps != 1U ||
        witness->zero_local_waivers != 1U || witness->independent_vm81_authority != 0U ||
        witness->independent_hash72_clock != 0U || witness->frontend_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!p185_i141_git(witness->cumulative_validated_head, P185_I141_VALIDATED_HEAD) ||
        !p185_i141_git(witness->cumulative_receipt_blob, P185_I141_CUMULATIVE_RECEIPT_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size=(uint32_t)sizeof(*out_binding);
    out_binding->version=p185_i141_version_word();
    out_binding->pass_number=HHS_EXACT_PASS219_INHERITED_PASS185_NUMBER;
    out_binding->classification=HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->cumulative_local_closure_bound=1U;
    out_binding->production_runtime_os_bound=1U;
    out_binding->browser_trace_bound=1U;
    out_binding->no_new_authority_bound=1U;
    memcpy(out_binding->cumulative_validated_head,P185_I141_VALIDATED_HEAD,HHS_EXACT_PASS185_I141_GIT_SHA_STRLEN);
    memcpy(out_binding->cumulative_receipt_blob,P185_I141_CUMULATIVE_RECEIPT_BLOB,HHS_EXACT_PASS185_I141_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
