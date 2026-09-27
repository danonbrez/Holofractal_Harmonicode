#ifndef HHS_PASS220_LITERT_NATIVE_MODEL_RUNTIME_V1_H
#define HHS_PASS220_LITERT_NATIVE_MODEL_RUNTIME_V1_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_LITERT_NATIVE_MODEL_RUNTIME_VERSION 1U
#define HHS_LITERT_NATIVE_MAX_TENSORS 16U
#define HHS_LITERT_NATIVE_MAX_RANK 8U
#define HHS_LITERT_NATIVE_SHA256_BYTES 32U
#define HHS_LITERT_NATIVE_HASH216_LEN 216U
#define HHS_LITERT_NATIVE_HASH216_STRLEN 217U

typedef enum HHSLiteRTNativeStatusV1 {
    HHS_LITERT_NATIVE_OK = 0,
    HHS_LITERT_NATIVE_ERR_ARGUMENT = 1,
    HHS_LITERT_NATIVE_ERR_VERSION = 2,
    HHS_LITERT_NATIVE_ERR_RANGE = 3,
    HHS_LITERT_NATIVE_ERR_TENSOR = 4,
    HHS_LITERT_NATIVE_ERR_IDENTITY = 5,
    HHS_LITERT_NATIVE_ERR_INVARIANT = 6
} HHSLiteRTNativeStatusV1;

typedef enum HHSLiteRTNativeBackendV1 {
    HHS_LITERT_NATIVE_BACKEND_NATIVE = 1,
    HHS_LITERT_NATIVE_BACKEND_CPU = 2,
    HHS_LITERT_NATIVE_BACKEND_GPU = 3,
    HHS_LITERT_NATIVE_BACKEND_NPU = 4,
    HHS_LITERT_NATIVE_BACKEND_EXTERNAL = 5
} HHSLiteRTNativeBackendV1;

typedef enum HHSLiteRTNativeTensorRoleV1 {
    HHS_LITERT_NATIVE_TENSOR_INPUT = 1,
    HHS_LITERT_NATIVE_TENSOR_OUTPUT = 2
} HHSLiteRTNativeTensorRoleV1;

typedef enum HHSLiteRTNativeDTypeV1 {
    HHS_LITERT_NATIVE_DTYPE_BOOL = 1,
    HHS_LITERT_NATIVE_DTYPE_INT8 = 2,
    HHS_LITERT_NATIVE_DTYPE_UINT8 = 3,
    HHS_LITERT_NATIVE_DTYPE_INT16 = 4,
    HHS_LITERT_NATIVE_DTYPE_UINT16 = 5,
    HHS_LITERT_NATIVE_DTYPE_INT32 = 6,
    HHS_LITERT_NATIVE_DTYPE_UINT32 = 7,
    HHS_LITERT_NATIVE_DTYPE_INT64 = 8,
    HHS_LITERT_NATIVE_DTYPE_UINT64 = 9,
    HHS_LITERT_NATIVE_DTYPE_FLOAT16 = 10,
    HHS_LITERT_NATIVE_DTYPE_FLOAT32 = 11,
    HHS_LITERT_NATIVE_DTYPE_FLOAT64 = 12,
    HHS_LITERT_NATIVE_DTYPE_BFLOAT16 = 13
} HHSLiteRTNativeDTypeV1;

typedef struct HHSLiteRTNativeTensorSpecV1 {
    uint32_t tensor_id;
    uint32_t role;
    uint32_t dtype;
    uint32_t rank;
    uint64_t dims[HHS_LITERT_NATIVE_MAX_RANK];
    uint8_t name_sha256[HHS_LITERT_NATIVE_SHA256_BYTES];
} HHSLiteRTNativeTensorSpecV1;

typedef struct HHSLiteRTNativeModelDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t generation;
    uint32_t backend;
    uint32_t context_tokens;
    uint32_t max_output_tokens;
    uint32_t tensor_count;
    uint32_t input_count;
    uint32_t output_count;
    uint8_t source_sha256[HHS_LITERT_NATIVE_SHA256_BYTES];
    char model_identity_hash216[HHS_LITERT_NATIVE_HASH216_STRLEN];
    HHSLiteRTNativeTensorSpecV1 tensors[HHS_LITERT_NATIVE_MAX_TENSORS];
} HHSLiteRTNativeModelDescriptorV1;

typedef struct HHSLiteRTNativeModelRegistrationV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t generation;
    uint32_t backend;
    uint32_t context_tokens;
    uint32_t max_output_tokens;
    uint32_t tensor_count;
    uint32_t input_count;
    uint32_t output_count;
    uint64_t registration_fingerprint64;
    uint8_t source_sha256[HHS_LITERT_NATIVE_SHA256_BYTES];
    char model_identity_hash216[HHS_LITERT_NATIVE_HASH216_STRLEN];
    HHSLiteRTNativeTensorSpecV1 tensors[HHS_LITERT_NATIVE_MAX_TENSORS];
    uint8_t native_registry_authority;
    uint8_t model_output_advisory_only;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t hash216_persistence_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t external_litert_compatibility_supported;
    uint8_t reserved0;
} HHSLiteRTNativeModelRegistrationV1;

uint32_t hhs_litert_native_model_runtime_version(void);

HHSLiteRTNativeStatusV1 hhs_litert_native_model_register(
    const HHSLiteRTNativeModelDescriptorV1 *descriptor,
    HHSLiteRTNativeModelRegistrationV1 *out_registration
);

HHSLiteRTNativeStatusV1 hhs_litert_native_model_validate_registration(
    const HHSLiteRTNativeModelRegistrationV1 *registration
);

#ifdef __cplusplus
}
#endif

#endif
