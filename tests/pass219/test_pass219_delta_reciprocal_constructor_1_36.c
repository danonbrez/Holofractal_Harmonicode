#include "hhs_pass219_delta_reciprocal_constructor_1_36.h"

#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { if (!(expr)) { \
    fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); return 1; \
} } while (0)

static const uint8_t EXPECTED_SOURCE[] =
    "∞ is the full manifold state space bigint serialization modulus at full 72⁷² saturation\n\n"
    "∆=(P²=pq+(2P/(p+q))^(-a²) for all P >1\n\n"
    "∆=Sqrt((A*B))*(A*B)/Sqrt((A*B))==A/B*B/A==((-x*y)^(((x+y^2)*(y+x^2))/((x²+y²)²*Sqrt((a*b)))))^x² where A,B are LHS,RHS and AB=P⁴\n"
    "P⁴≠1 because P²-pq=∆=((pq+(b²P/(p+q)))/P²)";

static const uint8_t EXPECTED_SHA256[32] = {
    0x6f, 0x30, 0xf2, 0x11, 0x43, 0x9b, 0xdc, 0x8a,
    0x2d, 0xcc, 0xf2, 0x18, 0x01, 0x80, 0x09, 0x83,
    0x53, 0x0b, 0x94, 0xe0, 0x29, 0xa5, 0xbe, 0x56,
    0x42, 0x61, 0x30, 0x87, 0x3f, 0x7e, 0x61, 0x2b
};

static const uint8_t EXPECTED_MODULUS[56] = {
    0x12, 0xd3, 0x46, 0x22, 0xf5, 0x55, 0xb9, 0x8f,
    0x10, 0x06, 0xbd, 0x86, 0x9f, 0x0b, 0x42, 0xd3,
    0x67, 0x97, 0xf6, 0xcd, 0x90, 0x9b, 0xf2, 0xf8,
    0xd3, 0xbf, 0x2b, 0xd1, 0x41, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

static HHSExactBigUIntView view(const uint8_t *bytes, uint32_t length) {
    HHSExactBigUIntView v;
    memset(&v, 0, sizeof(v));
    v.struct_size = sizeof(v);
    v.bytes_be = bytes;
    v.byte_length = length;
    return v;
}

int main(void) {
    HHSExactPass219DeltaConstructorAuthorityV1 authority;
    uint8_t source[HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_SOURCE_BYTES];
    uint8_t digest[32];
    uint8_t exposed_digest[32];
    uint8_t modulus[HHS_EXACT_PASS219_FULL_MANIFOLD_MODULUS_BYTES];
    size_t length = 0U;
    uint8_t canonical = 0U;
    uint8_t accepted = 0U;
    uint8_t zero[] = {0U};
    uint8_t one[] = {1U};
    uint8_t two[] = {2U};
    uint8_t p256[] = {1U, 0U};
    uint8_t bad_leading[] = {0U, 2U};
    uint8_t too_large[57];
    HHSExactBigUIntView v;

    memset(&authority, 0, sizeof(authority));
    authority.struct_size = sizeof(authority);
    CHECK(hhs_exact_pass219_delta_constructor_authority(&authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.version == HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_VERSION);
    CHECK(authority.constructor_source_bytes == HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_SOURCE_BYTES);
    CHECK(authority.infinity_is_full_manifold_bigint_modulus == 1U);
    CHECK(authority.modulus_is_72_pow_72 == 1U);
    CHECK(authority.universal_delta_p_gt_one_domain == 1U);
    CHECK(authority.reciprocal_surface_indivisible == 1U);
    CHECK(authority.directional_reciprocity_not_scalarized == 1U);
    CHECK(authority.lhs_rhs_are_typed_A_B_carriers == 1U);
    CHECK(authority.ab_equals_p4_source_bound == 1U);
    CHECK(authority.p4_not_one_source_bound == 1U);
    CHECK(authority.zero_one_infinity_state_geometry == 1U);
    CHECK(authority.trinary_boundary_geometry_distinct == 1U);
    CHECK(authority.full_delta_constructor_evaluator_available == 0U);
    CHECK(authority.candidate_only == 1U);
    CHECK(authority.floating_point_canonical_authority == 0U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.requires_lane5_boundary_1_35 == 1U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);

    CHECK(hhs_exact_pass219_delta_constructor_source(source, sizeof(source), &length) == HHS_EXACT_STATUS_OK);
    CHECK(length == sizeof(EXPECTED_SOURCE) - 1U);
    CHECK(length == HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_SOURCE_BYTES);
    CHECK(memcmp(source, EXPECTED_SOURCE, length) == 0);
    CHECK(SHA256(source, length, digest) != NULL);
    CHECK(memcmp(digest, EXPECTED_SHA256, sizeof(digest)) == 0);
    CHECK(hhs_exact_pass219_delta_constructor_source_sha256(exposed_digest) == HHS_EXACT_STATUS_OK);
    CHECK(memcmp(exposed_digest, EXPECTED_SHA256, sizeof(exposed_digest)) == 0);

    CHECK(hhs_exact_pass219_full_manifold_modulus72_72(modulus, sizeof(modulus), &length) == HHS_EXACT_STATUS_OK);
    CHECK(length == sizeof(EXPECTED_MODULUS));
    CHECK(memcmp(modulus, EXPECTED_MODULUS, sizeof(modulus)) == 0);

    v = view(zero, sizeof(zero));
    CHECK(hhs_exact_pass219_full_manifold_residue_validate(&v, &canonical, &accepted) == HHS_EXACT_STATUS_OK);
    CHECK(canonical == 1U && accepted == 1U);

    v = view(EXPECTED_MODULUS, sizeof(EXPECTED_MODULUS));
    CHECK(hhs_exact_pass219_full_manifold_residue_validate(&v, &canonical, &accepted) == HHS_EXACT_STATUS_OK);
    CHECK(canonical == 1U && accepted == 0U);

    memset(too_large, 0, sizeof(too_large));
    too_large[0] = 1U;
    v = view(too_large, sizeof(too_large));
    CHECK(hhs_exact_pass219_full_manifold_residue_validate(&v, &canonical, &accepted) == HHS_EXACT_STATUS_OK);
    CHECK(canonical == 1U && accepted == 0U);

    v = view(bad_leading, sizeof(bad_leading));
    CHECK(hhs_exact_pass219_full_manifold_residue_validate(&v, &canonical, &accepted) == HHS_EXACT_STATUS_OK);
    CHECK(canonical == 0U && accepted == 0U);

    v = view(zero, sizeof(zero));
    CHECK(hhs_exact_pass219_delta_p_domain_validate(&v, &canonical, &accepted) == HHS_EXACT_STATUS_OK);
    CHECK(canonical == 1U && accepted == 0U);
    v = view(one, sizeof(one));
    CHECK(hhs_exact_pass219_delta_p_domain_validate(&v, &canonical, &accepted) == HHS_EXACT_STATUS_OK);
    CHECK(canonical == 1U && accepted == 0U);
    v = view(two, sizeof(two));
    CHECK(hhs_exact_pass219_delta_p_domain_validate(&v, &canonical, &accepted) == HHS_EXACT_STATUS_OK);
    CHECK(canonical == 1U && accepted == 1U);
    v = view(p256, sizeof(p256));
    CHECK(hhs_exact_pass219_delta_p_domain_validate(&v, &canonical, &accepted) == HHS_EXACT_STATUS_OK);
    CHECK(canonical == 1U && accepted == 1U);
    v = view(bad_leading, sizeof(bad_leading));
    CHECK(hhs_exact_pass219_delta_p_domain_validate(&v, &canonical, &accepted) == HHS_EXACT_STATUS_OK);
    CHECK(canonical == 0U && accepted == 0U);

    printf(
        "PASS219_DELTA_RECIPROCAL_CONSTRUCTOR_PASS source_bytes=%u modulus_bytes=%u p_gt_1=1 scalarized=0 full_evaluator=0\n",
        (unsigned)HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_SOURCE_BYTES,
        (unsigned)HHS_EXACT_PASS219_FULL_MANIFOLD_MODULUS_BYTES
    );
    return 0;
}
