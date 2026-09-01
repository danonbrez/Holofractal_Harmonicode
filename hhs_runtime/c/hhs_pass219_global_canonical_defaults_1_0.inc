#include "../include/hhs_pass219_global_canonical_defaults_1_0.h"

#include <string.h>

static const HHSExactPass219CumulativeBindingKeyV1 HHS_PASS219_GLOBAL_DEFAULT_BINDINGS[] = {
    { 218U, 0U, 0U },
    { 217U, 0U, 0U },
    { 216U, 0U, 0U },
    { 215U, 0U, 0U },
    { 214U, 0U, 0U },
    { 213U, 0U, 0U },
    { 212U, 0U, 0U },
    { 211U, 0U, 0U },
    { 210U, 0U, 0U },
    { 209U, 0U, 0U },
    { 208U, 0U, 0U },
    { 207U, 0U, 0U },
    { 206U, 0U, 0U },
    { 205U, 0U, 0U },
    { 204U, 0U, 0U },
    { 203U, 0U, 0U },
    { 202U, 0U, 0U },
    { 201U, 0U, 0U },
    { 200U, 3U, 0U },
    { 200U, 2U, 0U },
    { 200U, 1U, 0U },
    { 199U, 0U, 0U },
    { 198U, 0U, 0U },
    { 197U, 0U, 0U },
    { 196U, 0U, 0U },
    { 195U, 0U, 0U },
    { 194U, 0U, 0U },
    { 193U, 0U, 0U },
    { 192U, 0U, 0U },
    { 191U, 0U, 0U },
    { 190U, 0U, 0U },
    { 189U, 0U, 0U },
    { 188U, 0U, 0U },
    { 187U, 0U, 0U },
    { 186U, 0U, 0U },
    { 185U, 0U, 0U },
    { 184U, 0U, 0U },
    { 183U, 0U, 0U },
    { 182U, 0U, 0U }
};

_Static_assert(
    sizeof(HHS_PASS219_GLOBAL_DEFAULT_BINDINGS) /
            sizeof(HHS_PASS219_GLOBAL_DEFAULT_BINDINGS[0]) ==
        HHS_EXACT_PASS219_GLOBAL_DEFAULT_BINDING_COUNT,
    "Pass219 global default binding census drift"
);

static uint32_t hhs_pass219_global_default_version_word(void) {
    return (HHS_EXACT_PASS219_GLOBAL_DEFAULT_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_GLOBAL_DEFAULT_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_GLOBAL_DEFAULT_VERSION_PATCH;
}

uint32_t hhs_exact_pass219_global_canonical_defaults_version(void) {
    return hhs_pass219_global_default_version_word();
}

HHSExactStatus hhs_exact_pass219_global_canonical_defaults_policy(
    HHSExactPass219GlobalCanonicalDefaultPolicyV1 *out_policy
) {
    if (out_policy == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }

    memset(out_policy, 0, sizeof(*out_policy));
    out_policy->struct_size = (uint32_t)sizeof(*out_policy);
    out_policy->version = hhs_pass219_global_default_version_word();
    out_policy->numbered_passes_are_additive = 1U;
    out_policy->successful_implementations_must_remain_reachable = 1U;
    out_policy->standalone_passes_allowed = 0U;
    out_policy->isolated_native_project_is_canonical_substitute = 0U;
    out_policy->cross_cutting_defaults_are_mandatory = 1U;
    out_policy->retroactive_repair_forward_required = 1U;
    out_policy->grandfather_bypass_allowed = 0U;
    out_policy->explicit_upgrade_or_deprecation_required = 1U;
    out_policy->singleton_vm81_authority_preserved = 1U;
    out_policy->exact_symbolic_authority_required = 1U;
    out_policy->wired_ceiling_pass = HHS_EXACT_PASS219_GLOBAL_DEFAULT_WIRED_CEILING;
    out_policy->wired_floor_pass = HHS_EXACT_PASS219_GLOBAL_DEFAULT_WIRED_FLOOR;
    out_policy->registered_binding_count = HHS_EXACT_PASS219_GLOBAL_DEFAULT_BINDING_COUNT;
    return HHS_EXACT_STATUS_OK;
}

size_t hhs_exact_pass219_global_canonical_defaults_binding_count(void) {
    return sizeof(HHS_PASS219_GLOBAL_DEFAULT_BINDINGS) /
           sizeof(HHS_PASS219_GLOBAL_DEFAULT_BINDINGS[0]);
}

HHSExactStatus hhs_exact_pass219_global_canonical_defaults_binding_at(
    size_t index,
    HHSExactPass219CumulativeBindingKeyV1 *out_binding
) {
    if (out_binding == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    if (index >= hhs_exact_pass219_global_canonical_defaults_binding_count()) {
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    *out_binding = HHS_PASS219_GLOBAL_DEFAULT_BINDINGS[index];
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_global_canonical_defaults_validate(void) {
    HHSExactPass219GlobalCanonicalDefaultPolicyV1 policy;
    size_t i;
    uint32_t seen[HHS_EXACT_PASS219_GLOBAL_DEFAULT_WIRED_CEILING + 1U] = {0U};

    if (hhs_exact_pass219_global_canonical_defaults_policy(&policy) !=
        HHS_EXACT_STATUS_OK) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (policy.numbered_passes_are_additive != 1U ||
        policy.successful_implementations_must_remain_reachable != 1U ||
        policy.standalone_passes_allowed != 0U ||
        policy.isolated_native_project_is_canonical_substitute != 0U ||
        policy.cross_cutting_defaults_are_mandatory != 1U ||
        policy.retroactive_repair_forward_required != 1U ||
        policy.grandfather_bypass_allowed != 0U ||
        policy.explicit_upgrade_or_deprecation_required != 1U ||
        policy.singleton_vm81_authority_preserved != 1U ||
        policy.exact_symbolic_authority_required != 1U ||
        policy.wired_ceiling_pass != HHS_EXACT_PASS219_GLOBAL_DEFAULT_WIRED_CEILING ||
        policy.wired_floor_pass != HHS_EXACT_PASS219_GLOBAL_DEFAULT_WIRED_FLOOR ||
        policy.registered_binding_count != HHS_EXACT_PASS219_GLOBAL_DEFAULT_BINDING_COUNT) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (hhs_exact_pass219_global_canonical_defaults_binding_count() !=
        HHS_EXACT_PASS219_GLOBAL_DEFAULT_BINDING_COUNT) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    for (i = 0U; i < hhs_exact_pass219_global_canonical_defaults_binding_count(); ++i) {
        HHSExactPass219CumulativeBindingKeyV1 key =
            HHS_PASS219_GLOBAL_DEFAULT_BINDINGS[i];

        if (key.pass_number < HHS_EXACT_PASS219_GLOBAL_DEFAULT_WIRED_FLOOR ||
            key.pass_number > HHS_EXACT_PASS219_GLOBAL_DEFAULT_WIRED_CEILING ||
            key.variant > HHS_EXACT_PASS219_BINDING_VARIANT_C) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        seen[key.pass_number] += 1U;
    }

    for (i = HHS_EXACT_PASS219_GLOBAL_DEFAULT_WIRED_FLOOR;
         i <= HHS_EXACT_PASS219_GLOBAL_DEFAULT_WIRED_CEILING;
         ++i) {
        const uint32_t expected = (i == 200U) ? 3U : 1U;
        if (seen[i] != expected) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }

    if (HHS_PASS219_GLOBAL_DEFAULT_BINDINGS[0].pass_number !=
            HHS_EXACT_PASS219_GLOBAL_DEFAULT_WIRED_CEILING ||
        HHS_PASS219_GLOBAL_DEFAULT_BINDINGS[
            HHS_EXACT_PASS219_GLOBAL_DEFAULT_BINDING_COUNT - 1U
        ].pass_number != HHS_EXACT_PASS219_GLOBAL_DEFAULT_WIRED_FLOOR) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    return HHS_EXACT_STATUS_OK;
}
