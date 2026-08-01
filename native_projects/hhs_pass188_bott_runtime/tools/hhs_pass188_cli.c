#include "hhs_pass188_bott_runtime.h"

#include <errno.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int parse_u32(const char *text, uint32_t *out) {
    char *end = NULL;
    unsigned long value;
    errno = 0;
    value = strtoul(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0' || value > UINT32_MAX) {
        return 0;
    }
    *out = (uint32_t)value;
    return 1;
}

static void print_transition(const HHS188Transition *t) {
    printf("{\n");
    printf("  \"classification\": \"%s\",\n", hhs188_classification_name(t->classification));
    printf("  \"input_projected_address\": %" PRIu32 ",\n", t->input.projected_address);
    printf("  \"output_projected_address\": %" PRIu32 ",\n", t->output.projected_address);
    printf("  \"g243\": %u,\n", (unsigned)t->input.g243);
    printf("  \"vm81_cell\": %u,\n", (unsigned)t->input.vm81_cell);
    printf("  \"operation_class8\": %u,\n", (unsigned)t->input.operation_class8);
    printf("  \"ordered_input_tag\": \"%s\",\n", t->ordered_input_tag);
    printf("  \"ordered_output_tag\": \"%s\",\n", t->ordered_output_tag);
    printf("  \"q144\": {\"row\": %u, \"column\": %u},\n",
           (unsigned)t->input.row12, (unsigned)t->input.column12);
    printf("  \"u72\": {\"pair\": %u, \"index\": %u},\n",
           (unsigned)t->input.pair72, (unsigned)t->input.index72);
    printf("  \"factorial_admitted\": %s,\n", t->input.factorial_admitted ? "true" : "false");
    printf("  \"closure_q144\": %s\n", t->input.closure_q144 ? "true" : "false");
    printf("}\n");
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s step <0..7> | transition <0..1259711> | hydrate\n", argv[0]);
        return 2;
    }
    if (strcmp(argv[1], "step") == 0) {
        uint32_t basis;
        if (argc != 3 || !parse_u32(argv[2], &basis) || basis > 7U) {
            fprintf(stderr, "invalid basis\n");
            return 2;
        }
        printf("%u\n", (unsigned)hhs188_bott_step((uint8_t)basis));
        return 0;
    }
    if (strcmp(argv[1], "transition") == 0) {
        uint32_t projected;
        HHS188Transition transition;
        HHS188Status status;
        if (argc != 3 || !parse_u32(argv[2], &projected)) {
            fprintf(stderr, "invalid projected address\n");
            return 2;
        }
        status = hhs188_transition_projected(projected, &transition);
        if (status != HHS188_STATUS_OK) {
            fprintf(stderr, "%s\n", hhs188_status_name(status));
            return 3;
        }
        print_transition(&transition);
        return 0;
    }
    if (strcmp(argv[1], "hydrate") == 0) {
        HHS188HydrationSummary summary;
        HHS188Status status = hhs188_hydrate(&summary);
        if (status != HHS188_STATUS_OK) {
            fprintf(stderr, "%s\n", hhs188_status_name(status));
            return 3;
        }
        printf("{\"classification\":\"HHS_PASS_188_FULL_HYDRATION_VERIFIED\","
               "\"hydrated_states\":%" PRIu64 ","
               "\"active_period_two_states\":%" PRIu64 ","
               "\"asymmetric_collapse_states\":%" PRIu64 ","
               "\"gear_preserved_states\":%" PRIu64 ","
               "\"coordinate_drift_states\":%" PRIu64 ","
               "\"deterministic_checksum_u64\":\"%016" PRIx64 "\"}\n",
               summary.hydrated_states,
               summary.active_period_two_states,
               summary.asymmetric_collapse_states,
               summary.gear_preserved_states,
               summary.coordinate_drift_states,
               summary.deterministic_checksum);
        return 0;
    }
    fprintf(stderr, "unknown command\n");
    return 2;
}
