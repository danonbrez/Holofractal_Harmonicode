#include "hhs_pass219_inherited_pass218_1_16.hpp"

#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstring>

static void fill_hash72(char out[HHS_EXACT_HASH72_STRLEN], std::size_t alphabet_index) {
    const char symbol = HHS_EXACT_HASH72_ALPHABET[alphabet_index % HHS_EXACT_HASH72_LEN];
    for (std::size_t index = 0; index < HHS_EXACT_HASH72_LEN; ++index)
        out[index] = symbol;
    out[HHS_EXACT_HASH72_LEN] = '\0';
}

static HHSExactPass218CompletionWitnessV1 valid_witness() {
    HHSExactPass218CompletionWitnessV1 witness{};
    witness.struct_size = static_cast<std::uint32_t>(sizeof(witness));
    witness.version = hhs_exact_pass219_inherited_pass218_version();
    witness.manifest_source_count = 7U;
    witness.completed_source_count = 7U;
    witness.terminal_completion_verified = 1U;
    witness.authoritative_manifest_exhausted = 1U;
    witness.final_cursor_exhausted = 1U;

    fill_hash72(witness.i47_receipt_hash72, 0U);
    fill_hash72(witness.i33_advance_receipt_hash72, 1U);
    fill_hash72(witness.i48_receipt_hash72, 2U);
    fill_hash72(witness.completion_proof_hash72, 3U);
    fill_hash72(witness.curriculum_identity_hash72, 4U);
    fill_hash72(witness.final_closure_hash72, 5U);
    std::memcpy(witness.i48_hash216,
                witness.i47_receipt_hash72,
                HHS_EXACT_HASH72_LEN);
    std::memcpy(witness.i48_hash216 + HHS_EXACT_HASH72_LEN,
                witness.i33_advance_receipt_hash72,
                HHS_EXACT_HASH72_LEN);
    std::memcpy(witness.i48_hash216 + (2U * HHS_EXACT_HASH72_LEN),
                witness.i48_receipt_hash72,
                HHS_EXACT_HASH72_LEN);
    witness.i48_hash216[216] = '\0';
    for (std::size_t index = 0; index < HHS_EXACT_PASS219_SHA256_BYTES; ++index) {
        witness.final_cursor_sha256[index] = static_cast<std::uint8_t>(index + 1U);
        witness.i30_generation_sha256[index] = static_cast<std::uint8_t>(index + 33U);
    }
    return witness;
}

int main() {
    const auto witness = valid_witness();
    const hhs::rna::InheritedPass218Completion completion(witness);
    assert(completion.status() == HHS_EXACT_STATUS_OK);
    assert(completion.wired());
    assert(!completion.grants_mutation_authority());
    assert(completion.record().pass_number == 218U);
    return 0;
}
