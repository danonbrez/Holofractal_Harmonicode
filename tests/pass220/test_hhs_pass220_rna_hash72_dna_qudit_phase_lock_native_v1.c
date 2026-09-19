#include "hhs_pass220_rna_hash72_dna_qudit_phase_lock_1_0.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define REQUIRE(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "requirement failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static int build_state(char out[HHS_EXACT_PASS220_SERIALIZED_CHARACTERS + 1U], unsigned shift) {
    size_t cursor = 0U;
    for (unsigned cell = 0U; cell < HHS_EXACT_PASS220_QUDIT_CELLS; ++cell) {
        char token[HHS_EXACT_PASS220_CELL_TOKEN_CHARACTERS + 1U];
        const unsigned value = (cell + shift) % 9U;
        const int written = snprintf(
            token,
            sizeof(token),
            "+%020llu/%020llue+%020llu",
            (unsigned long long)value,
            (unsigned long long)1U,
            (unsigned long long)0U);
        if (written != (int)HHS_EXACT_PASS220_CELL_TOKEN_CHARACTERS)
            return 0;
        memcpy(out + cursor, token, HHS_EXACT_PASS220_CELL_TOKEN_CHARACTERS);
        cursor += HHS_EXACT_PASS220_CELL_TOKEN_CHARACTERS;
    }
    if (cursor != HHS_EXACT_PASS220_SERIALIZED_CHARACTERS)
        return 0;
    out[cursor] = '\0';
    return 1;
}

int main(void) {
    HHSExactPass220PhaseLockDescriptorV1 descriptor;
    HHSExactPass220PhaseLockWitnessV1 witness;
    HHSExactPass220PhaseLockWitnessV1 changed_witness;
    char state[HHS_EXACT_PASS220_SERIALIZED_CHARACTERS + 1U];
    char changed[HHS_EXACT_PASS220_SERIALIZED_CHARACTERS + 1U];
    char tampered[HHS_EXACT_PASS220_SERIALIZED_CHARACTERS + 1U];

    REQUIRE(build_state(state, 0U));
    REQUIRE(build_state(changed, 1U));

    REQUIRE(hhs_exact_pass220_phase_lock_version() == HHS_EXACT_PASS220_PHASE_LOCK_VERSION);
    REQUIRE(hhs_exact_pass220_phase_lock_descriptor(&descriptor) == HHS_EXACT_STATUS_OK);
    REQUIRE(descriptor.serialized_characters == 5184U);
    REQUIRE(descriptor.hash72_chunks == 72U);
    REQUIRE(descriptor.hash72_chunk_characters == 72U);
    REQUIRE(descriptor.rna_window_characters == 3U);
    REQUIRE(descriptor.rna_windows_per_chunk == 24U);
    REQUIRE(descriptor.rna_windows_total == 1728U);
    REQUIRE(descriptor.qudit_cells == 81U);
    REQUIRE(descriptor.cell_token_characters == 64U);
    REQUIRE(descriptor.h36_cells == 36U);
    REQUIRE(descriptor.h36_magic_line == 111U);
    REQUIRE(descriptor.bidirectional_rna_scan == 1U);
    REQUIRE(descriptor.hash72_chunk_folding == 1U);
    REQUIRE(descriptor.xyzw_digital_dna_bound == 1U);
    REQUIRE(descriptor.vm81_qudit_bound == 1U);
    REQUIRE(descriptor.complete_state_is_operand == 1U);
    REQUIRE(descriptor.floating_point_authority == 0U);

    REQUIRE(hhs_exact_pass220_phase_lock_analyze(
        state, HHS_EXACT_PASS220_SERIALIZED_CHARACTERS, &witness) == HHS_EXACT_STATUS_OK);
    REQUIRE(witness.phase_locked == 1U);
    REQUIRE(witness.forward_characters == 5184U);
    REQUIRE(witness.reverse_characters == 5184U);
    REQUIRE(witness.hash72_chunks == 72U);
    REQUIRE(witness.rna_windows_total == 1728U);
    REQUIRE(witness.qudit_cells == 81U);
    REQUIRE(witness.coordinate_bijection == 1U);
    REQUIRE(witness.double_reverse_exact == 1U);
    REQUIRE(witness.palindromic_precision_exact == 1U);
    REQUIRE(witness.ordered_phase_lock == 1U);
    REQUIRE(witness.serialized_operand_phase_binding == 1U);
    REQUIRE(witness.all_cells_cover_operation64 == 1U);
    REQUIRE(witness.ordered_phase_binding_signature64 != 0U);
    REQUIRE(witness.complete_state_is_operand == 1U);

    static const uint8_t expected_rows[3][3] = {
        {1U, 2U, 3U},
        {2U, 4U, 6U},
        {3U, 6U, 9U},
    };
    static const uint8_t expected_palindromes[3][6] = {
        {1U, 2U, 3U, 3U, 2U, 1U},
        {2U, 4U, 6U, 6U, 4U, 2U},
        {3U, 6U, 9U, 9U, 6U, 3U},
    };
    for (size_t scale = 0U; scale < 3U; ++scale) {
        REQUIRE(memcmp(witness.scale_rows[scale], expected_rows[scale], 3U) == 0);
        REQUIRE(memcmp(witness.palindrome_rows[scale], expected_palindromes[scale], 6U) == 0);
        REQUIRE(witness.precision_remainder_numerator[scale] == 111U * (scale + 1U));
        REQUIRE(witness.precision_remainder_denominator[scale] == 1000U);
        REQUIRE(witness.scaled_palindrome_signature64[scale] != 0U);
    }
    REQUIRE(witness.q_minus_one_phase[0] == 1);
    REQUIRE(witness.q_minus_one_phase[1] == -1);
    REQUIRE(witness.q_minus_one_phase[2] == 1);
    REQUIRE(witness.q_minus_one_phase[3] == -1);
    for (size_t phase = 0U; phase < 4U; ++phase)
        REQUIRE(witness.q_minus_one_pair_counts[phase] == 324U);

    REQUIRE(witness.canonical_vm81_mutation_authority == 0U);
    REQUIRE(witness.canonical_hash72_authority == 0U);
    REQUIRE(witness.canonical_hash216_authority == 0U);
    REQUIRE(witness.canonical_persistence_authority == 0U);
    REQUIRE(witness.floating_point_authority == 0U);

    REQUIRE(hhs_exact_pass220_phase_lock_analyze(
        changed, HHS_EXACT_PASS220_SERIALIZED_CHARACTERS, &changed_witness) == HHS_EXACT_STATUS_OK);
    REQUIRE(changed_witness.state_offset_signature64 != witness.state_offset_signature64);
    REQUIRE(changed_witness.ordered_phase_binding_signature64 !=
            witness.ordered_phase_binding_signature64);
    REQUIRE(memcmp(
        changed_witness.scaled_palindrome_signature64,
        witness.scaled_palindrome_signature64,
        sizeof(witness.scaled_palindrome_signature64)) != 0);

    REQUIRE(hhs_exact_pass220_phase_lock_analyze(
        state, HHS_EXACT_PASS220_SERIALIZED_CHARACTERS - 1U, &witness) ==
        HHS_EXACT_STATUS_RANGE_ERROR);

    memcpy(tampered, state, sizeof(state));
    tampered[21] = 'x';
    REQUIRE(hhs_exact_pass220_phase_lock_analyze(
        tampered, HHS_EXACT_PASS220_SERIALIZED_CHARACTERS, &witness) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE);

    memcpy(tampered, state, sizeof(state));
    tampered[20] = '9';
    REQUIRE(hhs_exact_pass220_phase_lock_analyze(
        tampered, HHS_EXACT_PASS220_SERIALIZED_CHARACTERS, &witness) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE);

    puts("PASS220_I019_NATIVE_PHASE_LOCK_OK");
    return 0;
}
