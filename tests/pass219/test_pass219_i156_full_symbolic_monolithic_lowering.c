#include "hhs_runtime_exact_abi.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef struct OwnedRatio {
    uint8_t numerator[8];
    uint8_t denominator[8];
} OwnedRatio;

static void set_big(
    HHSExactBigUIntView *view,
    uint8_t *storage,
    uint64_t value
) {
    size_t start = 0U;
    size_t i;
    for (i = 0U; i < 8U; ++i)
        storage[7U - i] = (uint8_t)(value >> (i * 8U));
    while (start < 7U && storage[start] == 0U)
        ++start;
    view->struct_size = (uint32_t)sizeof(*view);
    view->byte_length = (uint32_t)(8U - start);
    view->bytes_be = storage + start;
}

static void set_ratio(
    HHSExactPass219SignedRatioViewV1 *ratio,
    OwnedRatio *owner,
    int8_t sign,
    uint64_t numerator,
    uint64_t denominator
) {
    memset(ratio, 0, sizeof(*ratio));
    memset(owner, 0, sizeof(*owner));
    ratio->struct_size = (uint32_t)sizeof(*ratio);
    ratio->sign = sign;
    set_big(&ratio->numerator, owner->numerator, numerator);
    set_big(&ratio->denominator, owner->denominator, denominator);
}

static int hash216_valid(const char *value) {
    size_t i;
    if (value == NULL ||
        value[HHS_EXACT_PASS219_FULL_SYMBOLIC_HASH216_LEN] != '\0')
        return 0;
    for (i = 0U;
         i < HHS_EXACT_PASS219_FULL_SYMBOLIC_HASH216_LEN;
         ++i) {
        if (strchr(HHS_EXACT_HASH72_ALPHABET, value[i]) == NULL)
            return 0;
    }
    return 1;
}

static int build_witness(
    HHSExactPass219FullSymbolicWitnessV1 *witness,
    OwnedRatio owners[HHS_EXACT_PASS219_FULL_SYMBOLIC_TERM_COUNT]
) {
    HHSExactPass219MonolithicDescriptorV1 descriptor;
    uint32_t i;

    if (hhs_exact_pass219_monolithic_descriptor(&descriptor) !=
        HHS_EXACT_STATUS_OK)
        return 0;

    memset(witness, 0, sizeof(*witness));
    witness->struct_size = (uint32_t)sizeof(*witness);
    witness->version = hhs_exact_pass219_full_symbolic_version();
    memcpy(
        witness->source_sha256,
        descriptor.machine_source_sha256,
        sizeof(witness->source_sha256));
    for (i = 0U; i < sizeof(witness->pass159_provenance_root); ++i)
        witness->pass159_provenance_root[i] = (uint8_t)(i + 1U);

    if (hhs_exact_pass219_octonion_expand(
            1U, 2U, 3U, 4U, &witness->octonion_state) !=
        HHS_EXACT_STATUS_OK)
        return 0;

    /*
     * The lowering verifier consumes values already produced by an exact
     * candidate evaluator.  Use one mathematically equal ratio across every
     * source edge to isolate and test the monolithic transaction mechanics.
     * 2/3 and 4/6 prove equality uses exact cross multiplication rather than
     * byte identity.
     */
    for (i = 0U;
         i < HHS_EXACT_PASS219_FULL_SYMBOLIC_TERM_COUNT;
         ++i) {
        if ((i & 1U) == 0U)
            set_ratio(&witness->terms[i], &owners[i], 1, 2U, 3U);
        else
            set_ratio(&witness->terms[i], &owners[i], 1, 4U, 6U);
    }
    return 1;
}

int main(void) {
    HHSExactPass219FullSymbolicDescriptorV1 descriptor;
    HHSExactPass219FullSymbolicWitnessV1 witness;
    HHSExactPass219FullSymbolicLoweringV1 lowering;
    OwnedRatio owners[HHS_EXACT_PASS219_FULL_SYMBOLIC_TERM_COUNT];
    uint32_t family;

    if (hhs_exact_pass219_full_symbolic_descriptor(&descriptor) !=
            HHS_EXACT_STATUS_OK ||
        descriptor.term_count != HHS_EXACT_PASS219_FULL_SYMBOLIC_TERM_COUNT ||
        descriptor.edge_count != HHS_EXACT_PASS219_MONOLITHIC_EDGE_COUNT ||
        descriptor.family_count != HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT ||
        descriptor.required_edge_mask !=
            HHS_EXACT_PASS219_MONOLITHIC_ALL_EDGE_MASK ||
        descriptor.required_family_mask != HHS_EXACT_PASS219_FAMILY_REQUIRED ||
        descriptor.residual_mask_on_complete_lowering != 0U ||
        descriptor.source_structure_preserved != 1U ||
        descriptor.all_edges_single_transaction != 1U ||
        descriptor.pass159_provenance_required != 1U ||
        descriptor.exact_big_ratio_cross_multiply != 1U ||
        descriptor.ordered_octonion_state_required != 1U ||
        descriptor.legacy_v1_full_symbolic_input_sufficient != 0U ||
        descriptor.candidate_value_producer_included != 0U ||
        descriptor.vm81_execution_included != 0U ||
        descriptor.hash72_execution_receipt_included != 0U ||
        descriptor.deterministic_replay_included != 0U ||
        descriptor.floating_point_authority != 0U ||
        descriptor.vm81_mutation_authority != 0U ||
        descriptor.hash72_commit_authority != 0U ||
        descriptor.persistence_mutation_authority != 0U)
        return 1;

    if (!build_witness(&witness, owners))
        return 2;

    if (hhs_exact_pass219_full_symbolic_lower(&witness, &lowering) !=
            HHS_EXACT_STATUS_OK ||
        lowering.decision != HHS_EXACT_PASS219_FULL_SYMBOLIC_LOWERED ||
        lowering.reject_reason != HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_NONE ||
        lowering.resolved_family_mask != HHS_EXACT_PASS219_FAMILY_REQUIRED ||
        lowering.failed_family_mask != 0U ||
        lowering.edge_satisfied_mask !=
            HHS_EXACT_PASS219_MONOLITHIC_ALL_EDGE_MASK ||
        lowering.edge_failed_mask != 0U ||
        lowering.edge_unresolved_mask != 0U ||
        lowering.residual_mask != 0U ||
        lowering.source_identity_exact != 1U ||
        lowering.provenance_root_bound != 1U ||
        lowering.all_values_exact != 1U ||
        lowering.one_candidate_state != 1U ||
        lowering.ordered_xy_yx_bound != 1U ||
        lowering.monolithic_chain_lowered != 1U ||
        lowering.candidate_value_producer_authority != 0U ||
        lowering.vm81_execution_verified != 0U ||
        lowering.hash72_execution_receipt_verified != 0U ||
        lowering.deterministic_replay_verified != 0U ||
        lowering.floating_point_authority != 0U ||
        lowering.vm81_mutation_authority != 0U ||
        lowering.hash72_commit_authority != 0U ||
        lowering.persistence_mutation_authority != 0U ||
        !hash216_valid(lowering.candidate_state_hash216))
        return 3;

    for (family = 0U;
         family < HHS_EXACT_PASS219_FULL_SYMBOLIC_FAMILY_COUNT;
         ++family) {
        if (!hash216_valid(lowering.family_witness_hash216[family]))
            return 4;
    }

    /* Edge 5 mismatch must reject the matrix/tensor/modular families. */
    if (!build_witness(&witness, owners))
        return 5;
    set_ratio(
        &witness.terms[HHS_EXACT_PASS219_FS_TERM_MOD_F_OVER_U_OVER_BT],
        &owners[HHS_EXACT_PASS219_FS_TERM_MOD_F_OVER_U_OVER_BT],
        1, 5U, 7U);
    if (hhs_exact_pass219_full_symbolic_lower(&witness, &lowering) !=
            HHS_EXACT_STATUS_OK ||
        lowering.decision != HHS_EXACT_PASS219_FULL_SYMBOLIC_REJECTED ||
        lowering.reject_reason !=
            HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_EDGE_MISMATCH ||
        (lowering.edge_failed_mask & (UINT64_C(1) << 5U)) == 0U ||
        (lowering.failed_family_mask &
            HHS_EXACT_PASS219_FAMILY_MATRIX) == 0U ||
        (lowering.failed_family_mask &
            HHS_EXACT_PASS219_FAMILY_TENSOR_SUBSTITUTION) == 0U ||
        (lowering.failed_family_mask &
            HHS_EXACT_PASS219_FAMILY_MODULAR) == 0U ||
        lowering.residual_mask != HHS_UQCEL_RESIDUAL_FULL_SOURCE)
        return 6;

    /* Source drift cannot be lowered. */
    if (!build_witness(&witness, owners))
        return 7;
    witness.source_sha256[0] ^= UINT8_C(1);
    if (hhs_exact_pass219_full_symbolic_lower(&witness, &lowering) !=
            HHS_EXACT_STATUS_OK ||
        lowering.decision != HHS_EXACT_PASS219_FULL_SYMBOLIC_REJECTED ||
        lowering.reject_reason !=
            HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_SOURCE_IDENTITY)
        return 8;

    /* A zero provenance root cannot identify one candidate transaction. */
    if (!build_witness(&witness, owners))
        return 9;
    memset(
        witness.pass159_provenance_root,
        0,
        sizeof(witness.pass159_provenance_root));
    if (hhs_exact_pass219_full_symbolic_lower(&witness, &lowering) !=
            HHS_EXACT_STATUS_OK ||
        lowering.decision != HHS_EXACT_PASS219_FULL_SYMBOLIC_REJECTED ||
        lowering.reject_reason !=
            HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_PROVENANCE_ROOT)
        return 10;

    /* sign=0 with nonzero numerator is a malformed exact ratio witness. */
    if (!build_witness(&witness, owners))
        return 11;
    witness.terms[0].sign = 0;
    if (hhs_exact_pass219_full_symbolic_lower(&witness, &lowering) !=
            HHS_EXACT_STATUS_OK ||
        lowering.decision != HHS_EXACT_PASS219_FULL_SYMBOLIC_REJECTED ||
        lowering.reject_reason !=
            HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_RATIO_ENCODING)
        return 12;

    puts("PASS219_I156_FULL_SYMBOLIC_MONOLITHIC_LOWERING_OK");
    return 0;
}
