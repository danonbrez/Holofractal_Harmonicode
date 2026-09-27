#include "hhs_pass220_litert_native_model_runtime_v1.h"

#include <assert.h>
#include <string.h>

static void fill_hash(uint8_t out[HHS_LITERT_NATIVE_SHA256_BYTES], uint8_t seed) {
    uint32_t i;
    for (i = 0U; i < HHS_LITERT_NATIVE_SHA256_BYTES; ++i)
        out[i] = (uint8_t)(seed + i);
}

static HHSLiteRTNativeModelDescriptorV1 descriptor(void) {
    HHSLiteRTNativeModelDescriptorV1 value;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = hhs_litert_native_model_runtime_version();
    value.generation = 7U;
    value.backend = HHS_LITERT_NATIVE_BACKEND_NATIVE;
    value.context_tokens = 8192U;
    value.max_output_tokens = 2048U;
    value.tensor_count = 2U;
    value.input_count = 1U;
    value.output_count = 1U;
    fill_hash(value.source_sha256, 1U);
    memset(value.model_identity_hash216, 'M', HHS_LITERT_NATIVE_HASH216_LEN);
    value.model_identity_hash216[HHS_LITERT_NATIVE_HASH216_LEN] = '\0';

    value.tensors[0].tensor_id = 1U;
    value.tensors[0].role = HHS_LITERT_NATIVE_TENSOR_INPUT;
    value.tensors[0].dtype = HHS_LITERT_NATIVE_DTYPE_INT32;
    value.tensors[0].rank = 2U;
    value.tensors[0].dims[0] = 1U;
    value.tensors[0].dims[1] = 4096U;
    fill_hash(value.tensors[0].name_sha256, 11U);

    value.tensors[1].tensor_id = 2U;
    value.tensors[1].role = HHS_LITERT_NATIVE_TENSOR_OUTPUT;
    value.tensors[1].dtype = HHS_LITERT_NATIVE_DTYPE_FLOAT32;
    value.tensors[1].rank = 3U;
    value.tensors[1].dims[0] = 1U;
    value.tensors[1].dims[1] = 1U;
    value.tensors[1].dims[2] = 256000U;
    fill_hash(value.tensors[1].name_sha256, 21U);
    return value;
}

int main(void) {
    HHSLiteRTNativeModelDescriptorV1 input = descriptor();
    HHSLiteRTNativeModelRegistrationV1 first;
    HHSLiteRTNativeModelRegistrationV1 replay;

    assert(hhs_litert_native_model_runtime_version() == 1U);
    assert(hhs_litert_native_model_register(&input, &first) == HHS_LITERT_NATIVE_OK);
    assert(hhs_litert_native_model_validate_registration(&first) == HHS_LITERT_NATIVE_OK);
    assert(first.registration_fingerprint64 != 0U);
    assert(first.native_registry_authority == 1U);
    assert(first.model_output_advisory_only == 1U);
    assert(first.vm81_mutation_authority == 0U);
    assert(first.hash72_commit_authority == 0U);
    assert(first.hash216_persistence_authority == 0U);
    assert(first.floating_point_canonical_authority == 0U);
    assert(first.external_litert_compatibility_supported == 1U);

    assert(hhs_litert_native_model_register(&input, &replay) == HHS_LITERT_NATIVE_OK);
    assert(first.registration_fingerprint64 == replay.registration_fingerprint64);
    assert(memcmp(&first.tensors, &replay.tensors, sizeof(first.tensors)) == 0);

    input.output_count = 2U;
    assert(hhs_litert_native_model_register(&input, &replay) == HHS_LITERT_NATIVE_ERR_RANGE);

    input = descriptor();
    input.tensors[1].dims[3] = 1U;
    assert(hhs_litert_native_model_register(&input, &replay) == HHS_LITERT_NATIVE_ERR_TENSOR);

    return 0;
}
