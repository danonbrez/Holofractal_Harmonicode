#include "hhs_pass189_hqlh.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void usage(const char *program) {
    fprintf(stderr, "usage: %s decode EXTENDED | validate [START END] | xnor A B | local CELL K\n", program);
}

static int parse_u32(const char *text, uint32_t *out) {
    char *end = NULL;
    unsigned long value = strtoul(text, &end, 10);
    if (end == text || *end != '\0' || value > UINT32_MAX) {
        return 0;
    }
    *out = (uint32_t)value;
    return 1;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        usage(argv[0]);
        return 2;
    }
    if (strcmp(argv[1], "decode") == 0 && argc == 3) {
        HHS189ContextAddress address;
        uint32_t extended;
        if (!parse_u32(argv[2], &extended) || hhs189_decode_context(extended, &address) != HHS189_OK) {
            fprintf(stderr, "invalid extended address\n");
            return 3;
        }
        printf("{\"extended\":%" PRIu32 ",\"projected\":%" PRIu32 ",\"permanent\":%" PRIu32 ",\"cell81\":%u,\"operation64\":%u,\"operationClass8\":%u,\"basis8\":%u,\"g243\":%u,\"kappa41\":%u,\"localK\":%d,\"layer36\":%u,\"q144\":[%u,%u],\"u72\":[%u,%u]}\n",
               address.extended, address.projected, address.permanent, address.cell81, address.operation64,
               address.operation_class8, address.ordered_basis8, address.g243, address.kappa41,
               address.local_k, address.layer36, address.q144_row, address.q144_column,
               address.u72_pair, address.u72_index);
        return 0;
    }
    if (strcmp(argv[1], "validate") == 0 && (argc == 2 || argc == 4)) {
        HHS189PartitionResult result;
        uint32_t start = 0U;
        uint32_t end = HHS189_CONTEXTUAL_STATES;
        if (argc == 4 && (!parse_u32(argv[2], &start) || !parse_u32(argv[3], &end))) {
            fprintf(stderr, "invalid partition\n");
            return 3;
        }
        if (hhs189_validate_partition(start, end, &result) != HHS189_OK) {
            fprintf(stderr, "validation failed\n");
            return 4;
        }
        printf("{\"classification\":\"HHS_PASS_189_HQLH_HYDRATION_VERIFIED\",\"start\":%" PRIu32 ",\"end\":%" PRIu32 ",\"visited\":%" PRIu64 ",\"reciprocalChecks\":%" PRIu64 ",\"coordinateDrift\":%" PRIu64 ",\"checksum\":\"%016" PRIx64 "\"}\n",
               result.start, result.end, result.visited, result.reciprocal_checks, result.coordinate_drift, result.checksum);
        return 0;
    }
    if (strcmp(argv[1], "xnor") == 0 && argc == 4) {
        uint32_t a;
        uint32_t b;
        if (!parse_u32(argv[2], &a) || !parse_u32(argv[3], &b)) {
            return 3;
        }
        printf("{\"a\":%u,\"b\":%u,\"xnor\":%u,\"signed\":%d}\n", (unsigned)(a & 1U), (unsigned)(b & 1U), hhs189_xnor_bit((uint8_t)a, (uint8_t)b), hhs189_signed_xnor((uint8_t)a, (uint8_t)b));
        return 0;
    }
    if (strcmp(argv[1], "local") == 0 && argc == 4) {
        uint32_t cell;
        long k;
        char *end = NULL;
        uint8_t local;
        if (!parse_u32(argv[2], &cell)) {
            return 3;
        }
        k = strtol(argv[3], &end, 10);
        if (end == argv[3] || *end != '\0' || k < -20 || k > 20 || hhs189_local_cell((uint8_t)cell, (int8_t)k, &local) != HHS189_OK) {
            return 3;
        }
        printf("{\"cell81\":%u,\"localK\":%ld,\"resolvedCell81\":%u}\n", (unsigned)cell, k, local);
        return 0;
    }
    usage(argv[0]);
    return 2;
}
