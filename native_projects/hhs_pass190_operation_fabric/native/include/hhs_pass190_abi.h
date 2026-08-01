#ifndef HHS_PASS190_ABI_H
#define HHS_PASS190_ABI_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_P190_ABI_VERSION_MAJOR 1u
#define HHS_P190_ABI_VERSION_MINOR 0u
#define HHS_P190_ABI_VERSION_PATCH 0u
#define HHS_P190_OPERATION_COUNT 10u
#define HHS_P190_PASS189_CONTEXT_COUNT UINT64_C(51648192)

typedef enum hhs_p190_result {
    HHS_P190_OK = 0,
    HHS_P190_INVALID_ARGUMENT = 1,
    HHS_P190_BUFFER_TOO_SMALL = 2,
    HHS_P190_RANGE_ERROR = 3,
    HHS_P190_STATE_CONFLICT = 4,
    HHS_P190_NOT_FOUND = 5
} hhs_p190_result;

typedef struct hhs_p190_context {
    int64_t counter;
    uint64_t receipt_index;
} hhs_p190_context;

typedef struct hhs_p190_status_info {
    uint32_t abi_major;
    uint32_t abi_minor;
    uint32_t abi_patch;
    uint32_t operation_count;
    int64_t counter;
    uint64_t receipt_index;
} hhs_p190_status_info;

typedef struct hhs_p190_pass189_address {
    uint64_t address;
    uint64_t projected;
    uint32_t cell81;
    uint32_t operation64;
    uint32_t gear243;
    uint32_t kappa41;
    int32_t local_k;
} hhs_p190_pass189_address;

typedef struct hhs_p190_kv_json {
    const char *key;
    const char *json_value;
} hhs_p190_kv_json;

typedef struct hhs_p190_operation_descriptor {
    const char *operation_id;
    const char *native_symbol;
    const char *vm81_binding;
    const char *native_profile;
    uint32_t slot;
    uint32_t mutates_state;
} hhs_p190_operation_descriptor;

const char *hhs_p190_result_string(hhs_p190_result result);
hhs_p190_result hhs_p190_context_init(hhs_p190_context *context);
hhs_p190_result hhs_p190_system_status(const hhs_p190_context *context, hhs_p190_status_info *out_status);
hhs_p190_result hhs_p190_python_len(size_t length, size_t *out_length);
hhs_p190_result hhs_p190_python_abs(int64_t value, int64_t *out_value);
hhs_p190_result hhs_p190_python_sorted_i64(const int64_t *input, size_t count, int reverse, int64_t *output, size_t output_count);
hhs_p190_result hhs_p190_list_with_appended_i64(const int64_t *input, size_t count, int64_t value, int64_t *output, size_t output_count, size_t *out_count);
hhs_p190_result hhs_p190_dict_get_json(const hhs_p190_kv_json *items, size_t count, const char *key, const char *default_json, const char **out_json);
hhs_p190_result hhs_p190_text_join(const char *separator, const char *const *values, size_t count, char *output, size_t output_size, size_t *out_length);
hhs_p190_result hhs_p190_math_gcd(int64_t a, int64_t b, int64_t *out_value);
hhs_p190_result hhs_p190_pass189_context_decode(uint64_t address, hhs_p190_pass189_address *out_address);
hhs_p190_result hhs_p190_state_counter_advance(hhs_p190_context *context, int64_t delta, int enforce_expected, int64_t expected_counter, int64_t *out_before, int64_t *out_after);
const hhs_p190_operation_descriptor *hhs_p190_operation_table(size_t *out_count);
const hhs_p190_operation_descriptor *hhs_p190_find_operation(const char *operation_id);

#ifdef __cplusplus
}
#endif

#endif
