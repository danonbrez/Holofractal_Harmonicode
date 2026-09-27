#include "hhs_pass220_litert_native_model_runtime_v1.h"

#include <stddef.h>
#include <string.h>

static int sha_nonzero(const uint8_t value[HHS_LITERT_NATIVE_SHA256_BYTES]) {
    uint32_t i;
    uint8_t acc = 0U;
    for (i = 0U; i < HHS_LITERT_NATIVE_SHA256_BYTES; ++i)
        acc = (uint8_t)(acc | value[i]);
    return acc != 0U;
}

static int hash216_valid(
    const char value[HHS_LITERT_NATIVE_HASH216_STRLEN]
) {
    uint32_t i;
    if (value[HHS_LITERT_NATIVE_HASH216_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_LITERT_NATIVE_HASH216_LEN; ++i) {
        const unsigned char c = (unsigned char)value[i];
        if (c < 33U || c > 126U)
            return 0;
    }
    return 1;
}

static int backend_valid(uint32_t value) {
    return value >= HHS_LITERT_NATIVE_BACKEND_NATIVE &&
           value <= HHS_LITERT_NATIVE_BACKEND_EXTERNAL;
}

static int dtype_valid(uint32_t value) {
    return value >= HHS_LITERT_NATIVE_DTYPE_BOOL &&
           value <= HHS_LITERT_NATIVE_DTYPE_BFLOAT16;
}

static HHSLiteRTNativeStatusV1 tensor_validate(
    const HHSLiteRTNativeTensorSpecV1 *tensor
) {
    uint32_t i;
    if (tensor == NULL || tensor->tensor_id == 0U)
        return HHS_LITERT_NATIVE_ERR_TENSOR;
    if (tensor->role != HHS_LITERT_NATIVE_TENSOR_INPUT &&
        tensor->role != HHS_LITERT_NATIVE_TENSOR_OUTPUT)
        return HHS_LITERT_NATIVE_ERR_TENSOR;
    if (!dtype_valid(tensor->dtype) ||
        tensor->rank == 0U ||
        tensor->rank > HHS_LITERT_NATIVE_MAX_RANK ||
        !sha_nonzero(tensor->name_sha256))
        return HHS_LITERT_NATIVE_ERR_TENSOR;
    for (i = 0U; i < tensor->rank; ++i) {
        if (tensor->dims[i] == 0U)
            return HHS_LITERT_NATIVE_ERR_TENSOR;
    }
    for (; i < HHS_LITERT_NATIVE_MAX_RANK; ++i) {
        if (tensor->dims[i] != 0U)
            return HHS_LITERT_NATIVE_ERR_TENSOR;
    }
    return HHS_LITERT_NATIVE_OK;
}

static uint64_t fold64(uint64_t h, uint64_t value) {
    uint32_t i;
    for (i = 0U; i < 8U; ++i) {
        h ^= (value >> (8U * i)) & UINT64_C(0xff);
        h *= UINT64_C(1099511628211);
    }
    return h;
}

static uint64_t descriptor_fingerprint(
    const HHSLiteRTNativeModelDescriptorV1 *descriptor
) {
    uint64_t h = UINT64_C(14695981039346656037);
    uint32_t i;
    uint32_t j;
    h = fold64(h, descriptor->generation);
    h = fold64(h, descriptor->backend);
    h = fold64(h, descriptor->context_tokens);
    h = fold64(h, descriptor->max_output_tokens);
    h = fold64(h, descriptor->tensor_count);
    h = fold64(h, descriptor->input_count);
    h = fold64(h, descriptor->output_count);
    for (i = 0U; i < HHS_LITERT_NATIVE_SHA256_BYTES; ++i) {
        h ^= descriptor->source_sha256[i];
        h *= UINT64_C(1099511628211);
    }
    for (i = 0U; i < HHS_LITERT_NATIVE_HASH216_LEN; ++i) {
        h ^= (uint8_t)descriptor->model_identity_hash216[i];
        h *= UINT64_C(1099511628211);
    }
    for (i = 0U; i < descriptor->tensor_count; ++i) {
        const HHSLiteRTNativeTensorSpecV1 *tensor = &descriptor->tensors[i];
        h = fold64(h, tensor->tensor_id);
        h = fold64(h, tensor->role);
        h = fold64(h, tensor->dtype);
        h = fold64(h, tensor->rank);
        for (j = 0U; j < tensor->rank; ++j)
            h = fold64(h, tensor->dims[j]);
        for (j = 0U; j < HHS_LITERT_NATIVE_SHA256_BYTES; ++j) {
            h ^= tensor->name_sha256[j];
            h *= UINT64_C(1099511628211);
        }
    }
    return h;
}

static HHSLiteRTNativeStatusV1 descriptor_validate(
    const HHSLiteRTNativeModelDescriptorV1 *descriptor
) {
    uint32_t i;
    uint32_t j;
    uint32_t inputs = 0U;
    uint32_t outputs = 0U;

    if (descriptor == NULL)
        return HHS_LITERT_NATIVE_ERR_ARGUMENT;
    if (descriptor->struct_size < sizeof(*descriptor) ||
        descriptor->version != HHS_LITERT_NATIVE_MODEL_RUNTIME_VERSION)
        return HHS_LITERT_NATIVE_ERR_VERSION;
    if (!backend_valid(descriptor->backend) ||
        descriptor->context_tokens == 0U ||
        descriptor->max_output_tokens == 0U ||
        descriptor->tensor_count == 0U ||
        descriptor->tensor_count > HHS_LITERT_NATIVE_MAX_TENSORS ||
        descriptor->input_count == 0U ||
        descriptor->output_count == 0U ||
        descriptor->input_count + descriptor->output_count != descriptor->tensor_count)
        return HHS_LITERT_NATIVE_ERR_RANGE;
    if (!sha_nonzero(descriptor->source_sha256) ||
        !hash216_valid(descriptor->model_identity_hash216))
        return HHS_LITERT_NATIVE_ERR_IDENTITY;

    for (i = 0U; i < descriptor->tensor_count; ++i) {
        HHSLiteRTNativeStatusV1 status = tensor_validate(&descriptor->tensors[i]);
        if (status != HHS_LITERT_NATIVE_OK)
            return status;
        if (descriptor->tensors[i].role == HHS_LITERT_NATIVE_TENSOR_INPUT)
            ++inputs;
        else
            ++outputs;
        for (j = 0U; j < i; ++j) {
            if (descriptor->tensors[i].tensor_id == descriptor->tensors[j].tensor_id)
                return HHS_LITERT_NATIVE_ERR_INVARIANT;
        }
    }
    if (inputs != descriptor->input_count || outputs != descriptor->output_count)
        return HHS_LITERT_NATIVE_ERR_INVARIANT;
    return HHS_LITERT_NATIVE_OK;
}

uint32_t hhs_litert_native_model_runtime_version(void) {
    return HHS_LITERT_NATIVE_MODEL_RUNTIME_VERSION;
}

HHSLiteRTNativeStatusV1 hhs_litert_native_model_register(
    const HHSLiteRTNativeModelDescriptorV1 *descriptor,
    HHSLiteRTNativeModelRegistrationV1 *out_registration
) {
    HHSLiteRTNativeStatusV1 status;
    if (out_registration == NULL)
        return HHS_LITERT_NATIVE_ERR_ARGUMENT;
    status = descriptor_validate(descriptor);
    if (status != HHS_LITERT_NATIVE_OK)
        return status;

    memset(out_registration, 0, sizeof(*out_registration));
    out_registration->struct_size = (uint32_t)sizeof(*out_registration);
    out_registration->version = HHS_LITERT_NATIVE_MODEL_RUNTIME_VERSION;
    out_registration->generation = descriptor->generation;
    out_registration->backend = descriptor->backend;
    out_registration->context_tokens = descriptor->context_tokens;
    out_registration->max_output_tokens = descriptor->max_output_tokens;
    out_registration->tensor_count = descriptor->tensor_count;
    out_registration->input_count = descriptor->input_count;
    out_registration->output_count = descriptor->output_count;
    out_registration->registration_fingerprint64 = descriptor_fingerprint(descriptor);
    memcpy(out_registration->source_sha256, descriptor->source_sha256,
           sizeof(out_registration->source_sha256));
    memcpy(out_registration->model_identity_hash216,
           descriptor->model_identity_hash216,
           sizeof(out_registration->model_identity_hash216));
    memcpy(out_registration->tensors, descriptor->tensors,
           sizeof(HHSLiteRTNativeTensorSpecV1) * descriptor->tensor_count);
    out_registration->native_registry_authority = 1U;
    out_registration->model_output_advisory_only = 1U;
    out_registration->vm81_mutation_authority = 0U;
    out_registration->hash72_commit_authority = 0U;
    out_registration->hash216_persistence_authority = 0U;
    out_registration->floating_point_canonical_authority = 0U;
    out_registration->external_litert_compatibility_supported = 1U;

    return hhs_litert_native_model_validate_registration(out_registration);
}

HHSLiteRTNativeStatusV1 hhs_litert_native_model_validate_registration(
    const HHSLiteRTNativeModelRegistrationV1 *registration
) {
    HHSLiteRTNativeModelDescriptorV1 descriptor;
    uint64_t expected;
    if (registration == NULL)
        return HHS_LITERT_NATIVE_ERR_ARGUMENT;
    if (registration->struct_size < sizeof(*registration) ||
        registration->version != HHS_LITERT_NATIVE_MODEL_RUNTIME_VERSION)
        return HHS_LITERT_NATIVE_ERR_VERSION;
    if (registration->native_registry_authority != 1U ||
        registration->model_output_advisory_only != 1U ||
        registration->vm81_mutation_authority != 0U ||
        registration->hash72_commit_authority != 0U ||
        registration->hash216_persistence_authority != 0U ||
        registration->floating_point_canonical_authority != 0U ||
        registration->external_litert_compatibility_supported != 1U)
        return HHS_LITERT_NATIVE_ERR_INVARIANT;

    memset(&descriptor, 0, sizeof(descriptor));
    descriptor.struct_size = (uint32_t)sizeof(descriptor);
    descriptor.version = HHS_LITERT_NATIVE_MODEL_RUNTIME_VERSION;
    descriptor.generation = registration->generation;
    descriptor.backend = registration->backend;
    descriptor.context_tokens = registration->context_tokens;
    descriptor.max_output_tokens = registration->max_output_tokens;
    descriptor.tensor_count = registration->tensor_count;
    descriptor.input_count = registration->input_count;
    descriptor.output_count = registration->output_count;
    memcpy(descriptor.source_sha256, registration->source_sha256,
           sizeof(descriptor.source_sha256));
    memcpy(descriptor.model_identity_hash216,
           registration->model_identity_hash216,
           sizeof(descriptor.model_identity_hash216));
    memcpy(descriptor.tensors, registration->tensors,
           sizeof(HHSLiteRTNativeTensorSpecV1) * registration->tensor_count);

    if (descriptor_validate(&descriptor) != HHS_LITERT_NATIVE_OK)
        return HHS_LITERT_NATIVE_ERR_INVARIANT;
    expected = descriptor_fingerprint(&descriptor);
    return expected == registration->registration_fingerprint64 && expected != 0U
        ? HHS_LITERT_NATIVE_OK
        : HHS_LITERT_NATIVE_ERR_INVARIANT;
}
