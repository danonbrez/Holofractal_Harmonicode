#include "hhs_pass220_litert_native_execution_graph_v1.h"

#include <assert.h>
#include <string.h>

static HHSLiteRTNativeGraphDescriptorV1 graph(void) {
    HHSLiteRTNativeGraphDescriptorV1 value;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = hhs_litert_native_graph_version();
    value.graph_id = 72U;
    value.tensor_count = 3U;
    value.operation_count = 1U;
    value.input_count = 2U;
    value.output_count = 1U;
    memset(value.graph_identity_hash216, 'G', HHS_LITERT_NATIVE_GRAPH_HASH216_LEN);
    value.graph_identity_hash216[HHS_LITERT_NATIVE_GRAPH_HASH216_LEN] = '\0';

    value.tensors[0].tensor_id = 1U;
    value.tensors[0].dtype = HHS_LITERT_NATIVE_GRAPH_DTYPE_FLOAT64;
    value.tensors[0].rank = 2U;
    value.tensors[0].flags = HHS_LITERT_NATIVE_GRAPH_TENSOR_INPUT;
    value.tensors[0].dims[0] = 2U;
    value.tensors[0].dims[1] = 1U;

    value.tensors[1].tensor_id = 2U;
    value.tensors[1].dtype = HHS_LITERT_NATIVE_GRAPH_DTYPE_FLOAT64;
    value.tensors[1].rank = 2U;
    value.tensors[1].flags = HHS_LITERT_NATIVE_GRAPH_TENSOR_INPUT;
    value.tensors[1].dims[0] = 1U;
    value.tensors[1].dims[1] = 3U;

    value.tensors[2].tensor_id = 3U;
    value.tensors[2].dtype = HHS_LITERT_NATIVE_GRAPH_DTYPE_FLOAT64;
    value.tensors[2].rank = 2U;
    value.tensors[2].flags = HHS_LITERT_NATIVE_GRAPH_TENSOR_OUTPUT;
    value.tensors[2].dims[0] = 2U;
    value.tensors[2].dims[1] = 3U;

    value.operations[0].operation_id = 1U;
    value.operations[0].kind = HHS_LITERT_NATIVE_GRAPH_OP_ADD;
    value.operations[0].left_tensor_id = 1U;
    value.operations[0].right_tensor_id = 2U;
    value.operations[0].output_tensor_id = 3U;
    return value;
}

int main(void) {
    HHSLiteRTNativeGraphDescriptorV1 input = graph();
    HHSLiteRTNativeGraphRegistrationV1 registration;

    assert(hhs_litert_native_graph_version() == 1U);
    assert(hhs_litert_native_graph_register(&input, &registration) ==
           HHS_LITERT_NATIVE_GRAPH_OK);
    assert(hhs_litert_native_graph_validate_registration(&registration) ==
           HHS_LITERT_NATIVE_GRAPH_OK);
    assert(registration.graph_fingerprint64 != 0U);
    assert(registration.topology_authority == 1U);
    assert(registration.numeric_execution_authority == 0U);
    assert(registration.numpy1_numeric_lowering_required == 1U);
    assert(registration.vm81_mutation_authority == 0U);
    assert(registration.host_float_canonical_authority == 0U);

    input = graph();
    input.tensors[2].dims[1] = 4U;
    assert(hhs_litert_native_graph_register(&input, &registration) ==
           HHS_LITERT_NATIVE_GRAPH_ERR_BROADCAST);

    input = graph();
    input.tensors[0].flags = 0U;
    assert(hhs_litert_native_graph_register(&input, &registration) ==
           HHS_LITERT_NATIVE_GRAPH_ERR_TOPOLOGY);

    return 0;
}
