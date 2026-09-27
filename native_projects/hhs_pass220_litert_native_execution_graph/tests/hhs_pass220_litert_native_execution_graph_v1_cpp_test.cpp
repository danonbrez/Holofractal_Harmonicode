#include "hhs_pass220_litert_native_execution_graph_v1.hpp"

#include <cassert>
#include <cstring>

int main() {
    HHSLiteRTNativeGraphDescriptorV1 descriptor{};
    descriptor.struct_size = static_cast<std::uint32_t>(sizeof(descriptor));
    descriptor.version = hhs_litert_native_graph_version();
    descriptor.graph_id = 81U;
    descriptor.tensor_count = 3U;
    descriptor.operation_count = 1U;
    descriptor.input_count = 2U;
    descriptor.output_count = 1U;
    std::memset(descriptor.graph_identity_hash216, 'Q', HHS_LITERT_NATIVE_GRAPH_HASH216_LEN);
    descriptor.graph_identity_hash216[HHS_LITERT_NATIVE_GRAPH_HASH216_LEN] = '\0';

    descriptor.tensors[0].tensor_id = 1U;
    descriptor.tensors[0].dtype = HHS_LITERT_NATIVE_GRAPH_DTYPE_INT64;
    descriptor.tensors[0].rank = 1U;
    descriptor.tensors[0].flags = HHS_LITERT_NATIVE_GRAPH_TENSOR_INPUT;
    descriptor.tensors[0].dims[0] = 3U;

    descriptor.tensors[1].tensor_id = 2U;
    descriptor.tensors[1].dtype = HHS_LITERT_NATIVE_GRAPH_DTYPE_INT64;
    descriptor.tensors[1].rank = 1U;
    descriptor.tensors[1].flags = HHS_LITERT_NATIVE_GRAPH_TENSOR_INPUT;
    descriptor.tensors[1].dims[0] = 3U;

    descriptor.tensors[2].tensor_id = 3U;
    descriptor.tensors[2].dtype = HHS_LITERT_NATIVE_GRAPH_DTYPE_INT64;
    descriptor.tensors[2].rank = 1U;
    descriptor.tensors[2].flags = HHS_LITERT_NATIVE_GRAPH_TENSOR_OUTPUT;
    descriptor.tensors[2].dims[0] = 3U;

    descriptor.operations[0].operation_id = 1U;
    descriptor.operations[0].kind = HHS_LITERT_NATIVE_GRAPH_OP_MULTIPLY;
    descriptor.operations[0].left_tensor_id = 1U;
    descriptor.operations[0].right_tensor_id = 2U;
    descriptor.operations[0].output_tensor_id = 3U;

    hhs::litert::NativeExecutionGraph graph(descriptor);
    assert(graph.status() == HHS_LITERT_NATIVE_GRAPH_OK);
    assert(hhs::litert::NativeExecutionGraph::topology_authority());
    assert(!hhs::litert::NativeExecutionGraph::numeric_execution_authority());
    assert(hhs::litert::NativeExecutionGraph::numpy1_numeric_lowering_required());
    assert(!hhs::litert::NativeExecutionGraph::vm81_mutation_authority());
    assert(!hhs::litert::NativeExecutionGraph::host_float_canonical_authority());
    return 0;
}
