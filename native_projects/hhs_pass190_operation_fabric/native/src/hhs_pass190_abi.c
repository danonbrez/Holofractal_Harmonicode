#include "hhs_pass190_abi.h"

#include <limits.h>
#include <string.h>

#include "../generated/hhs_pass190_operation_table.inc"

static uint64_t hhs_abs_u64(int64_t value) {
    if (value >= 0) {
        return (uint64_t)value;
    }
    return (uint64_t)(-(value + 1)) + UINT64_C(1);
}

const char *hhs_p190_result_string(hhs_p190_result result) {
    switch (result) {
        case HHS_P190_OK: return "ok";
        case HHS_P190_INVALID_ARGUMENT: return "invalid_argument";
        case HHS_P190_BUFFER_TOO_SMALL: return "buffer_too_small";
        case HHS_P190_RANGE_ERROR: return "range_error";
        case HHS_P190_STATE_CONFLICT: return "state_conflict";
        case HHS_P190_NOT_FOUND: return "not_found";
        default: return "unknown";
    }
}

hhs_p190_result hhs_p190_context_init(hhs_p190_context *context) {
    if (context == NULL) {
        return HHS_P190_INVALID_ARGUMENT;
    }
    context->counter = 0;
    context->receipt_index = 0;
    return HHS_P190_OK;
}

hhs_p190_result hhs_p190_system_status(const hhs_p190_context *context, hhs_p190_status_info *out_status) {
    if (context == NULL || out_status == NULL) {
        return HHS_P190_INVALID_ARGUMENT;
    }
    out_status->abi_major = HHS_P190_ABI_VERSION_MAJOR;
    out_status->abi_minor = HHS_P190_ABI_VERSION_MINOR;
    out_status->abi_patch = HHS_P190_ABI_VERSION_PATCH;
    out_status->operation_count = HHS_P190_OPERATION_COUNT;
    out_status->counter = context->counter;
    out_status->receipt_index = context->receipt_index;
    return HHS_P190_OK;
}

hhs_p190_result hhs_p190_python_len(size_t length, size_t *out_length) {
    if (out_length == NULL) {
        return HHS_P190_INVALID_ARGUMENT;
    }
    *out_length = length;
    return HHS_P190_OK;
}

hhs_p190_result hhs_p190_python_abs(int64_t value, int64_t *out_value) {
    if (out_value == NULL) {
        return HHS_P190_INVALID_ARGUMENT;
    }
    if (value == INT64_MIN) {
        return HHS_P190_RANGE_ERROR;
    }
    *out_value = value < 0 ? -value : value;
    return HHS_P190_OK;
}

hhs_p190_result hhs_p190_python_sorted_i64(const int64_t *input, size_t count, int reverse, int64_t *output, size_t output_count) {
    size_t i;
    if ((count > 0 && (input == NULL || output == NULL)) || output_count < count) {
        return output_count < count ? HHS_P190_BUFFER_TOO_SMALL : HHS_P190_INVALID_ARGUMENT;
    }
    for (i = 0; i < count; ++i) {
        output[i] = input[i];
    }
    for (i = 1; i < count; ++i) {
        int64_t value = output[i];
        size_t j = i;
        while (j > 0) {
            int move = reverse ? output[j - 1] < value : output[j - 1] > value;
            if (!move) {
                break;
            }
            output[j] = output[j - 1];
            --j;
        }
        output[j] = value;
    }
    return HHS_P190_OK;
}

hhs_p190_result hhs_p190_list_with_appended_i64(const int64_t *input, size_t count, int64_t value, int64_t *output, size_t output_count, size_t *out_count) {
    size_t i;
    if (out_count == NULL || (count > 0 && (input == NULL || output == NULL))) {
        return HHS_P190_INVALID_ARGUMENT;
    }
    if (count == SIZE_MAX || output_count < count + 1u) {
        return HHS_P190_BUFFER_TOO_SMALL;
    }
    for (i = 0; i < count; ++i) {
        output[i] = input[i];
    }
    output[count] = value;
    *out_count = count + 1u;
    return HHS_P190_OK;
}

hhs_p190_result hhs_p190_dict_get_json(const hhs_p190_kv_json *items, size_t count, const char *key, const char *default_json, const char **out_json) {
    size_t i;
    if (key == NULL || default_json == NULL || out_json == NULL || (count > 0 && items == NULL)) {
        return HHS_P190_INVALID_ARGUMENT;
    }
    for (i = 0; i < count; ++i) {
        if (items[i].key == NULL || items[i].json_value == NULL) {
            return HHS_P190_INVALID_ARGUMENT;
        }
        if (strcmp(items[i].key, key) == 0) {
            *out_json = items[i].json_value;
            return HHS_P190_OK;
        }
    }
    *out_json = default_json;
    return HHS_P190_OK;
}

hhs_p190_result hhs_p190_text_join(const char *separator, const char *const *values, size_t count, char *output, size_t output_size, size_t *out_length) {
    size_t required = 0;
    size_t separator_length;
    size_t i;
    char *cursor;
    if (separator == NULL || out_length == NULL || (count > 0 && values == NULL)) {
        return HHS_P190_INVALID_ARGUMENT;
    }
    separator_length = strlen(separator);
    for (i = 0; i < count; ++i) {
        size_t value_length;
        if (values[i] == NULL) {
            return HHS_P190_INVALID_ARGUMENT;
        }
        value_length = strlen(values[i]);
        if (required > SIZE_MAX - value_length) {
            return HHS_P190_RANGE_ERROR;
        }
        required += value_length;
        if (i + 1u < count) {
            if (required > SIZE_MAX - separator_length) {
                return HHS_P190_RANGE_ERROR;
            }
            required += separator_length;
        }
    }
    *out_length = required;
    if (output == NULL || output_size <= required) {
        return HHS_P190_BUFFER_TOO_SMALL;
    }
    cursor = output;
    for (i = 0; i < count; ++i) {
        size_t value_length = strlen(values[i]);
        memcpy(cursor, values[i], value_length);
        cursor += value_length;
        if (i + 1u < count) {
            memcpy(cursor, separator, separator_length);
            cursor += separator_length;
        }
    }
    *cursor = '\0';
    return HHS_P190_OK;
}

hhs_p190_result hhs_p190_math_gcd(int64_t a, int64_t b, int64_t *out_value) {
    uint64_t left;
    uint64_t right;
    if (out_value == NULL) {
        return HHS_P190_INVALID_ARGUMENT;
    }
    left = hhs_abs_u64(a);
    right = hhs_abs_u64(b);
    while (right != 0u) {
        uint64_t remainder = left % right;
        left = right;
        right = remainder;
    }
    if (left > (uint64_t)INT64_MAX) {
        return HHS_P190_RANGE_ERROR;
    }
    *out_value = (int64_t)left;
    return HHS_P190_OK;
}

hhs_p190_result hhs_p190_pass189_context_decode(uint64_t address, hhs_p190_pass189_address *out_address) {
    uint64_t projected;
    uint64_t permanent;
    if (out_address == NULL) {
        return HHS_P190_INVALID_ARGUMENT;
    }
    if (address >= HHS_P190_PASS189_CONTEXT_COUNT) {
        return HHS_P190_RANGE_ERROR;
    }
    projected = address / UINT64_C(41);
    permanent = projected / UINT64_C(243);
    out_address->address = address;
    out_address->projected = projected;
    out_address->cell81 = (uint32_t)(permanent / UINT64_C(64));
    out_address->operation64 = (uint32_t)(permanent % UINT64_C(64));
    out_address->gear243 = (uint32_t)(projected % UINT64_C(243));
    out_address->kappa41 = (uint32_t)(address % UINT64_C(41));
    out_address->local_k = (int32_t)out_address->kappa41 - 20;
    return HHS_P190_OK;
}

hhs_p190_result hhs_p190_state_counter_advance(hhs_p190_context *context, int64_t delta, int enforce_expected, int64_t expected_counter, int64_t *out_before, int64_t *out_after) {
    int64_t before;
    if (context == NULL || out_before == NULL || out_after == NULL) {
        return HHS_P190_INVALID_ARGUMENT;
    }
    if (enforce_expected != 0 && context->counter != expected_counter) {
        return HHS_P190_STATE_CONFLICT;
    }
    before = context->counter;
    if ((delta > 0 && before > INT64_MAX - delta) || (delta < 0 && before < INT64_MIN - delta)) {
        return HHS_P190_RANGE_ERROR;
    }
    context->counter = before + delta;
    context->receipt_index += UINT64_C(1);
    *out_before = before;
    *out_after = context->counter;
    return HHS_P190_OK;
}

const hhs_p190_operation_descriptor *hhs_p190_operation_table(size_t *out_count) {
    if (out_count != NULL) {
        *out_count = HHS_P190_OPERATION_COUNT;
    }
    return HHS_P190_OPERATIONS;
}

const hhs_p190_operation_descriptor *hhs_p190_find_operation(const char *operation_id) {
    size_t i;
    if (operation_id == NULL) {
        return NULL;
    }
    for (i = 0; i < HHS_P190_OPERATION_COUNT; ++i) {
        if (strcmp(HHS_P190_OPERATIONS[i].operation_id, operation_id) == 0) {
            return &HHS_P190_OPERATIONS[i];
        }
    }
    return NULL;
}
