#include "hhs_gfcc.h"

#include <stdio.h>
#include <string.h>

static int fail(const char *operation, hhs_gfcc_status status) {
    fprintf(stderr, "{\"operation\":\"%s\",\"status\":\"%s\"}\n", operation, hhs_gfcc_status_name(status));
    return 1;
}

int main(void) {
    hhs_gfcc_context ctx;
    hhs_gfcc_config config;
    hhs_gfcc_spec spec;
    hhs_gfcc_parameters parameters;
    hhs_dependency_graph graph;
    hhs_shell_closure closure;
    hhs_vm81_state vm81;
    hhs_hash72_projection hash72;
    hhs_hash216_index hash216;
    hhs_gfcc_validation_report validation;
    hhs_gfcc_status status;

    memset(&config, 0, sizeof(config));
    config.struct_size = (uint32_t)sizeof(config);
    config.abi_version = HHS_GFCC_ABI_VERSION;
    hhs_hash72_compute("HHS_PASS_152_AUTHORITY_ROOT", 27u, &config.authority_root);
    status = hhs_gfcc_context_init(&ctx, &config);
    if (status != HHS_GFCC_OK) return fail("context_init", status);

    memset(&spec, 0, sizeof(spec));
    spec.schema_version = 1u;
    spec.interpretation_version = 1u;
    spec.fibonacci_stage = 8u;
    spec.a2 = 1; spec.b2 = 2; spec.c2 = 3; spec.d2 = 5; spec.e2 = 8;
    status = hhs_gfcc_build_parameters(&ctx, &spec, &parameters);
    if (status != HHS_GFCC_OK) return fail("build_parameters", status);
    status = hhs_gfcc_load_parameters(&ctx, &parameters);
    if (status != HHS_GFCC_OK) return fail("load_parameters", status);

    memset(&graph, 0, sizeof(graph));
    graph.node_count = 7u;
    graph.shell_count = 2u;
    graph.numerator_closed = 1u;
    graph.denominator_closed = 1u;
    status = hhs_gfcc_close_shells(&ctx, &graph, &closure);
    if (status != HHS_GFCC_OK) return fail("close_shells", status);
    status = hhs_gfcc_construct_vm81(&ctx, &parameters, &vm81);
    if (status != HHS_GFCC_OK) return fail("construct_vm81", status);
    status = hhs_gfcc_project_hash72(&ctx, &vm81, &hash72);
    if (status != HHS_GFCC_OK) return fail("project_hash72", status);
    status = hhs_gfcc_index_hash216(&ctx, &vm81, &hash72, &hash216);
    if (status != HHS_GFCC_OK) return fail("index_hash216", status);
    status = hhs_gfcc_validate(&ctx, &validation);
    if (status != HHS_GFCC_OK) return fail("validate", status);

    printf("{\"contract_id\":\"HHS-P152-GFCC\",\"stage_ratio\":{\"numerator\":%lld,\"denominator\":%lld},\"numerator_shell\":%lld,\"denominator_shell\":%lld,\"terminal_residual\":%lld,\"vm81_cells\":%u,\"hash72\":\"%s\",\"hash216\":\"%s\",\"validation\":%u}\n",
        (long long)parameters.golden_stage_ratio.numerator,
        (long long)parameters.golden_stage_ratio.denominator,
        (long long)closure.numerator.closed_value.numerator,
        (long long)closure.denominator.closed_value.numerator,
        (long long)closure.residual.numerator,
        vm81.cell_count,
        hash72.value.value,
        hash216.value.value,
        validation.all_valid);
    return 0;
}
