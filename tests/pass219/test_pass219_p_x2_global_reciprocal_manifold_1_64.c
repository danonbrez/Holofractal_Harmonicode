#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

int main(void) {
    HHSExactPass219PX2ManifoldAuthorityV1 authority;
    HHSExactPass219PX2ManifoldReceiptV1 receipt;
    uint8_t raw[HHS_EXACT_PASS219_PX2_CORRECTION_RAW_BYTES];
    uint8_t parsed[HHS_EXACT_PASS219_PX2_CORRECTION_PARSE_BYTES];
    size_t raw_len = 0U;
    size_t parsed_len = 0U;

    memset(&authority, 0, sizeof(authority));
    assert(hhs_exact_pass219_px2_manifold_authority(&authority) == HHS_EXACT_STATUS_OK);
    assert(authority.reciprocal_correction_surface_mandatory == 1U);
    assert(authority.correction_raw_source_preserved == 1U);
    assert(authority.correction_balanced_parse_required == 1U);
    assert(authority.correction_scalar_projection_witness_only == 1U);
    assert(authority.scalar_simplification_authority == 0U);
    assert(authority.delta_cancellation_authority == 0U);
    assert(authority.canonical_vm81_mutation_authority == 0U);

    assert(hhs_exact_pass219_px2_correction_raw_source(
        raw, sizeof(raw), &raw_len) == HHS_EXACT_STATUS_OK);
    assert(raw_len == HHS_EXACT_PASS219_PX2_CORRECTION_RAW_BYTES);
    assert(memcmp(
        raw,
        "((p/q)*(q/p))/(P²-pq)=(q-p))P/(p+q)",
        raw_len) == 0);

    assert(hhs_exact_pass219_px2_correction_parse_source(
        parsed, sizeof(parsed), &parsed_len) == HHS_EXACT_STATUS_OK);
    assert(parsed_len == HHS_EXACT_PASS219_PX2_CORRECTION_PARSE_BYTES);
    assert(memcmp(
        parsed,
        "((p/q)*(q/p))/(P²-pq)=((q-p)*P)/(p+q)",
        parsed_len) == 0);

    memset(&receipt, 0, sizeof(receipt));
    assert(hhs_exact_pass219_px2_manifold_verify(&receipt) == HHS_EXACT_STATUS_OK);
    assert(receipt.decision == HHS_EXACT_PASS219_PX2_DECISION_VERIFIED);
    assert(receipt.source_hash_verified == 1U);
    assert(receipt.parentheses_balanced == 1U);
    assert(receipt.typed_relation_edges_preserved == 1U);
    assert(receipt.correction_raw_hash_verified == 1U);
    assert(receipt.correction_parse_hash_verified == 1U);
    assert(receipt.correction_raw_source_preserved == 1U);
    assert(receipt.correction_balanced_parse_preserved == 1U);
    assert(receipt.correction_native_order_preserved == 1U);
    assert(receipt.correction_scalar_projection_closed == 1U);
    assert(receipt.scalar_simplification_authority == 0U);
    assert(receipt.equality_reversal_authority == 0U);
    assert(receipt.delta_cancellation_authority == 0U);
    assert(receipt.floating_point_canonical_authority == 0U);
    assert(receipt.canonical_vm81_mutation_authority == 0U);
    assert(receipt.canonical_hash72_authority == 0U);
    assert(receipt.canonical_hash216_authority == 0U);
    return 0;
}
