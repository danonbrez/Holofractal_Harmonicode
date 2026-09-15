#ifndef HHS_PASS219_HASH216_FRACTAL_QUDIT_ADMISSION_1_45_H
#define HHS_PASS219_HASH216_FRACTAL_QUDIT_ADMISSION_1_45_H

#include "hhs_pass219_lane5_repository_capability_reverse_discovery_1_44.h"
#include "hhs_pass219_vm81_environmental_recovery_1_32.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_VERSION UINT32_C(0x0001002D)
#define HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_NAMESPACE UINT32_C(0x0002192D)
#define HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_BLOCK UINT32_C(5184)
#define HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_HASH72_RADIX UINT32_C(72)
#define HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_VM81_CELLS UINT32_C(81)
#define HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_LANE64 UINT32_C(64)
#define HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_LEVELS UINT32_C(36)

#define HHS_EXACT_PASS219_FQ_SCOPE_SCALING UINT64_C(0x0001)
#define HHS_EXACT_PASS219_FQ_SCOPE_LOCAL_BIJECTION UINT64_C(0x0002)
#define HHS_EXACT_PASS219_FQ_SCOPE_PQ_WINDOW UINT64_C(0x0004)
#define HHS_EXACT_PASS219_FQ_SCOPE_CONSTRUCTOR UINT64_C(0x0008)
#define HHS_EXACT_PASS219_FQ_SCOPE_LO_SHU_RECIPROCAL UINT64_C(0x0010)
#define HHS_EXACT_PASS219_FQ_SCOPE_MASS_FACTORIZATION UINT64_C(0x0020)
#define HHS_EXACT_PASS219_FQ_SCOPE_PARENT_HASH216 UINT64_C(0x0040)
#define HHS_EXACT_PASS219_FQ_SCOPE_CHILD_HASH216 UINT64_C(0x0080)
#define HHS_EXACT_PASS219_FQ_SCOPE_SIGNED_ENVIRONMENT UINT64_C(0x0100)
#define HHS_EXACT_PASS219_FQ_SCOPE_REQUIRED UINT64_C(0x01FF)

typedef enum HHSExactPass219Hash216FractalQuditReasonV1 {
    HHS_EXACT_PASS219_FQ_REASON_NONE = 0,
    HHS_EXACT_PASS219_FQ_REASON_SCOPE = 1,
    HHS_EXACT_PASS219_FQ_REASON_SCALING = 2,
    HHS_EXACT_PASS219_FQ_REASON_LOCAL_BIJECTION = 3,
    HHS_EXACT_PASS219_FQ_REASON_PQ_WINDOW = 4,
    HHS_EXACT_PASS219_FQ_REASON_CONSTRUCTOR = 5,
    HHS_EXACT_PASS219_FQ_REASON_LO_SHU_RECIPROCAL = 6,
    HHS_EXACT_PASS219_FQ_REASON_MASS_FACTORIZATION = 7,
    HHS_EXACT_PASS219_FQ_REASON_PARENT_HASH216 = 8,
    HHS_EXACT_PASS219_FQ_REASON_INHERITED_ADMISSION = 9,
    HHS_EXACT_PASS219_FQ_REASON_CHILD_HASH216 = 10,
    HHS_EXACT_PASS219_FQ_REASON_RECEIPT_REPLAY = 11
} HHSExactPass219Hash216FractalQuditReasonV1;

typedef struct HHSExactPass219Hash216FractalQuditWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint64_t declared_scope_mask;
    uint16_t local5184;
    uint16_t bigint5184[HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_LEVELS];
    uint8_t hash72_major;
    uint8_t hash72_minor;
    uint8_t cell81;
    uint8_t operation64;
    int8_t u72_left;
    int8_t u72_right;
    int8_t xy_plus_zw;
    uint8_t lo_shu_n;
    uint8_t lo_shu_antipode;
    int8_t sigma;
    uint8_t reserved0[2];
    int64_t mass_t;
    int64_t mass_x;
    int64_t mass_y;
    int64_t mass_D;
    int64_t mass_N;
} HHSExactPass219Hash216FractalQuditWitnessV1;

typedef struct HHSExactPass219Hash216FractalQuditReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t reason;
    uint64_t declared_scope_mask;
    uint64_t verified_scope_mask;
    uint64_t failed_scope_mask;
    uint16_t local5184;
    uint16_t bigint5184[HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_LEVELS];
    uint8_t hash72_major;
    uint8_t hash72_minor;
    uint8_t cell81;
    uint8_t operation64;
    uint8_t lo_shu_n;
    uint8_t lo_shu_antipode;
    int8_t sigma;
    uint8_t reserved0;
    int64_t mass_D;
    int64_t mass_N;
    uint64_t witness_signature64;
    uint64_t parent_signature64;
    uint64_t child_signature64;
    uint64_t inherited_decision_signature64;
    uint64_t environment_witness_sequence;
    uint64_t receipt_signature64;
    char witness_hash72[HHS_EXACT_HASH72_STRLEN];
    HHSExactPass219Hash216TransitionViewV1 proof_transition;
    uint8_t accepted;
    uint8_t exact_integer_only;
    uint8_t scaling_closed;
    uint8_t dual_coordinate_verified;
    uint8_t pq_window_verified;
    uint8_t constructor_verified;
    uint8_t lo_shu_reciprocal_verified;
    uint8_t mass_factorization_verified;
    uint8_t parent_hash216_verified;
    uint8_t child_hash216_verified;
    uint8_t signed_environment_verified;
    uint8_t inherited_canonical_admission_verified;
    uint8_t proof_transition_indexed;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t receipt_clock_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t reserved1[4];
} HHSExactPass219Hash216FractalQuditReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_hash216_fractal_qudit_admission_version(void);

/* Pure pre-hydration verifier. It cannot mutate VM81 or create canonical receipts. */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hash216_fractal_qudit_witness_validate(
    const HHSExactUQCELInputV1 *input,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    const HHSExactPass219Hash216FractalQuditWitnessV1 *witness
);

/*
 * Proof-carrying Hash216 hydration gate. It accepts only an already-successful
 * canonical result produced by hhs_exact_pass219_vm81_environment_admit_signed,
 * verifies the equation/geometry witness against that result, and emits a
 * non-authoritative indexed Hash216 proof transition. It cannot mutate VM81,
 * sign, persist, advance a receipt clock, or replace inherited canonical
 * Hash72/Hash216 authority.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hash216_fractal_qudit_hydrate_proof(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *committed_frame,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    const HHSExactPass219RNAAdmissionV1 *admission,
    const HHSExactPass219VM81PQCFirewallReceiptV1 *firewall_receipt,
    const HHSExactPass219VM81PQCSignatureReceiptV1 *signature_receipt,
    const HHSExactPass219VM81EnvironmentReceiptV1 *environment_receipt,
    const HHSExactPass219Hash216FractalQuditWitnessV1 *witness,
    HHSExactPass219Hash216FractalQuditReceiptV1 *out_proof_receipt
);

/* Deterministic proof replay; no mutation, signing, persistence, or clock authority. */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hash216_fractal_qudit_receipt_replay(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *committed_frame,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    const HHSExactPass219RNAAdmissionV1 *admission,
    const HHSExactPass219VM81PQCFirewallReceiptV1 *firewall_receipt,
    const HHSExactPass219VM81PQCSignatureReceiptV1 *signature_receipt,
    const HHSExactPass219VM81EnvironmentReceiptV1 *environment_receipt,
    const HHSExactPass219Hash216FractalQuditWitnessV1 *witness,
    const HHSExactPass219Hash216FractalQuditReceiptV1 *proof_receipt
);

#ifdef __cplusplus
}
#endif

#endif
