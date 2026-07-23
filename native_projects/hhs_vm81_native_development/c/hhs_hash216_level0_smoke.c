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
    HHSHash216 first;
    HHSHash216 replay;
    HHSHash216 different;
    HHSHash216 reciprocal;
    HHSHash216 restored;

    hhs_hash216_clear(&first);
    hhs_hash216_clear(&replay);
    hhs_hash216_clear(&different);
    hhs_hash216_clear(&reciprocal);
    hhs_hash216_clear(&restored);

    hhs_hash216_compute(payload_a, sizeof(payload_a), &first);
    hhs_hash216_compute(payload_a, sizeof(payload_a), &replay);
    hhs_hash216_compute(payload_b, sizeof(payload_b), &different);

    if (strlen(first.value) != HHS_HASH216_LEN) {
        return reject("Hash216 length is not exactly 216 positions");
    }
    if (!hhs_hash216_equal(&first, &replay)) {
        return reject("Hash216 replay mismatch");
    }
    if (hhs_hash216_equal(&first, &different)) {
        return reject("distinct payloads collapsed to the same Hash216 value in the smoke vector");
    }

    hhs_hash216_reciprocal(&first, &reciprocal);
    hhs_hash216_reciprocal(&reciprocal, &restored);
    if (!hhs_hash216_equal(&first, &restored)) {
        return reject("Hash216 reciprocal roundtrip failed");
    }

    puts("HASH216_IDENTITY_FOUNDATION_SMOKE_PASSED");
    return 0;
}
