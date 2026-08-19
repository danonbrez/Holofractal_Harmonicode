#include "hhs_pass219_inherited_pass218_1_16.h"

#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static void fill_hash72(char out[HHS_EXACT_HASH72_STRLEN], size_t alphabet_index) {
    size_t index;
    const char symbol = HHS_EXACT_HASH72_ALPHABET[alphabet_index % HHS_EXACT_HASH72_LEN];
    for (index = 0U; index < HHS_EXACT_HASH72_LEN; ++index)
        out[index] = symbol;
    out[HHS_EXACT_HASH72_LEN] = '\0';
}

static HHSExactPass218CompletionWitnessV1 valid_witness(void) {
    HHSExactPass218CompletionWitnessV1 witness;
    size_t index;
    memset(&witness, 0, sizeof(witness));
    witness.struct_size = (uint32_t)sizeof(witness);
    witness.version = hhs_exact_pass219_inherited_pass218_version();
    witness.manifest_source_count = 7U;
    witness.completed_source_count = 7U;
    witness.terminal_completion_verified = 1U;
    witness.authoritative_manifest_exhausted = 1U;
    witness.final_cursor_exhausted = 1U;
    witness.pass219_handoff_authority_minted = 0U;
    witness.vm81_authorization_invoked = 0U;

    fill_hash72(witness.i47_receipt_hash72, 0U);
    fill_hash72(witness.i33_advance_receipt_hash72, 1U);
    fill_hash72(witness.i48_receipt_hash72, 2U);
    fill_hash72(witness.completion_proof_hash72, 3U);
    fill_hash72(witness.curriculum_identity_hash72, 4U);
    fill_hash72(witness.final_closure_hash72, 5U);
    memcpy(witness.i48_hash216,
           witness.i47_receipt_hash72,
           HHS_EXACT_HASH72_LEN);
    memcpy(witness.i48_hash216 + HHS_EXACT_HASH72_LEN,
           witness.i33_advance_receipt_hash72,
           HHS_EXACT_HASH72_LEN);
    memcpy(witness.i48_hash216 + (2U * HHS_EXACT_HASH72_LEN),
           witness.i48_receipt_hash72,
           HHS_EXACT_HASH72_LEN);
    witness.i48_hash216[216] = '\0';
    for (index = 0U; index < HHS_EXACT_PASS219_SHA256_BYTES; ++index) {
        witness.final_cursor_sha256[index] = (uint8_t)(index + 1U);
        witness.i30_generation_sha256[index] = (uint8_t)(index + 33U);
    }
    return witness;
}

int main(void) {
    HHSExactPass218CompletionWitnessV1 witness = valid_witness();
    HHSExactPass219InheritedPass218BindingV1 binding;
    HHSExactStatus status;

    memset(&binding, 0, sizeof(binding));
    status = hhs_exact_pass219_bind_pass218_completion(&witness, &binding);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(binding.pass_number == 218U);
    assert(binding.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(binding.completion_seal_bound == 1U);
    assert(binding.receipt_semantics_preserved == 1U);
    assert(binding.continuation_identity_exposed == 1U);
    assert(binding.canonical_execution_reachable == 1U);
    assert(binding.cxx_mutation_authority == 0U);
    assert(binding.vm81_mutation_authority == 0U);
    assert(binding.pass219_handoff_authority_minted == 0U);
    assert(strcmp(binding.i48_receipt_hash72, witness.i48_receipt_hash72) == 0);
    assert(strcmp(binding.i48_hash216, witness.i48_hash216) == 0);

    witness.completed_source_count = 6U;
    assert(hhs_exact_pass219_bind_pass218_completion(&witness, &binding) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    witness = valid_witness();
    witness.i48_hash216[HHS_EXACT_HASH72_LEN] = witness.i48_hash216[0];
    assert(hhs_exact_pass219_bind_pass218_completion(&witness, &binding) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    witness = valid_witness();
    witness.pass219_handoff_authority_minted = 1U;
    assert(hhs_exact_pass219_bind_pass218_completion(&witness, &binding) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    return 0;
}
