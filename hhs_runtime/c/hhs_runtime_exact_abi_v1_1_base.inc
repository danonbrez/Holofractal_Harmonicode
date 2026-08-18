#include "../include/hhs_runtime_exact_abi.h"

#include <string.h>

_Static_assert(HHS_EXACT_HASH72_LEN * HHS_EXACT_HASH72_LEN == HHS_EXACT_HASH72_COORDS,
               "Hash72 positional plane must contain 5184 coordinates");
_Static_assert(HHS_EXACT_VM81_CELLS * HHS_EXACT_PHASE_PAIR_COUNT == HHS_EXACT_HASH72_COORDS,
               "VM81 ordered phase address plane must contain 5184 coordinates");
_Static_assert(sizeof(HHSExactVM81Frame) == HHS_EXACT_VM81_FRAME_BYTES,
               "VM81 exact frame must contain 648 bytes");

const char HHS_EXACT_HASH72_ALPHABET[HHS_EXACT_HASH72_STRLEN] =
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";

static const uint8_t HHS_EXACT_PHASE_ANCHOR[HHS_EXACT_PHASE_BASIS_COUNT] = {
    18U, 54U, 18U, 54U, 0U, 36U, 0U, 36U
};

static uint32_t hhs_exact_version_word(void) {
    return (HHS_EXACT_ABI_VERSION_MAJOR << 16) |
           (HHS_EXACT_ABI_VERSION_MINOR << 8) |
           HHS_EXACT_ABI_VERSION_PATCH;
}

static uint8_t hhs_exact_wrap72_u16(uint16_t value) {
    return (uint8_t)(value % HHS_EXACT_HASH72_LEN);
}

static uint16_t hhs_exact_basis_tag(uint8_t basis) {
    static const uint16_t tags[HHS_EXACT_PHASE_BASIS_COUNT] = {
        UINT16_C(0x0058), UINT16_C(0x0059), UINT16_C(0x005A), UINT16_C(0x0057),
        UINT16_C(0x5859), UINT16_C(0x5958), UINT16_C(0x5A57), UINT16_C(0x575A)
    };
    return tags[basis];
}

static int hhs_exact_phase_override(uint8_t left, uint8_t right, uint8_t *phase) {
    struct PairPhase { uint8_t left; uint8_t right; uint8_t phase; };
    static const struct PairPhase overrides[] = {
        {HHS_EXACT_PHASE_X,  HHS_EXACT_PHASE_Y,  0U},
        {HHS_EXACT_PHASE_Y,  HHS_EXACT_PHASE_X, 36U},
        {HHS_EXACT_PHASE_Z,  HHS_EXACT_PHASE_W,  0U},
        {HHS_EXACT_PHASE_W,  HHS_EXACT_PHASE_Z, 36U},
        {HHS_EXACT_PHASE_XY, HHS_EXACT_PHASE_YX,36U},
        {HHS_EXACT_PHASE_YX, HHS_EXACT_PHASE_XY,36U},
        {HHS_EXACT_PHASE_ZW, HHS_EXACT_PHASE_WZ,36U},
        {HHS_EXACT_PHASE_WZ, HHS_EXACT_PHASE_ZW,36U},
        {HHS_EXACT_PHASE_XY, HHS_EXACT_PHASE_ZW, 0U},
        {HHS_EXACT_PHASE_ZW, HHS_EXACT_PHASE_XY, 0U},
        {HHS_EXACT_PHASE_YX, HHS_EXACT_PHASE_WZ, 0U},
        {HHS_EXACT_PHASE_WZ, HHS_EXACT_PHASE_YX, 0U}
    };
    size_t i;
    for (i = 0; i < sizeof(overrides) / sizeof(overrides[0]); ++i) {
        if (overrides[i].left == left && overrides[i].right == right) {
            *phase = overrides[i].phase;
            return 1;
        }
    }
    return 0;
}

uint32_t hhs_exact_abi_version(void) {
    return hhs_exact_version_word();
}

HHSExactStatus hhs_exact_abi_descriptor(HHSExactABIDescriptor *out) {
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->abi_version = hhs_exact_version_word();
    out->hash72_len = HHS_EXACT_HASH72_LEN;
    out->hash72_coords = HHS_EXACT_HASH72_COORDS;
    out->vm81_cells = HHS_EXACT_VM81_CELLS;
    out->vm81_word_bits = HHS_EXACT_VM81_WORD_BITS;
    out->vm81_frame_bits = HHS_EXACT_VM81_FRAME_BITS;
    out->vm81_frame_bytes = HHS_EXACT_VM81_FRAME_BYTES;
    out->phase_basis_count = HHS_EXACT_PHASE_BASIS_COUNT;
    out->phase_pair_count = HHS_EXACT_PHASE_PAIR_COUNT;
    out->x86_max_instruction_bytes = HHS_EXACT_X86_MAX_INSTRUCTION_BYTES;
    out->legacy_v1_layout_preserved = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_hash72_coord_encode(
    uint8_t position,
    uint8_t symbol_index,
    uint16_t *out_coord
) {
    if (out_coord == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (position >= HHS_EXACT_HASH72_LEN || symbol_index >= HHS_EXACT_HASH72_LEN)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    *out_coord = (uint16_t)((uint16_t)position * HHS_EXACT_HASH72_LEN + symbol_index);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_hash72_coord_decode(
    uint16_t coord,
    uint8_t *out_position,
    uint8_t *out_symbol_index
) {
    if (out_position == NULL || out_symbol_index == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (coord >= HHS_EXACT_HASH72_COORDS)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    *out_position = (uint8_t)(coord / HHS_EXACT_HASH72_LEN);
    *out_symbol_index = (uint8_t)(coord % HHS_EXACT_HASH72_LEN);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_vm5184_address_encode(
    uint8_t cell81,
    uint8_t left_basis8,
    uint8_t right_basis8,
    uint16_t *out_address
) {
    uint16_t operation;
    if (out_address == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (cell81 >= HHS_EXACT_VM81_CELLS ||
        left_basis8 >= HHS_EXACT_PHASE_BASIS_COUNT ||
        right_basis8 >= HHS_EXACT_PHASE_BASIS_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    operation = (uint16_t)((uint16_t)left_basis8 * HHS_EXACT_PHASE_BASIS_COUNT + right_basis8);
    *out_address = (uint16_t)((uint16_t)cell81 * HHS_EXACT_PHASE_PAIR_COUNT + operation);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_vm5184_address_decode(
    uint16_t address,
    uint8_t *out_cell81,
    uint8_t *out_left_basis8,
    uint8_t *out_right_basis8
) {
    uint8_t operation;
    if (out_cell81 == NULL || out_left_basis8 == NULL || out_right_basis8 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (address >= HHS_EXACT_HASH72_COORDS)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    *out_cell81 = (uint8_t)(address / HHS_EXACT_PHASE_PAIR_COUNT);
    operation = (uint8_t)(address % HHS_EXACT_PHASE_PAIR_COUNT);
    *out_left_basis8 = (uint8_t)(operation / HHS_EXACT_PHASE_BASIS_COUNT);
    *out_right_basis8 = (uint8_t)(operation % HHS_EXACT_PHASE_BASIS_COUNT);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_phase_product(
    uint8_t left_basis,
    uint8_t right_basis,
    HHSExactPhaseProduct *out
) {
    uint8_t raw;
    uint8_t phase;
    uint8_t tag_basis;
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (left_basis >= HHS_EXACT_PHASE_BASIS_COUNT || right_basis >= HHS_EXACT_PHASE_BASIS_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->abi_version = hhs_exact_version_word();
    out->left_basis = left_basis;
    out->right_basis = right_basis;
    raw = hhs_exact_wrap72_u16((uint16_t)HHS_EXACT_PHASE_ANCHOR[left_basis] +
                               (uint16_t)HHS_EXACT_PHASE_ANCHOR[right_basis]);
    phase = raw;
    (void)hhs_exact_phase_override(left_basis, right_basis, &phase);
    out->raw_additive_phase = raw;
    out->phase = phase;

    tag_basis = left_basis;
    if (left_basis == HHS_EXACT_PHASE_X && right_basis == HHS_EXACT_PHASE_Y)
        tag_basis = HHS_EXACT_PHASE_XY;
    else if (left_basis == HHS_EXACT_PHASE_Y && right_basis == HHS_EXACT_PHASE_X)
        tag_basis = HHS_EXACT_PHASE_YX;
    else if (left_basis == HHS_EXACT_PHASE_Z && right_basis == HHS_EXACT_PHASE_W)
        tag_basis = HHS_EXACT_PHASE_ZW;
    else if (left_basis == HHS_EXACT_PHASE_W && right_basis == HHS_EXACT_PHASE_Z)
        tag_basis = HHS_EXACT_PHASE_WZ;
    out->ordered_tag = hhs_exact_basis_tag(tag_basis);

    if ((left_basis == HHS_EXACT_PHASE_X && right_basis == HHS_EXACT_PHASE_Y) ||
        (left_basis == HHS_EXACT_PHASE_Z && right_basis == HHS_EXACT_PHASE_W))
        out->orientation = 1U;
    else if ((left_basis == HHS_EXACT_PHASE_Y && right_basis == HHS_EXACT_PHASE_X) ||
             (left_basis == HHS_EXACT_PHASE_W && right_basis == HHS_EXACT_PHASE_Z))
        out->orientation = 2U;
    else
        out->orientation = 0U;
    out->closure = (uint8_t)(phase == 0U || phase == 36U);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_vm81_frame_import_le(
    const uint8_t *bytes,
    size_t length,
    HHSExactVM81Frame *out_frame
) {
    uint32_t cell;
    if (bytes == NULL || out_frame == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (length != HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    for (cell = 0; cell < HHS_EXACT_VM81_CELLS; ++cell) {
        uint64_t word = 0;
        uint32_t byte_index;
        for (byte_index = 0; byte_index < 8U; ++byte_index)
            word |= ((uint64_t)bytes[(size_t)cell * 8U + byte_index]) << (8U * byte_index);
        out_frame->words[cell] = word;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_vm81_frame_export_le(
    const HHSExactVM81Frame *frame,
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    uint32_t cell;
    if (out_length != NULL)
        *out_length = HHS_EXACT_VM81_FRAME_BYTES;
    if (frame == NULL || out_bytes == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (capacity < HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    for (cell = 0; cell < HHS_EXACT_VM81_CELLS; ++cell) {
        uint64_t word = frame->words[cell];
        uint32_t byte_index;
        for (byte_index = 0; byte_index < 8U; ++byte_index)
            out_bytes[(size_t)cell * 8U + byte_index] = (uint8_t)((word >> (8U * byte_index)) & UINT64_C(0xFF));
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_x86_64_ingress_exact(
    const uint8_t *bytes,
    size_t length,
    HHSExactX86InstructionBytes *out_instruction
) {
    if (bytes == NULL || out_instruction == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (length == 0U || length > HHS_EXACT_X86_MAX_INSTRUCTION_BYTES)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    memset(out_instruction, 0, sizeof(*out_instruction));
    out_instruction->struct_size = (uint32_t)sizeof(*out_instruction);
    out_instruction->abi_version = hhs_exact_version_word();
    out_instruction->length = (uint8_t)length;
    memcpy(out_instruction->bytes, bytes, length);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_x86_64_egress_exact(
    const HHSExactX86InstructionBytes *instruction,
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    size_t length;
    if (instruction == NULL || out_bytes == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (instruction->struct_size < sizeof(*instruction) || instruction->abi_version != hhs_exact_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    length = instruction->length;
    if (length == 0U || length > HHS_EXACT_X86_MAX_INSTRUCTION_BYTES)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (out_length != NULL)
        *out_length = length;
    if (capacity < length)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    memcpy(out_bytes, instruction->bytes, length);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_x86_64_bytecode_copy_exact(
    const uint8_t *input,
    size_t length,
    uint8_t *output,
    size_t capacity,
    size_t *out_length
) {
    if (out_length != NULL)
        *out_length = length;
    if ((length != 0U && input == NULL) || (length != 0U && output == NULL))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (capacity < length)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    if (length != 0U)
        memmove(output, input, length);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_abi_validate(void) {
    uint16_t coord;
    uint16_t address;
    HHSExactPhaseProduct xy;
    HHSExactPhaseProduct yx;
    uint8_t position;
    uint8_t symbol;
    uint8_t cell;
    uint8_t left;
    uint8_t right;
    uint16_t encoded;
    static const uint8_t x86_probe[] = {0xF3U, 0x48U, 0x01U, 0xD8U};
    HHSExactX86InstructionBytes instruction;
    uint8_t out[HHS_EXACT_X86_MAX_INSTRUCTION_BYTES];
    size_t out_length = 0U;

    if (strlen(HHS_EXACT_HASH72_ALPHABET) != HHS_EXACT_HASH72_LEN)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (coord = 0U; coord < HHS_EXACT_HASH72_COORDS; ++coord) {
        if (hhs_exact_hash72_coord_decode(coord, &position, &symbol) != HHS_EXACT_STATUS_OK ||
            hhs_exact_hash72_coord_encode(position, symbol, &encoded) != HHS_EXACT_STATUS_OK ||
            encoded != coord)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    for (address = 0U; address < HHS_EXACT_HASH72_COORDS; ++address) {
        if (hhs_exact_vm5184_address_decode(address, &cell, &left, &right) != HHS_EXACT_STATUS_OK ||
            hhs_exact_vm5184_address_encode(cell, left, right, &encoded) != HHS_EXACT_STATUS_OK ||
            encoded != address)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (hhs_exact_phase_product(HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y, &xy) != HHS_EXACT_STATUS_OK ||
        hhs_exact_phase_product(HHS_EXACT_PHASE_Y, HHS_EXACT_PHASE_X, &yx) != HHS_EXACT_STATUS_OK ||
        xy.phase != 0U || yx.phase != 36U || xy.ordered_tag == yx.ordered_tag)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (hhs_x86_64_ingress_exact(x86_probe, sizeof(x86_probe), &instruction) != HHS_EXACT_STATUS_OK ||
        hhs_x86_64_egress_exact(&instruction, out, sizeof(out), &out_length) != HHS_EXACT_STATUS_OK ||
        out_length != sizeof(x86_probe) || memcmp(out, x86_probe, sizeof(x86_probe)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}
