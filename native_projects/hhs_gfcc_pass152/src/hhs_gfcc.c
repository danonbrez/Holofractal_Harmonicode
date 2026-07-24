#include "hhs_gfcc.h"

#include <limits.h>
#include <string.h>

#define HHS_GFCC_SYMBOL_A2 1u
#define HHS_GFCC_SYMBOL_B2 2u
#define HHS_GFCC_SYMBOL_C2 3u
#define HHS_GFCC_SYMBOL_D2 4u
#define HHS_GFCC_SYMBOL_E2 5u
#define HHS_GFCC_DEPENDENCY_GOLDEN_STAGE 1u
#define HHS_GFCC_CONSTRAINT_NONARY 0x01u
#define HHS_GFCC_CONSTRAINT_PHASE 0x02u
#define HHS_GFCC_CONSTRAINT_SCALE 0x04u
#define HHS_GFCC_CONSTRAINT_ANCESTRY 0x08u

static hhs_gfcc_exact hhs_exact(int64_t numerator, int64_t denominator) {
    hhs_gfcc_exact out;
    out.numerator = numerator;
    out.denominator = denominator;
    return out;
}

static int hhs_exact_equal(hhs_gfcc_exact a, hhs_gfcc_exact b) {
    return a.numerator == b.numerator && a.denominator == b.denominator;
}

static int hhs_ratio_valid(hhs_gfcc_exact_ratio value) {
    return value.denominator > 0;
}

static int hhs_hash72_is_set(const HHSHash72 *value) {
    return value && value->value[0] != '\0' && value->value[HHS_HASH72_LEN] == '\0';
}

static int hhs_hash216_is_set(const HHSHash216 *value) {
    return value && value->value[0] != '\0' && value->value[HHS_HASH216_LEN] == '\0';
}

static void hhs_put_u32_be(unsigned char *buffer, size_t *offset, uint32_t value) {
    buffer[(*offset)++] = (unsigned char)((value >> 24) & 0xffu);
    buffer[(*offset)++] = (unsigned char)((value >> 16) & 0xffu);
    buffer[(*offset)++] = (unsigned char)((value >> 8) & 0xffu);
    buffer[(*offset)++] = (unsigned char)(value & 0xffu);
}

static void hhs_put_u64_be(unsigned char *buffer, size_t *offset, uint64_t value) {
    unsigned int shift;
    for (shift = 0u; shift < 64u; shift += 8u) {
        buffer[(*offset)++] = (unsigned char)((value >> (56u - shift)) & 0xffu);
    }
}

static void hhs_put_i64_be(unsigned char *buffer, size_t *offset, int64_t value) {
    hhs_put_u64_be(buffer, offset, (uint64_t)value);
}

static void hhs_put_bytes(unsigned char *buffer, size_t *offset, const void *data, size_t size) {
    memcpy(buffer + *offset, data, size);
    *offset += size;
}

static uint64_t hhs_abs_i64_to_u64(int64_t value) {
    if (value >= 0) {
        return (uint64_t)value;
    }
    return (uint64_t)(-(value + 1)) + 1u;
}

static int64_t hhs_min_i64(int64_t a, int64_t b) {
    return a < b ? a : b;
}

static int64_t hhs_max_i64(int64_t a, int64_t b) {
    return a > b ? a : b;
}

static hhs_gfcc_status hhs_set_status(hhs_gfcc_context *ctx, hhs_gfcc_status status) {
    if (ctx) {
        ctx->last_status = status;
    }
    return status;
}

static void hhs_make_receipt(
    hhs_gfcc_context *ctx,
    const char *operation,
    const void *payload,
    size_t payload_size,
    HHSHash72 *out
) {
    unsigned char buffer[512];
    size_t offset = 0u;
    size_t operation_size = strlen(operation);
    size_t copy_size = payload_size;
    if (operation_size > 96u) operation_size = 96u;
    if (copy_size > 256u) copy_size = 256u;
    memset(buffer, 0, sizeof(buffer));
    hhs_put_u32_be(buffer, &offset, HHS_GFCC_ABI_VERSION);
    hhs_put_u64_be(buffer, &offset, ctx ? ctx->deterministic_step : 0u);
    if (ctx) {
        hhs_put_bytes(buffer, &offset, ctx->authority_root.value, HHS_HASH72_LEN);
        hhs_put_bytes(buffer, &offset, ctx->last_receipt.value, HHS_HASH72_LEN);
    }
    hhs_put_u32_be(buffer, &offset, (uint32_t)operation_size);
    hhs_put_bytes(buffer, &offset, operation, operation_size);
    hhs_put_u32_be(buffer, &offset, (uint32_t)copy_size);
    if (payload && copy_size) hhs_put_bytes(buffer, &offset, payload, copy_size);
    hhs_hash72_compute(buffer, offset, out);
    if (ctx) ctx->last_receipt = *out;
}

static int hhs_checked_add_i64(int64_t a, int64_t b, int64_t *out) {
    if (!out) return 0;
    if ((b > 0 && a > INT64_MAX - b) || (b < 0 && a < INT64_MIN - b)) return 0;
    *out = a + b;
    return 1;
}

static hhs_gfcc_status hhs_fibonacci_ratio(uint32_t stage, hhs_gfcc_exact_ratio *out) {
    uint32_t i;
    int64_t a = 1;
    int64_t b = 1;
    int64_t next;
    if (!out || stage < 2u || stage > 92u) return HHS_GFCC_RESOURCE_BOUNDED;
    for (i = 2u; i <= stage; ++i) {
        if (!hhs_checked_add_i64(a, b, &next)) return HHS_GFCC_RESOURCE_BOUNDED;
        a = b;
        b = next;
    }
    out->numerator = b;
    out->denominator = a;
    return HHS_GFCC_OK;
}

uint32_t hhs_gfcc_vm81_index(uint32_t row, uint32_t column) {
    return (row < 9u && column < 9u) ? (9u * row + column) : HHS_GFCC_VM81_CELLS;
}

hhs_gfcc_status hhs_gfcc_vm81_inverse(uint32_t index, uint32_t *row, uint32_t *column) {
    if (!row || !column) return HHS_GFCC_INVALID_ARGUMENT;
    if (index >= HHS_GFCC_VM81_CELLS) return HHS_GFCC_VM81_MAP_ERROR;
    *row = index / 9u;
    *column = index % 9u;
    return HHS_GFCC_OK;
}

hhs_gfcc_status hhs_gfcc_context_init(hhs_gfcc_context *ctx, const hhs_gfcc_config *config) {
    if (!ctx || !config) return HHS_GFCC_INVALID_ARGUMENT;
    memset(ctx, 0, sizeof(*ctx));
    if (config->struct_size < sizeof(*config) || config->abi_version != HHS_GFCC_ABI_VERSION) {
        return hhs_set_status(ctx, HHS_GFCC_INVALID_SPEC);
    }
    if (!hhs_hash72_is_set(&config->authority_root)) {
        return hhs_set_status(ctx, HHS_GFCC_INVALID_ARGUMENT);
    }
    ctx->struct_size = (uint32_t)sizeof(*ctx);
    ctx->abi_version = HHS_GFCC_ABI_VERSION;
    ctx->initialized = 1u;
    ctx->authority_root = config->authority_root;
    hhs_hash72_clear(&ctx->last_receipt);
    ctx->last_status = HHS_GFCC_OK;
    return HHS_GFCC_OK;
}

hhs_gfcc_status hhs_gfcc_build_parameters(hhs_gfcc_context *ctx, const hhs_gfcc_spec *spec, hhs_gfcc_parameters *out) {
    unsigned char serialized[512];
    size_t offset = 0u;
    hhs_gfcc_exact_ratio ratio;
    hhs_gfcc_status status;
    if (!ctx || !ctx->initialized || !spec || !out) return hhs_set_status(ctx, HHS_GFCC_INVALID_ARGUMENT);
    memset(out, 0, sizeof(*out));
    if (spec->schema_version != 1u || spec->interpretation_version != 1u) return hhs_set_status(ctx, HHS_GFCC_INVALID_SPEC);
    if (spec->a2 != 1 || spec->b2 != 2 || spec->c2 != 3 || spec->d2 != 5 || spec->e2 != 8) {
        return hhs_set_status(ctx, HHS_GFCC_INVALID_SYMBOL);
    }
    if (spec->c2 != spec->b2 + spec->a2 || spec->d2 != spec->c2 + spec->b2 || spec->e2 != spec->d2 + spec->c2) {
        return hhs_set_status(ctx, HHS_GFCC_INVALID_DEPENDENCY);
    }
    status = hhs_fibonacci_ratio(spec->fibonacci_stage, &ratio);
    if (status != HHS_GFCC_OK) return hhs_set_status(ctx, status);
    out->schema_version = 1u;
    out->interpretation_version = 1u;
    out->a2 = hhs_exact(1, 1);
    out->b2 = hhs_exact(2, 1);
    out->c2 = hhs_exact(3, 1);
    out->d2 = hhs_exact(5, 1);
    out->e2 = hhs_exact(8, 1);
    out->numerator_shell.root_symbol = HHS_GFCC_SYMBOL_E2;
    out->numerator_shell.dependency_count = 2u;
    out->numerator_shell.dependency_symbols[0] = HHS_GFCC_SYMBOL_D2;
    out->numerator_shell.dependency_symbols[1] = HHS_GFCC_SYMBOL_C2;
    out->numerator_shell.closed_value = hhs_exact(8, 1);
    out->numerator_shell.closed = 1u;
    out->denominator_shell.root_symbol = HHS_GFCC_SYMBOL_B2;
    out->denominator_shell.dependency_count = 3u;
    out->denominator_shell.dependency_symbols[0] = HHS_GFCC_SYMBOL_A2;
    out->denominator_shell.dependency_symbols[1] = HHS_GFCC_SYMBOL_A2;
    out->denominator_shell.dependency_symbols[2] = HHS_GFCC_SYMBOL_C2;
    out->denominator_shell.closed_value = hhs_exact(4, 1);
    out->denominator_shell.closed = 1u;
    out->projected_state = hhs_exact(2, 1);
    out->terminal_residual = hhs_exact(0, 1);
    out->golden_stage_ratio = ratio;
    out->golden_limit.symbol_id = 1u;
    out->golden_limit.polynomial[0] = 1;
    out->golden_limit.polynomial[1] = -1;
    out->golden_limit.polynomial[2] = -1;
    out->golden_limit.positive_root = 1u;
    out->inverse_diagonal_scale.symbol_id = 2u;
    out->inverse_diagonal_scale.polynomial[0] = 2;
    out->inverse_diagonal_scale.polynomial[1] = 0;
    out->inverse_diagonal_scale.polynomial[2] = -1;
    out->inverse_diagonal_scale.positive_root = 1u;
    out->delta369.ring_modulus = 9u;
    {
        static const uint8_t zero_partition[9] = {0u,3u,6u,1u,4u,7u,2u,5u,8u};
        static const uint8_t one_partition[9] = {3u,6u,9u,1u,4u,7u,2u,5u,8u};
        memcpy(out->delta369.zero_indexed_partition, zero_partition, sizeof(zero_partition));
        memcpy(out->delta369.one_indexed_partition, one_partition, sizeof(one_partition));
    }
    out->delta369.active_indexing = 0u;
    out->delta369.matrix_rows = 3u;
    out->delta369.matrix_columns = 3u;
    out->delta369.coordinate_dimensions = 4u;
    out->delta369.phase_lane_count = 3u;
    memset(serialized, 0, sizeof(serialized));
    hhs_put_u32_be(serialized, &offset, out->schema_version);
    hhs_put_u32_be(serialized, &offset, out->interpretation_version);
    hhs_put_i64_be(serialized, &offset, out->a2.numerator);
    hhs_put_i64_be(serialized, &offset, out->b2.numerator);
    hhs_put_i64_be(serialized, &offset, out->c2.numerator);
    hhs_put_i64_be(serialized, &offset, out->d2.numerator);
    hhs_put_i64_be(serialized, &offset, out->e2.numerator);
    hhs_put_i64_be(serialized, &offset, out->numerator_shell.closed_value.numerator);
    hhs_put_i64_be(serialized, &offset, out->denominator_shell.closed_value.numerator);
    hhs_put_i64_be(serialized, &offset, out->terminal_residual.numerator);
    hhs_put_i64_be(serialized, &offset, ratio.numerator);
    hhs_put_i64_be(serialized, &offset, ratio.denominator);
    hhs_put_bytes(serialized, &offset, out->delta369.zero_indexed_partition, 9u);
    hhs_hash72_compute(serialized, offset, &out->source_digest);
    hhs_hash216_compute(serialized, offset, &out->parameter_digest);
    hhs_make_receipt(ctx, "GFCC_BUILD_PARAMETERS", serialized, offset, &ctx->last_receipt);
    return hhs_set_status(ctx, HHS_GFCC_OK);
}

hhs_gfcc_status hhs_gfcc_load_parameters(hhs_gfcc_context *ctx, const hhs_gfcc_parameters *parameters) {
    if (!ctx || !ctx->initialized || !parameters) return hhs_set_status(ctx, HHS_GFCC_INVALID_ARGUMENT);
    if (!parameters->numerator_shell.closed || !parameters->denominator_shell.closed) return hhs_set_status(ctx, HHS_GFCC_SHELL_UNRESOLVED);
    if (!hhs_exact_equal(parameters->terminal_residual, hhs_exact(0, 1))) return hhs_set_status(ctx, HHS_GFCC_EXACTNESS_VIOLATION);
    if (parameters->delta369.ring_modulus != 9u || parameters->delta369.coordinate_dimensions < 4u) return hhs_set_status(ctx, HHS_GFCC_DELTA_COLLAPSE);
    if (!hhs_ratio_valid(parameters->golden_stage_ratio)) return hhs_set_status(ctx, HHS_GFCC_EXACTNESS_VIOLATION);
    ctx->parameters = *parameters;
    ctx->parameters_loaded = 1u;
    hhs_make_receipt(ctx, "GFCC_LOAD_PARAMETERS", parameters->parameter_digest.value, HHS_HASH216_LEN, &ctx->last_receipt);
    return hhs_set_status(ctx, HHS_GFCC_OK);
}

hhs_gfcc_status hhs_gfcc_close_shells(hhs_gfcc_context *ctx, const hhs_dependency_graph *graph, hhs_shell_closure *out) {
    if (!ctx || !ctx->initialized || !ctx->parameters_loaded || !graph || !out) return hhs_set_status(ctx, HHS_GFCC_INVALID_ARGUMENT);
    memset(out, 0, sizeof(*out));
    if (graph->node_count < 7u || graph->shell_count != 2u) return hhs_set_status(ctx, HHS_GFCC_INVALID_DEPENDENCY);
    if (!graph->numerator_closed || !graph->denominator_closed) return hhs_set_status(ctx, HHS_GFCC_SHELL_UNRESOLVED);
    out->numerator = ctx->parameters.numerator_shell;
    out->denominator = ctx->parameters.denominator_shell;
    out->quotient = hhs_exact(2, 1);
    out->residual = hhs_exact(0, 1);
    out->ancestry_preserved = 1u;
    hhs_make_receipt(ctx, "GFCC_CLOSE_SHELLS", out, sizeof(*out), &ctx->last_receipt);
    return hhs_set_status(ctx, HHS_GFCC_OK);
}

hhs_gfcc_status hhs_gfcc_construct_vm81(hhs_gfcc_context *ctx, const hhs_gfcc_parameters *parameters, hhs_vm81_state *out) {
    unsigned char serialized[4096];
    size_t offset = 0u;
    uint32_t index;
    if (!ctx || !ctx->initialized || !parameters || !out) return hhs_set_status(ctx, HHS_GFCC_INVALID_ARGUMENT);
    if (!parameters->numerator_shell.closed || !parameters->denominator_shell.closed) return hhs_set_status(ctx, HHS_GFCC_SHELL_UNRESOLVED);
    memset(out, 0, sizeof(*out));
    out->cell_count = HHS_GFCC_VM81_CELLS;
    for (index = 0u; index < HHS_GFCC_VM81_CELLS; ++index) {
        hhs_vm81_fractal_cell *cell = &out->cells[index];
        uint32_t row;
        uint32_t column;
        if (hhs_gfcc_vm81_inverse(index, &row, &column) != HHS_GFCC_OK || hhs_gfcc_vm81_index(row, column) != index) {
            memset(out, 0, sizeof(*out));
            return hhs_set_status(ctx, HHS_GFCC_VM81_MAP_ERROR);
        }
        cell->cell_index = index;
        cell->row = (uint8_t)row;
        cell->column = (uint8_t)column;
        cell->nonary_residue = (uint8_t)((row + column) % 9u);
        cell->phase_lane = (uint8_t)(cell->nonary_residue % 3u);
        cell->scale_depth = row;
        cell->parent_cell = row == 0u ? HHS_GFCC_NO_PARENT : hhs_gfcc_vm81_index(row - 1u, column);
        cell->child_mask = row == 8u ? 0u : (1u << (column % 9u));
        cell->symbol = (uint32_t)cell->nonary_residue;
        cell->exact_state = parameters->golden_stage_ratio;
        cell->dependency = HHS_GFCC_DEPENDENCY_GOLDEN_STAGE;
        cell->constraints = HHS_GFCC_CONSTRAINT_NONARY | HHS_GFCC_CONSTRAINT_PHASE | HHS_GFCC_CONSTRAINT_SCALE | HHS_GFCC_CONSTRAINT_ANCESTRY;
        hhs_hash72_clear(&cell->hash72_projection);
        hhs_hash216_clear(&cell->hash216_index);
        hhs_put_u32_be(serialized, &offset, cell->cell_index);
        serialized[offset++] = cell->row;
        serialized[offset++] = cell->column;
        serialized[offset++] = cell->nonary_residue;
        serialized[offset++] = cell->phase_lane;
        hhs_put_u32_be(serialized, &offset, cell->scale_depth);
        hhs_put_i64_be(serialized, &offset, cell->exact_state.numerator);
        hhs_put_i64_be(serialized, &offset, cell->exact_state.denominator);
    }
    hhs_hash72_compute(serialized, offset, &out->state_hash72);
    hhs_hash216_compute(serialized, offset, &out->state_hash216);
    hhs_make_receipt(ctx, "GFCC_CONSTRUCT_VM81", serialized, offset, &ctx->last_receipt);
    return hhs_set_status(ctx, HHS_GFCC_OK);
}

hhs_gfcc_status hhs_gfcc_project_hash72(hhs_gfcc_context *ctx, const hhs_vm81_state *vm81, hhs_hash72_projection *out) {
    unsigned char serialized[512];
    size_t offset = 0u;
    if (!ctx || !ctx->initialized || !ctx->parameters_loaded || !vm81 || !out) return hhs_set_status(ctx, HHS_GFCC_INVALID_ARGUMENT);
    if (vm81->cell_count != HHS_GFCC_VM81_CELLS || !hhs_hash72_is_set(&vm81->state_hash72)) return hhs_set_status(ctx, HHS_GFCC_VM81_MAP_ERROR);
    memset(out, 0, sizeof(*out));
    hhs_put_bytes(serialized, &offset, ctx->authority_root.value, HHS_HASH72_LEN);
    hhs_put_bytes(serialized, &offset, vm81->state_hash72.value, HHS_HASH72_LEN);
    hhs_put_bytes(serialized, &offset, vm81->state_hash216.value, HHS_HASH216_LEN);
    hhs_put_i64_be(serialized, &offset, ctx->parameters.golden_stage_ratio.numerator);
    hhs_put_i64_be(serialized, &offset, ctx->parameters.golden_stage_ratio.denominator);
    hhs_put_i64_be(serialized, &offset, ctx->parameters.terminal_residual.numerator);
    hhs_hash72_compute(serialized, offset, &out->value);
    out->predecessor = ctx->last_receipt;
    out->source_cell_count = vm81->cell_count;
    out->stage_ratio = ctx->parameters.golden_stage_ratio;
    out->nonary_phase = vm81->cells[0].phase_lane;
    out->projection_mode = 1u;
    hhs_make_receipt(ctx, "GFCC_PROJECT_HASH72", out->value.value, HHS_HASH72_LEN, &ctx->last_receipt);
    return hhs_set_status(ctx, HHS_GFCC_OK);
}

hhs_gfcc_status hhs_gfcc_index_hash216(hhs_gfcc_context *ctx, const hhs_vm81_state *vm81, const hhs_hash72_projection *hash72, hhs_hash216_index *out) {
    unsigned char serialized[512];
    size_t offset = 0u;
    if (!ctx || !ctx->initialized || !ctx->parameters_loaded || !vm81 || !hash72 || !out) return hhs_set_status(ctx, HHS_GFCC_INVALID_ARGUMENT);
    if (!hhs_hash72_is_set(&hash72->value) || !hhs_hash216_is_set(&vm81->state_hash216)) return hhs_set_status(ctx, HHS_GFCC_HASH72_ERROR);
    memset(out, 0, sizeof(*out));
    hhs_put_bytes(serialized, &offset, ctx->authority_root.value, HHS_HASH72_LEN);
    hhs_put_bytes(serialized, &offset, hash72->value.value, HHS_HASH72_LEN);
    hhs_put_bytes(serialized, &offset, vm81->state_hash216.value, HHS_HASH216_LEN);
    hhs_put_bytes(serialized, &offset, ctx->parameters.parameter_digest.value, HHS_HASH216_LEN);
    hhs_hash216_compute(serialized, offset, &out->value);
    out->position_count = HHS_GFCC_HASH216_POSITIONS;
    out->mapping_version = 1u;
    out->source_hash72 = hash72->value;
    hhs_make_receipt(ctx, "GFCC_INDEX_HASH216", out->value.value, HHS_HASH216_LEN, &ctx->last_receipt);
    return hhs_set_status(ctx, HHS_GFCC_OK);
}

hhs_gfcc_status hhs_gfcc_build_transform(hhs_gfcc_context *ctx, const hhs_transform_request *request, hhs_transform_result *out) {
    if (!ctx || !ctx->initialized || !ctx->parameters_loaded || !request || !out) return hhs_set_status(ctx, HHS_GFCC_INVALID_ARGUMENT);
    if (!hhs_ratio_valid(request->stage_ratio) || request->phase >= 72u || request->vm81_cell >= 81u) return hhs_set_status(ctx, HHS_GFCC_INVALID_GEOMETRY);
    memset(out, 0, sizeof(*out));
    out->x_q16 = request->x_q16;
    out->y_q16 = request->y_q16;
    out->stage_ratio = request->stage_ratio;
    out->phase = request->phase;
    out->shell_depth = request->shell_depth;
    out->vm81_cell = request->vm81_cell;
    out->exact_source_bound = 1u;
    hhs_make_receipt(ctx, "GFCC_BUILD_TRANSFORM", out, sizeof(*out), &ctx->last_receipt);
    return hhs_set_status(ctx, HHS_GFCC_OK);
}

static int hhs_collision_identity_valid(const hhs_collision_object *object) {
    return object && hhs_ratio_valid(object->scale) && object->phase < 72u && object->vm81_cell < 81u && hhs_hash72_is_set(&object->hash72) && hhs_hash216_is_set(&object->hash216) && object->half_width_q16 >= 0 && object->half_height_q16 >= 0;
}

hhs_gfcc_status hhs_gfcc_build_collision_constraint(hhs_gfcc_context *ctx, const hhs_collision_pair *pair, hhs_collision_constraint *out) {
    int64_t dx;
    int64_t dy;
    int64_t sum_half_x;
    int64_t sum_half_y;
    uint64_t abs_dx;
    uint64_t abs_dy;
    int64_t overlap_x;
    int64_t overlap_y;
    if (!ctx || !ctx->initialized || !ctx->parameters_loaded || !pair || !out) return hhs_set_status(ctx, HHS_GFCC_INVALID_ARGUMENT);
    memset(out, 0, sizeof(*out));
    if (!hhs_collision_identity_valid(&pair->a) || !hhs_collision_identity_valid(&pair->b)) return hhs_set_status(ctx, HHS_GFCC_INVALID_GEOMETRY);
    if (!hhs_checked_add_i64(pair->a.half_width_q16, pair->b.half_width_q16, &sum_half_x) || !hhs_checked_add_i64(pair->a.half_height_q16, pair->b.half_height_q16, &sum_half_y)) return hhs_set_status(ctx, HHS_GFCC_RESOURCE_BOUNDED);
    if (!hhs_checked_add_i64(pair->b.x_q16, -pair->a.x_q16, &dx) || !hhs_checked_add_i64(pair->b.y_q16, -pair->a.y_q16, &dy)) return hhs_set_status(ctx, HHS_GFCC_RESOURCE_BOUNDED);
    abs_dx = hhs_abs_i64_to_u64(dx);
    abs_dy = hhs_abs_i64_to_u64(dy);
    if (abs_dx > (uint64_t)INT64_MAX || abs_dy > (uint64_t)INT64_MAX) return hhs_set_status(ctx, HHS_GFCC_RESOURCE_BOUNDED);
    overlap_x = sum_half_x - (int64_t)abs_dx;
    overlap_y = sum_half_y - (int64_t)abs_dy;
    out->signed_separation_x_q16 = (int64_t)abs_dx - sum_half_x;
    out->signed_separation_y_q16 = (int64_t)abs_dy - sum_half_y;
    out->penetration_x_q16 = hhs_max_i64(0, overlap_x);
    out->penetration_y_q16 = hhs_max_i64(0, overlap_y);
    out->phase_admissible = ((pair->a.phase + 72u - pair->b.phase) % 3u) == 0u;
    out->scale_admissible = hhs_exact_equal(pair->a.scale, pair->b.scale);
    out->identity_continuity = 1u;
    if (overlap_x <= 0 || overlap_y <= 0) {
        out->outcome = HHS_GFCC_NO_COLLISION;
    } else if (!out->phase_admissible) {
        out->outcome = HHS_GFCC_PHASE_CONFLICT;
    } else if (!out->scale_admissible) {
        out->outcome = HHS_GFCC_SCALE_CONFLICT;
    } else {
        out->outcome = HHS_GFCC_CONTACT_CONSTRAINED;
        if (overlap_x <= overlap_y) out->correction_x_q16 = dx >= 0 ? overlap_x : -overlap_x;
        else out->correction_y_q16 = dy >= 0 ? overlap_y : -overlap_y;
    }
    hhs_make_receipt(ctx, "GFCC_BUILD_COLLISION", out, sizeof(*out), &ctx->last_receipt);
    return hhs_set_status(ctx, HHS_GFCC_OK);
}

hhs_gfcc_status hhs_gfcc_enforce_collision(hhs_gfcc_context *ctx, const hhs_collision_pair *pair, const hhs_collision_constraint *constraint, hhs_collision_result *out) {
    hhs_collision_object corrected;
    if (!ctx || !ctx->initialized || !ctx->parameters_loaded || !pair || !constraint || !out) return hhs_set_status(ctx, HHS_GFCC_INVALID_ARGUMENT);
    memset(out, 0, sizeof(*out));
    corrected = pair->b;
    if (constraint->outcome == HHS_GFCC_CONTACT_CONSTRAINED) {
        if (!hhs_checked_add_i64(corrected.x_q16, constraint->correction_x_q16, &corrected.x_q16) || !hhs_checked_add_i64(corrected.y_q16, constraint->correction_y_q16, &corrected.y_q16)) return hhs_set_status(ctx, HHS_GFCC_RESOURCE_BOUNDED);
        out->outcome = HHS_GFCC_CORRECTION_APPLIED;
    } else {
        out->outcome = constraint->outcome;
    }
    out->corrected_b = corrected;
    out->invariants_preserved = hhs_exact_equal(corrected.scale, pair->b.scale) && corrected.phase == pair->b.phase && corrected.vm81_cell == pair->b.vm81_cell && hhs_hash72_equal(&corrected.hash72, &pair->b.hash72) && hhs_hash216_equal(&corrected.hash216, &pair->b.hash216);
    if (!out->invariants_preserved) return hhs_set_status(ctx, HHS_GFCC_COLLISION_INVARIANT_ERROR);
    hhs_make_receipt(ctx, "GFCC_ENFORCE_COLLISION", out, sizeof(*out), &out->receipt);
    return hhs_set_status(ctx, HHS_GFCC_OK);
}

hhs_gfcc_status hhs_gfcc_step(hhs_gfcc_context *ctx, const hhs_gfcc_step_input *input, hhs_gfcc_step_result *out) {
    hhs_gfcc_status status;
    if (!ctx || !ctx->initialized || !ctx->parameters_loaded || !input || !out) return hhs_set_status(ctx, HHS_GFCC_INVALID_ARGUMENT);
    memset(out, 0, sizeof(*out));
    out->step_before = ctx->deterministic_step;
    status = hhs_gfcc_construct_vm81(ctx, &ctx->parameters, &out->vm81);
    if (status != HHS_GFCC_OK) return status;
    status = hhs_gfcc_project_hash72(ctx, &out->vm81, &out->hash72);
    if (status != HHS_GFCC_OK) return status;
    status = hhs_gfcc_index_hash216(ctx, &out->vm81, &out->hash72, &out->hash216);
    if (status != HHS_GFCC_OK) return status;
    if (input->collision_enabled) {
        hhs_collision_constraint constraint;
        status = hhs_gfcc_build_collision_constraint(ctx, &input->collision_pair, &constraint);
        if (status != HHS_GFCC_OK) return status;
        status = hhs_gfcc_enforce_collision(ctx, &input->collision_pair, &constraint, &out->collision);
        if (status != HHS_GFCC_OK) return status;
    } else {
        out->collision.outcome = HHS_GFCC_NO_COLLISION;
        out->collision.invariants_preserved = 1u;
    }
    ctx->deterministic_step += 1u;
    out->step_after = ctx->deterministic_step;
    hhs_make_receipt(ctx, "GFCC_STEP", out, sizeof(*out), &out->receipt);
    return hhs_set_status(ctx, HHS_GFCC_OK);
}

hhs_gfcc_status hhs_gfcc_validate(hhs_gfcc_context *ctx, hhs_gfcc_validation_report *out) {
    uint32_t index;
    if (!ctx || !ctx->initialized || !ctx->parameters_loaded || !out) return hhs_set_status(ctx, HHS_GFCC_INVALID_ARGUMENT);
    memset(out, 0, sizeof(*out));
    out->square_states_valid = hhs_exact_equal(ctx->parameters.a2, hhs_exact(1,1)) && hhs_exact_equal(ctx->parameters.b2, hhs_exact(2,1)) && hhs_exact_equal(ctx->parameters.c2, hhs_exact(3,1)) && hhs_exact_equal(ctx->parameters.d2, hhs_exact(5,1)) && hhs_exact_equal(ctx->parameters.e2, hhs_exact(8,1));
    out->shells_closed = ctx->parameters.numerator_shell.closed && ctx->parameters.denominator_shell.closed;
    out->terminal_zero = hhs_exact_equal(ctx->parameters.terminal_residual, hhs_exact(0,1));
    out->delta_not_collapsed = ctx->parameters.delta369.ring_modulus == 9u && ctx->parameters.delta369.coordinate_dimensions >= 4u;
    out->vm81_reversible = 1u;
    for (index = 0u; index < 81u; ++index) {
        uint32_t row;
        uint32_t column;
        if (hhs_gfcc_vm81_inverse(index, &row, &column) != HHS_GFCC_OK || hhs_gfcc_vm81_index(row, column) != index) out->vm81_reversible = 0u;
    }
    {
        hhs_vm81_state a;
        hhs_vm81_state b;
        hhs_hash72_projection h72a;
        hhs_hash72_projection h72b;
        hhs_hash216_index h216a;
        hhs_hash216_index h216b;
        out->hash72_deterministic = hhs_gfcc_construct_vm81(ctx, &ctx->parameters, &a) == HHS_GFCC_OK && hhs_gfcc_construct_vm81(ctx, &ctx->parameters, &b) == HHS_GFCC_OK && hhs_gfcc_project_hash72(ctx, &a, &h72a) == HHS_GFCC_OK && hhs_gfcc_project_hash72(ctx, &b, &h72b) == HHS_GFCC_OK && hhs_hash72_equal(&h72a.value, &h72b.value);
        out->hash216_deterministic = out->hash72_deterministic && hhs_gfcc_index_hash216(ctx, &a, &h72a, &h216a) == HHS_GFCC_OK && hhs_gfcc_index_hash216(ctx, &b, &h72b, &h216b) == HHS_GFCC_OK && hhs_hash216_equal(&h216a.value, &h216b.value);
    }
    out->all_valid = out->square_states_valid && out->shells_closed && out->terminal_zero && out->delta_not_collapsed && out->vm81_reversible && out->hash72_deterministic && out->hash216_deterministic;
    return hhs_set_status(ctx, out->all_valid ? HHS_GFCC_OK : HHS_GFCC_INTERNAL_ERROR);
}

hhs_gfcc_status hhs_gfcc_replay(hhs_gfcc_context *ctx, const hhs_gfcc_receipt_chain *chain, hhs_gfcc_replay_report *out) {
    if (!ctx || !ctx->initialized || !chain || !out) return hhs_set_status(ctx, HHS_GFCC_INVALID_ARGUMENT);
    memset(out, 0, sizeof(*out));
    if (chain->receipt_count == 0u || chain->receipt_count > 32u) return hhs_set_status(ctx, HHS_GFCC_RECEIPT_ERROR);
    if (!hhs_hash72_equal(&chain->authority_root, &ctx->authority_root)) return hhs_set_status(ctx, HHS_GFCC_REPLAY_MISMATCH);
    out->receipt_count = chain->receipt_count;
    out->observed_terminal_receipt = chain->receipts[chain->receipt_count - 1u];
    out->match = hhs_hash72_equal(&out->observed_terminal_receipt, &ctx->last_receipt);
    return hhs_set_status(ctx, out->match ? HHS_GFCC_OK : HHS_GFCC_REPLAY_MISMATCH);
}

const char *hhs_gfcc_status_name(hhs_gfcc_status status) {
    static const char *const names[] = {
        "HHS_GFCC_OK", "HHS_GFCC_INVALID_ARGUMENT", "HHS_GFCC_INVALID_SPEC", "HHS_GFCC_INVALID_SYMBOL",
        "HHS_GFCC_INVALID_DEPENDENCY", "HHS_GFCC_DEPENDENCY_CYCLE", "HHS_GFCC_SHELL_UNRESOLVED",
        "HHS_GFCC_PROJECTION_BEFORE_CLOSURE", "HHS_GFCC_EXACTNESS_VIOLATION", "HHS_GFCC_FLOAT_AUTHORITY_VIOLATION",
        "HHS_GFCC_DELTA_COLLAPSE", "HHS_GFCC_NONARY_INDEX_ERROR", "HHS_GFCC_DECIMAL_PROJECTION_ERROR",
        "HHS_GFCC_VM81_MAP_ERROR", "HHS_GFCC_HASH72_ERROR", "HHS_GFCC_HASH216_ERROR",
        "HHS_GFCC_SHADER_GENERATION_ERROR", "HHS_GFCC_SHADER_COMPILATION_ERROR", "HHS_GFCC_COLLISION_CONSTRAINT_ERROR",
        "HHS_GFCC_COLLISION_INVARIANT_ERROR", "HHS_GFCC_BUILD_ERROR", "HHS_GFCC_RESOURCE_BOUNDED",
        "HHS_GFCC_RECEIPT_ERROR", "HHS_GFCC_REPLAY_MISMATCH", "HHS_GFCC_INTERNAL_ERROR"
    };
    if ((unsigned int)status >= (sizeof(names) / sizeof(names[0]))) return "HHS_GFCC_UNKNOWN";
    return names[(unsigned int)status];
}
