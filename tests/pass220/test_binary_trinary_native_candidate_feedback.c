/* Pass 220 - source-bound native candidate feedback and replay.
 *
 * Feed the exact binary recovered from the Lo Shu/HNAN cross-view into the
 * inherited Pass 219 64-thread VM81 candidate program; replay the result;
 * feed the resulting egress frame to that SAME candidate program and replay.
 *
 * This does NOT bind 648 bytes to the typed SYMBOL_DELTA operand and does not
 * assert canonical monolithic proof or VM81 mutation authority. The native
 * candidate kernel and all source-order semantics are inherited unchanged.
 */
#include "hhs_pass219_exact_vm81_candidate_adapter_1_21_3.h"

#include <stdio.h>
#include <string.h>

static int load_frame(const char *path, HHSExactVM81Frame *frame) {
    FILE *source = fopen(path, "rb");
    if (source == NULL) return 0;
    if (fread(frame, 1U, sizeof(*frame), source) != sizeof(*frame) ||
        fgetc(source) != EOF) {
        fclose(source);
        return 0;
    }
    return fclose(source) == 0;
}

int main(int argc, char **argv) {
    HHSExactPass219VM81ProgramV1 program;
    HHSExactPass219VM81ProgramV1 unchanged;
    HHSExactVM81Frame recovered;
    HHSExactPass219VM81ExecutionV1 initial;
    HHSExactPass219VM81ExecutionV1 feedback;
    HHSExactPass219VM81ReplayV1 replay_initial;
    HHSExactPass219VM81ReplayV1 replay_feedback;
    const HHSExactVM81Frame *second_input;

    if (argc != 2 || !load_frame(argv[1], &recovered)) return 2;
    memset(&program, 0, sizeof(program));
    if (hhs_exact_pass219_vm81_lower_monolithic_structure(&program) !=
        HHS_EXACT_STATUS_OK) return 3;
    unchanged = program;

    if (program.symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_DELTA] !=
        HHS_EXACT_PASS219_VM81_SYMBOL_DELTA ||
        program.source_structure_complete != 1U ||
        program.effectful_lowering_complete != 1U ||
        program.source_semantics_complete != 0U ||
        program.full_symbolic_identity_required != 1U)
        return 4;

    memset(&initial, 0, sizeof(initial));
    if (hhs_exact_pass219_vm81_execute_candidate(&program, &recovered, &initial)
        != HHS_EXACT_STATUS_OK) return 5;
    if (memcmp(&initial.before_frame, &recovered, sizeof(recovered)) != 0 ||
        initial.exact_kernel_execution_observed != 1U ||
        initial.candidate_frame_bound != 1U ||
        initial.canonical_monolithic_proof != 0U ||
        initial.vm81_mutation_authority != 0U ||
        initial.hash72_commit_authority != 0U) return 6;
    memset(&replay_initial, 0, sizeof(replay_initial));
    if (hhs_exact_pass219_vm81_replay_candidate(
        &program, &recovered, &initial, &replay_initial) != HHS_EXACT_STATUS_OK ||
        replay_initial.replay_verified != 1U) return 7;

    second_input = &initial.after_frame;
    memset(&feedback, 0, sizeof(feedback));
    if (hhs_exact_pass219_vm81_execute_candidate(
        &program, second_input, &feedback) != HHS_EXACT_STATUS_OK) return 8;
    if (memcmp(&feedback.before_frame, second_input, sizeof(*second_input)) != 0 ||
        feedback.exact_kernel_execution_observed != 1U ||
        feedback.source_identity_valid != 1U ||
        feedback.canonical_monolithic_proof != 0U ||
        feedback.vm81_mutation_authority != 0U ||
        feedback.hash72_commit_authority != 0U) return 9;
    memset(&replay_feedback, 0, sizeof(replay_feedback));
    if (hhs_exact_pass219_vm81_replay_candidate(
        &program, second_input, &feedback, &replay_feedback) != HHS_EXACT_STATUS_OK ||
        replay_feedback.replay_verified != 1U) return 10;
    if (memcmp(&program, &unchanged, sizeof(program)) != 0) return 11;
    if (memcmp(initial.source_sha256, feedback.source_sha256,
               HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES) != 0) return 12;

    {
        HHSExactPass219VM81ExecutionV1 forged_feedback = feedback;
        HHSExactPass219VM81ReplayV1 negative;
        forged_feedback.after_frame.words[40] ^= UINT64_C(1);
        memset(&negative, 0, sizeof(negative));
        if (hhs_exact_pass219_vm81_replay_candidate(
            &program, second_input, &forged_feedback, &negative) !=
            HHS_EXACT_STATUS_INVARIANT_FAILURE ||
            negative.replay_verified != 0U ||
            negative.frame_equal != 0U) return 13;
    }
    {
        HHSExactPass219VM81ProgramV1 forged_delta_address = program;
        forged_delta_address.symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_DELTA] =
            forged_delta_address.symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_Q];
        HHSExactPass219VM81ExecutionV1 discarded;
        memset(&discarded, 0, sizeof(discarded));
        if (hhs_exact_pass219_vm81_execute_candidate(
            &forged_delta_address, second_input, &discarded) !=
            HHS_EXACT_STATUS_INVARIANT_FAILURE) return 14;
    }
    {
        HHSExactPass219VM81ProgramV1 forged_semantics = program;
        HHSExactPass219VM81ExecutionV1 discarded;
        forged_semantics.source_semantics_complete = 1U;
        memset(&discarded, 0, sizeof(discarded));
        if (hhs_exact_pass219_vm81_execute_candidate(
            &forged_semantics, second_input, &discarded) !=
            HHS_EXACT_STATUS_INVARIANT_FAILURE) return 15;
    }
    /* The canonical adapter's Delta cell is one 64-bit native register;
     * a complete 648-byte egress is NOT silently scalarized into that cell. */
    if (sizeof(recovered) != 648U ||
        sizeof(recovered.words[HHS_EXACT_PASS219_VM81_SYMBOL_DELTA]) != 8U)
        return 16;

    puts("PASS220_SOURCE_BOUND_VM81_CANDIDATE_FRAME_FEEDBACK_REPLAY_PASS");
    puts("SYMBOL_DELTA_TYPED_REINJECTION_NOT_CLAIMED");
    return 0;
}
