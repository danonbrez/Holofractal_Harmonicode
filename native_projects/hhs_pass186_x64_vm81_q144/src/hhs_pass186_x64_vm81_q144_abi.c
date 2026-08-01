#include "hhs_pass186_x64_vm81_q144_abi.h"

#include <limits.h>
#include <string.h>

_Static_assert(HHS186_Q12 * HHS186_Q12 == HHS186_Q144,
               "12*12 must equal 144");
_Static_assert(HHS186_FACTORIAL_Q144_LANES * HHS186_Q144 == HHS186_FACTORIAL_7,
               "35*144 must equal 7!");
_Static_assert(HHS186_Q144_LANES * HHS186_Q144 == HHS186_VM5184_STATES,
               "36*144 must equal 5184");
_Static_assert(HHS186_VM81_CELLS * HHS186_VM81_OPERATIONS_PER_CELL == HHS186_VM5184_STATES,
               "81*64 must equal 5184");
_Static_assert(HHS186_VM5184_STATES * HHS186_G243_CONTROLS == HHS186_HYDRATED_STATES,
               "5184*243 must equal 1259712");
_Static_assert(HHS186_HYDRATED_STATES + 1U == HHS186_OUTER_ENVELOPE_MODULUS,
               "outer envelope must be internal cardinality plus one");

static int hhs186_checked_mul_i64(int64_t left, int64_t right, int64_t *out) {
    if (out == NULL) {
        return 0;
    }
    if (left == 0 || right == 0) {
        *out = 0;
        return 1;
    }
    if (left > 0) {
        if (right > 0) {
            if (left > INT64_MAX / right) {
                return 0;
            }
        } else if (right < INT64_MIN / left) {
            return 0;
        }
    } else if (right > 0) {
        if (left < INT64_MIN / right) {
            return 0;
        }
    } else if (left != 0 && right < INT64_MAX / left) {
        return 0;
    }
    *out = left * right;
    return 1;
}

static uint16_t hhs186_basis_tag(uint8_t basis) {
    static const uint16_t tags[8] = {
        UINT16_C(0x0058),
        UINT16_C(0x0059),
        UINT16_C(0x005A),
        UINT16_C(0x0057),
        UINT16_C(0x5859),
        UINT16_C(0x5958),
        UINT16_C(0x5A57),
        UINT16_C(0x575A)
    };
    return tags[basis];
}

static void hhs186_ordered_operands(
    uint8_t basis,
    int64_t x,
    int64_t y,
    int64_t z,
    int64_t w,
    int64_t *left,
    int64_t *right
) {
    switch ((HHS186OrderedBasis)basis) {
        case HHS186_BASIS_X:  *left = x; *right = 1; break;
        case HHS186_BASIS_Y:  *left = y; *right = 1; break;
        case HHS186_BASIS_Z:  *left = z; *right = 1; break;
        case HHS186_BASIS_W:  *left = w; *right = 1; break;
        case HHS186_BASIS_XY: *left = x; *right = y; break;
        case HHS186_BASIS_YX: *left = y; *right = x; break;
        case HHS186_BASIS_ZW: *left = z; *right = w; break;
        case HHS186_BASIS_WZ: *left = w; *right = z; break;
        default: *left = 0; *right = 0; break;
    }
}

static HHS186Status hhs186_validate_quantization(const HHS186Quantization *q) {
    if (q == NULL) {
        return HHS186_STATUS_INVALID_ARGUMENT;
    }
    if (q->struct_size < sizeof(*q) || q->abi_version != HHS186_ABI_VERSION) {
        return HHS186_STATUS_ABI_VERSION_MISMATCH;
    }
    if (q->g243 >= HHS186_G243_CONTROLS ||
        q->opcode_lane36 >= HHS186_Q144_LANES ||
        q->root_row12 >= HHS186_Q12 ||
        q->root_col12 >= HHS186_Q12) {
        return HHS186_STATUS_RANGE_ERROR;
    }
    return HHS186_STATUS_OK;
}

HHS186Status hhs186_x64_vm81_q144_map(
    int64_t x,
    int64_t y,
    int64_t z,
    int64_t w,
    const HHS186Quantization *quantization,
    HHS186MappingResult *result
) {
    uint32_t q144_index;
    uint32_t instruction_state;
    uint32_t projected_state;
    uint8_t operation;
    uint8_t basis;
    int64_t ordered_left;
    int64_t ordered_right;
    int64_t product;
    HHS186Status status;

    if (result == NULL) {
        return HHS186_STATUS_INVALID_ARGUMENT;
    }
    memset(result, 0, sizeof(*result));
    result->struct_size = (uint32_t)sizeof(*result);
    result->abi_version = HHS186_ABI_VERSION;

    status = hhs186_validate_quantization(quantization);
    if (status != HHS186_STATUS_OK) {
        result->status = (uint32_t)status;
        return status;
    }

    q144_index = (uint32_t)quantization->root_row12 * HHS186_Q12 +
                 (uint32_t)quantization->root_col12;
    instruction_state = (uint32_t)quantization->opcode_lane36 * HHS186_Q144 +
                        q144_index;
    projected_state = instruction_state * HHS186_G243_CONTROLS +
                      (uint32_t)quantization->g243;

    operation = (uint8_t)(instruction_state % HHS186_VM81_OPERATIONS_PER_CELL);
    basis = (uint8_t)(operation & UINT8_C(7));
    hhs186_ordered_operands(
        basis, x, y, z, w, &ordered_left, &ordered_right
    );
    if (!hhs186_checked_mul_i64(ordered_left, ordered_right, &product)) {
        result->status = HHS186_STATUS_ARITHMETIC_OVERFLOW;
        return HHS186_STATUS_ARITHMETIC_OVERFLOW;
    }

    result->status = HHS186_STATUS_OK;
    result->instruction_state5184 = instruction_state;
    result->projected_state5184_243 = projected_state;
    result->q144_index = q144_index;
    result->vm81_cell = (uint16_t)(instruction_state / HHS186_VM81_OPERATIONS_PER_CELL);
    result->vm81_operation64 = operation;
    result->ordered_basis = basis;
    result->operation_class8 = (uint8_t)(operation >> 3);
    result->factorial_admitted = (uint8_t)(instruction_state < HHS186_FACTORIAL_7);
    result->closure_q144_lane = (uint8_t)(quantization->opcode_lane36 == HHS186_FACTORIAL_Q144_LANES);
    result->u72_pair = (uint8_t)(q144_index / HHS186_U72_RING);
    result->u72_index = (uint8_t)(q144_index % HHS186_U72_RING);
    result->root_row12 = quantization->root_row12;
    result->root_col12 = quantization->root_col12;
    result->opcode_lane36 = quantization->opcode_lane36;
    result->g243 = quantization->g243;
    result->ordered_tag = hhs186_basis_tag(basis);
    result->ordered_left = ordered_left;
    result->ordered_right = ordered_right;
    result->ordered_product_witness = product;
    result->factorial7 = HHS186_FACTORIAL_7;
    result->q144 = HHS186_Q144;
    result->vm5184 = HHS186_VM5184_STATES;
    result->hydrated_cardinality = HHS186_HYDRATED_STATES;
    result->outer_envelope_modulus = HHS186_OUTER_ENVELOPE_MODULUS;

    if (result->vm81_cell >= HHS186_VM81_CELLS ||
        result->projected_state5184_243 >= HHS186_HYDRATED_STATES ||
        result->u72_pair > 1U) {
        result->status = HHS186_STATUS_INVARIANT_FAILURE;
        return HHS186_STATUS_INVARIANT_FAILURE;
    }
    return HHS186_STATUS_OK;
}

HHS186Status hhs186_x64_vm81_q144_unproject(
    uint32_t projected_state,
    HHS186Quantization *quantization,
    HHS186MappingResult *coordinates
) {
    uint32_t instruction_state;
    uint32_t q144_index;

    if (quantization == NULL || coordinates == NULL) {
        return HHS186_STATUS_INVALID_ARGUMENT;
    }
    if (projected_state >= HHS186_HYDRATED_STATES) {
        return HHS186_STATUS_RANGE_ERROR;
    }

    instruction_state = projected_state / HHS186_G243_CONTROLS;
    q144_index = instruction_state % HHS186_Q144;

    memset(quantization, 0, sizeof(*quantization));
    quantization->struct_size = (uint32_t)sizeof(*quantization);
    quantization->abi_version = HHS186_ABI_VERSION;
    quantization->g243 = (uint16_t)(projected_state % HHS186_G243_CONTROLS);
    quantization->opcode_lane36 = (uint8_t)(instruction_state / HHS186_Q144);
    quantization->root_row12 = (uint8_t)(q144_index / HHS186_Q12);
    quantization->root_col12 = (uint8_t)(q144_index % HHS186_Q12);

    memset(coordinates, 0, sizeof(*coordinates));
    coordinates->struct_size = (uint32_t)sizeof(*coordinates);
    coordinates->abi_version = HHS186_ABI_VERSION;
    coordinates->status = HHS186_STATUS_OK;
    coordinates->instruction_state5184 = instruction_state;
    coordinates->projected_state5184_243 = projected_state;
    coordinates->q144_index = q144_index;
    coordinates->vm81_cell = (uint16_t)(instruction_state / HHS186_VM81_OPERATIONS_PER_CELL);
    coordinates->vm81_operation64 = (uint8_t)(instruction_state % HHS186_VM81_OPERATIONS_PER_CELL);
    coordinates->ordered_basis = (uint8_t)(coordinates->vm81_operation64 & UINT8_C(7));
    coordinates->operation_class8 = (uint8_t)(coordinates->vm81_operation64 >> 3);
    coordinates->factorial_admitted = (uint8_t)(instruction_state < HHS186_FACTORIAL_7);
    coordinates->closure_q144_lane = (uint8_t)(quantization->opcode_lane36 == HHS186_FACTORIAL_Q144_LANES);
    coordinates->u72_pair = (uint8_t)(q144_index / HHS186_U72_RING);
    coordinates->u72_index = (uint8_t)(q144_index % HHS186_U72_RING);
    coordinates->root_row12 = quantization->root_row12;
    coordinates->root_col12 = quantization->root_col12;
    coordinates->opcode_lane36 = quantization->opcode_lane36;
    coordinates->g243 = quantization->g243;
    coordinates->ordered_tag = hhs186_basis_tag(coordinates->ordered_basis);
    coordinates->factorial7 = HHS186_FACTORIAL_7;
    coordinates->q144 = HHS186_Q144;
    coordinates->vm5184 = HHS186_VM5184_STATES;
    coordinates->hydrated_cardinality = HHS186_HYDRATED_STATES;
    coordinates->outer_envelope_modulus = HHS186_OUTER_ENVELOPE_MODULUS;
    return HHS186_STATUS_OK;
}
