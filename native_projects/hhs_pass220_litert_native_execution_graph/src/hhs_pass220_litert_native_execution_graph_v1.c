#include "hhs_pass220_litert_native_execution_graph_v1.h"

#include <stddef.h>
#include <string.h>

static int hash216_valid(
    const char value[HHS_LITERT_NATIVE_GRAPH_HASH216_STRLEN]
) {
    uint32_t i;
    if (value[HHS_LITERT_NATIVE_GRAPH_HASH216_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_LITERT_NATIVE_GRAPH_HASH216_LEN; ++i) {
        const unsigned char c = (unsigned char)value[i];
        if (c < 33U || c > 126U)
            return 0;
    }
    return 1;
}

static int dtype_valid(uint32_t dtype) {
    return dtype == HHS_LITERT_NATIVE_GRAPH_DTYPE_INT64 ||
           dtype == HHS_LITERT_NATIVE_GRAPH_DTYPE_FLOAT64;
}

static int op_kind_valid(uint32_t kind) {
    return kind >= HHS_LITERT_NATIVE_GRAPH_OP_ADD &&
           kind <= HHS_LITERT_NATIVE_GRAPH_OP_MULTIPLY;
}

static const HHSLiteRTNativeGraphTensorV1 *find_tensor(
    const HHSLiteRTNativeGraphDescriptorV1 *descriptor,
    uint32_t tensor_id,
    uint32_t *out_index
) {
    uint32_t i;
    for (i = 0U; i < descriptor->tensor_count; ++i) {
        if (descriptor->tensors[i].tensor_id == tensor_id) {
            if (out_index != NULL)
                *out_index = i;
            return &descriptor->tensors[i];
        }
    }
    return NULL;
}

static int tensor_shape_valid(const HHSLiteRTNativeGraphTensorV1 *tensor) {
    uint32_t i;
    if (tensor->rank > HHS_LITERT_NATIVE_GRAPH_MAX_RANK)
        return 0;
    for (i = 0U; i < tensor->rank; ++i) {
        if (tensor->dims[i] == 0U)
            return 0;
    }
    for (; i < HHS_LITERT_NATIVE_GRAPH_MAX_RANK; ++i) {
        if (tensor->dims[i] != 0U)
            return 0;
    }
    return 1;
}

static int broadcast_matches(
    const HHSLiteRTNativeGraphTensorV1 *left,
    const HHSLiteRTNativeGraphTensorV1 *right,
    const HHSLiteRTNativeGraphTensorV1 *output
) {
    uint32_t out_rank = left->rank > right->rank ? left->rank : right->rank;
    uint32_t offset;
    if (output->rank != out_rank)
        return 0;
    for (offset = 0U; offset < out_rank; ++offset) {
        uint64_t ld = 1U;
        uint64_t rd = 1U;
        uint64_t expected;
        uint32_t out_index = out_rank - 1U - offset;
        if (offset < left->rank)
            ld = left->dims[left->rank - 1U - offset];
        if (offset < right->rank)
            rd = right->dims[right->rank - 1U - offset];
        if (ld != rd && ld != 1U && rd != 1U)
            return 0;
        expected = ld > rd ? ld : rd;
        if (output->dims[out_index] != expected)
            return 0;
    }
    return 1;
}

static uint64_t mix64(uint64_t h, uint64_t value) {
    uint32_t i;
    for (i = 0U; i < 8U; ++i) {
        h ^= (value >> (8U * i)) & UINT64_C(0xff);
        h *= UINT64_C(1099511628211);
    }
    return h;
}

static uint64_t fingerprint(
    const HHSLiteRTNativeGraphDescriptorV1 *descriptor
) {
    uint64_t h = UINT64_C(14695981039346656037);
    uint32_t i;
    uint32_t j;
    h = mix64(h, descriptor->graph_id);
    h = mix64(h, descriptor->tensor_count);
    h = mix64(h, descriptor->operation_count);
    h = mix64(h, descriptor->input_count);
    h = mix64(h, descriptor->output_count);
    for (i = 0U; i < HHS_LITERT_NATIVE_GRAPH_HASH216_LEN; ++i) {
        h ^= (uint8_t)descriptor->graph_identity_hash216[i];
        h *= UINT64_C(1099511628211);
    }
    for (i = 0U; i < descriptor->tensor_count; ++i) {
        const HHSLiteRTNativeGraphTensorV1 *tensor = &descriptor->tensors[i];
        h = mix64(h, tensor->tensor_id);
        h = mix64(h, tensor->dtype);
        h = mix64(h, tensor->rank);
        h = mix64(h, tensor->flags);
        for (j = 0U; j < tensor->rank; ++j)
            h = mix64(h, tensor->dims[j]);
    }
    for (i = 0U; i < descriptor->operation_count; ++i) {
        const HHSLiteRTNativeGraphOperationV1 *op = &descriptor->operations[i];
        h = mix64(h, op->operation_id);
        h = mix64(h, op->kind);
        h = mix64(h, op->left_tensor_id);
        h = mix64(h, op->right_tensor_id);
        h = mix64(h, op->output_tensor_id);
    }
    return h;
}

static HHSLiteRTNativeGraphStatusV1 descriptor_validate(
    const HHSLiteRTNativeGraphDescriptorV1 *descriptor
) {
    uint8_t available[HHS_LITERT_NATIVE_GRAPH_MAX_TENSORS] = {0U};
    uint8_t produced[HHS_LITERT_NATIVE_GRAPH_MAX_TENSORS] = {0U};
    uint32_t inputs = 0U;
    uint32_t outputs = 0U;
    uint32_t i;
    uint32_t j;

    if (descriptor == NULL)
        return HHS_LITERT_NATIVE_GRAPH_ERR_ARGUMENT;
    if (descriptor->struct_size < sizeof(*descriptor) ||
        descriptor->version != HHS_LITERT_NATIVE_GRAPH_VERSION)
        return HHS_LITERT_NATIVE_GRAPH_ERR_VERSION;
    if (descriptor->graph_id == 0U ||
        descriptor->tensor_count == 0U ||
        descriptor->tensor_count > HHS_LITERT_NATIVE_GRAPH_MAX_TENSORS ||
        descriptor->operation_count == 0U ||
        descriptor->operation_count > HHS_LITERT_NATIVE_GRAPH_MAX_OPS ||
        descriptor->input_count == 0U ||
        descriptor->output_count == 0U)
        return HHS_LITERT_NATIVE_GRAPH_ERR_RANGE;
    if (!hash216_valid(descriptor->graph_identity_hash216))
        return HHS_LITERT_NATIVE_GRAPH_ERR_IDENTITY;

    for (i = 0U; i < descriptor->tensor_count; ++i) {
        const HHSLiteRTNativeGraphTensorV1 *tensor = &descriptor->tensors[i];
        const uint32_t allowed_flags =
            HHS_LITERT_NATIVE_GRAPH_TENSOR_INPUT |
            HHS_LITERT_NATIVE_GRAPH_TENSOR_OUTPUT |
            HHS_LITERT_NATIVE_GRAPH_TENSOR_CONSTANT;
        if (tensor->tensor_id == 0U ||
            !dtype_valid(tensor->dtype) ||
            !tensor_shape_valid(tensor) ||
            (tensor->flags & ~allowed_flags) != 0U ||
            (tensor->flags & HHS_LITERT_NATIVE_GRAPH_TENSOR_INPUT &&
             tensor->flags & HHS_LITERT_NATIVE_GRAPH_TENSOR_CONSTANT))
            return HHS_LITERT_NATIVE_GRAPH_ERR_TENSOR;
        for (j = 0U; j < i; ++j) {
            if (descriptor->tensors[j].tensor_id == tensor->tensor_id)
                return HHS_LITERT_NATIVE_GRAPH_ERR_TENSOR;
        }
        if ((tensor->flags & HHS_LITERT_NATIVE_GRAPH_TENSOR_INPUT) != 0U) {
            ++inputs;
            available[i] = 1U;
        }
        if ((tensor->flags & HHS_LITERT_NATIVE_GRAPH_TENSOR_CONSTANT) != 0U)
            available[i] = 1U;
        if ((tensor->flags & HHS_LITERT_NATIVE_GRAPH_TENSOR_OUTPUT) != 0U)
            ++outputs;
    }
    if (inputs != descriptor->input_count || outputs != descriptor->output_count)
        return HHS_LITERT_NATIVE_GRAPH_ERR_TOPOLOGY;

    for (i = 0U; i < descriptor->operation_count; ++i) {
        const HHSLiteRTNativeGraphOperationV1 *op = &descriptor->operations[i];
        const HHSLiteRTNativeGraphTensorV1 *left;
        const HHSLiteRTNativeGraphTensorV1 *right;
        const HHSLiteRTNativeGraphTensorV1 *out;
        uint32_t left_index;
        uint32_t right_index;
        uint32_t out_index;

        if (op->operation_id == 0U || !op_kind_valid(op->kind))
            return HHS_LITERT_NATIVE_GRAPH_ERR_OPERATION;
        for (j = 0U; j < i; ++j) {
            if (descriptor->operations[j].operation_id == op->operation_id)
                return HHS_LITERT_NATIVE_GRAPH_ERR_OPERATION;
        }

        left = find_tensor(descriptor, op->left_tensor_id, &left_index);
        right = find_tensor(descriptor, op->right_tensor_id, &right_index);
        out = find_tensor(descriptor, op->output_tensor_id, &out_index);
        if (left == NULL || right == NULL || out == NULL)
            return HHS_LITERT_NATIVE_GRAPH_ERR_TOPOLOGY;
        if (!available[left_index] || !available[right_index])
            return HHS_LITERT_NATIVE_GRAPH_ERR_TOPOLOGY;
        if (produced[out_index] ||
            (out->flags & (HHS_LITERT_NATIVE_GRAPH_TENSOR_INPUT |
                           HHS_LITERT_NATIVE_GRAPH_TENSOR_CONSTANT)) != 0U)
            return HHS_LITERT_NATIVE_GRAPH_ERR_TOPOLOGY;
        if (left->dtype != right->dtype || left->dtype != out->dtype)
            return HHS_LITERT_NATIVE_GRAPH_ERR_TENSOR;
        if (!broadcast_matches(left, right, out))
            return HHS_LITERT_NATIVE_GRAPH_ERR_BROADCAST;

        available[out_index] = 1U;
        produced[out_index] = 1U;
    }

    for (i = 0U; i < descriptor->tensor_count; ++i) {
        if ((descriptor->tensors[i].flags &
             HHS_LITERT_NATIVE_GRAPH_TENSOR_OUTPUT) != 0U &&
            !available[i])
            return HHS_LITERT_NATIVE_GRAPH_ERR_TOPOLOGY;
    }
    return HHS_LITERT_NATIVE_GRAPH_OK;
}

uint32_t hhs_litert_native_graph_version(void) {
    return HHS_LITERT_NATIVE_GRAPH_VERSION;
}

HHSLiteRTNativeGraphStatusV1 hhs_litert_native_graph_register(
    const HHSLiteRTNativeGraphDescriptorV1 *descriptor,
    HHSLiteRTNativeGraphRegistrationV1 *out_registration
) {
    HHSLiteRTNativeGraphStatusV1 status;
    if (out_registration == NULL)
        return HHS_LITERT_NATIVE_GRAPH_ERR_ARGUMENT;
    status = descriptor_validate(descriptor);
    if (status != HHS_LITERT_NATIVE_GRAPH_OK)
        return status;

    memset(out_registration, 0, sizeof(*out_registration));
    out_registration->struct_size = (uint32_t)sizeof(*out_registration);
    out_registration->version = HHS_LITERT_NATIVE_GRAPH_VERSION;
    out_registration->graph_id = descriptor->graph_id;
    out_registration->tensor_count = descriptor->tensor_count;
    out_registration->operation_count = descriptor->operation_count;
    out_registration->input_count = descriptor->input_count;
    out_registration->output_count = descriptor->output_count;
    out_registration->graph_fingerprint64 = fingerprint(descriptor);
    memcpy(out_registration->graph_identity_hash216,
           descriptor->graph_identity_hash216,
           sizeof(out_registration->graph_identity_hash216));
    memcpy(out_registration->tensors, descriptor->tensors,
           sizeof(HHSLiteRTNativeGraphTensorV1) * descriptor->tensor_count);
    memcpy(out_registration->operations, descriptor->operations,
           sizeof(HHSLiteRTNativeGraphOperationV1) * descriptor->operation_count);
    out_registration->topology_authority = 1U;
    out_registration->numeric_execution_authority = 0U;
    out_registration->vm81_mutation_authority = 0U;
    out_registration->hash72_commit_authority = 0U;
    out_registration->hash216_persistence_authority = 0U;
    out_registration->host_float_canonical_authority = 0U;
    out_registration->numpy1_numeric_lowering_required = 1U;

    return hhs_litert_native_graph_validate_registration(out_registration);
}

HHSLiteRTNativeGraphStatusV1 hhs_litert_native_graph_validate_registration(
    const HHSLiteRTNativeGraphRegistrationV1 *registration
) {
    HHSLiteRTNativeGraphDescriptorV1 descriptor;
    uint64_t expected;
    if (registration == NULL)
        return HHS_LITERT_NATIVE_GRAPH_ERR_ARGUMENT;
    if (registration->struct_size < sizeof(*registration) ||
        registration->version != HHS_LITERT_NATIVE_GRAPH_VERSION)
        return HHS_LITERT_NATIVE_GRAPH_ERR_VERSION;
    if (registration->topology_authority != 1U ||
        registration->numeric_execution_authority != 0U ||
        registration->vm81_mutation_authority != 0U ||
        registration->hash72_commit_authority != 0U ||
        registration->hash216_persistence_authority != 0U ||
        registration->host_float_canonical_authority != 0U ||
        registration->numpy1_numeric_lowering_required != 1U)
        return HHS_LITERT_NATIVE_GRAPH_ERR_TOPOLOGY;

    memset(&descriptor, 0, sizeof(descriptor));
    descriptor.struct_size = (uint32_t)sizeof(descriptor);
    descriptor.version = HHS_LITERT_NATIVE_GRAPH_VERSION;
    descriptor.graph_id = registration->graph_id;
    descriptor.tensor_count = registration->tensor_count;
    descriptor.operation_count = registration->operation_count;
    descriptor.input_count = registration->input_count;
    descriptor.output_count = registration->output_count;
    memcpy(descriptor.graph_identity_hash216,
           registration->graph_identity_hash216,
           sizeof(descriptor.graph_identity_hash216));
    memcpy(descriptor.tensors, registration->tensors,
           sizeof(HHSLiteRTNativeGraphTensorV1) * registration->tensor_count);
    memcpy(descriptor.operations, registration->operations,
           sizeof(HHSLiteRTNativeGraphOperationV1) * registration->operation_count);

    if (descriptor_validate(&descriptor) != HHS_LITERT_NATIVE_GRAPH_OK)
        return HHS_LITERT_NATIVE_GRAPH_ERR_TOPOLOGY;
    expected = fingerprint(&descriptor);
    return expected == registration->graph_fingerprint64 && expected != 0U
        ? HHS_LITERT_NATIVE_GRAPH_OK
        : HHS_LITERT_NATIVE_GRAPH_ERR_IDENTITY;
}
