#ifndef HHS_PASS219_AUDIO_SECURITY_TRANSPORT_1_0_H
#define HHS_PASS219_AUDIO_SECURITY_TRANSPORT_1_0_H

#include "hhs_pass219_raw5184_octonion_audio_hydration_1_0.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_AUDIO_SECURITY_TRANSPORT_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_AUDIO_SECURITY_TRANSPORT_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_AUDIO_SECURITY_TRANSPORT_VERSION_PATCH 0U

typedef struct HHSExactPass219AudioSecurityTransportWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t signed_capability_verified;
    uint32_t capability_scope_bound;
    uint32_t raw5184_audio_hydration_bound;
    uint32_t harmonic_time_audio_ecc_required;
    uint32_t harmonic_time_audio_ecc_valid;
    uint32_t internal_pq_oriented_signal_required;
    uint32_t internal_pq_oriented_signal_valid;
    uint32_t receipt_replay_binding_required;
    uint32_t auxiliary_persistence_only;
    uint32_t public_crypto_primitive;
    uint32_t standardized_pq_crypto_claim;
    uint32_t independent_key_or_kem_authority;
    uint32_t canonical_vm81_mutation_authority;
    uint32_t new_hash72_mint_authority;
    uint32_t hash216_persistence_authority;
    uint32_t floating_point_canonical_authority;
    char binding_hash72[HHS_EXACT_HASH72_STRLEN];
} HHSExactPass219AudioSecurityTransportWitnessV1;

typedef struct HHSExactPass219AudioSecurityTransportAdmissionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t admitted;
    uint32_t signed_capability_bound;
    uint32_t raw5184_audio_hydration_bound;
    uint32_t harmonic_time_audio_ecc_bound;
    uint32_t internal_pq_oriented_signal_bound;
    uint32_t receipt_replay_binding_bound;
    uint32_t auxiliary_persistence_only;
    uint32_t public_crypto_primitive;
    uint32_t standardized_pq_crypto_claim;
    uint32_t independent_key_or_kem_authority;
    uint32_t canonical_vm81_mutation_authority;
    uint32_t new_hash72_mint_authority;
    uint32_t hash216_persistence_authority;
    uint32_t floating_point_canonical_authority;
    char binding_hash72[HHS_EXACT_HASH72_STRLEN];
} HHSExactPass219AudioSecurityTransportAdmissionV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_audio_security_transport_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_audio_security_transport_admit(
    const HHSExactPass219AudioSecurityTransportWitnessV1 *witness,
    HHSExactPass219AudioSecurityTransportAdmissionV1 *out_admission
);

#ifdef __cplusplus
}
#endif

#endif
