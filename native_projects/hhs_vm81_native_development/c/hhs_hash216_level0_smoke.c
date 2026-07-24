#include "hhs_hash216.h"

#include <stdio.h>
#include <string.h>

static int reject(const char* message) {
    fprintf(stderr, "%s\n", message);
    return 1;
}

int main(void) {
    static const unsigned char payload_a[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    static const unsigned char payload_b[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 10};
    HHSHash72 hash72_first;
    HHSHash72 hash72_replay;
    HHSHash72 hash72_reciprocal;
    HHSHash72 hash72_restored;
    HHSHash216 hash216_first;
    HHSHash216 hash216_replay;
    HHSHash216 hash216_different;
    HHSHash216 hash216_reciprocal;
    HHSHash216 hash216_restored;

    hhs_hash72_clear(&hash72_first);
    hhs_hash72_clear(&hash72_replay);
    hhs_hash72_clear(&hash72_reciprocal);
    hhs_hash72_clear(&hash72_restored);
    hhs_hash216_clear(&hash216_first);
    hhs_hash216_clear(&hash216_replay);
    hhs_hash216_clear(&hash216_different);
    hhs_hash216_clear(&hash216_reciprocal);
    hhs_hash216_clear(&hash216_restored);

    if (hash72_first.value[0] != '\0' || hash216_first.value[0] != '\0') {
        return reject("clear did not zero the caller-owned hash output");
    }

    hhs_hash72_compute(payload_a, sizeof(payload_a), &hash72_first);
    hhs_hash72_compute(payload_a, sizeof(payload_a), &hash72_replay);
    if (strlen(hash72_first.value) != HHS_HASH72_LEN) {
        return reject("Hash72 length is not exactly 72 positions");
    }
    if (!hhs_hash72_equal(&hash72_first, &hash72_replay)) {
        return reject("Hash72 replay mismatch");
    }
    hhs_hash72_reciprocal(&hash72_first, &hash72_reciprocal);
    hhs_hash72_reciprocal(&hash72_reciprocal, &hash72_restored);
    if (!hhs_hash72_equal(&hash72_first, &hash72_restored)) {
        return reject("Hash72 reciprocal roundtrip failed");
    }

    hhs_hash216_compute(payload_a, sizeof(payload_a), &hash216_first);
    hhs_hash216_compute(payload_a, sizeof(payload_a), &hash216_replay);
    hhs_hash216_compute(payload_b, sizeof(payload_b), &hash216_different);

    if (strlen(hash216_first.value) != HHS_HASH216_LEN) {
        return reject("Hash216 length is not exactly 216 positions");
    }
    if (!hhs_hash216_equal(&hash216_first, &hash216_replay)) {
        return reject("Hash216 replay mismatch");
    }
    if (hhs_hash216_equal(&hash216_first, &hash216_different)) {
        return reject("distinct payloads collapsed to the same Hash216 value in the smoke vector");
    }

    hhs_hash216_reciprocal(&hash216_first, &hash216_reciprocal);
    hhs_hash216_reciprocal(&hash216_reciprocal, &hash216_restored);
    if (!hhs_hash216_equal(&hash216_first, &hash216_restored)) {
        return reject("Hash216 reciprocal roundtrip failed");
    }

    puts("HASH72_HASH216_COMPLETE_LINKED_ABI_SMOKE_PASSED");
    return 0;
}
