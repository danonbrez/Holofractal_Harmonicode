#include "hhs_pass220_litert_native_model_runtime_v1.hpp"

#include <cassert>
#include <cstdint>
#include <cstring>

int main() {
    HHSLiteRTNativeModelDescriptorV1 descriptor{};
    descriptor.struct_size = static_cast<std::uint32_t>(sizeof(descriptor));
    descriptor.version = hhs_litert_native_model_runtime_version();
    descriptor.generation = 1U;
    descriptor.backend = HHS_LITERT_NATIVE_BACKEND_NATIVE;
    descriptor.context_tokens = 4096U;
    descriptor.max_output_tokens = 1024U;
    descriptor.tensor_count = 2U;
    descriptor.input_count = 1U;
    descriptor.output_count = 1U;
    for (std::uint32_t i = 0U; i < HHS_LITERT_NATIVE_SHA256_BYTES; ++i)
        descriptor.source_sha256[i] = static_cast<std::uint8_t>(i + 1U);
    std::memset(descriptor.model_identity_hash216, 'L', HHS_LITERT_NATIVE_HASH216_LEN);
    descriptor.model_identity_hash216[HHS_LITERT_NATIVE_HASH216_LEN] = '\0';

    descriptor.tensors[0].tensor_id = 1U;
    descriptor.tensors[0].role = HHS_LITERT_NATIVE_TENSOR_INPUT;
    descriptor.tensors[0].dtype = HHS_LITERT_NATIVE_DTYPE_INT32;
    descriptor.tensors[0].rank = 2U;
    descriptor.tensors[0].dims[0] = 1U;
    descriptor.tensors[0].dims[1] = 1024U;
    descriptor.tensors[0].name_sha256[0] = 1U;

    descriptor.tensors[1].tensor_id = 2U;
    descriptor.tensors[1].role = HHS_LITERT_NATIVE_TENSOR_OUTPUT;
    descriptor.tensors[1].dtype = HHS_LITERT_NATIVE_DTYPE_FLOAT32;
    descriptor.tensors[1].rank = 3U;
    descriptor.tensors[1].dims[0] = 1U;
    descriptor.tensors[1].dims[1] = 1U;
    descriptor.tensors[1].dims[2] = 32000U;
    descriptor.tensors[1].name_sha256[0] = 2U;

    hhs::litert::NativeModelRuntimeRegistration registration(descriptor);
    assert(registration.status() == HHS_LITERT_NATIVE_OK);
    assert(hhs::litert::NativeModelRuntimeRegistration::model_output_advisory_only());
    assert(!hhs::litert::NativeModelRuntimeRegistration::vm81_mutation_authority());
    assert(!hhs::litert::NativeModelRuntimeRegistration::hash72_commit_authority());
    assert(!hhs::litert::NativeModelRuntimeRegistration::hash216_persistence_authority());
    assert(!hhs::litert::NativeModelRuntimeRegistration::floating_point_canonical_authority());
    assert(hhs::litert::NativeModelRuntimeRegistration::external_litert_compatibility_supported());
    return 0;
}
