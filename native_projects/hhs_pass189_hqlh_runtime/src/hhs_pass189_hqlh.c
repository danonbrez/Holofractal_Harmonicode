#include "hhs_pass189_hqlh.h"

#include <limits.h>

/*
 * Positive deltas are a frozen Lo Shu-ranked permutation of 1..20.
 * Generation rule:
 *   seed = [4,9,2,3,5,7,8,1,6]
 *   sort n in 1..20 by (seed[(n-1) mod 9], floor((n-1)/9), n)
 * Negative coordinates use the exact additive inverse over Z_81.
 */
static const int8_t HHS189_LO_SHU_POSITIVE_DELTAS[20] = {
    8, 17, 3, 12, 4, 13, 1, 10, 19, 5,
    14, 9, 18, 6, 15, 7, 16, 2, 11, 20
};

static uint64_t fnv1a_u32(uint64_t checksum, uint32_t value) {
    uint32_t shift;
    for (shift = 0U; shift < 32U; shift += 8U) {
        checksum ^= (uint64_t)((value >> shift) & UINT32_C(0xff));
        checksum *= UINT64_C(1099511628211);
    }
    return checksum;
}

int hhs189_decode_context(uint32_t extended, HHS189ContextAddress *out) {
    uint32_t projected;
    uint32_t permanent;
    uint32_t q144;
    if (out == NULL) {
        return HHS189_ERR_NULL;
    }
    if (extended >= HHS189_CONTEXTUAL_STATES) {
        return HHS189_ERR_RANGE;
    }
    projected = extended / HHS189_LOCAL_COORDINATES;
    permanent = projected / HHS189_G243_CONTROLS;
    q144 = permanent % HHS189_Q144_STATES;

    out->extended = extended;
    out->projected = projected;
    out->permanent = permanent;
    out->g243 = (uint16_t)(projected % HHS189_G243_CONTROLS);
    out->cell81 = (uint8_t)(permanent / HHS189_OPERATIONS_PER_CELL);
    out->operation64 = (uint8_t)(permanent % HHS189_OPERATIONS_PER_CELL);
    out->operation_class8 = (uint8_t)(out->operation64 >> 3U);
    out->ordered_basis8 = (uint8_t)(out->operation64 & UINT8_C(7));
    out->kappa41 = (uint8_t)(extended % HHS189_LOCAL_COORDINATES);
    out->local_k = (int8_t)((int32_t)out->kappa41 - INT32_C(20));
    out->layer36 = (uint8_t)(permanent / HHS189_Q144_STATES);
    out->q144_row = (uint8_t)(q144 / UINT32_C(12));
    out->q144_column = (uint8_t)(q144 % UINT32_C(12));
    out->u72_pair = (uint8_t)(q144 / HHS189_U72_STATES);
    out->u72_index = (uint8_t)(q144 % HHS189_U72_STATES);
    return HHS189_OK;
}

int hhs189_encode_context(const HHS189ContextAddress *address, uint32_t *extended_out) {
    uint32_t permanent;
    uint32_t projected;
    uint32_t extended;
    if (address == NULL || extended_out == NULL) {
        return HHS189_ERR_NULL;
    }
    if (address->cell81 >= HHS189_VM81_CELLS ||
        address->operation64 >= HHS189_OPERATIONS_PER_CELL ||
        address->g243 >= HHS189_G243_CONTROLS ||
        address->kappa41 >= HHS189_LOCAL_COORDINATES) {
        return HHS189_ERR_RANGE;
    }
    permanent = (uint32_t)address->cell81 * HHS189_OPERATIONS_PER_CELL + (uint32_t)address->operation64;
    projected = permanent * HHS189_G243_CONTROLS + (uint32_t)address->g243;
    extended = projected * HHS189_LOCAL_COORDINATES + (uint32_t)address->kappa41;
    if (extended >= HHS189_CONTEXTUAL_STATES) {
        return HHS189_ERR_RANGE;
    }
    *extended_out = extended;
    return HHS189_OK;
}

const int8_t *hhs189_lo_shu_positive_delta_table(size_t *count_out) {
    if (count_out != NULL) {
        *count_out = sizeof(HHS189_LO_SHU_POSITIVE_DELTAS) / sizeof(HHS189_LO_SHU_POSITIVE_DELTAS[0]);
    }
    return HHS189_LO_SHU_POSITIVE_DELTAS;
}

int hhs189_lo_shu_delta(int8_t local_k, int8_t *delta_out) {
    uint8_t magnitude;
    int8_t value;
    if (delta_out == NULL) {
        return HHS189_ERR_NULL;
    }
    if (local_k < -20 || local_k > 20) {
        return HHS189_ERR_RANGE;
    }
    if (local_k == 0) {
        *delta_out = 0;
        return HHS189_OK;
    }
    magnitude = (uint8_t)(local_k < 0 ? -local_k : local_k);
    value = HHS189_LO_SHU_POSITIVE_DELTAS[magnitude - UINT8_C(1)];
    *delta_out = local_k < 0 ? (int8_t)-value : value;
    return HHS189_OK;
}

int hhs189_local_cell(uint8_t cell81, int8_t local_k, uint8_t *cell_out) {
    int8_t delta;
    int32_t result;
    int status;
    if (cell_out == NULL) {
        return HHS189_ERR_NULL;
    }
    if (cell81 >= HHS189_VM81_CELLS) {
        return HHS189_ERR_RANGE;
    }
    status = hhs189_lo_shu_delta(local_k, &delta);
    if (status != HHS189_OK) {
        return status;
    }
    result = ((int32_t)cell81 + (int32_t)delta) % INT32_C(81);
    if (result < 0) {
        result += INT32_C(81);
    }
    *cell_out = (uint8_t)result;
    return HHS189_OK;
}

uint8_t hhs189_xnor_bit(uint8_t a, uint8_t b) {
    return (uint8_t)(UINT8_C(1) - ((a ^ b) & UINT8_C(1)));
}

int8_t hhs189_signed_xnor(uint8_t a, uint8_t b) {
    return ((a ^ b) & UINT8_C(1)) == 0U ? INT8_C(1) : INT8_C(-1);
}

int8_t hhs189_ternary_orientation(uint8_t cell81, uint8_t nucleus81, uint8_t a, uint8_t b) {
    int32_t displacement;
    int8_t sign;
    if (cell81 >= HHS189_VM81_CELLS || nucleus81 >= HHS189_VM81_CELLS) {
        return 0;
    }
    displacement = ((int32_t)cell81 - (int32_t)nucleus81 + INT32_C(40)) % INT32_C(81);
    if (displacement < 0) {
        displacement += INT32_C(81);
    }
    displacement -= INT32_C(40);
    sign = displacement < 0 ? INT8_C(-1) : (displacement > 0 ? INT8_C(1) : INT8_C(0));
    return (int8_t)(sign * hhs189_signed_xnor(a, b));
}

int hhs189_validate_partition(uint32_t start, uint32_t end, HHS189PartitionResult *out) {
    uint32_t extended;
    uint64_t checksum = UINT64_C(1469598103934665603);
    uint64_t reciprocal_checks = 0;
    uint64_t coordinate_drift = 0;
    if (out == NULL) {
        return HHS189_ERR_NULL;
    }
    if (start > end || end > HHS189_CONTEXTUAL_STATES) {
        return HHS189_ERR_RANGE;
    }
    for (extended = start; extended < end; ++extended) {
        HHS189ContextAddress decoded;
        uint32_t encoded = 0;
        uint8_t local = 0;
        uint8_t inverse = 0;
        int status = hhs189_decode_context(extended, &decoded);
        if (status != HHS189_OK || hhs189_encode_context(&decoded, &encoded) != HHS189_OK) {
            return HHS189_ERR_INVARIANT;
        }
        if (encoded != extended) {
            ++coordinate_drift;
        }
        if (hhs189_local_cell(decoded.cell81, decoded.local_k, &local) != HHS189_OK ||
            hhs189_local_cell(local, (int8_t)-decoded.local_k, &inverse) != HHS189_OK) {
            return HHS189_ERR_INVARIANT;
        }
        if (inverse != decoded.cell81) {
            return HHS189_ERR_INVARIANT;
        }
        ++reciprocal_checks;
        checksum = fnv1a_u32(checksum, extended);
        checksum = fnv1a_u32(checksum, encoded);
        checksum = fnv1a_u32(checksum, decoded.projected);
        checksum = fnv1a_u32(checksum, (uint32_t)decoded.cell81);
        checksum = fnv1a_u32(checksum, (uint32_t)decoded.operation64);
        checksum = fnv1a_u32(checksum, (uint32_t)decoded.g243);
        checksum = fnv1a_u32(checksum, (uint32_t)decoded.kappa41);
        checksum = fnv1a_u32(checksum, (uint32_t)local);
    }
    out->start = start;
    out->end = end;
    out->visited = (uint64_t)end - (uint64_t)start;
    out->reciprocal_checks = reciprocal_checks;
    out->coordinate_drift = coordinate_drift;
    out->checksum = checksum;
    return coordinate_drift == 0U ? HHS189_OK : HHS189_ERR_DRIFT;
}
