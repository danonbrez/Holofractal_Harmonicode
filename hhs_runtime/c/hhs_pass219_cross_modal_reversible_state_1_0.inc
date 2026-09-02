#include "../include/hhs_pass219_cross_modal_reversible_state_1_0.h"

#include <stddef.h>
#include <string.h>

static int hhs_p219_xmodal_mul_u64(uint64_t a, uint64_t b, uint64_t *out) {
    if (out == NULL) {
        return 0;
    }
    if (a != 0u && b > UINT64_MAX / a) {
        return 0;
    }
    *out = a * b;
    return 1;
}

static int hhs_p219_xmodal_add_u64(uint64_t a, uint64_t b, uint64_t *out) {
    if (out == NULL || b > UINT64_MAX - a) {
        return 0;
    }
    *out = a + b;
    return 1;
}

HHSExactPass219CrossModalStatusV1
hhs_exact_pass219_cross_modal_state_validate(
    const HHSExactPass219CrossModalStateWitnessV1 *witness) {
    if (witness == NULL) {
        return HHS_PASS219_CROSS_MODAL_NULL;
    }
    if (witness->version != HHS_PASS219_CROSS_MODAL_VERSION ||
        witness->depth > HHS_PASS219_CROSS_MODAL_MAX_DEPTH ||
        witness->required_modalities < 2u ||
        witness->required_modalities > HHS_PASS219_CROSS_MODAL_MAX_MODALITIES ||
        witness->constraints_total == 0u ||
        witness->constraints_total > HHS_PASS219_CROSS_MODAL_MAX_CONSTRAINTS) {
        return HHS_PASS219_CROSS_MODAL_RANGE_ERROR;
    }
    if (witness->genesis_lineage_bound != 1u ||
        witness->hash216_lineage_bound != 1u) {
        return HHS_PASS219_CROSS_MODAL_LINEAGE_ERROR;
    }
    if (witness->ordered_phase_path_bound != 1u) {
        return HHS_PASS219_CROSS_MODAL_PHASE_ORDER_ERROR;
    }
    if (witness->mapped_modalities != witness->required_modalities) {
        return HHS_PASS219_CROSS_MODAL_MODALITY_COVERAGE_ERROR;
    }
    if (witness->reversible_edges_required == 0u ||
        witness->reversible_edges_verified != witness->reversible_edges_required) {
        return HHS_PASS219_CROSS_MODAL_ROUNDTRIP_ERROR;
    }
    if (witness->constraints_passed != witness->constraints_total ||
        witness->global_constraint_root_bound != 1u ||
        witness->modality_registry_root_bound != 1u) {
        return HHS_PASS219_CROSS_MODAL_CONSTRAINT_ERROR;
    }
    if (witness->singleton_vm81_authority_required != 1u ||
        witness->candidate_mutation_authority != 0u ||
        witness->floating_point_authority != 0u) {
        return HHS_PASS219_CROSS_MODAL_AUTHORITY_ERROR;
    }
    return HHS_PASS219_CROSS_MODAL_OK;
}

HHSExactPass219CrossModalStatusV1
hhs_exact_pass219_cross_modal_work_plan(
    uint32_t depth,
    uint32_t modalities,
    uint32_t constraints_per_state,
    uint32_t cached_prefix_depth,
    uint32_t changed_constraints,
    uint32_t prefix_proof_valid,
    uint32_t hub_roundtrip_verified,
    HHSExactPass219CrossModalWorkPlanV1 *out) {
    uint64_t dm = 0u;
    uint64_t baseline_constraints = 0u;
    uint64_t directed_pairs = 0u;
    uint64_t baseline_translations = 0u;
    uint64_t baseline_total = 0u;
    uint64_t active_depth = 0u;
    uint64_t candidate_constraints = 0u;
    uint64_t changed_constraint_checks = 0u;
    uint64_t hub_checks_per_state = 0u;
    uint64_t candidate_translations = 0u;
    uint64_t candidate_total = 0u;
    uint64_t tmp = 0u;
    int candidate_safe = 0;

    if (out == NULL) {
        return HHS_PASS219_CROSS_MODAL_NULL;
    }
    memset(out, 0, sizeof(*out));
    if (depth == 0u || depth > HHS_PASS219_CROSS_MODAL_MAX_DEPTH ||
        modalities < 2u || modalities > HHS_PASS219_CROSS_MODAL_MAX_MODALITIES ||
        constraints_per_state == 0u ||
        constraints_per_state > HHS_PASS219_CROSS_MODAL_MAX_CONSTRAINTS ||
        cached_prefix_depth > depth ||
        changed_constraints > constraints_per_state ||
        prefix_proof_valid > 1u ||
        hub_roundtrip_verified > 1u) {
        return HHS_PASS219_CROSS_MODAL_RANGE_ERROR;
    }

    if (!hhs_p219_xmodal_mul_u64((uint64_t)depth, (uint64_t)modalities, &dm) ||
        !hhs_p219_xmodal_mul_u64(dm, (uint64_t)constraints_per_state, &baseline_constraints) ||
        !hhs_p219_xmodal_mul_u64((uint64_t)modalities, (uint64_t)(modalities - 1u), &directed_pairs) ||
        !hhs_p219_xmodal_mul_u64((uint64_t)depth, directed_pairs, &baseline_translations) ||
        !hhs_p219_xmodal_add_u64(baseline_constraints, baseline_translations, &tmp) ||
        !hhs_p219_xmodal_add_u64(tmp, (uint64_t)depth, &baseline_total)) {
        return HHS_PASS219_CROSS_MODAL_OVERFLOW;
    }

    active_depth = (uint64_t)depth - (uint64_t)cached_prefix_depth;
    if (!hhs_p219_xmodal_mul_u64(active_depth, (uint64_t)modalities, &dm) ||
        !hhs_p219_xmodal_mul_u64(dm, (uint64_t)constraints_per_state, &candidate_constraints) ||
        !hhs_p219_xmodal_mul_u64((uint64_t)changed_constraints, (uint64_t)modalities, &changed_constraint_checks) ||
        !hhs_p219_xmodal_add_u64(candidate_constraints, changed_constraint_checks, &candidate_constraints) ||
        !hhs_p219_xmodal_mul_u64(2u, (uint64_t)modalities, &hub_checks_per_state) ||
        !hhs_p219_xmodal_mul_u64(active_depth + 1u, hub_checks_per_state, &candidate_translations) ||
        !hhs_p219_xmodal_add_u64(candidate_constraints, candidate_translations, &tmp) ||
        !hhs_p219_xmodal_add_u64(tmp, (uint64_t)depth, &candidate_total)) {
        return HHS_PASS219_CROSS_MODAL_OVERFLOW;
    }

    candidate_safe =
        prefix_proof_valid == 1u &&
        hub_roundtrip_verified == 1u &&
        cached_prefix_depth > 0u &&
        candidate_total < baseline_total;

    out->version = HHS_PASS219_CROSS_MODAL_VERSION;
    out->depth = depth;
    out->modalities = modalities;
    out->constraints_per_state = constraints_per_state;
    out->cached_prefix_depth = cached_prefix_depth;
    out->changed_constraints = changed_constraints;
    out->prefix_proof_valid = prefix_proof_valid;
    out->hub_roundtrip_verified = hub_roundtrip_verified;
    out->optimization_selected = candidate_safe ? 1u : 0u;
    out->complete_fallback = candidate_safe ? 0u : 1u;
    out->baseline_constraint_checks = baseline_constraints;
    out->baseline_translation_checks = baseline_translations;
    out->baseline_authority_checks = depth;
    out->baseline_total_work = baseline_total;
    out->candidate_constraint_checks = candidate_constraints;
    out->candidate_translation_checks = candidate_translations;
    out->candidate_authority_checks = depth;
    out->candidate_total_work = candidate_total;
    out->selected_total_work = candidate_safe ? candidate_total : baseline_total;
    out->exact_work_saved = candidate_safe ? baseline_total - candidate_total : 0u;

    return HHS_PASS219_CROSS_MODAL_OK;
}
