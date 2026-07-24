#ifndef HHS_GFCC_H
#define HHS_GFCC_H

#include <stddef.h>
#include <stdint.h>
#include "hhs_hash216.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_GFCC_ABI_VERSION 1u
#define HHS_GFCC_VM81_CELLS 81u
#define HHS_GFCC_HASH72_POSITIONS 72u
#define HHS_GFCC_HASH216_POSITIONS 216u
#define HHS_GFCC_Q16_ONE 65536ll
#define HHS_GFCC_NO_PARENT 0xffffffffu

typedef enum hhs_gfcc_status {
    HHS_GFCC_OK = 0,
    HHS_GFCC_INVALID_ARGUMENT = 1,
    HHS_GFCC_INVALID_SPEC = 2,
    HHS_GFCC_INVALID_SYMBOL = 3,
    HHS_GFCC_INVALID_DEPENDENCY = 4,
    HHS_GFCC_DEPENDENCY_CYCLE = 5,
    HHS_GFCC_SHELL_UNRESOLVED = 6,
    HHS_GFCC_PROJECTION_BEFORE_CLOSURE = 7,
    HHS_GFCC_EXACTNESS_VIOLATION = 8,
    HHS_GFCC_FLOAT_AUTHORITY_VIOLATION = 9,
    HHS_GFCC_DELTA_COLLAPSE = 10,
    HHS_GFCC_NONARY_INDEX_ERROR = 11,
    HHS_GFCC_DECIMAL_PROJECTION_ERROR = 12,
    HHS_GFCC_VM81_MAP_ERROR = 13,
    HHS_GFCC_HASH72_ERROR = 14,
    HHS_GFCC_HASH216_ERROR = 15,
    HHS_GFCC_SHADER_GENERATION_ERROR = 16,
    HHS_GFCC_SHADER_COMPILATION_ERROR = 17,
    HHS_GFCC_COLLISION_CONSTRAINT_ERROR = 18,
    HHS_GFCC_COLLISION_INVARIANT_ERROR = 19,
    HHS_GFCC_BUILD_ERROR = 20,
    HHS_GFCC_RESOURCE_BOUNDED = 21,
    HHS_GFCC_RECEIPT_ERROR = 22,
    HHS_GFCC_REPLAY_MISMATCH = 23,
    HHS_GFCC_INTERNAL_ERROR = 24
} hhs_gfcc_status;

typedef enum hhs_gfcc_collision_outcome {
    HHS_GFCC_NO_COLLISION = 0,
    HHS_GFCC_CONTACT_ADMISSIBLE = 1,
    HHS_GFCC_CONTACT_CONSTRAINED = 2,
    HHS_GFCC_CORRECTION_APPLIED = 3,
    HHS_GFCC_PHASE_CONFLICT = 4,
    HHS_GFCC_SCALE_CONFLICT = 5,
    HHS_GFCC_VM81_STATE_CONFLICT = 6,
    HHS_GFCC_HASH72_PROJECTION_CONFLICT = 7,
    HHS_GFCC_HASH216_INDEX_CONFLICT = 8,
    HHS_GFCC_DEPENDENCY_UNRESOLVED = 9,
    HHS_GFCC_COLLISION_RESOURCE_BOUNDED = 10,
    HHS_GFCC_INVALID_GEOMETRY = 11,
    HHS_GFCC_COLLISION_REPLAY_MISMATCH = 12
} hhs_gfcc_collision_outcome;

typedef struct hhs_gfcc_exact {
    int64_t numerator;
    int64_t denominator;
} hhs_gfcc_exact;

typedef hhs_gfcc_exact hhs_gfcc_exact_ratio;

typedef struct hhs_gfcc_symbolic_irrational {
    uint32_t symbol_id;
    int32_t polynomial[3];
    uint32_t positive_root;
} hhs_gfcc_symbolic_irrational;

typedef struct hhs_gfcc_dependency_shell {
    uint32_t root_symbol;
    uint32_t dependency_count;
    uint32_t dependency_symbols[4];
    hhs_gfcc_exact closed_value;
    uint32_t closed;
} hhs_gfcc_dependency_shell;

typedef struct hhs_gfcc_delta369 {
    uint32_t ring_modulus;
    uint8_t zero_indexed_partition[9];
    uint8_t one_indexed_partition[9];
    uint32_t active_indexing;
    uint32_t matrix_rows;
    uint32_t matrix_columns;
    uint32_t coordinate_dimensions;
    uint32_t phase_lane_count;
} hhs_gfcc_delta369;

typedef struct hhs_vm81_fractal_cell {
    uint32_t cell_index;
    uint8_t row;
    uint8_t column;
    uint8_t nonary_residue;
    uint8_t phase_lane;
    uint32_t scale_depth;
    uint32_t parent_cell;
    uint32_t child_mask;
    uint32_t symbol;
    hhs_gfcc_exact exact_state;
    uint32_t dependency;
    uint32_t constraints;
    HHSHash72 hash72_projection;
    HHSHash216 hash216_index;
} hhs_vm81_fractal_cell;

typedef struct hhs_vm81_state {
    uint32_t cell_count;
    hhs_vm81_fractal_cell cells[HHS_GFCC_VM81_CELLS];
    HHSHash72 state_hash72;
    HHSHash216 state_hash216;
} hhs_vm81_state;

typedef struct hhs_hash72_projection {
    HHSHash72 value;
    HHSHash72 predecessor;
    uint32_t source_cell_count;
    hhs_gfcc_exact_ratio stage_ratio;
    uint32_t nonary_phase;
    uint32_t projection_mode;
} hhs_hash72_projection;

typedef struct hhs_hash216_index {
    HHSHash216 value;
    uint32_t position_count;
    uint32_t mapping_version;
    HHSHash72 source_hash72;
} hhs_hash216_index;

typedef struct hhs_gfcc_parameters {
    uint32_t schema_version;
    uint32_t interpretation_version;
    hhs_gfcc_exact a2;
    hhs_gfcc_exact b2;
    hhs_gfcc_exact c2;
    hhs_gfcc_exact d2;
    hhs_gfcc_exact e2;
    hhs_gfcc_dependency_shell numerator_shell;
    hhs_gfcc_dependency_shell denominator_shell;
    hhs_gfcc_exact projected_state;
    hhs_gfcc_exact terminal_residual;
    hhs_gfcc_exact_ratio golden_stage_ratio;
    hhs_gfcc_symbolic_irrational golden_limit;
    hhs_gfcc_symbolic_irrational inverse_diagonal_scale;
    hhs_gfcc_delta369 delta369;
    HHSHash72 source_digest;
    HHSHash216 parameter_digest;
} hhs_gfcc_parameters;

typedef struct hhs_gfcc_spec {
    uint32_t schema_version;
    uint32_t interpretation_version;
    uint32_t fibonacci_stage;
    int64_t a2;
    int64_t b2;
    int64_t c2;
    int64_t d2;
    int64_t e2;
} hhs_gfcc_spec;

typedef struct hhs_gfcc_config {
    uint32_t struct_size;
    uint32_t abi_version;
    HHSHash72 authority_root;
} hhs_gfcc_config;

typedef struct hhs_gfcc_context {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t initialized;
    uint32_t parameters_loaded;
    uint64_t deterministic_step;
    HHSHash72 authority_root;
    hhs_gfcc_parameters parameters;
    HHSHash72 last_receipt;
    hhs_gfcc_status last_status;
} hhs_gfcc_context;

typedef struct hhs_shell_closure {
    hhs_gfcc_dependency_shell numerator;
    hhs_gfcc_dependency_shell denominator;
    hhs_gfcc_exact quotient;
    hhs_gfcc_exact residual;
    uint32_t ancestry_preserved;
} hhs_shell_closure;

typedef struct hhs_dependency_graph {
    uint32_t node_count;
    uint32_t shell_count;
    uint32_t numerator_closed;
    uint32_t denominator_closed;
} hhs_dependency_graph;

typedef struct hhs_transform_request {
    int64_t x_q16;
    int64_t y_q16;
    hhs_gfcc_exact_ratio stage_ratio;
    uint32_t phase;
    uint32_t shell_depth;
    uint32_t vm81_cell;
} hhs_transform_request;

typedef struct hhs_transform_result {
    int64_t x_q16;
    int64_t y_q16;
    hhs_gfcc_exact_ratio stage_ratio;
    uint32_t phase;
    uint32_t shell_depth;
    uint32_t vm81_cell;
    uint32_t exact_source_bound;
} hhs_transform_result;

typedef struct hhs_collision_object {
    uint32_t object_id;
    int64_t x_q16;
    int64_t y_q16;
    int64_t half_width_q16;
    int64_t half_height_q16;
    hhs_gfcc_exact_ratio scale;
    uint32_t phase;
    uint32_t vm81_cell;
    HHSHash72 hash72;
    HHSHash216 hash216;
} hhs_collision_object;

typedef struct hhs_collision_pair {
    hhs_collision_object a;
    hhs_collision_object b;
} hhs_collision_pair;

typedef struct hhs_collision_constraint {
    hhs_gfcc_collision_outcome outcome;
    int64_t signed_separation_x_q16;
    int64_t signed_separation_y_q16;
    int64_t penetration_x_q16;
    int64_t penetration_y_q16;
    int64_t correction_x_q16;
    int64_t correction_y_q16;
    uint32_t phase_admissible;
    uint32_t scale_admissible;
    uint32_t identity_continuity;
} hhs_collision_constraint;

typedef struct hhs_collision_result {
    hhs_gfcc_collision_outcome outcome;
    hhs_collision_object corrected_b;
    uint32_t invariants_preserved;
    HHSHash72 receipt;
} hhs_collision_result;

typedef struct hhs_gfcc_step_input {
    uint32_t input_event;
    hhs_collision_pair collision_pair;
    uint32_t collision_enabled;
} hhs_gfcc_step_input;

typedef struct hhs_gfcc_step_result {
    uint64_t step_before;
    uint64_t step_after;
    hhs_vm81_state vm81;
    hhs_hash72_projection hash72;
    hhs_hash216_index hash216;
    hhs_collision_result collision;
    HHSHash72 receipt;
} hhs_gfcc_step_result;

typedef struct hhs_gfcc_validation_report {
    uint32_t square_states_valid;
    uint32_t shells_closed;
    uint32_t terminal_zero;
    uint32_t delta_not_collapsed;
    uint32_t vm81_reversible;
    uint32_t hash72_deterministic;
    uint32_t hash216_deterministic;
    uint32_t all_valid;
} hhs_gfcc_validation_report;

typedef struct hhs_gfcc_receipt_chain {
    uint32_t receipt_count;
    HHSHash72 receipts[32];
    HHSHash72 authority_root;
} hhs_gfcc_receipt_chain;

typedef struct hhs_gfcc_replay_report {
    uint32_t match;
    uint32_t receipt_count;
    HHSHash72 observed_terminal_receipt;
} hhs_gfcc_replay_report;

hhs_gfcc_status hhs_gfcc_context_init(hhs_gfcc_context *ctx, const hhs_gfcc_config *config);
hhs_gfcc_status hhs_gfcc_load_parameters(hhs_gfcc_context *ctx, const hhs_gfcc_parameters *parameters);
hhs_gfcc_status hhs_gfcc_build_parameters(hhs_gfcc_context *ctx, const hhs_gfcc_spec *spec, hhs_gfcc_parameters *out);
hhs_gfcc_status hhs_gfcc_close_shells(hhs_gfcc_context *ctx, const hhs_dependency_graph *graph, hhs_shell_closure *out);
hhs_gfcc_status hhs_gfcc_construct_vm81(hhs_gfcc_context *ctx, const hhs_gfcc_parameters *parameters, hhs_vm81_state *out);
hhs_gfcc_status hhs_gfcc_project_hash72(hhs_gfcc_context *ctx, const hhs_vm81_state *vm81, hhs_hash72_projection *out);
hhs_gfcc_status hhs_gfcc_index_hash216(hhs_gfcc_context *ctx, const hhs_vm81_state *vm81, const hhs_hash72_projection *hash72, hhs_hash216_index *out);
hhs_gfcc_status hhs_gfcc_build_transform(hhs_gfcc_context *ctx, const hhs_transform_request *request, hhs_transform_result *out);
hhs_gfcc_status hhs_gfcc_build_collision_constraint(hhs_gfcc_context *ctx, const hhs_collision_pair *pair, hhs_collision_constraint *out);
hhs_gfcc_status hhs_gfcc_enforce_collision(hhs_gfcc_context *ctx, const hhs_collision_pair *pair, const hhs_collision_constraint *constraint, hhs_collision_result *out);
hhs_gfcc_status hhs_gfcc_step(hhs_gfcc_context *ctx, const hhs_gfcc_step_input *input, hhs_gfcc_step_result *out);
hhs_gfcc_status hhs_gfcc_validate(hhs_gfcc_context *ctx, hhs_gfcc_validation_report *out);
hhs_gfcc_status hhs_gfcc_replay(hhs_gfcc_context *ctx, const hhs_gfcc_receipt_chain *chain, hhs_gfcc_replay_report *out);
uint32_t hhs_gfcc_vm81_index(uint32_t row, uint32_t column);
hhs_gfcc_status hhs_gfcc_vm81_inverse(uint32_t index, uint32_t *row, uint32_t *column);
const char *hhs_gfcc_status_name(hhs_gfcc_status status);

#ifdef __cplusplus
}
#endif

#endif
