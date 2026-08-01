#include "hhs_pass190_abi.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static void test_registry(void) {
    size_t count = 0;
    const hhs_p190_operation_descriptor *table = hhs_p190_operation_table(&count);
    assert(table != NULL);
    assert(count == HHS_P190_OPERATION_COUNT);
    assert(strcmp(table[0].operation_id, "system.status") == 0);
    assert(strcmp(table[9].operation_id, "state.counter.advance") == 0);
    assert(hhs_p190_find_operation("math.gcd") != NULL);
    assert(hhs_p190_find_operation("missing") == NULL);
}

static void test_pure_operations(void) {
    int64_t absolute = 0;
    int64_t gcd = 0;
    int64_t sorted[4] = {0};
    int64_t input[4] = {5, -1, 3, 3};
    int64_t appended[3] = {0};
    int64_t source[2] = {1, 2};
    size_t appended_count = 0;
    size_t length = 0;
    char joined[32];
    size_t joined_length = 0;
    const char *values[3] = {"alpha", "beta", "gamma"};
    hhs_p190_kv_json items[2] = {{"a", "1"}, {"b", "{\"x\":2}"}};
    const char *json_value = NULL;

    assert(hhs_p190_python_len(72u, &length) == HHS_P190_OK && length == 72u);
    assert(hhs_p190_python_abs(-12, &absolute) == HHS_P190_OK && absolute == 12);
    assert(hhs_p190_python_sorted_i64(input, 4u, 0, sorted, 4u) == HHS_P190_OK);
    assert(sorted[0] == -1 && sorted[1] == 3 && sorted[2] == 3 && sorted[3] == 5);
    assert(hhs_p190_list_with_appended_i64(source, 2u, 9, appended, 3u, &appended_count) == HHS_P190_OK);
    assert(appended_count == 3u && appended[0] == 1 && appended[1] == 2 && appended[2] == 9);
    assert(hhs_p190_dict_get_json(items, 2u, "b", "null", &json_value) == HHS_P190_OK);
    assert(strcmp(json_value, "{\"x\":2}") == 0);
    assert(hhs_p190_dict_get_json(items, 2u, "z", "null", &json_value) == HHS_P190_OK);
    assert(strcmp(json_value, "null") == 0);
    assert(hhs_p190_text_join("/", values, 3u, joined, sizeof(joined), &joined_length) == HHS_P190_OK);
    assert(strcmp(joined, "alpha/beta/gamma") == 0 && joined_length == strlen(joined));
    assert(hhs_p190_math_gcd(84, -30, &gcd) == HHS_P190_OK && gcd == 6);
}

static void test_address_and_state(void) {
    hhs_p190_pass189_address address;
    hhs_p190_context context;
    hhs_p190_status_info status;
    int64_t before = 0;
    int64_t after = 0;

    assert(hhs_p190_pass189_context_decode(UINT64_C(51648191), &address) == HHS_P190_OK);
    assert(address.cell81 == 80u && address.operation64 == 63u && address.gear243 == 242u);
    assert(address.kappa41 == 40u && address.local_k == 20);
    assert(hhs_p190_context_init(&context) == HHS_P190_OK);
    assert(hhs_p190_state_counter_advance(&context, 5, 1, 0, &before, &after) == HHS_P190_OK);
    assert(before == 0 && after == 5 && context.receipt_index == 1u);
    assert(hhs_p190_state_counter_advance(&context, 1, 1, 0, &before, &after) == HHS_P190_STATE_CONFLICT);
    assert(hhs_p190_system_status(&context, &status) == HHS_P190_OK);
    assert(status.operation_count == 10u && status.counter == 5 && status.receipt_index == 1u);
}

static void test_negative_paths(void) {
    int64_t value = 0;
    int64_t output[1] = {0};
    int64_t input[2] = {2, 1};
    size_t required = 0;
    const char *values[1] = {"x"};
    assert(hhs_p190_python_abs(INT64_MIN, &value) == HHS_P190_RANGE_ERROR);
    assert(hhs_p190_python_sorted_i64(input, 2u, 0, output, 1u) == HHS_P190_BUFFER_TOO_SMALL);
    assert(hhs_p190_text_join("", values, 1u, NULL, 0u, &required) == HHS_P190_BUFFER_TOO_SMALL);
    assert(required == 1u);
    assert(hhs_p190_pass189_context_decode(HHS_P190_PASS189_CONTEXT_COUNT, NULL) == HHS_P190_INVALID_ARGUMENT);
}

int main(void) {
    test_registry();
    test_pure_operations();
    test_address_and_state();
    test_negative_paths();
    puts("HHS Pass 190 iteration 3 native ABI tests passed");
    return 0;
}
