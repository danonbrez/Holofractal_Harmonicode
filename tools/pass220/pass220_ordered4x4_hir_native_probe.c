/* Scoped native ABI conformance: source identity + deterministic HIR lowering.
 * Does NOT test or claim numerical matrix power, VM81 admission or receipts.
 */
#include "hhs_runtime_exact_abi.h"
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(condition, message) do { \
  if (!(condition)) { fprintf(stderr,"FAIL:%s\n",message); return 1; } \
} while(0)

int main(void) {
    const char *path="contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode";
    FILE *handle=fopen(path,"rb");
    uint8_t source[HHS220_ORDERED4X4_SOURCE_BYTES+1U];
    HHSExactVM81Frame candidate, replay;
    HHS220Ordered4x4HIRWitnessV1 witness, replay_witness, bad_witness;
    size_t bytes;
    HHSExactStatus result;
    CHECK(handle != NULL,"source file open");
    bytes=fread(source,1U,sizeof(source),handle);
    CHECK(ferror(handle)==0,"source read");
    CHECK(fclose(handle)==0,"source close");
    CHECK(bytes==HHS220_ORDERED4X4_SOURCE_BYTES,"source byte width");

    result=hhs_exact_pass220_ordered4x4_lower(source,bytes,&candidate,&witness);
    CHECK(result==HHS_EXACT_STATUS_OK,"source-locked native lowering");
    CHECK(witness.source_identity_verified==1U,"source exact");
    CHECK(witness.ordered_topology_verified==1U,"ordered topology exact");
    CHECK(witness.rows==4U && witness.columns==4U,"4x4 shape");
    CHECK(witness.matrix_occurrences==4U && witness.literal_cells==64U,"64 literal cells");
    CHECK(witness.exponent_negative==1U && witness.exponent_magnitude==4U,"ordered negative exponent");
    CHECK(witness.numerator_negative_operand_count==2U,"two negative numerator operands");
    CHECK(witness.typed_s_unresolved==1U && witness.typed_v_unresolved==1U,"no s/v substitution");
    CHECK(witness.matrix_power_value_derived==0U && witness.native_matrix_division_evaluated==0U,"native operators not falsely evaluated");
    CHECK(witness.vm81_admission_executed==0U,"no VM81 admission");
    CHECK(witness.hash72_commit_authority==0U && witness.hash216_commit_authority==0U,"no receipt authority");
    CHECK(witness.canonical_vm81_mutation_authority==0U,"no mutation authority");
    CHECK(candidate.words[0]==UINT64_C(0x483232304e344d50),"frame identity");
    CHECK(candidate.words[2]==UINT64_C(0x2d34),"exponent token");
    CHECK(candidate.words[4]==UINT64_C(1),"first matrix cell");
    CHECK((candidate.words[8]&UINT64_C(255))==UINT64_C(255),"signed literal retained as token");
    CHECK(candidate.words[67]==(UINT64_C(3)<<16U|UINT64_C(15)<<8U),"last closure cell");
    CHECK(candidate.words[80]==UINT64_C(0x7673),"unresolved s and v");

    result=hhs_exact_pass220_ordered4x4_lower(source,bytes,&replay,&replay_witness);
    CHECK(result==HHS_EXACT_STATUS_OK,"deterministic rebuild accepted");
    CHECK(memcmp(&candidate,&replay,sizeof(candidate))==0,"deterministic frame byte equality");
    CHECK(memcmp(&witness,&replay_witness,sizeof(witness))==0,"deterministic witness byte equality");

    source[0] ^= 1U;
    result=hhs_exact_pass220_ordered4x4_lower(source,bytes,&replay,&bad_witness);
    CHECK(result != HHS_EXACT_STATUS_OK,"source drift rejected");
    CHECK(bad_witness.source_identity_verified==0U,"drift no identity claim");
    CHECK(bad_witness.hash72_commit_authority==0U,"drift no receipt authority");
    CHECK(replay.words[0]==0U,"drift no emitted candidate");
    source[0] ^= 1U;
    result=hhs_exact_pass220_ordered4x4_lower(source,bytes-1U,&replay,&bad_witness);
    CHECK(result != HHS_EXACT_STATUS_OK,"truncated source rejected");
    result=hhs_exact_pass220_ordered4x4_lower(NULL,bytes,&replay,&bad_witness);
    CHECK(result != HHS_EXACT_STATUS_OK,"null source rejected");
    result=hhs_exact_pass220_ordered4x4_lower(source,bytes,NULL,&bad_witness);
    CHECK(result != HHS_EXACT_STATUS_OK,"null frame rejected");

    puts("{\"schema\":\"HHS_PASS220_ORDERED4X4_NATIVE_HIR_PROBE_V1\","
         "\"source_verified\":true,\"ordered_topology_verified\":true,"
         "\"deterministic_frame_rebuild\":true,\"negative_cases_rejected\":true,"
         "\"vm81_admission_executed\":false,\"matrix_value_derived\":false,"
         "\"hash72_commit_authority\":false,\"hash216_commit_authority\":false,"
         "\"canonical_mutation_authority\":false}");
    return 0;
}
