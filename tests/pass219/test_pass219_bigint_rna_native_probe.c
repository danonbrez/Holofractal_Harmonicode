#include "hhs_pass219_rna_vm5184_abi_1_33.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int fail(const char *message) {
    fprintf(stderr, "%s\n", message);
    return 1;
}

int main(int argc, char **argv) {
    FILE *stream;
    uint8_t raw[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t raw_before[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t exported[HHS_EXACT_VM81_FRAME_BYTES];
    HHSExactVM81Frame frame;
    HHSExactPass219Hash216TransitionViewV1 transition;
    HHSExactUQCELInputV1 input;
    HHSExactPass219Holo4PreparedV1 prepared;
    HHSExactPass219Holo4DecisionV1 decision;
    size_t count;
    size_t written = 0U;
    uint8_t one = 1U;
    int trailing;
    int identity_preserved;
    int authority_closed;

    if (argc != 2)
        return fail("USAGE:test_pass219_bigint_rna_native_probe <raw648>");

    stream = fopen(argv[1], "rb");
    if (stream == NULL)
        return fail("RAW_FRAME_OPEN_FAILED");
    count = fread(raw, 1U, sizeof(raw), stream);
    trailing = fgetc(stream);
    fclose(stream);
    if (count != sizeof(raw) || trailing != EOF)
        return fail("RAW_FRAME_MUST_BE_EXACTLY_648_BYTES");

    memcpy(raw_before, raw, sizeof(raw));
    memset(&frame, 0, sizeof(frame));
    if (hhs_exact_vm81_frame_import_le(raw, sizeof(raw), &frame) != HHS_EXACT_STATUS_OK)
        return fail("VM81_IMPORT_FAILED");
    memset(exported, 0, sizeof(exported));
    if (hhs_exact_vm81_frame_export_le(&frame, exported, sizeof(exported), &written) != HHS_EXACT_STATUS_OK)
        return fail("VM81_EXPORT_FAILED");
    if (written != sizeof(exported))
        return fail("VM81_EXPORT_LENGTH_MISMATCH");

    memset(&transition, 0, sizeof(transition));
    if (hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&transition) != HHS_EXACT_STATUS_OK)
        return fail("GENESIS_HASH216_REFERENCE_FAILED");
    if (hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&transition) != HHS_EXACT_STATUS_OK)
        return fail("GENESIS_HASH216_REFERENCE_VERIFY_FAILED");

    memset(&input, 0, sizeof(input));
    input.struct_size = (uint32_t)sizeof(input);
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.delta.struct_size = (uint32_t)sizeof(input.delta);
    input.delta.byte_length = 1U;
    input.delta.bytes_be = &one;

    memset(&prepared, 0, sizeof(prepared));
    memset(&decision, 0, sizeof(decision));
    if (hhs_exact_pass219_rna_raw5184_route(
            &input,
            raw,
            sizeof(raw),
            &transition,
            HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
            0,
            &prepared,
            &decision) != HHS_EXACT_STATUS_OK)
        return fail("RNA_VM5184_ROUTE_FAILED");

    identity_preserved =
        memcmp(prepared.source_transition_identity216,
               transition.transition_identity216,
               HHS_EXACT_UQCEL_HASH216_STRLEN) == 0 &&
        memcmp(decision.source_transition_identity216,
               transition.transition_identity216,
               HHS_EXACT_UQCEL_HASH216_STRLEN) == 0;

    authority_closed =
        prepared.candidate_only == 1U &&
        prepared.exact_integer_only == 1U &&
        prepared.canonical_mutation_authority == 0U &&
        prepared.canonical_hash72_authority == 0U &&
        prepared.canonical_hash216_authority == 0U &&
        prepared.canonical_persistence_authority == 0U &&
        prepared.floating_point_authority == 0U &&
        decision.candidate_only == 1U &&
        decision.exact_integer_only == 1U &&
        decision.canonical_mutation_authority == 0U &&
        decision.canonical_hash72_authority == 0U &&
        decision.canonical_hash216_authority == 0U &&
        decision.canonical_persistence_authority == 0U &&
        decision.floating_point_authority == 0U;

    printf(
        "status=0 selected_lane=%u graph_signature64=%llu tensor_signature64=%llu "
        "decision_signature64=%llu raw_unchanged=%u import_export_exact=%u "
        "hash216_reference_verified=1 transition_identity_preserved=%u "
        "authority_closed=%u word_visits=%u graph_edge_visits=%u\n",
        (unsigned)decision.selected_lane,
        (unsigned long long)prepared.graph_signature64,
        (unsigned long long)prepared.tensor_signature64,
        (unsigned long long)decision.decision_signature64,
        (unsigned)(memcmp(raw_before, raw, sizeof(raw)) == 0),
        (unsigned)(memcmp(raw_before, exported, sizeof(raw_before)) == 0),
        (unsigned)identity_preserved,
        (unsigned)authority_closed,
        (unsigned)prepared.word_visits,
        (unsigned)prepared.graph_edge_visits);

    return 0;
}
