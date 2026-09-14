#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <string.h>

static HHSExactPass219AudioSecurityTransportWitnessV1 valid_witness(void) {
    HHSExactPass219AudioSecurityTransportWitnessV1 witness;
    memset(&witness, 0, sizeof(witness));
    witness.struct_size = (uint32_t)sizeof(witness);
    witness.version = hhs_exact_pass219_audio_security_transport_version();
    witness.signed_capability_verified = 1U;
    witness.capability_scope_bound = 1U;
    witness.raw5184_audio_hydration_bound = 1U;
    witness.harmonic_time_audio_ecc_required = 1U;
    witness.harmonic_time_audio_ecc_valid = 1U;
    witness.internal_pq_oriented_signal_required = 1U;
    witness.internal_pq_oriented_signal_valid = 1U;
    witness.receipt_replay_binding_required = 1U;
    witness.auxiliary_persistence_only = 1U;
    memcpy(witness.binding_hash72, HHS_EXACT_HASH72_ALPHABET, HHS_EXACT_HASH72_LEN);
    witness.binding_hash72[HHS_EXACT_HASH72_LEN] = '\0';
    return witness;
}

int main(void) {
    HHSExactPass219AudioSecurityTransportWitnessV1 witness = valid_witness();
    HHSExactPass219AudioSecurityTransportAdmissionV1 admission;
    HHSExactStatus status;

    assert(hhs_exact_pass219_audio_security_transport_version() == (1U << 16));
    memset(&admission, 0, sizeof(admission));
    status = hhs_exact_pass219_audio_security_transport_admit(&witness, &admission);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(admission.admitted == 1U);
    assert(admission.signed_capability_bound == 1U);
    assert(admission.raw5184_audio_hydration_bound == 1U);
    assert(admission.harmonic_time_audio_ecc_bound == 1U);
    assert(admission.internal_pq_oriented_signal_bound == 1U);
    assert(admission.receipt_replay_binding_bound == 1U);
    assert(admission.auxiliary_persistence_only == 1U);
    assert(admission.public_crypto_primitive == 0U);
    assert(admission.standardized_pq_crypto_claim == 0U);
    assert(admission.independent_key_or_kem_authority == 0U);
    assert(admission.canonical_vm81_mutation_authority == 0U);
    assert(admission.new_hash72_mint_authority == 0U);
    assert(admission.hash216_persistence_authority == 0U);
    assert(admission.floating_point_canonical_authority == 0U);
    assert(strcmp(admission.binding_hash72, witness.binding_hash72) == 0);

    witness = valid_witness();
    witness.harmonic_time_audio_ecc_valid = 0U;
    assert(hhs_exact_pass219_audio_security_transport_admit(&witness, &admission) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    witness = valid_witness();
    witness.public_crypto_primitive = 1U;
    assert(hhs_exact_pass219_audio_security_transport_admit(&witness, &admission) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    witness = valid_witness();
    witness.binding_hash72[0] = '\n';
    assert(hhs_exact_pass219_audio_security_transport_admit(&witness, &admission) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    return 0;
}
