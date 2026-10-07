#include "hhs_pass220_i078_vm81_candidate_boundary_expansion_1_0.h"

#include <stdio.h>
#include <string.h>

static int emit_boundary(uint32_t node_id) {
    HHSExactVM81Frame frame;
    HHSExactPass220I078BoundaryV1 boundary;
    HHSExactStatus status;

    memset(&frame, 0, sizeof(frame));
    memset(&boundary, 0, sizeof(boundary));

    status = hhs_exact_pass220_i078_reference_candidate(node_id, &frame);
    if (status != HHS_EXACT_STATUS_OK)
        return 0;

    status = hhs_exact_pass220_i078_expand_candidate_boundary(
        node_id, &frame, &boundary);
    if (status != HHS_EXACT_STATUS_OK ||
        boundary.decision != HHS_EXACT_PASS220_I078_ADMIT)
        return 0;

    printf(
        "{"
        "\"node_id\":%u,"
        "\"decision\":%u,"
        "\"reason\":%u,"
        "\"frame_words\":%u,"
        "\"scale\":[%u,%u],"
        "\"scale_words_verified\":%u,"
        "\"zero_word_count\":%u,"
        "\"zero_fixed_point_words_verified\":%u,"
        "\"i077_execution_verified\":%u,"
        "\"candidate_frame_exact\":%u,"
        "\"uqcel_identity_evaluated\":%u,"
        "\"uqcel_transition_matches_i077\":%u,"
        "\"exact_scale1001_verified\":%u,"
        "\"zero_energy_fixed_point_verified\":%u,"
        "\"delta_e_zero\":%u,"
        "\"psi_zero\":%u,"
        "\"omega_true\":%u,"
        "\"deterministic_replay_verified\":%u,"
        "\"fail_closed_boundary\":%u,"
        "\"host_matrixpower_used\":%u,"
        "\"square_matrix_fallback_used\":%u,"
        "\"floating_point_used\":%u,"
        "\"numeric_exponent_evaluated\":%u,"
        "\"canonical_state_persisted\":%u,"
        "\"delta_e\":[%lld,%llu],"
        "\"psi\":[%lld,%llu],"
        "\"candidate_sha256\":\"%s\","
        "\"scale_witness_sha256\":\"%s\","
        "\"i077_receipt_hash72\":\"%s\","
        "\"i077_transition_hash216\":\"%s\","
        "\"boundary_change_hash72\":\"%s\","
        "\"boundary_receipt_hash72\":\"%s\","
        "\"boundary_hash216\":\"%s\","
        "\"boundary_identity216\":\"%s\""
        "}",
        (unsigned int)boundary.node_id,
        (unsigned int)boundary.decision,
        (unsigned int)boundary.reason,
        (unsigned int)boundary.frame_words,
        (unsigned int)boundary.scale_numerator,
        (unsigned int)boundary.scale_denominator,
        (unsigned int)boundary.scale_words_verified,
        (unsigned int)boundary.zero_word_count,
        (unsigned int)boundary.zero_fixed_point_words_verified,
        (unsigned int)boundary.i077_execution_verified,
        (unsigned int)boundary.candidate_frame_exact,
        (unsigned int)boundary.uqcel_identity_evaluated,
        (unsigned int)boundary.uqcel_transition_matches_i077,
        (unsigned int)boundary.exact_scale1001_verified,
        (unsigned int)boundary.zero_energy_fixed_point_verified,
        (unsigned int)boundary.delta_e_zero,
        (unsigned int)boundary.psi_zero,
        (unsigned int)boundary.omega_true,
        (unsigned int)boundary.deterministic_replay_verified,
        (unsigned int)boundary.fail_closed_boundary,
        (unsigned int)boundary.host_matrixpower_used,
        (unsigned int)boundary.square_matrix_fallback_used,
        (unsigned int)boundary.floating_point_used,
        (unsigned int)boundary.numeric_exponent_evaluated,
        (unsigned int)boundary.canonical_state_persisted,
        (long long)boundary.delta_e_numerator,
        (unsigned long long)boundary.delta_e_denominator,
        (long long)boundary.psi_numerator,
        (unsigned long long)boundary.psi_denominator,
        boundary.candidate_sha256,
        boundary.scale_witness_sha256,
        boundary.i077_receipt_hash72,
        boundary.i077_transition_hash216,
        boundary.boundary_change_hash72,
        boundary.boundary_receipt_hash72,
        boundary.boundary_hash216,
        boundary.boundary_identity216
    );
    return 1;
}

int main(void) {
    HHSExactPass220I078DescriptorV1 descriptor;
    HHSExactVM81Frame frame;
    HHSExactPass220I078BoundaryV1 rejected;
    HHSExactStatus status;

    memset(&descriptor, 0, sizeof(descriptor));
    status = hhs_exact_pass220_i078_descriptor(&descriptor);
    if (status != HHS_EXACT_STATUS_OK)
        return 1;

    memset(&frame, 0, sizeof(frame));
    status = hhs_exact_pass220_i078_reference_candidate(0U, &frame);
    if (status != HHS_EXACT_STATUS_OK)
        return 1;
    frame.words[30] ^= UINT64_C(1);
    memset(&rejected, 0, sizeof(rejected));
    status = hhs_exact_pass220_i078_expand_candidate_boundary(
        0U, &frame, &rejected);
    if (status != HHS_EXACT_STATUS_INVARIANT_FAILURE ||
        rejected.decision != HHS_EXACT_PASS220_I078_REJECT ||
        rejected.reason != HHS_EXACT_PASS220_I078_REASON_CANDIDATE_IDENTITY)
        return 1;

    printf(
        "{"
        "\"schema\":\"HHS_PASS_220_I078_NATIVE_PROBE_V1\","
        "\"descriptor\":{"
        "\"node_count\":%u,"
        "\"frame_words\":%u,"
        "\"scale\":[%u,%u],"
        "\"root_seed\":[%llu,%u],"
        "\"i077_binding_required\":%u,"
        "\"downstream_candidate_ingress\":%u,"
        "\"byte_exact_candidate_identity\":%u,"
        "\"uqcel_identity_evaluation\":%u,"
        "\"exact_rational_scale1001\":%u,"
        "\"zero_energy_fixed_point\":%u,"
        "\"delta_e_zero_required\":%u,"
        "\"psi_zero_required\":%u,"
        "\"omega_true_required\":%u,"
        "\"deterministic_replay_required\":%u,"
        "\"fail_closed_invalid_candidate\":%u,"
        "\"host_matrixpower_authority\":%u,"
        "\"host_square_matrix_fallback_authority\":%u,"
        "\"floating_point_authority\":%u,"
        "\"numeric_exponent_evaluation_authority\":%u,"
        "\"canonical_vm81_mutation_authority\":%u,"
        "\"canonical_hash72_commit_authority\":%u,"
        "\"canonical_hash216_commit_authority\":%u,"
        "\"canonical_persistence_authority\":%u,"
        "\"external_egress_authority\":%u"
        "},"
        "\"mutated_candidate_rejected\":true,"
        "\"boundaries\":[",
        (unsigned int)descriptor.node_count,
        (unsigned int)descriptor.frame_words,
        (unsigned int)descriptor.scale_numerator,
        (unsigned int)descriptor.scale_denominator,
        (unsigned long long)descriptor.root_seed_numerator,
        (unsigned int)descriptor.root_seed_denominator,
        (unsigned int)descriptor.i077_binding_required,
        (unsigned int)descriptor.downstream_candidate_ingress,
        (unsigned int)descriptor.byte_exact_candidate_identity,
        (unsigned int)descriptor.uqcel_identity_evaluation,
        (unsigned int)descriptor.exact_rational_scale1001,
        (unsigned int)descriptor.zero_energy_fixed_point,
        (unsigned int)descriptor.delta_e_zero_required,
        (unsigned int)descriptor.psi_zero_required,
        (unsigned int)descriptor.omega_true_required,
        (unsigned int)descriptor.deterministic_replay_required,
        (unsigned int)descriptor.fail_closed_invalid_candidate,
        (unsigned int)descriptor.host_matrixpower_authority,
        (unsigned int)descriptor.host_square_matrix_fallback_authority,
        (unsigned int)descriptor.floating_point_authority,
        (unsigned int)descriptor.numeric_exponent_evaluation_authority,
        (unsigned int)descriptor.canonical_vm81_mutation_authority,
        (unsigned int)descriptor.canonical_hash72_commit_authority,
        (unsigned int)descriptor.canonical_hash216_commit_authority,
        (unsigned int)descriptor.canonical_persistence_authority,
        (unsigned int)descriptor.external_egress_authority
    );

    if (!emit_boundary(0U))
        return 1;
    printf(",");
    if (!emit_boundary(1U))
        return 1;
    printf("]}\n");

    return 0;
}
