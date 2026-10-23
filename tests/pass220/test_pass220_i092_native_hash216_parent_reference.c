/* Pass 220 I092: actual original C ABI Hash216 indexed reference preflight.
 *
 * Tests I090/I091 candidate triplet through the REAL ORIGINAL:
 * hhs_exact_pass219_vm81_pqc_hash216_reference_init
 * hhs_exact_pass219_vm81_pqc_hash216_reference_verify.
 *
 * The reference proves consistent Hash72 inputs, derived Hash216 index
 * arrays and exact ordered triplet. It does NOT prove the candidate parent
 * was previously committed. No signed mutation or production key is used.
 */
#include "hhs_pass219_vm81_pqc_firewall_1_30.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int fail(const char *message) {
    fprintf(stderr,"I092_%s\n",message);
    return 1;
}
static int valid_input(const char *word) {
    /* Alphabet admission is enforced by the authoritative native
     * reference_init function, not by a copied local table. */
    return word != NULL && strlen(word) == HHS_EXACT_HASH72_LEN;
}
int main(int argc,char **argv) {
    HHSExactPass219Hash216TransitionViewV1 reference;
    HHSExactPass219Hash216TransitionViewV1 genesis;
    HHSExactPass219Hash216TransitionViewV1 swapped;
    char previous[HHS_EXACT_HASH72_STRLEN];
    char change[HHS_EXACT_HASH72_STRLEN];
    char receipt[HHS_EXACT_HASH72_STRLEN];
    char triplet[HHS_EXACT_UQCEL_HASH216_STRLEN];
    int native_valid=0;
    int native_tamper_denied=0;
    int native_swap_changes_identity=0;
    int exact_triplet=0;
    int distinct_native_genesis=0;
    int mode;
    HHSExactStatus status;

    if (argc!=5)
        return fail("USAGE_mode_previous72_change72_receipt72");
    if (!valid_input(argv[2]) || !valid_input(argv[3]) ||
        !valid_input(argv[4]))
        return fail("INVALID_72_GLYPH_SOURCE");
    if (strcmp(argv[1],"verify")==0) mode=0;
    else if (strcmp(argv[1],"tamper-index")==0) mode=1;
    else if (strcmp(argv[1],"reverse-lanes")==0) mode=2;
    else return fail("UNKNOWN_MODE");

    memcpy(previous,argv[2],HHS_EXACT_HASH72_STRLEN);
    memcpy(change,argv[3],HHS_EXACT_HASH72_STRLEN);
    memcpy(receipt,argv[4],HHS_EXACT_HASH72_STRLEN);
    memcpy(triplet,previous,HHS_EXACT_HASH72_LEN);
    memcpy(triplet+HHS_EXACT_HASH72_LEN,change,HHS_EXACT_HASH72_LEN);
    memcpy(triplet+2U*HHS_EXACT_HASH72_LEN,receipt,HHS_EXACT_HASH72_LEN);
    triplet[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN]='\0';
    memset(&reference,0,sizeof(reference));
    status=hhs_exact_pass219_vm81_pqc_hash216_reference_init(
        previous,change,receipt,&reference);
    if (status!=HHS_EXACT_STATUS_OK)
        return fail("ORIGINAL_NATIVE_REFERENCE_INIT_REJECTED");
    native_valid=(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(
        &reference)==HHS_EXACT_STATUS_OK);
    if (!native_valid ||
        reference.resolved_index_count!=HHS_EXACT_PASS219_HASH216_OCCURRENCES)
        return fail("ORIGINAL_NATIVE_INDEXED_REFERENCE_INVALID");
    exact_triplet=(memcmp(reference.transition_word216,triplet,
        HHS_EXACT_UQCEL_HASH216_STRLEN)==0);
    if (!exact_triplet)
        return fail("ORIGINAL_NATIVE_SOURCE_TRIPLET_DRIFT");

    memset(&genesis,0,sizeof(genesis));
    if (hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&genesis)
        !=HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&genesis)
        !=HHS_EXACT_STATUS_OK)
        return fail("ORIGINAL_NATIVE_GENESIS_NOT_VERIFIED");
    distinct_native_genesis=memcmp(
        reference.transition_identity216,genesis.transition_identity216,
        HHS_EXACT_UQCEL_HASH216_STRLEN)!=0;
    if (!distinct_native_genesis)
        return fail("I090_CANDIDATE_MUST_NOT_BE_NATIVE_GENESIS");

    if (mode==1) {
        reference.occurrences[83].sha256_index_record[9]^=UINT8_C(1);
        native_tamper_denied=(
            hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&reference)
            !=HHS_EXACT_STATUS_OK);
        if (!native_tamper_denied)
            return fail("TAMPERED_SHA256_INDEX_ACCEPTED");
    } else if (mode==2) {
        memset(&swapped,0,sizeof(swapped));
        if (hhs_exact_pass219_vm81_pqc_hash216_reference_init(
              change,previous,receipt,&swapped)!=HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&swapped)
              !=HHS_EXACT_STATUS_OK)
            return fail("SWAPPED_VALID_SOURCE_UNVERIFIABLE");
        native_swap_changes_identity=memcmp(
            swapped.transition_identity216,
            reference.transition_identity216,
            HHS_EXACT_UQCEL_HASH216_STRLEN)!=0;
        if (!native_swap_changes_identity)
            return fail("DIRECTIONAL_PARENT_LANE_ALIAS");
    }
    printf(
        "mode=%d original_native_reference_verified=%d "
        "original_native_index_count=%u original_triplet_exact=%d "
        "candidate_distinct_from_native_genesis=%d "
        "tampered_index_rejected=%d reversed_lanes_distinct=%d "
        "canonical_signed_admission_invoked=0 canonical_vm81_mutation=0 "
        "previous_committed_parent_proven=0 "
        "native_parent_identity216=%s "
        "native_source_triplet216=%s\n",
        mode,native_valid,(unsigned)reference.resolved_index_count,
        exact_triplet,distinct_native_genesis,native_tamper_denied,
        native_swap_changes_identity,
        mode==1 ? "" : (mode==2 ? swapped.transition_identity216 :
                            reference.transition_identity216),triplet);
    return 0;
}
