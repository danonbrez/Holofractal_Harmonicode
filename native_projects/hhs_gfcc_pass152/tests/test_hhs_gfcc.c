#include "hhs_gfcc.h"

#include <stdio.h>
#include <string.h>

#define REQUIRE(condition, message) do { if (!(condition)) { fprintf(stderr, "%s\n", message); return 1; } } while (0)

static hhs_collision_pair make_pair(const hhs_gfcc_parameters *parameters, const hhs_hash72_projection *hash72, const hhs_hash216_index *hash216) {
    hhs_collision_pair pair;
    memset(&pair, 0, sizeof(pair));
    pair.a.object_id = 1u;
    pair.a.x_q16 = 0;
    pair.a.y_q16 = 0;
    pair.a.half_width_q16 = HHS_GFCC_Q16_ONE;
    pair.a.half_height_q16 = HHS_GFCC_Q16_ONE;
    pair.a.scale = parameters->golden_stage_ratio;
    pair.a.phase = 6u;
    pair.a.vm81_cell = 40u;
    pair.a.hash72 = hash72->value;
    pair.a.hash216 = hash216->value;
    pair.b = pair.a;
    pair.b.object_id = 2u;
    pair.b.x_q16 = HHS_GFCC_Q16_ONE + HHS_GFCC_Q16_ONE / 2;
    pair.b.phase = 9u;
    pair.b.vm81_cell = 41u;
    return pair;
}

int main(void) {
    hhs_gfcc_config config;
    hhs_gfcc_context ctx;
    hhs_gfcc_context replay_ctx;
    hhs_gfcc_spec spec;
    hhs_gfcc_spec invalid_spec;
    hhs_gfcc_parameters parameters;
    hhs_gfcc_parameters replay_parameters;
    hhs_gfcc_parameters rejected_parameters;
    hhs_dependency_graph graph;
    hhs_dependency_graph unresolved_graph;
    hhs_shell_closure closure;
    hhs_vm81_state vm81_a;
    hhs_vm81_state vm81_b;
    hhs_hash72_projection hash72_a;
    hhs_hash72_projection hash72_b;
    hhs_hash216_index hash216_a;
    hhs_hash216_index hash216_b;
    hhs_transform_request transform_request;
    hhs_transform_result transform_result;
    hhs_collision_pair pair;
    hhs_collision_pair phase_pair;
    hhs_collision_constraint constraint;
    hhs_collision_constraint phase_constraint;
    hhs_collision_result collision_result;
    hhs_gfcc_step_input step_input;
    hhs_gfcc_step_result step_result;
    hhs_gfcc_validation_report validation;
    hhs_gfcc_receipt_chain chain;
    hhs_gfcc_replay_report replay;
    hhs_gfcc_status status;
    uint32_t index;

    memset(&config, 0, sizeof(config));
    config.struct_size = (uint32_t)sizeof(config);
    config.abi_version = HHS_GFCC_ABI_VERSION;
    hhs_hash72_compute("HHS_PASS_152_AUTHORITY_ROOT", 27u, &config.authority_root);
    REQUIRE(hhs_gfcc_context_init(&ctx, &config) == HHS_GFCC_OK, "context init failed");

    memset(&spec, 0, sizeof(spec));
    spec.schema_version = 1u;
    spec.interpretation_version = 1u;
    spec.fibonacci_stage = 8u;
    spec.a2 = 1; spec.b2 = 2; spec.c2 = 3; spec.d2 = 5; spec.e2 = 8;
    REQUIRE(hhs_gfcc_build_parameters(&ctx, &spec, &parameters) == HHS_GFCC_OK, "parameter construction failed");
    REQUIRE(parameters.a2.numerator == 1 && parameters.b2.numerator == 2 && parameters.c2.numerator == 3 && parameters.d2.numerator == 5 && parameters.e2.numerator == 8, "square states invalid");
    REQUIRE(parameters.numerator_shell.closed_value.numerator == 8, "numerator shell did not close to 8");
    REQUIRE(parameters.denominator_shell.closed_value.numerator == 4, "denominator shell did not close to 4");
    REQUIRE(parameters.terminal_residual.numerator == 0, "terminal residual did not close to zero");
    REQUIRE(parameters.golden_stage_ratio.numerator == 34 && parameters.golden_stage_ratio.denominator == 21, "finite Fibonacci ratio is incorrect");
    REQUIRE(parameters.delta369.ring_modulus == 9u && parameters.delta369.coordinate_dimensions == 4u, "delta369 collapsed");
    REQUIRE(hhs_gfcc_load_parameters(&ctx, &parameters) == HHS_GFCC_OK, "parameter load failed");

    memset(&graph, 0, sizeof(graph));
    graph.node_count = 7u; graph.shell_count = 2u; graph.numerator_closed = 1u; graph.denominator_closed = 1u;
    REQUIRE(hhs_gfcc_close_shells(&ctx, &graph, &closure) == HHS_GFCC_OK, "shell closure failed");
    REQUIRE(closure.ancestry_preserved == 1u && closure.quotient.numerator == 2 && closure.residual.numerator == 0, "shell ancestry or projection failed");

    REQUIRE(hhs_gfcc_construct_vm81(&ctx, &parameters, &vm81_a) == HHS_GFCC_OK, "VM81 construction failed");
    REQUIRE(hhs_gfcc_construct_vm81(&ctx, &parameters, &vm81_b) == HHS_GFCC_OK, "VM81 replay construction failed");
    REQUIRE(vm81_a.cell_count == 81u && hhs_hash72_equal(&vm81_a.state_hash72, &vm81_b.state_hash72), "VM81 replay mismatch");
    for (index = 0u; index < 81u; ++index) {
        uint32_t row;
        uint32_t column;
        REQUIRE(hhs_gfcc_vm81_inverse(index, &row, &column) == HHS_GFCC_OK, "VM81 inverse failed");
        REQUIRE(hhs_gfcc_vm81_index(row, column) == index, "VM81 map is not reversible");
        REQUIRE(vm81_a.cells[index].cell_index == index, "VM81 duplicate or missing cell assignment");
    }
    REQUIRE(hhs_gfcc_vm81_index(9u, 0u) == 81u, "invalid VM81 row accepted");
    REQUIRE(hhs_gfcc_vm81_inverse(81u, &index, &index) == HHS_GFCC_VM81_MAP_ERROR, "invalid VM81 cell index accepted");

    REQUIRE(hhs_gfcc_project_hash72(&ctx, &vm81_a, &hash72_a) == HHS_GFCC_OK, "Hash72 projection failed");
    REQUIRE(hhs_gfcc_project_hash72(&ctx, &vm81_b, &hash72_b) == HHS_GFCC_OK, "Hash72 replay projection failed");
    REQUIRE(strlen(hash72_a.value.value) == 72u && hhs_hash72_equal(&hash72_a.value, &hash72_b.value), "Hash72 determinism failed");
    REQUIRE(hhs_gfcc_index_hash216(&ctx, &vm81_a, &hash72_a, &hash216_a) == HHS_GFCC_OK, "Hash216 indexing failed");
    REQUIRE(hhs_gfcc_index_hash216(&ctx, &vm81_b, &hash72_b, &hash216_b) == HHS_GFCC_OK, "Hash216 replay indexing failed");
    REQUIRE(hash216_a.position_count == 216u && strlen(hash216_a.value.value) == 216u && hhs_hash216_equal(&hash216_a.value, &hash216_b.value), "Hash216 determinism failed");

    memset(&transform_request, 0, sizeof(transform_request));
    transform_request.x_q16 = 3 * HHS_GFCC_Q16_ONE;
    transform_request.y_q16 = 4 * HHS_GFCC_Q16_ONE;
    transform_request.stage_ratio = parameters.golden_stage_ratio;
    transform_request.phase = 9u;
    transform_request.shell_depth = 3u;
    transform_request.vm81_cell = 40u;
    REQUIRE(hhs_gfcc_build_transform(&ctx, &transform_request, &transform_result) == HHS_GFCC_OK, "transform construction failed");
    REQUIRE(transform_result.exact_source_bound == 1u && transform_result.stage_ratio.numerator == 34, "transform lost exact source binding");

    pair = make_pair(&parameters, &hash72_a, &hash216_a);
    REQUIRE(hhs_gfcc_build_collision_constraint(&ctx, &pair, &constraint) == HHS_GFCC_OK, "collision constraint construction failed");
    REQUIRE(constraint.outcome == HHS_GFCC_CONTACT_CONSTRAINED && constraint.correction_x_q16 != 0, "collision was not constrained deterministically");
    REQUIRE(hhs_gfcc_enforce_collision(&ctx, &pair, &constraint, &collision_result) == HHS_GFCC_OK, "collision enforcement failed");
    REQUIRE(collision_result.outcome == HHS_GFCC_CORRECTION_APPLIED && collision_result.invariants_preserved == 1u, "collision correction violated invariants");
    REQUIRE(collision_result.corrected_b.phase == pair.b.phase && collision_result.corrected_b.vm81_cell == pair.b.vm81_cell, "collision changed symbolic identity");

    phase_pair = pair;
    phase_pair.b.phase = 10u;
    REQUIRE(hhs_gfcc_build_collision_constraint(&ctx, &phase_pair, &phase_constraint) == HHS_GFCC_OK, "phase conflict construction failed");
    REQUIRE(phase_constraint.outcome == HHS_GFCC_PHASE_CONFLICT, "phase conflict was not classified");

    memset(&step_input, 0, sizeof(step_input));
    step_input.input_event = 1u;
    step_input.collision_pair = pair;
    step_input.collision_enabled = 1u;
    REQUIRE(hhs_gfcc_step(&ctx, &step_input, &step_result) == HHS_GFCC_OK, "GFCC step failed");
    REQUIRE(step_result.step_after == step_result.step_before + 1u && step_result.collision.invariants_preserved == 1u, "step closure failed");
    REQUIRE(hhs_gfcc_validate(&ctx, &validation) == HHS_GFCC_OK && validation.all_valid == 1u, "native validation failed");

    memset(&chain, 0, sizeof(chain));
    chain.receipt_count = 1u;
    chain.receipts[0] = ctx.last_receipt;
    chain.authority_root = ctx.authority_root;
    REQUIRE(hhs_gfcc_replay(&ctx, &chain, &replay) == HHS_GFCC_OK && replay.match == 1u, "receipt replay failed");
    chain.authority_root.value[0] = chain.authority_root.value[0] == '0' ? '1' : '0';
    REQUIRE(hhs_gfcc_replay(&ctx, &chain, &replay) == HHS_GFCC_REPLAY_MISMATCH, "different authority root replay was accepted");

    invalid_spec = spec;
    invalid_spec.c2 = 4;
    memset(&rejected_parameters, 0x5a, sizeof(rejected_parameters));
    status = hhs_gfcc_build_parameters(&ctx, &invalid_spec, &rejected_parameters);
    REQUIRE(status == HHS_GFCC_INVALID_SYMBOL, "altered square state was accepted");
    REQUIRE(rejected_parameters.schema_version == 0u, "rejected parameter build published partial output");

    unresolved_graph = graph;
    unresolved_graph.denominator_closed = 0u;
    memset(&closure, 0x5a, sizeof(closure));
    REQUIRE(hhs_gfcc_close_shells(&ctx, &unresolved_graph, &closure) == HHS_GFCC_SHELL_UNRESOLVED, "projection with unresolved shell was accepted");

    REQUIRE(hhs_gfcc_context_init(&replay_ctx, &config) == HHS_GFCC_OK, "replay context init failed");
    REQUIRE(hhs_gfcc_build_parameters(&replay_ctx, &spec, &replay_parameters) == HHS_GFCC_OK, "replay parameter build failed");
    REQUIRE(hhs_hash216_equal(&parameters.parameter_digest, &replay_parameters.parameter_digest), "parameter construction replay mismatch");

    puts("GOLDEN_FRACTAL_CORRESPONDENCE_NATIVE_CORE_PASSED");
    return 0;
}
