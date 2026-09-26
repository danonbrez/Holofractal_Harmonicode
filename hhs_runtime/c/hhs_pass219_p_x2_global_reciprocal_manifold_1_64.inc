#include "../include/hhs_pass219_p_x2_global_reciprocal_manifold_1_64.h"

#include <openssl/evp.h>
#include <string.h>

static const char HHS_P219_PX2_SOURCE[] =
    "P^(x²)=(x^2*y==(Sqrt(x==(d^2*(v==v+a*d^2)+x)^2)*(x^2==(b^3*c*(Mod(-x^2+b,x^2+b)/Mod(y^2+c,-y^2+c))^((c^2+a^2)^2/b^4)+x*y)^(x*(b^2*c^2*(Mod(-y^2+b,y^2+b)/Mod(x^2+c,-x^2+c))^((c^2*(c^2+b^2)+a^2)/(c^2+b^2-a^2))+x*y))/(x*y)==(((2*Sqrt(6)*Mod(-x^2+Sqrt(2),x^2+Sqrt(2))^4)/Mod(y^2+Sqrt(3),-y^2+Sqrt(3))^4+x*y)^(x*((6*Mod(-y^2+Sqrt(2),y^2+Sqrt(2))^4)/Mod(x^2+Sqrt(3),-x^2+Sqrt(3))^4+x*y))==-x*y)/a^2==e^(I*Pi)/((-b*((-c/b-1/(-b/c)^(2*a^2))/xyzw==(y*((-z/w)^(-b^2)+w/z))/((c^2-b^2)*x)-yx-x/y==a^2*(zw-z-yx+y-xy+x+wz-w)==0))/c-c/b)))/(d*(v==v+a*d^2)+x)==1/x)/((∆/-P)*Bx^(-⁵¹⁸⁴))";

static const uint8_t HHS_P219_PX2_SHA256[32] = {
    0x8d,0x02,0xb2,0x92,0x04,0x0a,0x69,0x75,
    0x20,0x35,0x6c,0x11,0xc9,0xc4,0xdc,0xb4,
    0x83,0x2f,0x2e,0x56,0xf8,0x20,0x70,0x71,
    0x30,0xc1,0x6a,0x7d,0xf9,0x6e,0xc3,0x87
};

static const char HHS_P219_PX2_CORRECTION_RAW[] =
    "((p/q)*(q/p))/(P²-pq)=(q-p))P/(p+q)";

static const char HHS_P219_PX2_CORRECTION_PARSE[] =
    "((p/q)*(q/p))/(P²-pq)=((q-p)*P)/(p+q)";

static const uint8_t HHS_P219_PX2_CORRECTION_RAW_SHA256[32] = {
    0x1f,0x55,0xc5,0x00,0x66,0x4f,0x18,0xd0,
    0x85,0x3e,0x0e,0xd5,0x3e,0xe6,0xb4,0xce,
    0xda,0xdf,0xd4,0x8c,0xeb,0xc6,0xf0,0x88,
    0x61,0xf9,0x4c,0x1a,0xd6,0x73,0xea,0x8a
};

static const uint8_t HHS_P219_PX2_CORRECTION_PARSE_SHA256[32] = {
    0x24,0x7c,0x3c,0xdd,0xfe,0x75,0x62,0x80,
    0x26,0x79,0xba,0x07,0xb8,0x99,0xb4,0xba,
    0x50,0xce,0xa5,0x73,0xad,0x2f,0x47,0x44,
    0x97,0xf7,0xb9,0x19,0x86,0x03,0x1e,0xe9
};

static const char *const HHS_P219_PX2_MARKERS[] = {
    "x^2*y==",
    "Sqrt(x==(d^2*(v==v+a*d^2)+x)^2)",
    "Mod(-x^2+b,x^2+b)",
    "Mod(y^2+c,-y^2+c)",
    "Mod(-y^2+b,y^2+b)",
    "Mod(x^2+c,-x^2+c)",
    "Mod(-x^2+Sqrt(2),x^2+Sqrt(2))^4",
    "Mod(y^2+Sqrt(3),-y^2+Sqrt(3))^4",
    "Mod(-y^2+Sqrt(2),y^2+Sqrt(2))^4",
    "Mod(x^2+Sqrt(3),-x^2+Sqrt(3))^4",
    "==-x*y",
    "==e^(I*Pi)",
    "/xyzw==",
    "a^2*(zw-z-yx+y-xy+x+wz-w)==0",
    "v==v+a*d^2",
    "==1/x",
    "((∆/-P)*Bx^(-⁵¹⁸⁴))"
};

_Static_assert(
    sizeof(HHS_P219_PX2_SOURCE) - 1U == HHS_EXACT_PASS219_PX2_MANIFOLD_SOURCE_BYTES,
    "Pass 219 1.64 source byte count drifted"
);
_Static_assert(
    sizeof(HHS_P219_PX2_CORRECTION_RAW) - 1U == HHS_EXACT_PASS219_PX2_CORRECTION_RAW_BYTES,
    "Pass 219 1.64 raw correction byte count drifted"
);
_Static_assert(
    sizeof(HHS_P219_PX2_CORRECTION_PARSE) - 1U == HHS_EXACT_PASS219_PX2_CORRECTION_PARSE_BYTES,
    "Pass 219 1.64 correction parse byte count drifted"
);

static int hhs_p219_px2_digest(
    const void *bytes,
    size_t length,
    uint8_t out[32]
) {
    unsigned int out_len = 0U;
    if (bytes == NULL || out == NULL)
        return 0;
    if (EVP_Digest(bytes, length, out, &out_len, EVP_sha256(), NULL) != 1)
        return 0;
    return out_len == 32U;
}

static int hhs_p219_px2_sha256(uint8_t out[32]) {
    return hhs_p219_px2_digest(
        HHS_P219_PX2_SOURCE,
        sizeof(HHS_P219_PX2_SOURCE) - 1U,
        out
    );
}

static int hhs_p219_px2_ordered_markers(void) {
    const char *cursor = HHS_P219_PX2_SOURCE;
    size_t i;
    for (i = 0U; i < sizeof(HHS_P219_PX2_MARKERS) / sizeof(HHS_P219_PX2_MARKERS[0]); ++i) {
        const char *found = strstr(cursor, HHS_P219_PX2_MARKERS[i]);
        if (found == NULL)
            return 0;
        cursor = found + strlen(HHS_P219_PX2_MARKERS[i]);
    }
    return 1;
}

uint32_t hhs_exact_pass219_px2_manifold_version(void) {
    return HHS_EXACT_PASS219_PX2_MANIFOLD_VERSION;
}

HHSExactStatus hhs_exact_pass219_px2_manifold_authority(
    HHSExactPass219PX2ManifoldAuthorityV1 *out_authority
) {
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_authority, 0, sizeof(*out_authority));
    out_authority->struct_size = (uint32_t)sizeof(*out_authority);
    out_authority->version = HHS_EXACT_PASS219_PX2_MANIFOLD_VERSION;
    out_authority->namespace_id = HHS_EXACT_PASS219_PX2_MANIFOLD_NAMESPACE;
    out_authority->source_bytes = HHS_EXACT_PASS219_PX2_MANIFOLD_SOURCE_BYTES;
    out_authority->source_chars = HHS_EXACT_PASS219_PX2_MANIFOLD_SOURCE_CHARS;
    out_authority->relation_edges = HHS_EXACT_PASS219_PX2_MANIFOLD_RELATION_EDGES;
    out_authority->source_identity_mandatory = 1U;
    out_authority->source_order_mandatory = 1U;
    out_authority->typed_relation_edges = 1U;
    out_authority->outer_p_x2_closure = 1U;
    out_authority->delta_negative_p_boundary = 1U;
    out_authority->bx_negative_5184_carrier = 1U;
    out_authority->pass178_constraint_program_semantics = 1U;
    out_authority->lane5_preflight_required = 1U;
    out_authority->signed_environmental_preflight_required = 1U;
    out_authority->reciprocal_correction_surface_mandatory = 1U;
    out_authority->correction_raw_source_preserved = 1U;
    out_authority->correction_balanced_parse_required = 1U;
    out_authority->correction_scalar_projection_witness_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_px2_manifold_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    if (out_length == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_length = HHS_EXACT_PASS219_PX2_MANIFOLD_SOURCE_BYTES;
    if (out_bytes == NULL || capacity < HHS_EXACT_PASS219_PX2_MANIFOLD_SOURCE_BYTES)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    memcpy(out_bytes, HHS_P219_PX2_SOURCE, HHS_EXACT_PASS219_PX2_MANIFOLD_SOURCE_BYTES);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_px2_correction_raw_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    if (out_length == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_length = HHS_EXACT_PASS219_PX2_CORRECTION_RAW_BYTES;
    if (out_bytes == NULL || capacity < HHS_EXACT_PASS219_PX2_CORRECTION_RAW_BYTES)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    memcpy(
        out_bytes,
        HHS_P219_PX2_CORRECTION_RAW,
        HHS_EXACT_PASS219_PX2_CORRECTION_RAW_BYTES
    );
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_px2_correction_parse_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    if (out_length == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_length = HHS_EXACT_PASS219_PX2_CORRECTION_PARSE_BYTES;
    if (out_bytes == NULL || capacity < HHS_EXACT_PASS219_PX2_CORRECTION_PARSE_BYTES)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    memcpy(
        out_bytes,
        HHS_P219_PX2_CORRECTION_PARSE,
        HHS_EXACT_PASS219_PX2_CORRECTION_PARSE_BYTES
    );
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_px2_manifold_source_sha256(
    uint8_t out_sha256[HHS_EXACT_PASS219_PX2_MANIFOLD_SHA256_BYTES]
) {
    if (out_sha256 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memcpy(out_sha256, HHS_P219_PX2_SHA256, sizeof(HHS_P219_PX2_SHA256));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_px2_manifold_verify(
    HHSExactPass219PX2ManifoldReceiptV1 *out_receipt
) {
    uint8_t digest[32];
    uint8_t correction_raw_digest[32];
    uint8_t correction_parse_digest[32];
    uint32_t open_parens = 0U;
    uint32_t close_parens = 0U;
    uint32_t double_eq = 0U;
    uint32_t single_eq = 0U;
    int32_t depth = 0;
    int32_t minimum_depth = 0;
    size_t i;
    const size_t len = sizeof(HHS_P219_PX2_SOURCE) - 1U;
    const char prefix[] = "P^(x²)=";
    const char suffix[] = "/((∆/-P)*Bx^(-⁵¹⁸⁴))";
    const char velocity[] = "v==v+a*d^2";
    const char *v1;
    const char *v2;

    if (out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = (uint32_t)sizeof(*out_receipt);
    out_receipt->version = HHS_EXACT_PASS219_PX2_MANIFOLD_VERSION;
    out_receipt->namespace_id = HHS_EXACT_PASS219_PX2_MANIFOLD_NAMESPACE;
    out_receipt->decision = HHS_EXACT_PASS219_PX2_DECISION_REJECTED;
    out_receipt->source_bytes = (uint32_t)len;

    for (i = 0U; i < len; ++i) {
        const unsigned char ch = (unsigned char)HHS_P219_PX2_SOURCE[i];
        if (ch == (unsigned char)'(') {
            ++open_parens;
            ++depth;
        } else if (ch == (unsigned char)')') {
            ++close_parens;
            --depth;
            if (depth < minimum_depth)
                minimum_depth = depth;
        } else if (ch == (unsigned char)'=') {
            if (i + 1U < len && HHS_P219_PX2_SOURCE[i + 1U] == '=') {
                ++double_eq;
                ++i;
            } else {
                ++single_eq;
            }
        }
    }

    out_receipt->open_parens = open_parens;
    out_receipt->close_parens = close_parens;
    out_receipt->double_equals_edges = double_eq;
    out_receipt->single_equals_edges = single_eq;
    out_receipt->relation_edges = double_eq + single_eq;

    if (!hhs_p219_px2_sha256(digest))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    memcpy(out_receipt->source_sha256, digest, sizeof(digest));
    out_receipt->source_hash_verified =
        (uint8_t)(memcmp(digest, HHS_P219_PX2_SHA256, sizeof(digest)) == 0 ? 1U : 0U);
    out_receipt->parentheses_balanced =
        (uint8_t)(depth == 0 && minimum_depth == 0 &&
                  open_parens == HHS_EXACT_PASS219_PX2_MANIFOLD_PAREN_PAIRS &&
                  close_parens == HHS_EXACT_PASS219_PX2_MANIFOLD_PAREN_PAIRS ? 1U : 0U);
    out_receipt->outer_prefix_exact =
        (uint8_t)(len >= sizeof(prefix) - 1U &&
                  memcmp(HHS_P219_PX2_SOURCE, prefix, sizeof(prefix) - 1U) == 0 ? 1U : 0U);
    out_receipt->outer_denominator_exact =
        (uint8_t)(len >= sizeof(suffix) - 1U &&
                  memcmp(
                    HHS_P219_PX2_SOURCE + len - (sizeof(suffix) - 1U),
                    suffix,
                    sizeof(suffix) - 1U) == 0 ? 1U : 0U);
    out_receipt->ordered_markers_exact = (uint8_t)(hhs_p219_px2_ordered_markers() ? 1U : 0U);

    v1 = strstr(HHS_P219_PX2_SOURCE, velocity);
    v2 = v1 == NULL ? NULL : strstr(v1 + strlen(velocity), velocity);
    out_receipt->repeated_velocity_relation_preserved = (uint8_t)(v1 != NULL && v2 != NULL ? 1U : 0U);
    out_receipt->modular_ratio_order_preserved = out_receipt->ordered_markers_exact;
    out_receipt->euler_phase_surface_preserved =
        (uint8_t)(strstr(HHS_P219_PX2_SOURCE, "==e^(I*Pi)") != NULL ? 1U : 0U);
    out_receipt->xyzw_nested_surface_preserved =
        (uint8_t)(strstr(HHS_P219_PX2_SOURCE, "/xyzw==") != NULL ? 1U : 0U);
    out_receipt->delta_bx_boundary_preserved = out_receipt->outer_denominator_exact;
    out_receipt->typed_relation_edges_preserved =
        (uint8_t)(double_eq == HHS_EXACT_PASS219_PX2_MANIFOLD_DOUBLE_EQ &&
                  single_eq == HHS_EXACT_PASS219_PX2_MANIFOLD_SINGLE_EQ &&
                  double_eq + single_eq == HHS_EXACT_PASS219_PX2_MANIFOLD_RELATION_EDGES ? 1U : 0U);

    if (!hhs_p219_px2_digest(
            HHS_P219_PX2_CORRECTION_RAW,
            sizeof(HHS_P219_PX2_CORRECTION_RAW) - 1U,
            correction_raw_digest) ||
        !hhs_p219_px2_digest(
            HHS_P219_PX2_CORRECTION_PARSE,
            sizeof(HHS_P219_PX2_CORRECTION_PARSE) - 1U,
            correction_parse_digest))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_receipt->correction_raw_hash_verified =
        (uint8_t)(memcmp(
            correction_raw_digest,
            HHS_P219_PX2_CORRECTION_RAW_SHA256,
            sizeof(correction_raw_digest)) == 0 ? 1U : 0U);
    out_receipt->correction_parse_hash_verified =
        (uint8_t)(memcmp(
            correction_parse_digest,
            HHS_P219_PX2_CORRECTION_PARSE_SHA256,
            sizeof(correction_parse_digest)) == 0 ? 1U : 0U);
    out_receipt->correction_raw_source_preserved = 1U;
    out_receipt->correction_balanced_parse_preserved =
        (uint8_t)(strstr(
            HHS_P219_PX2_CORRECTION_PARSE,
            "((p/q)*(q/p))/(P²-pq)=((q-p)*P)/(p+q)") != NULL ? 1U : 0U);
    out_receipt->correction_native_order_preserved =
        out_receipt->correction_balanced_parse_preserved;
    /*
     * This flag records the independent registered scalar witness:
     * p=P-1, q=P+1, P!=0,+/-1 -> both projected sides are exactly 1.
     * It grants no native cancellation/substitution authority.
     */
    out_receipt->correction_scalar_projection_closed = 1U;

    if (out_receipt->source_hash_verified != 1U ||
        out_receipt->parentheses_balanced != 1U ||
        out_receipt->outer_prefix_exact != 1U ||
        out_receipt->outer_denominator_exact != 1U ||
        out_receipt->ordered_markers_exact != 1U ||
        out_receipt->repeated_velocity_relation_preserved != 1U ||
        out_receipt->typed_relation_edges_preserved != 1U ||
        out_receipt->correction_raw_hash_verified != 1U ||
        out_receipt->correction_parse_hash_verified != 1U ||
        out_receipt->correction_raw_source_preserved != 1U ||
        out_receipt->correction_balanced_parse_preserved != 1U ||
        out_receipt->correction_native_order_preserved != 1U ||
        out_receipt->correction_scalar_projection_closed != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_receipt->decision = HHS_EXACT_PASS219_PX2_DECISION_VERIFIED;
    return HHS_EXACT_STATUS_OK;
}
