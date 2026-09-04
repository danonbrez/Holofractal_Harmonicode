#include "hhs_runtime_abi.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

static const char HHS219_I163_RING_ALPHABET[73] =
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";

int hhs219_i163_hash72_ring_reverse_witness(const char receipt_hash72[73]) {
    HHSHash72RingState prior;
    HHSHash72RingState current;
    HHSHash72RingState restored;
    size_t i;

    if (receipt_hash72 == NULL || receipt_hash72[72] != '\0')
        return 0;

    hhs_hash72_ring_init(&prior);
    current = prior;
    for (i = 0U; i < 72U; ++i) {
        const char *symbol = strchr(HHS219_I163_RING_ALPHABET, receipt_hash72[i]);
        int64_t delta;
        if (symbol == NULL)
            return 0;
        delta = (int64_t)(symbol - HHS219_I163_RING_ALPHABET);
        if (!hhs_hash72_ring_rotate(&current, (uint8_t)i, delta))
            return 0;
    }

    if (!hhs_hash72_dna_validate(&current) ||
        !hhs_hash72_reverse_state(&current, &restored) ||
        !hhs_hash72_dna_validate(&restored))
        return 0;

    return memcmp(prior.positions, restored.positions, sizeof(prior.positions)) == 0 &&
           memcmp(prior.dna, restored.dna, sizeof(prior.dna)) == 0;
}
