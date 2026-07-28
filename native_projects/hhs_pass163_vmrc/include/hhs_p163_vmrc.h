#ifndef HHS_P163_VMRC_H
#define HHS_P163_VMRC_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_P163_VMRC_ABI_VERSION UINT32_C(1)
#define HHS_P163_VMRC_THREADS UINT32_C(64)
#define HHS_P163_VMRC_POSITIONS UINT32_C(81)
#define HHS_P163_VMRC_PORT_POSITIONS UINT32_C(9)
#define HHS_P163_VMRC_PARAMETER_POSITIONS UINT32_C(72)
#define HHS_P163_VMRC_COORDINATES UINT32_C(5184)
#define HHS_P163_VMRC_SNAPSHOT_BYTES UINT32_C(648)
#define HHS_P163_VMRC_BASE64_SYMBOLS UINT32_C(864)

typedef enum hhs_p163_vmrc_status {
    HHS_P163_VMRC_OK = 0,
    HHS_P163_VMRC_INVALID_ARGUMENT = 1,
    HHS_P163_VMRC_OUT_OF_RANGE = 2,
    HHS_P163_VMRC_BUFFER_TOO_SMALL = 3,
    HHS_P163_VMRC_MALFORMED_BASE64 = 4,
    HHS_P163_VMRC_NONCANONICAL_BASE64 = 5,
    HHS_P163_VMRC_DIRECT_MUTATION_DENIED = 6
} hhs_p163_vmrc_status;

typedef struct hhs_p163_vmrc_snapshot {
    uint32_t abi_version;
    uint8_t bytes[HHS_P163_VMRC_SNAPSHOT_BYTES];
} hhs_p163_vmrc_snapshot;

hhs_p163_vmrc_status hhs_p163_vmrc_snapshot_init(
    hhs_p163_vmrc_snapshot *snapshot
);
hhs_p163_vmrc_status hhs_p163_vmrc_snapshot_get(
    const hhs_p163_vmrc_snapshot *snapshot,
    uint32_t position,
    uint32_t thread,
    uint8_t *value_out
);
hhs_p163_vmrc_status hhs_p163_vmrc_snapshot_authority_set(
    hhs_p163_vmrc_snapshot *snapshot,
    uint32_t position,
    uint32_t thread,
    uint8_t value,
    const void *authority_token,
    const void *expected_authority_token
);
hhs_p163_vmrc_status hhs_p163_vmrc_base64_encode(
    const hhs_p163_vmrc_snapshot *snapshot,
    char *output,
    size_t output_capacity,
    size_t *output_length
);
hhs_p163_vmrc_status hhs_p163_vmrc_base64_decode(
    const char *input,
    size_t input_length,
    hhs_p163_vmrc_snapshot *snapshot_out
);

#ifdef __cplusplus
}
#endif

#endif
