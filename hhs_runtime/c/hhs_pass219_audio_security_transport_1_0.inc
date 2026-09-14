#include "../include/hhs_pass219_audio_security_transport_1_0.h"

#include <stddef.h>
#include <string.h>

static uint32_t pass219_audio_security_transport_version_word(void) {
    return (HHS_EXACT_PASS219_AUDIO_SECURITY_TRANSPORT_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_AUDIO_SECURITY_TRANSPORT_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_AUDIO_SECURITY_TRANSPORT_VERSION_PATCH;
}

static int pass219_audio_security_transport_hash72_valid(
    const char value[HHS_EXACT_HASH72_STRLEN]
) {
    size_t index;
    if (value == NULL || value[HHS_EXACT_HASH72_LEN] != '\0') return 0;
    for (index = 0U; index < HHS_EXACT_HASH72_LEN; ++index) {
        if (strchr(HHS_EXACT_HASH72_ALPHABET, value[index]) == NULL) return 0;
    }
    return 1;
}

uint32_t hhs_exact_pass219_audio_security_transport_version(void) {
    return pass219_audio_security_transport_version_word();
}

HHSExactStatus hhs_exact_pass219_audio_security_transport_admit(
    const HHSExactPass219AudioSecurityTransportWitnessV1 *witness,
    HHSExactPass219AudioSecurityTransportAdmissionV1 *out_admission
) {
    if (witness == NULL || out_admission == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != pass219_audio_security_transport_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->signed_capability_verified != 1U ||
        witness->capability_scope_bound != 1U ||
        witness->raw5184_audio_hydration_bound != 1U ||
        witness->harmonic_time_audio_ecc_required != 1U ||
        witness->harmonic_time_audio_ecc_valid != 1U ||
        witness->internal_pq_oriented_signal_required != 1U ||
        witness->internal_pq_oriented_signal_valid != 1U ||
        witness->receipt_replay_binding_required != 1U ||
        witness->auxiliary_persistence_only != 1U ||
        witness->public_crypto_primitive != 0U ||
        witness->standardized_pq_crypto_claim != 0U ||
        witness->independent_key_or_kem_authority != 0U ||
        witness->canonical_vm81_mutation_authority != 0U ||
        witness->new_hash72_mint_authority != 0U ||
        witness->hash216_persistence_authority != 0U ||
        witness->floating_point_canonical_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!pass219_audio_security_transport_hash72_valid(witness->binding_hash72))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_admission, 0, sizeof(*out_admission));
    out_admission->struct_size = (uint32_t)sizeof(*out_admission);
    out_admission->version = pass219_audio_security_transport_version_word();
    out_admission->admitted = 1U;
    out_admission->signed_capability_bound = 1U;
    out_admission->raw5184_audio_hydration_bound = 1U;
    out_admission->harmonic_time_audio_ecc_bound = 1U;
    out_admission->internal_pq_oriented_signal_bound = 1U;
    out_admission->receipt_replay_binding_bound = 1U;
    out_admission->auxiliary_persistence_only = 1U;
    out_admission->public_crypto_primitive = 0U;
    out_admission->standardized_pq_crypto_claim = 0U;
    out_admission->independent_key_or_kem_authority = 0U;
    out_admission->canonical_vm81_mutation_authority = 0U;
    out_admission->new_hash72_mint_authority = 0U;
    out_admission->hash216_persistence_authority = 0U;
    out_admission->floating_point_canonical_authority = 0U;
    memcpy(
        out_admission->binding_hash72,
        witness->binding_hash72,
        HHS_EXACT_HASH72_STRLEN
    );
    return HHS_EXACT_STATUS_OK;
}
