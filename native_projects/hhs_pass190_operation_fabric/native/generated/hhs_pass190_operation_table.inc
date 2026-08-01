/* Generated from HHS_OPERATION_REGISTRY_V1.json. Do not edit by hand. */
static const hhs_p190_operation_descriptor HHS_P190_OPERATIONS[HHS_P190_OPERATION_COUNT] = {
    {"system.status", "hhs_p190_system_status", "VM81:status", "status-v1", 0u, 0u},
    {"python.len", "hhs_p190_python_len", "VM81:len", "length-v1", 1u, 0u},
    {"python.abs", "hhs_p190_python_abs", "VM81:abs", "int64-v1", 2u, 0u},
    {"python.sorted", "hhs_p190_python_sorted_i64", "VM81:sorted", "int64-array-v1", 3u, 0u},
    {"list.with_appended", "hhs_p190_list_with_appended_i64", "VM81:list.with_appended", "int64-array-v1", 4u, 0u},
    {"dict.get", "hhs_p190_dict_get_json", "VM81:dict.get", "utf8-key-json-value-v1", 5u, 0u},
    {"text.join", "hhs_p190_text_join", "VM81:text.join", "utf8-sequence-v1", 6u, 0u},
    {"math.gcd", "hhs_p190_math_gcd", "VM81:math.gcd", "int64-v1", 7u, 0u},
    {"pass189.context.decode", "hhs_p190_pass189_context_decode", "VM81:P189.decode", "pass189-address-v1", 8u, 0u},
    {"state.counter.advance", "hhs_p190_state_counter_advance", "VM81:state.counter.advance", "singleton-counter-v1", 9u, 1u}
};
