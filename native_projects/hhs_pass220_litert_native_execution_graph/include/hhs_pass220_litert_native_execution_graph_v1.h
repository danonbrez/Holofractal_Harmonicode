#ifndef HHS_PASS220_LITERT_NATIVE_EXECUTION_GRAPH_V1_H
#define HHS_PASS220_LITERT_NATIVE_EXECUTION_GRAPH_V1_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_LITERT_NATIVE_GRAPH_VERSION 1U
#define HHS_LITERT_NATIVE_GRAPH_MAX_TENSORS 32U
#define HHS_LITERT_NATIVE_GRAPH_MAX_OPS 64U
#define HHS_LITERT_NATIVE_GRAPH_MAX_RANK 8U
#define HHS_LITERT_NATIVE_GRAPH_HASH216_LEN 216U
#define HHS_LITERT_NATIVE_GRAPH_HASH216_STRLEN 217U

#define HHS_LITERT_NATIVE_GRAPH_TENSOR_INPUT UINT32_C(0x01)
#define HHS_LITERT_NATIVE_GRAPH_TENSOR_OUTPUT UINT32_C(0x02)
#define HHS_LITERT_NATIVE_GRAPH_TENSOR_CONSTANT UINT32_C(0x04)

typedef enum HHSLiteRTNativeGraphStatusV1 {
    HHS_LITERT_NATIVE_GRAPH_OK = 0,
    HHS_LITERT_NATIVE_GRAPH_ERR_ARGUMENT = 1,
    HHS_LITERT_NATIVE_GRAPH_ERR_VERSION = 2,
    HHS_LITERT_NATIVE_GRAPH_ERR_RANGE = 3,
    HHS_LITERT_NATIVE_GRAPH_ERR_TENSOR = 4,
    HHS_LITERT_NATIVE_GRAPH_ERR_OPERATION = 5,
    HHS_LITERT_NATIVE_GRAPH_ERR_TOPOLOGY = 6,
    HHS_LITERT_NATIVE_GRAPH_ERR_BROADCAST = 7,
    HHS_LITERT_NATIVE_GRAPH_ERR_IDENTITY = 8
} HHSLiteRTNativeGraphStatusV1;

typedef enum HHSLiteRTNativeGraphDTypeV1 {
    HHS_LITERT_NATIVE_GRAPH_DTYPE_INT64 = 1,
    HHS_LITERT_NATIVE_GRAPH_DTYPE_FLOAT64 = 2
} HHSLiteRTNativeGraphDTypeV1;

typedef enum HHSLiteRTNativeGraphOpKindV1 {
    HHS_LITERT_NATIVE_GRAPH_OP_ADD = 1,
    HHS_LITERT_NATIVE_GRAPH_OP_SUBTRACT = 2,
    HHS_LITERT_NATIVE_GRAPH_OP_MULTIPLY = 3
} HHSLiteRTNativeGraphOpKindV1;

typedef struct HHSLiteRTNativeGraphTensorV1 {
    uint32_t tensor_id;
    uint32_t dtype;
    uint32_t rank;
    uint32_t flags;
    uint64_t dims[HHS_LITERT_NATIVE_GRAPH_MAX_RANK];
} HHSLiteRTNativeGraphTensorV1;

typedef struct HHSLiteRTNativeGraphOperationV1 {
    uint32_t operation_id;
    uint32_t kind;
    uint32_t left_tensor_id;
    uint32_t right_tensor_id;
    uint32_t output_tensor_id;
    uint32_t reserved0;
} HHSLiteRTNativeGraphOperationV1;

typedef struct HHSLiteRTNativeGraphDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t graph_id;
    uint32_t tensor_count;
    uint32_t operation_count;
    uint32_t input_count;
    uint32_t output_count;
    uint32_t reserved0;
    char graph_identity_hash216[HHS_LITERT_NATIVE_GRAPH_HASH216_STRLEN];
    HHSLiteRTNativeGraphTensorV1 tensors[HHS_LITERT_NATIVE_GRAPH_MAX_TENSORS];
    HHSLiteRTNativeGraphOperationV1 operations[HHS_LITERT_NATIVE_GRAPH_MAX_OPS];
} HHSLiteRTNativeGraphDescriptorV1;

typedef struct HHSLiteRTNativeGraphRegistrationV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t graph_id;
    uint32_t tensor_count;
    uint32_t operation_count;
    uint32_t input_count;
    uint32_t output_count;
    uint32_t reserved0;
    uint64_t graph_fingerprint64;
    char graph_identity_hash216[HHS_LITERT_NATIVE_GRAPH_HASH216_STRLEN];
    HHSLiteRTNativeGraphTensorV1 tensors[HHS_LITERT_NATIVE_GRAPH_MAX_TENSORS];
    HHSLiteRTNativeGraphOperationV1 operations[HHS_LITERT_NATIVE_GRAPH_MAX_OPS];
    uint8_t topology_authority;
    uint8_t numeric_execution_authority;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t hash216_persistence_authority;
    uint8_t host_float_canonical_authority;
    uint8_t numpy1_numeric_lowering_required;
    uint8_t reserved1;
} HHSLiteRTNativeGraphRegistrationV1;

uint32_t hhs_litert_native_graph_version(void);

HHSLiteRTNativeGraphStatusV1 hhs_litert_native_graph_register(
    const HHSLiteRTNativeGraphDescriptorV1 *descriptor,
    HHSLiteRTNativeGraphRegistrationV1 *out_registration
);

HHSLiteRTNativeGraphStatusV1 hhs_litert_native_graph_validate_registration(
    const HHSLiteRTNativeGraphRegistrationV1 *registration
);

#ifdef __cplusplus
}
#endif

#endif
