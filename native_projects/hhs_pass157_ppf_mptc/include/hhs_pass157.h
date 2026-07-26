#ifndef HHS_PASS157_H
#define HHS_PASS157_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS157_ABI_VERSION 1U
#define HHS157_CENTERLINE_COUNT 11U
#define HHS157_TENSOR_CELLS 9U
#define HHS157_VM81_CELLS 81U
#define HHS157_HASH72_STRLEN 73U
#define HHS157_HASH216_STRLEN 217U
#define HHS157_SOURCE_MAX 2048U
#define HHS157_FOLD_PATH_MAX 256U

#define HHS157_CONTRACT_ID "HHS-P157-PPF-MPTC"
#define HHS157_CONTRACT_VERSION "1.1.0"
#define HHS157_LOCAL_STATUS "HHS_PASS_157_NATIVE_CORE_VERIFIED"
#define HHS157_INCOMPLETE_INHERITED "HHS_PASS_157_INCOMPLETE_INHERITED_FOUNDATION"
#define HHS157_INCOMPLETE_LIVE_DEPENDENCY "HHS_PASS_157_INCOMPLETE_LIVE_DEPENDENCY"

typedef enum HHS157Status {
    HHS157_OK = 0,
    HHS157_INVALID_ARGUMENT = 1,
    HHS157_OVERFLOW = 2,
    HHS157_DIVIDE_BY_ZERO = 3,
    HHS157_PYTHAGOREAN_MISMATCH = 4,
    HHS157_RECIPROCAL_MEMBRANE_MISMATCH = 5,
    HHS157_DELTA_MISMATCH = 6,
    HHS157_CENTERLINE_ORDER_MISMATCH = 7,
    HHS157_PHASE_RECONSTRUCTION_MISMATCH = 8,
    HHS157_VM81_REJECTED = 9,
    HHS157_KERNEL_DRIFT = 10,
    HHS157_RECEIPT_MISMATCH = 11,
    HHS157_REPLAY_MISMATCH = 12,
    HHS157_SERIALIZATION_BOUNDED = 13,
    HHS157_SOURCE_BOUNDED = 14
} HHS157Status;

typedef struct HHS157Plastic {
    int64_t c0;
    int64_t c1;
    int64_t c2;
} HHS157Plastic;

typedef struct HHS157Pythagorean {
    int64_t a;
    int64_t b;
    int64_t c;
    int64_t a2;
    int64_t b2;
    int64_t c2;
} HHS157Pythagorean;

typedef struct HHS157PhaseLane {
    int64_t modulus;
    int64_t quotient;
    int64_t residue;
} HHS157PhaseLane;

typedef struct HHS157TensorCell {
    uint8_t lo_shu_digit;
    uint8_t phase_lane;
    int64_t polynomial_component;
    uint64_t fibonacci_component;
    HHS157Plastic plastic_component;
    int64_t phase_residue;
    int64_t combined_scalar;
} HHS157TensorCell;

typedef struct HHS157Request {
    uint32_t abi_version;
    int64_t P;
    int64_t p;
    int64_t q;
    int64_t euclid_m;
    int64_t euclid_n;
    int64_t full_rotation;
    int64_t local_modulus;
    int64_t centerline[HHS157_CENTERLINE_COUNT];
    char fold_path[HHS157_FOLD_PATH_MAX];
    char source_expression[HHS157_SOURCE_MAX];
} HHS157Request;

typedef struct HHS157AuthorityReceipt {
    uint32_t abi_version;
    uint64_t runtime_magic;
    uint32_t runtime_abi_major;
    uint32_t runtime_abi_minor;
    uint32_t runtime_abi_patch;
    uint64_t runtime_state_size;
    uint64_t step_before;
    uint64_t step_after;
    uint64_t witness_before;
    uint64_t witness_after;
    char parent_hash72[HHS157_HASH72_STRLEN];
    char state_hash72[HHS157_HASH72_STRLEN];
    char receipt_hash72[HHS157_HASH72_STRLEN];
    char kernel_profile_hash216[HHS157_HASH216_STRLEN];
    char transition_hash216[HHS157_HASH216_STRLEN];
    char admission_seal_hash216[HHS157_HASH216_STRLEN];
} HHS157AuthorityReceipt;

typedef struct HHS157Result {
    uint32_t abi_version;
    int64_t P2;
    int64_t P4;
    int64_t A;
    int64_t B;
    int64_t pq;
    int64_t Delta;
    int64_t xy;
    int64_t yx;
    HHS157Pythagorean triple;
    HHS157PhaseLane local_phase;
    HHS157PhaseLane orthogonal_phase[3];
    HHS157TensorCell tensor[HHS157_TENSOR_CELLS];
    int64_t centerline[HHS157_CENTERLINE_COUNT];
    uint16_t vm81_cells[HHS157_VM81_CELLS];
    char source_hash216[HHS157_HASH216_STRLEN];
    char fold_hash216[HHS157_HASH216_STRLEN];
    char tensor_hash216[HHS157_HASH216_STRLEN];
    char vm81_projection_hash216[HHS157_HASH216_STRLEN];
    char result_hash216[HHS157_HASH216_STRLEN];
    uint8_t pythagorean_verified;
    uint8_t reciprocal_membrane_verified;
    uint8_t delta_verified;
    uint8_t centerline_verified;
    uint8_t phase_reconstruction_verified;
    uint8_t pass155_fold_verified;
    uint8_t pass156_membrane_verified;
    uint8_t pass156_1_dependency_hardened;
} HHS157Result;

HHS157Status hhs157_phase_decompose(int64_t n, int64_t modulus, HHS157PhaseLane *out);
HHS157Status hhs157_plastic_power(uint32_t exponent, HHS157Plastic *out);
HHS157Status hhs157_construct(const HHS157Request *request, HHS157Result *result);
HHS157Status hhs157_admit(const HHS157Request *request, HHS157Result *result, void *runtime_state, HHS157AuthorityReceipt *receipt);
HHS157Status hhs157_verify_receipt(const HHS157Request *request, const HHS157Result *result, const HHS157AuthorityReceipt *receipt);
HHS157Status hhs157_replay_verify(const HHS157Request *request, const HHS157Result *expected, const HHS157AuthorityReceipt *expected_receipt);
HHS157Status hhs157_serialize_json(const HHS157Request *request, const HHS157Result *result, const HHS157AuthorityReceipt *receipt, char *out, size_t out_size, size_t *written);
const char *hhs157_status_string(HHS157Status status);

#ifdef __cplusplus
}
#endif

#endif
