#include "hhs_pass189_hqlh.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

static int require(int condition, const char *message) {
    if (!condition) {
        fprintf(stderr, "FAIL: %s\n", message);
        return 0;
    }
    return 1;
}

int main(void) {
    HHS189ContextAddress address;
    HHS189PartitionResult result;
    uint32_t encoded = 0;
    uint32_t i;
    int ok = 1;

    ok &= require(hhs189_decode_context(0U, &address) == HHS189_OK, "decode zero");
    ok &= require(address.cell81 == 0U && address.operation64 == 0U && address.g243 == 0U && address.local_k == -20, "zero coordinates");
    ok &= require(hhs189_encode_context(&address, &encoded) == HHS189_OK && encoded == 0U, "encode zero");

    ok &= require(hhs189_decode_context(HHS189_CONTEXTUAL_STATES - 1U, &address) == HHS189_OK, "decode max");
    ok &= require(address.cell81 == 80U && address.operation64 == 63U && address.g243 == 242U && address.local_k == 20, "max coordinates");
    ok &= require(hhs189_encode_context(&address, &encoded) == HHS189_OK && encoded == HHS189_CONTEXTUAL_STATES - 1U, "encode max");
    ok &= require(hhs189_decode_context(HHS189_CONTEXTUAL_STATES, &address) == HHS189_ERR_RANGE, "reject overflow");
    ok &= require(hhs189_decode_context(0U, NULL) == HHS189_ERR_NULL, "reject null");

    for (i = 0U; i < 4U; ++i) {
        uint8_t a = (uint8_t)((i >> 1U) & 1U);
        uint8_t b = (uint8_t)(i & 1U);
        uint8_t expected = (uint8_t)(a == b ? 1U : 0U);
        int8_t signed_expected = a == b ? 1 : -1;
        ok &= require(hhs189_xnor_bit(a, b) == expected, "XNOR truth table");
        ok &= require(hhs189_signed_xnor(a, b) == signed_expected, "signed XNOR truth table");
    }

    for (i = 0U; i < 81U; ++i) {
        int k;
        for (k = -20; k <= 20; ++k) {
            uint8_t local;
            uint8_t inverse;
            ok &= require(hhs189_local_cell((uint8_t)i, (int8_t)k, &local) == HHS189_OK, "local cell");
            ok &= require(hhs189_local_cell(local, (int8_t)-k, &inverse) == HHS189_OK && inverse == i, "reciprocal local cell");
        }
    }

    ok &= require(hhs189_ternary_orientation(HHS189_GLOBAL_NUCLEUS, HHS189_GLOBAL_NUCLEUS, 0U, 0U) == 0, "nucleus zero");
    ok &= require(hhs189_ternary_orientation(41U, HHS189_GLOBAL_NUCLEUS, 0U, 0U) == 1, "positive orientation");
    ok &= require(hhs189_ternary_orientation(39U, HHS189_GLOBAL_NUCLEUS, 0U, 0U) == -1, "negative orientation");
    ok &= require(hhs189_ternary_orientation(41U, HHS189_GLOBAL_NUCLEUS, 0U, 1U) == -1, "XNOR phase reversal");

    ok &= require(hhs189_validate_partition(0U, HHS189_CONTEXTUAL_STATES, &result) == HHS189_OK, "full contextual validation");
    ok &= require(result.visited == HHS189_CONTEXTUAL_STATES, "full contextual count");
    ok &= require(result.reciprocal_checks == HHS189_CONTEXTUAL_STATES, "full reciprocal count");
    ok &= require(result.coordinate_drift == 0U, "zero coordinate drift");

    if (!ok) {
        return 1;
    }
    printf("HHS_PASS_189_HQLH_NATIVE_PASS contexts=%" PRIu64 " reciprocal=%" PRIu64 " drift=%" PRIu64 " checksum=%016" PRIx64 "\n",
           result.visited, result.reciprocal_checks, result.coordinate_drift, result.checksum);
    return 0;
}
