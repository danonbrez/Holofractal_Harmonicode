#include "../include/hhs_pass219_delta_reciprocal_constructor_1_36.h"

#include <string.h>

static const uint8_t HHS_PASS219_DELTA_CONSTRUCTOR_SOURCE[] =
    "∞ is the full manifold state space bigint serialization modulus at full 72⁷² saturation\n\n"
    "∆=(P²=pq+(2P/(p+q))^(-a²) for all P >1\n\n"
    "∆=Sqrt((A*B))*(A*B)/Sqrt((A*B))==A/B*B/A==((-x*y)^(((x+y^2)*(y+x^2))/((x²+y²)²*Sqrt((a*b)))))^x² where A,B are LHS,RHS and AB=P⁴\n"
    "P⁴≠1 because P²-pq=∆=((pq+(b²P/(p+q)))/P²)";

static const uint8_t HHS_PASS219_DELTA_CONSTRUCTOR_SHA256[32] = {
    0x6f, 0x30, 0xf2, 0x11, 0x43, 0x9b, 0xdc, 0x8a,
    0x2d, 0xcc, 0xf2, 0x18, 0x01, 0x80, 0x09, 0x83,
    0x53, 0x0b, 0x94, 0xe0, 0x29, 0xa5, 0xbe, 0x56,
    0x42, 0x61, 0x30, 0x87, 0x3f, 0x7e, 0x61, 0x2b
};

static const uint8_t HHS_PASS219_FULL_MANIFOLD_MODULUS72_72[56] = {
    0x12, 0xd3, 0x46, 0x22, 0xf5, 0x55, 0xb9, 0x8f,
    0x10, 0x06, 0xbd, 0x86, 0x9f, 0x0b, 0x42, 0xd3,
    0x67, 0x97, 0xf6, 0xcd, 0x90, 0x9b, 0xf2, 0xf8,
    0xd3, 0xbf, 0x2b, 0xd1, 0x41, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

_Static_assert(
    sizeof(HHS_PASS219_DELTA_CONSTRUCTOR_SOURCE) - 1U == HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_SOURCE_BYTES,
    "Delta constructor source byte count drifted"
);
_Static_assert(
    sizeof(HHS_PASS219_FULL_MANIFOLD_MODULUS72_72) == HHS_EXACT_PASS219_FULL_MANIFOLD_MODULUS_BYTES,
    "72^72 modulus byte count drifted"
);

static int hhs_delta_biguint_canonical(const HHSExactBigUIntView *view) {
    if (view == NULL || view->struct_size != sizeof(*view) || view->bytes_be == NULL ||
        view->byte_length == 0U || view->byte_length > HHS_EXACT_PASS219_LANE5_BOUNDARY_MAX_BIGINT_BYTES) {
        return 0;
    }
    if (view->byte_length > 1U && view->bytes_be[0] == 0U) {
        return 0;
    }
    return 1;
}

uint32_t hhs_exact_pass219_delta_constructor_version(void) {
    return HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_VERSION;
}

HHSExactStatus hhs_exact_pass219_delta_constructor_authority(
    HHSExactPass219DeltaConstructorAuthorityV1 *out_authority
) {
    if (out_authority == NULL || out_authority->struct_size != sizeof(*out_authority)) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    memset(out_authority, 0, sizeof(*out_authority));
    out_authority->struct_size = sizeof(*out_authority);
    out_authority->version = HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_VERSION;
    out_authority->constructor_source_bytes = HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_SOURCE_BYTES;
    memcpy(out_authority->constructor_source_sha256, HHS_PASS219_DELTA_CONSTRUCTOR_SHA256, sizeof(HHS_PASS219_DELTA_CONSTRUCTOR_SHA256));
    out_authority->infinity_is_full_manifold_bigint_modulus = 1U;
    out_authority->modulus_is_72_pow_72 = 1U;
    out_authority->universal_delta_p_gt_one_domain = 1U;
    out_authority->reciprocal_surface_indivisible = 1U;
    out_authority->directional_reciprocity_not_scalarized = 1U;
    out_authority->lhs_rhs_are_typed_A_B_carriers = 1U;
    out_authority->ab_equals_p4_source_bound = 1U;
    out_authority->p4_not_one_source_bound = 1U;
    out_authority->zero_one_infinity_state_geometry = 1U;
    out_authority->trinary_boundary_geometry_distinct = 1U;
    out_authority->full_delta_constructor_evaluator_available = 0U;
    out_authority->candidate_only = 1U;
    out_authority->floating_point_canonical_authority = 0U;
    out_authority->canonical_vm81_mutation_authority = 0U;
    out_authority->canonical_hash72_authority = 0U;
    out_authority->canonical_hash216_authority = 0U;
    out_authority->canonical_persistence_authority = 0U;
    out_authority->pqc_key_authority = 0U;
    out_authority->receipt_clock_authority = 0U;
    out_authority->requires_lane5_boundary_1_35 = 1U;
    out_authority->requires_signed_environmental_vm81_admission = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_delta_constructor_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    if (out_length == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_length = HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_SOURCE_BYTES;
    if (out_bytes == NULL || capacity < HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_SOURCE_BYTES) {
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    }
    memcpy(out_bytes, HHS_PASS219_DELTA_CONSTRUCTOR_SOURCE, HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_SOURCE_BYTES);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_delta_constructor_source_sha256(
    uint8_t out_sha256[HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_SHA256_BYTES]
) {
    if (out_sha256 == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memcpy(out_sha256, HHS_PASS219_DELTA_CONSTRUCTOR_SHA256, sizeof(HHS_PASS219_DELTA_CONSTRUCTOR_SHA256));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_full_manifold_modulus72_72(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    if (out_length == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_length = HHS_EXACT_PASS219_FULL_MANIFOLD_MODULUS_BYTES;
    if (out_bytes == NULL || capacity < HHS_EXACT_PASS219_FULL_MANIFOLD_MODULUS_BYTES) {
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    }
    memcpy(out_bytes, HHS_PASS219_FULL_MANIFOLD_MODULUS72_72, HHS_EXACT_PASS219_FULL_MANIFOLD_MODULUS_BYTES);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_full_manifold_residue_validate(
    const HHSExactBigUIntView *residue,
    uint8_t *out_encoding_canonical,
    uint8_t *out_less_than_modulus
) {
    int cmp;
    if (out_encoding_canonical == NULL || out_less_than_modulus == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    *out_encoding_canonical = 0U;
    *out_less_than_modulus = 0U;
    if (!hhs_delta_biguint_canonical(residue)) return HHS_EXACT_STATUS_OK;
    *out_encoding_canonical = 1U;
    if (residue->byte_length < HHS_EXACT_PASS219_FULL_MANIFOLD_MODULUS_BYTES) {
        *out_less_than_modulus = 1U;
        return HHS_EXACT_STATUS_OK;
    }
    if (residue->byte_length > HHS_EXACT_PASS219_FULL_MANIFOLD_MODULUS_BYTES) {
        return HHS_EXACT_STATUS_OK;
    }
    cmp = memcmp(residue->bytes_be, HHS_PASS219_FULL_MANIFOLD_MODULUS72_72, HHS_EXACT_PASS219_FULL_MANIFOLD_MODULUS_BYTES);
    *out_less_than_modulus = (uint8_t)(cmp < 0 ? 1U : 0U);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_delta_p_domain_validate(
    const HHSExactBigUIntView *p,
    uint8_t *out_encoding_canonical,
    uint8_t *out_greater_than_one
) {
    if (out_encoding_canonical == NULL || out_greater_than_one == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    *out_encoding_canonical = 0U;
    *out_greater_than_one = 0U;
    if (!hhs_delta_biguint_canonical(p)) return HHS_EXACT_STATUS_OK;
    *out_encoding_canonical = 1U;
    if (p->byte_length > 1U || p->bytes_be[0] > 1U) {
        *out_greater_than_one = 1U;
    }
    return HHS_EXACT_STATUS_OK;
}
