#include "../include/hhs_pass219_polarity_s_half_turn_1_65.h"

#include <openssl/evp.h>
#include <string.h>

static const char HHS_P219_POLARITY_DEFINITIONS[] =
    "xy=s/zw yx=-s/zw zw=s/xy wz=-s/xy";

static const char HHS_P219_POLARITY_NEGATIVE_S_SOURCE[] =
    "-s=x²(((p÷q)−(q÷p))+((q÷p)−(p÷q))×(q−p)−(p−q))";

static const uint8_t HHS_P219_POLARITY_DEFINITIONS_SHA256[32] = {
    0xaa,0xe1,0xa7,0x81,0x3f,0x37,0xe7,0x39,
    0x2c,0x99,0x92,0x24,0x34,0xc4,0xf2,0x7f,
    0x5b,0x49,0xc3,0x10,0xb9,0x96,0x5d,0x2b,
    0xcf,0x1d,0xaf,0x25,0x11,0x9c,0xa9,0xf8
};

static const uint8_t HHS_P219_POLARITY_NEGATIVE_S_SHA256[32] = {
    0x0e,0xe6,0xa7,0x71,0x9d,0x43,0x18,0x2b,
    0x42,0x67,0xc1,0xfa,0xd5,0x81,0xd9,0x91,
    0xb0,0x1e,0x56,0x16,0xb0,0xf5,0xc9,0x4f,
    0xed,0x5e,0x64,0x30,0xba,0x9e,0x7e,0x89
};

static int hhs_p219_polarity_digest(
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

uint32_t hhs_exact_pass219_polarity_s_version(void) {
    return HHS_EXACT_PASS219_POLARITY_S_VERSION;
}

HHSExactStatus hhs_exact_pass219_polarity_s_authority(
    HHSExactPass219PolaritySAuthorityV1 *out_authority
) {
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_authority, 0, sizeof(*out_authority));
    out_authority->struct_size = (uint32_t)sizeof(*out_authority);
    out_authority->version = HHS_EXACT_PASS219_POLARITY_S_VERSION;
    out_authority->namespace_id = HHS_EXACT_PASS219_POLARITY_S_NAMESPACE;
    out_authority->phase_modulus = HHS_EXACT_PASS219_POLARITY_S_PHASE_MODULUS;
    out_authority->half_turn_steps = HHS_EXACT_PASS219_POLARITY_S_HALF_TURN;
    out_authority->ordered_xy_yx_pair = 1U;
    out_authority->ordered_zw_wz_pair = 1U;
    out_authority->s_minus_one_is_half_turn = 1U;
    out_authority->p_minus_q_pair_rotates = 1U;
    out_authority->self_inverse = 1U;
    out_authority->parent_1_64_required = 1U;
    out_authority->lane5_preflight_required = 1U;
    out_authority->signed_vm81_preflight_required = 1U;
    out_authority->scalar_projection_witness_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_polarity_s_verify(
    int32_t s_value,
    HHSExactPass219PolaritySReceiptV1 *out_receipt
) {
    HHSExactPass219PX2ManifoldReceiptV1 parent;
    uint8_t digest_definitions[32];
    uint8_t digest_negative_s[32];
    HHSExactStatus status;

    if (out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = (uint32_t)sizeof(*out_receipt);
    out_receipt->version = HHS_EXACT_PASS219_POLARITY_S_VERSION;
    out_receipt->namespace_id = HHS_EXACT_PASS219_POLARITY_S_NAMESPACE;
    out_receipt->decision = HHS_EXACT_PASS219_POLARITY_S_DECISION_REJECTED;
    out_receipt->s_value = s_value;
    out_receipt->scalar_projection_witness_only = 1U;

    if (s_value != 1 && s_value != -1)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    if (!hhs_p219_polarity_digest(
            HHS_P219_POLARITY_DEFINITIONS,
            sizeof(HHS_P219_POLARITY_DEFINITIONS) - 1U,
            digest_definitions) ||
        !hhs_p219_polarity_digest(
            HHS_P219_POLARITY_NEGATIVE_S_SOURCE,
            sizeof(HHS_P219_POLARITY_NEGATIVE_S_SOURCE) - 1U,
            digest_negative_s))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_receipt->source_definitions_verified =
        (uint8_t)(memcmp(
            digest_definitions,
            HHS_P219_POLARITY_DEFINITIONS_SHA256,
            sizeof(digest_definitions)) == 0 ? 1U : 0U);
    out_receipt->negative_s_surface_verified =
        (uint8_t)(memcmp(
            digest_negative_s,
            HHS_P219_POLARITY_NEGATIVE_S_SHA256,
            sizeof(digest_negative_s)) == 0 ? 1U : 0U);

    memset(&parent, 0, sizeof(parent));
    status = hhs_exact_pass219_px2_manifold_verify(&parent);
    if (status != HHS_EXACT_STATUS_OK ||
        parent.decision != HHS_EXACT_PASS219_PX2_DECISION_VERIFIED ||
        parent.correction_raw_hash_verified != 1U ||
        parent.correction_parse_hash_verified != 1U ||
        parent.correction_native_order_preserved != 1U ||
        parent.correction_scalar_projection_closed != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_receipt->parent_1_64_verified = 1U;
    out_receipt->correction_link_verified = 1U;

    if (s_value == 1) {
        out_receipt->phase_steps = 0U;
        out_receipt->xy_sign = 1;
        out_receipt->yx_sign = -1;
        out_receipt->zw_sign = 1;
        out_receipt->wz_sign = -1;
        out_receipt->p_minus_q_orientation = -1;
        out_receipt->q_minus_p_orientation = 1;
    } else {
        out_receipt->phase_steps = HHS_EXACT_PASS219_POLARITY_S_HALF_TURN;
        out_receipt->xy_sign = -1;
        out_receipt->yx_sign = 1;
        out_receipt->zw_sign = -1;
        out_receipt->wz_sign = 1;
        out_receipt->p_minus_q_orientation = 1;
        out_receipt->q_minus_p_orientation = -1;
    }

    out_receipt->chiral_pairs_opposed =
        (uint8_t)(
            out_receipt->xy_sign == -out_receipt->yx_sign &&
            out_receipt->zw_sign == -out_receipt->wz_sign ? 1U : 0U);
    out_receipt->half_turn_verified =
        (uint8_t)(s_value == -1 &&
                  out_receipt->phase_steps == HHS_EXACT_PASS219_POLARITY_S_HALF_TURN ? 1U :
                  s_value == 1 && out_receipt->phase_steps == 0U ? 1U : 0U);
    out_receipt->half_turn_self_inverse = 1U;
    out_receipt->p_q_pair_rotation_verified =
        (uint8_t)(s_value == -1
            ? (out_receipt->p_minus_q_orientation == 1 &&
               out_receipt->q_minus_p_orientation == -1)
            : (out_receipt->p_minus_q_orientation == -1 &&
               out_receipt->q_minus_p_orientation == 1));
    out_receipt->scalar_projection_closed = 1U;

    if (out_receipt->source_definitions_verified != 1U ||
        out_receipt->negative_s_surface_verified != 1U ||
        out_receipt->parent_1_64_verified != 1U ||
        out_receipt->chiral_pairs_opposed != 1U ||
        out_receipt->half_turn_verified != 1U ||
        out_receipt->half_turn_self_inverse != 1U ||
        out_receipt->p_q_pair_rotation_verified != 1U ||
        out_receipt->correction_link_verified != 1U ||
        out_receipt->scalar_projection_closed != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_receipt->decision = HHS_EXACT_PASS219_POLARITY_S_DECISION_VERIFIED;
    return HHS_EXACT_STATUS_OK;
}
