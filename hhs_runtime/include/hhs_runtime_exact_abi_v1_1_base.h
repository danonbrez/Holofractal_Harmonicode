#ifndef HHS_RUNTIME_EXACT_ABI_H
#define HHS_RUNTIME_EXACT_ABI_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_ABI_VERSION_MAJOR 1U
#define HHS_EXACT_ABI_VERSION_MINOR 1U
#define HHS_EXACT_ABI_VERSION_PATCH 0U

#define HHS_EXACT_HASH72_LEN 72U
#define HHS_EXACT_HASH72_STRLEN 73U
#define HHS_EXACT_HASH72_COORDS 5184U
#define HHS_EXACT_VM81_CELLS 81U
#define HHS_EXACT_VM81_WORD_BITS 64U
#define HHS_EXACT_VM81_FRAME_BITS 5184U
#define HHS_EXACT_VM81_FRAME_BYTES 648U
#define HHS_EXACT_PHASE_BASIS_COUNT 8U
#define HHS_EXACT_PHASE_PAIR_COUNT 64U
#define HHS_EXACT_X86_MAX_INSTRUCTION_BYTES 15U

#if defined(_WIN32)
#  define HHS_EXACT_API __declspec(dllexport)
#else
#  define HHS_EXACT_API __attribute__((visibility("default")))
#endif

typedef enum HHSExactStatus {
    HHS_EXACT_STATUS_OK = 0,
    HHS_EXACT_STATUS_INVALID_ARGUMENT = 1,
    HHS_EXACT_STATUS_RANGE_ERROR = 2,
    HHS_EXACT_STATUS_BUFFER_TOO_SMALL = 3,
    HHS_EXACT_STATUS_VERSION_MISMATCH = 4,
    HHS_EXACT_STATUS_INVARIANT_FAILURE = 5
} HHSExactStatus;

typedef enum HHSExactPhaseBasis {
    HHS_EXACT_PHASE_X = 0,
    HHS_EXACT_PHASE_Y = 1,
    HHS_EXACT_PHASE_Z = 2,
    HHS_EXACT_PHASE_W = 3,
    HHS_EXACT_PHASE_XY = 4,
    HHS_EXACT_PHASE_YX = 5,
    HHS_EXACT_PHASE_ZW = 6,
    HHS_EXACT_PHASE_WZ = 7
} HHSExactPhaseBasis;

typedef struct HHSExactRational64 {
    int64_t numerator;
    uint64_t denominator;
} HHSExactRational64;

typedef struct HHSExactPhaseProduct {
    uint32_t struct_size;
    uint32_t abi_version;
    uint8_t left_basis;
    uint8_t right_basis;
    uint8_t phase;
    uint8_t raw_additive_phase;
    uint8_t orientation;
    uint8_t closure;
    uint16_t ordered_tag;
} HHSExactPhaseProduct;

typedef struct HHSExactVM81Frame {
    uint64_t words[HHS_EXACT_VM81_CELLS];
} HHSExactVM81Frame;

typedef struct HHSExactX86InstructionBytes {
    uint32_t struct_size;
    uint32_t abi_version;
    uint8_t length;
    uint8_t bytes[HHS_EXACT_X86_MAX_INSTRUCTION_BYTES];
} HHSExactX86InstructionBytes;

typedef struct HHSExactABIDescriptor {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t hash72_len;
    uint32_t hash72_coords;
    uint32_t vm81_cells;
    uint32_t vm81_word_bits;
    uint32_t vm81_frame_bits;
    uint32_t vm81_frame_bytes;
    uint32_t phase_basis_count;
    uint32_t phase_pair_count;
    uint32_t x86_max_instruction_bytes;
    uint32_t legacy_v1_layout_preserved;
} HHSExactABIDescriptor;

extern const char HHS_EXACT_HASH72_ALPHABET[HHS_EXACT_HASH72_STRLEN];

HHS_EXACT_API uint32_t hhs_exact_abi_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_abi_descriptor(HHSExactABIDescriptor *out);
HHS_EXACT_API HHSExactStatus hhs_exact_abi_validate(void);

HHS_EXACT_API HHSExactStatus hhs_exact_hash72_coord_encode(
    uint8_t position,
    uint8_t symbol_index,
    uint16_t *out_coord
);

HHS_EXACT_API HHSExactStatus hhs_exact_hash72_coord_decode(
    uint16_t coord,
    uint8_t *out_position,
    uint8_t *out_symbol_index
);

HHS_EXACT_API HHSExactStatus hhs_exact_vm5184_address_encode(
    uint8_t cell81,
    uint8_t left_basis8,
    uint8_t right_basis8,
    uint16_t *out_address
);

HHS_EXACT_API HHSExactStatus hhs_exact_vm5184_address_decode(
    uint16_t address,
    uint8_t *out_cell81,
    uint8_t *out_left_basis8,
    uint8_t *out_right_basis8
);

HHS_EXACT_API HHSExactStatus hhs_exact_phase_product(
    uint8_t left_basis,
    uint8_t right_basis,
    HHSExactPhaseProduct *out
);

HHS_EXACT_API HHSExactStatus hhs_exact_vm81_frame_import_le(
    const uint8_t *bytes,
    size_t length,
    HHSExactVM81Frame *out_frame
);

HHS_EXACT_API HHSExactStatus hhs_exact_vm81_frame_export_le(
    const HHSExactVM81Frame *frame,
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
);

HHS_EXACT_API HHSExactStatus hhs_x86_64_ingress_exact(
    const uint8_t *bytes,
    size_t length,
    HHSExactX86InstructionBytes *out_instruction
);

HHS_EXACT_API HHSExactStatus hhs_x86_64_egress_exact(
    const HHSExactX86InstructionBytes *instruction,
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
);

HHS_EXACT_API HHSExactStatus hhs_x86_64_bytecode_copy_exact(
    const uint8_t *input,
    size_t length,
    uint8_t *output,
    size_t capacity,
    size_t *out_length
);

#ifdef __cplusplus
}
#endif

#endif
