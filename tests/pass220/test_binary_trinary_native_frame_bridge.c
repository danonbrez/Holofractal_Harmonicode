/* Pass 220: recovered trinary-lift egress bytes enter the inherited native
 * 648-byte VM81 frame, then existing RNA candidate reconstruction, rollback,
 * and composed admission. This does not equate the frame to symbolic UCE Delta.
 * The Pass 219 fixture is included only to reuse its frozen witness builders,
 * index resolver and exact parameter profile without altering the original.
 */
#define main hhs_pass219_inherited_conformance_main
#include "../pass219/test_pass219_rna_admission_lowering_1_12.c"
#undef main

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    HHSExactPass219TranscriptionWitnessV1 witness;
    HHSExactUQCELInputV1 input;
    HHSExactVM81Frame predecessor;
    HHSExactVM81Frame recovered_egress;
    HHSExactVM81Frame reconstructed;
    HHSExactVM81Frame rolled_back;
    HHSExactVM81Frame committed;
    HHSExactPass219RNAAdmissionCandidateV1 candidate;
    HHSExactPass219RNAAdmissionLoweringV1 lowering;
    ResolverContext resolver = {0U};
    uint8_t frontier[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES];
    FILE *in;
    size_t i;

    if (argc != 2)
        return 2;
    in = fopen(argv[1], "rb");
    if (in == NULL)
        return 3;
    if (fread(&recovered_egress, 1, sizeof(recovered_egress), in) !=
        sizeof(recovered_egress) || fgetc(in) != EOF) {
        fclose(in);
        return 4;
    }
    if (fclose(in) != 0)
        return 5;

    witness = make_witness();
    input = make_input();
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        predecessor.words[i] = UINT64_C(0xA5A5A5A500000000) ^ (uint64_t)i;
    for (i = 0U; i < sizeof(frontier); ++i)
        frontier[i] = (uint8_t)(i * 7U + 3U);

    assert(hhs_exact_pass219_rna_admission_candidate_from_witness(
        &witness, &predecessor, &recovered_egress, frontier, &candidate)
        == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_candidate_reconstruct(
        &candidate, &reconstructed) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&reconstructed, &recovered_egress, sizeof(recovered_egress)) == 0);
    assert(hhs_exact_pass219_rna_candidate_rollback(
        &candidate, &rolled_back) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&rolled_back, &predecessor, sizeof(predecessor)) == 0);
    assert(hhs_exact_pass219_rna_lower_to_vm81(
        &candidate, &input, test_index_resolver, &resolver,
        &committed, &lowering) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&committed, &recovered_egress, sizeof(recovered_egress)) == 0);
    assert(lowering.authority_invoked == 1U);
    assert(lowering.frame_committed == 1U);
    assert(lowering.rollback_verified == 1U);
    assert(resolver.calls == HHS_EXACT_PASS219_HASH216_OCCURRENCES);
    /* Preserve the canonical constraints and source lineage unchanged. */
    assert(memcmp(lowering.admission.transition.previous_hash72,
                  input.previous_hash72, HHS_EXACT_HASH72_STRLEN) == 0);
    puts("PASS220_NATIVE_LIFTED_EGRESS_FRAME_RECONSTRUCTION_ROLLBACK_ADMISSION_PASS");
    return 0;
}
