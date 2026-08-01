#ifndef HHS_PASS186_X64_VM81_Q144_ABI_H
#define HHS_PASS186_X64_VM81_Q144_ABI_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS186_ABI_VERSION 1U
#define HHS186_Q12 12U
#define HHS186_Q144 144U
#define HHS186_FACTORIAL_7 5040U
#define HHS186_FACTORIAL_Q144_LANES 35U
#define HHS186_Q144_LANES 36U
#define HHS186_VM81_CELLS 81U
#define HHS186_VM81_OPERATIONS_PER_CELL 64U
#define HHS186_VM5184_STATES 5184U
#define HHS186_G243_CONTROLS 243U
#define HHS186_HYDRATED_STATES 1259712U
#define HHS186_OUTER_ENVELOPE_MODULUS 1259713U
#define HHS186_U72_RING 72U

#if defined(_WIN32)
#  define HHS186_API __declspec(dllexport)
#else
#  define HHS186_API __attribute__((visibility("default")))
#endif

typedef enum HHS186Status {
    HHS186_STATUS_OK = 0,
    HHS186_STATUS_INVALID_ARGUMENT = 1,
    HHS186_STATUS_ABI_VERSION_MISMATCH = 2,
    HHS186_STATUS_RANGE_ERROR = 3,
    HHS186_STATUS_ARITHMETIC_OVERFLOW = 4,
    HHS186_STATUS_INVARIANT_FAILURE = 5
} HHS186Status;

typedef enum HHS186OrderedBasis {
    HHS186_BASIS_X = 0,
    HHS186_BASIS_Y = 1,
    HHS186_BASIS_Z = 2,
    HHS186_BASIS_W = 3,
    HHS186_BASIS_XY = 4,
    HHS186_BASIS_YX = 5,
    HHS186_BASIS_ZW = 6,
    HHS186_BASIS_WZ = 7
} HHS186OrderedBasis;

typedef struct HHS186Quantization {
    uint32_t struct_size;
    uint32_t abi_version;
    uint16_t g243;
    uint8_t opcode_lane36;
    uint8_t root_row12;
    uint8_t root_col12;
    uint8_t reserved[3];
} HHS186Quantization;

typedef struct HHS186RegisterImage {
    int64_t ingress_rdi_x;
    int64_t ingress_rsi_y;
    int64_t ingress_rdx_z;
    int64_t ingress_rcx_w;
    int64_t canonical_r8_x;
    int64_t canonical_r9_y;
    int64_t canonical_r10_z;
    int64_t canonical_r11_w;
} HHS186RegisterImage;

typedef struct HHS186MappingResult {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t status;
    uint32_t instruction_state5184;
    uint32_t projected_state5184_243;
    uint32_t q144_index;
    uint16_t vm81_cell;
    uint8_t vm81_operation64;
    uint8_t ordered_basis;
    uint8_t operation_class8;
    uint8_t factorial_admitted;
    uint8_t closure_q144_lane;
    uint8_t u72_pair;
    uint8_t u72_index;
    uint8_t root_row12;
    uint8_t root_col12;
    uint8_t opcode_lane36;
    uint8_t reserved0;
    uint16_t g243;
    uint16_t ordered_tag;
    int64_t ordered_left;
    int64_t ordered_right;
    int64_t ordered_product_witness;
    uint32_t factorial7;
    uint32_t q144;
    uint32_t vm5184;
    uint32_t hydrated_cardinality;
    uint32_t outer_envelope_modulus;
} HHS186MappingResult;

/*
 * System V AMD64 ingress contract:
 *   RDI=x, RSI=y, RDX=z, RCX=w, R8=&quantization, R9=&result.
 * The function preserves ordered-basis identity even when integer magnitudes
 * coincide (for example xy and yx).
 */
HHS186_API
HHS186Status hhs186_x64_vm81_q144_map(
    int64_t x,
    int64_t y,
    int64_t z,
    int64_t w,
    const HHS186Quantization *quantization,
    HHS186MappingResult *result
);

HHS186_API
HHS186Status hhs186_x64_vm81_q144_unproject(
    uint32_t projected_state,
    HHS186Quantization *quantization,
    HHS186MappingResult *coordinates
);

/* x86_64 System V assembly probe. */
HHS186_API
void hhs186_x64_capture_xyzw_registers(
    int64_t x,
    int64_t y,
    int64_t z,
    int64_t w,
    HHS186RegisterImage *image
);

#ifdef __cplusplus
}
#endif

#endif
