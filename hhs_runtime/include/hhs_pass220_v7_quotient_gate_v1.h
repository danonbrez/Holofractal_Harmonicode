#ifndef HHS_PASS220_V7_QUOTIENT_GATE_V1_H
#define HHS_PASS220_V7_QUOTIENT_GATE_V1_H

#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

/* Source-specific, candidate-only Pass169 five-mode admissibility membrane.
 * No input flag, provider fixture, or hash authorizes a VM81 state mutation.
 */
#define HHS220_V7_QUOTIENT_VERSION UINT32_C(0x00010000)
#define HHS220_V7_SOURCE_BYTES 70U
#define HHS220_V7_HNAN_ALL_RULES UINT32_C(0x7fff)

enum HHS220V7Mode {
    HHS220_V7_MODE_UNDECLARED=0,
    HHS220_V7_ELEMENTWISE_SCALAR_QUOTIENT=1,
    HHS220_V7_RIGHT_MATRIX_SOLVE=2,
    HHS220_V7_LEFT_MATRIX_SOLVE=3,
    HHS220_V7_SCALAR_DENOMINATOR=4,
    HHS220_V7_DECLARED_FRACTAL_NESTING=5
};
enum HHS220V7Decision {
    HHS220_V7_REJECT=0,
    HHS220_V7_UNRESOLVED_PROVIDER=1,
    HHS220_V7_INHERIT_NATIVE_DISPATCH=2
};
enum HHS220V7Reason {
    HHS220_V7_INVALID_CALL=1,
    HHS220_V7_SOURCE_MISMATCH=2,
    HHS220_V7_UNKNOWN_MODE=3,
    HHS220_V7_HNAN_AUTHORITY_FAILED=4,
    HHS220_V7_FORBIDDEN_TRANSFORMATION=5,
    HHS220_V7_MODE_NOT_DECLARED=6,
    HHS220_V7_NATIVE_QUOTIENT_PROVIDER_MISSING=7,
    HHS220_V7_FABRICATED_COMMIT=8,
    HHS220_V7_NATIVE_TYPE_DISPATCH_REQUIRED=9
};

typedef struct HHS220V7QuotientInput {
    uint32_t struct_size;
    uint32_t version;
    const uint8_t *source;
    size_t source_bytes;
    uint32_t declared_mode;
    uint8_t scalarize_ordered_carriers;
    uint8_t commute_phase_products;
    uint8_t cancel_global_denominator;
    uint8_t reverse_ordered_equality;
    uint8_t claim_vm81_commit;
    uint8_t claim_hash72_commit;
    uint8_t claim_hash216_commit;
    uint8_t reserved[1];
} HHS220V7QuotientInput;

typedef struct HHS220V7QuotientResult {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason;
    uint32_t declared_mode;
    uint32_t native_hnan_rule_mask;
    uint8_t source_exact;
    uint8_t hnan_15_rule_graph_verified;
    uint8_t xy_yx_order_verified;
    uint8_t zw_wz_order_verified;
    uint8_t typed_mode_lexically_registered;
    uint8_t native_quotient_provider_available;
    uint8_t matrix_inverse_verified;
    uint8_t global_environment_verified;
    uint8_t canonical_vm81_admission_verified;
    uint8_t hash72_commit_authority;
    uint8_t hash216_commit_authority;
    uint8_t canonical_persistence_mutated;
    uint8_t source_sha256[32];
    uint8_t native_type_dispatch_required;
} HHS220V7QuotientResult;

/* REJECT only actual source/order/type/security violations. A source
 * lacking a lexical quotient mode is delegated to the existing native
 * typed VMIR, rather than rejected as a purported invalid tensor state.
 * INHERIT_NATIVE_DISPATCH and UNRESOLVED_PROVIDER cannot mint VM81 state.
 */
int hhs220_v7_quotient_preflight(const HHS220V7QuotientInput *input,
                                HHS220V7QuotientResult *out);
const char *hhs220_v7_mode_name(uint32_t mode);
#ifdef __cplusplus
}
#endif
#endif
