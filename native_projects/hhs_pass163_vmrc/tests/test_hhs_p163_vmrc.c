#include "hhs_p163_vmrc.h"

#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

int main(void) {
    hhs_p163_vmrc_snapshot snapshot;
    hhs_p163_vmrc_snapshot decoded;
    char encoded[HHS_P163_VMRC_BASE64_SYMBOLS + 1U];
    size_t encoded_length = 0U;
    uint8_t value = UINT8_C(0);
    int authority = 1;
    int peer = 2;

    assert(
        HHS_P163_VMRC_THREADS * HHS_P163_VMRC_POSITIONS
        == HHS_P163_VMRC_COORDINATES
    );
    assert(
        HHS_P163_VMRC_PORT_POSITIONS
        + HHS_P163_VMRC_PARAMETER_POSITIONS
        == HHS_P163_VMRC_POSITIONS
    );
    assert(
        HHS_P163_VMRC_COORDINATES / UINT32_C(8)
        == HHS_P163_VMRC_SNAPSHOT_BYTES
    );
    assert(
        HHS_P163_VMRC_SNAPSHOT_BYTES * UINT32_C(4) / UINT32_C(3)
        == HHS_P163_VMRC_BASE64_SYMBOLS
    );

    assert(
        hhs_p163_vmrc_snapshot_init(&snapshot)
        == HHS_P163_VMRC_OK
    );
    assert(
        hhs_p163_vmrc_snapshot_authority_set(
            &snapshot,
            80U,
            63U,
            1U,
            &authority,
            &authority
        ) == HHS_P163_VMRC_OK
    );
    assert(
        hhs_p163_vmrc_snapshot_get(
            &snapshot,
            80U,
            63U,
            &value
        ) == HHS_P163_VMRC_OK
    );
    assert(value == UINT8_C(1));
    assert(
        hhs_p163_vmrc_snapshot_authority_set(
            &snapshot,
            0U,
            0U,
            1U,
            &peer,
            &authority
        ) == HHS_P163_VMRC_DIRECT_MUTATION_DENIED
    );
    assert(
        hhs_p163_vmrc_snapshot_authority_set(
            &snapshot,
            81U,
            0U,
            1U,
            &authority,
            &authority
        ) == HHS_P163_VMRC_OUT_OF_RANGE
    );
    assert(
        hhs_p163_vmrc_snapshot_authority_set(
            &snapshot,
            0U,
            64U,
            1U,
            &authority,
            &authority
        ) == HHS_P163_VMRC_OUT_OF_RANGE
    );

    assert(
        hhs_p163_vmrc_base64_encode(
            &snapshot,
            encoded,
            sizeof(encoded),
            &encoded_length
        ) == HHS_P163_VMRC_OK
    );
    assert(encoded_length == (size_t)HHS_P163_VMRC_BASE64_SYMBOLS);
    assert(strchr(encoded, '=') == NULL);
    assert(
        hhs_p163_vmrc_base64_decode(
            encoded,
            encoded_length,
            &decoded
        ) == HHS_P163_VMRC_OK
    );
    assert(
        memcmp(
            snapshot.bytes,
            decoded.bytes,
            sizeof(snapshot.bytes)
        ) == 0
    );

    encoded[0] = '!';
    assert(
        hhs_p163_vmrc_base64_decode(
            encoded,
            encoded_length,
            &decoded
        ) == HHS_P163_VMRC_MALFORMED_BASE64
    );
    return 0;
}
