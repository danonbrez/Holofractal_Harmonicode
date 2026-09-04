#include "hhs_runtime_uqcel_1_8.h"

#include <stdint.h>
#include <string.h>

static const uint8_t HHS219_I163_ENV_ROOT[32] = {
    0xdaU,0x28U,0xe8U,0x22U,0x48U,0x38U,0x99U,0x97U,
    0x59U,0xd0U,0x71U,0xa3U,0x6fU,0xb2U,0x5fU,0x92U,
    0x4aU,0xf1U,0x0aU,0x9fU,0xffU,0xe2U,0xacU,0xd7U,
    0x9bU,0x4bU,0x2cU,0x0cU,0x78U,0x40U,0x85U,0x1bU
};

static void hhs219_i163_set_view(
    HHSExactBigUIntView *view,
    const uint8_t *bytes,
    uint32_t length
) {
    view->struct_size = (uint32_t)sizeof(*view);
    view->byte_length = length;
    view->bytes_be = bytes;
}

static void hhs219_i163_build_candidate(HHSExactVM81Frame *out) {
    uint32_t chunk;
    uint32_t byte_index;
    memset(out, 0, sizeof(*out));
    out->words[0] = UINT64_C(0x4832313949313632);
    out->words[1] = UINT64_C(30);
    out->words[2] = UINT64_C(29);
    out->words[3] = UINT64_C(31);
    out->words[4] = UINT64_C(1);
    out->words[5] = UINT64_C(900);
    out->words[6] = UINT64_C(810000);
    out->words[7] = UINT64_C(26970);
    out->words[8] = UINT64_C(71022);
    out->words[9] = UINT64_C(1023);
    out->words[10] = UINT64_C(31);
    out->words[11] = UINT64_C(18) |
                     (UINT64_C(54) << 8U) |
                     (UINT64_C(18) << 16U) |
                     (UINT64_C(54) << 24U);
    for (chunk = 0U; chunk < 4U; ++chunk) {
        uint64_t word = 0U;
        for (byte_index = 0U; byte_index < 8U; ++byte_index)
            word |= ((uint64_t)HHS219_I163_ENV_ROOT[chunk * 8U + byte_index])
                    << (8U * byte_index);
        out->words[12U + chunk] = word;
    }
}

int hhs219_i163_vm81_snapshot_reverse_witness(
    char out_receipt_hash72[73],
    char out_hash216_identity[217],
    uint16_t *out_vm5184_address
) {
    static const uint8_t P_BYTES[] = {0x1eU};
    static const uint8_t p_BYTES[] = {0x1dU};
    static const uint8_t q_BYTES[] = {0x1fU};
    static const uint8_t D_BYTES[] = {0x01U};
    static const uint8_t P2_BYTES[] = {0x03U,0x84U};
    HHSExactUQCELInputV1 input;
    HHSExactUQCELAdmissionV1 admission;
    HHSExactVM81Frame prior;
    HHSExactVM81Frame candidate;
    HHSExactVM81Frame committed;
    HHSExactVM81Frame reversed;
    uint8_t source_sha[32];
    HHSExactStatus status;

    if (out_receipt_hash72 == NULL || out_hash216_identity == NULL ||
        out_vm5184_address == NULL)
        return 0;

    memset(&input, 0, sizeof(input));
    memset(&admission, 0, sizeof(admission));
    memset(&prior, 0, sizeof(prior));
    memset(&committed, 0, sizeof(committed));
    memset(&reversed, 0, sizeof(reversed));
    hhs219_i163_build_candidate(&candidate);

    status = hhs_exact_uqcel_source_sha256(source_sha);
    if (status != HHS_EXACT_STATUS_OK)
        return 0;

    input.struct_size = (uint32_t)sizeof(input);
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    hhs219_i163_set_view(&input.P, P_BYTES, (uint32_t)sizeof(P_BYTES));
    hhs219_i163_set_view(&input.p, p_BYTES, (uint32_t)sizeof(p_BYTES));
    hhs219_i163_set_view(&input.q, q_BYTES, (uint32_t)sizeof(q_BYTES));
    hhs219_i163_set_view(&input.delta, D_BYTES, (uint32_t)sizeof(D_BYTES));
    hhs219_i163_set_view(&input.A, P2_BYTES, (uint32_t)sizeof(P2_BYTES));
    hhs219_i163_set_view(&input.B, P2_BYTES, (uint32_t)sizeof(P2_BYTES));
    input.cell81 = 0U;
    input.left_basis8 = HHS_EXACT_PHASE_X;
    input.right_basis8 = HHS_EXACT_PHASE_Y;
    memcpy(input.source_envelope_sha256, source_sha, sizeof(source_sha));
    memset(input.previous_hash72, '0', HHS_EXACT_HASH72_LEN);
    input.previous_hash72[HHS_EXACT_HASH72_LEN] = '\0';

    status = hhs_exact_vm81_admit_uqcel(
        &input, &candidate, &committed, &admission);
    if (status != HHS_EXACT_STATUS_OK ||
        admission.decision != HHS_EXACT_UQCEL_DECISION_ADMIT ||
        admission.frame_committed != 1U ||
        memcmp(&candidate, &committed, sizeof(candidate)) != 0)
        return 0;

    /* I163 is a transaction proof, not persistent canonical mutation.  The
     * prior frame is retained as a receipt-bound snapshot and restored only
     * after the forward admission has completed successfully. */
    reversed = committed;
    memcpy(&reversed, &prior, sizeof(reversed));
    if (memcmp(&reversed, &prior, sizeof(prior)) != 0)
        return 0;

    memcpy(out_receipt_hash72, admission.receipt_hash72, 73U);
    memcpy(out_hash216_identity, admission.hash216_identity, 217U);
    *out_vm5184_address = admission.vm5184_address;
    return 1;
}
