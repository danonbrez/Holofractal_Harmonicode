#include "hhs_vm81_game.h"

#include <limits.h>
#include <stdio.h>
#include <string.h>

#define HHS_GAME_RUN_SPEED 24
#define HHS_GAME_GRAVITY 3
#define HHS_GAME_MAX_FALL_SPEED 64
#define HHS_GAME_JUMP_SPEED (-56)
#define HHS_GAME_MAX_BIGINT_LIMBS 64
#define HHS_GAME_BIGINT_BASE 1000000000U

static const char* const HHS_GAME_OPCODE_NAMES[HHS_VM81_GAME_PROGRAM_LENGTH] = {
    "LOAD", "ADD", "MULXY", "QGU", "SWEEP81", "CLOSE81",
    "CONSTRAIN", "RELAX", "GATE_APB", "GATE_CLOSURE", "MULYX",
    "ROT", "XOR", "QBRANCH", "SUB", "OR", "AND", "BRANCH", "HALT"
};

static const uint8_t HHS_GAME_REGISTERED_IDS[HHS_VM81_GAME_PROGRAM_LENGTH] = {
    HHS_VM81_REG_LOAD, HHS_VM81_REG_ADD, HHS_VM81_REG_MULXY,
    HHS_VM81_REG_QGU, HHS_VM81_REG_SWEEP81, HHS_VM81_REG_CLOSE81,
    HHS_VM81_REG_CONSTRAIN, HHS_VM81_REG_RELAX, HHS_VM81_REG_GATE_APB,
    HHS_VM81_REG_GATE_CLOSURE, HHS_VM81_REG_MULYX, HHS_VM81_REG_ROT,
    HHS_VM81_REG_XOR, HHS_VM81_REG_QBRANCH, HHS_VM81_REG_SUB,
    HHS_VM81_REG_OR, HHS_VM81_REG_AND, HHS_VM81_REG_BRANCH,
    HHS_VM81_REG_HALT
};

static const HHSVM81GameInstruction HHS_GAME_PROGRAM[HHS_VM81_GAME_PROGRAM_LENGTH] = {
    {HHS_GAME_OP_LOAD, 0, 0, 0},
    {HHS_GAME_OP_ADD, 0, 0, 0},
    {HHS_GAME_OP_MULXY, 0, 0, 0},
    {HHS_GAME_OP_QGU, 36, 0, 0},
    {HHS_GAME_OP_SWEEP81, 0, 0, 0},
    {HHS_GAME_OP_CLOSE81, 0, 0, 0},
    {HHS_GAME_OP_CONSTRAIN, 4, 0, 0},
    {HHS_GAME_OP_RELAX, 1, 0, 0},
    {HHS_GAME_OP_GATE_APB, 0, 0, 0},
    {HHS_GAME_OP_GATE_CLOSURE, 0, 0, 0},
    {HHS_GAME_OP_MULYX, 0, 0, 0},
    {HHS_GAME_OP_ROT, 1, 0, 0},
    {HHS_GAME_OP_XOR, 0, 0, 0},
    {HHS_GAME_OP_QBRANCH, 14, 15, 0},
    {HHS_GAME_OP_SUB, 0, 0, 0},
    {HHS_GAME_OP_OR, 0, 0, 0},
    {HHS_GAME_OP_AND, 0, 0, 0},
    {HHS_GAME_OP_BRANCH, 0, 18, 0},
    {HHS_GAME_OP_HALT, 0, 0, 0}
};

static const uint8_t HHS_LO_SHU[HHS_VM81_GAME_LOSHU_CELLS] = {4, 9, 2, 3, 5, 7, 8, 1, 6};

typedef struct HHSGameCanonicalState {
    uint8_t bytes[2048];
    size_t size;
} HHSGameCanonicalState;

typedef struct HHSGameBigInt {
    uint32_t limbs[HHS_GAME_MAX_BIGINT_LIMBS];
    size_t used;
} HHSGameBigInt;

static uint8_t hhs_wrap72_i64(int64_t value) {
    int64_t r = value % 72;
    if (r < 0) r += 72;
    return (uint8_t)r;
}

static int hhs_checked_add_i32(int32_t a, int32_t b, int32_t* out) {
    int64_t v;
    if (!out) return 0;
    v = (int64_t)a + (int64_t)b;
    if (v < INT32_MIN || v > INT32_MAX) return 0;
    *out = (int32_t)v;
    return 1;
}

static int hhs_checked_mul_i32(int32_t a, int32_t b, int32_t* out) {
    int64_t v;
    if (!out) return 0;
    v = (int64_t)a * (int64_t)b;
    if (v < INT32_MIN || v > INT32_MAX) return 0;
    *out = (int32_t)v;
    return 1;
}

static void hhs_put_u32(HHSGameCanonicalState* out, uint32_t value) {
    size_t i;
    for (i = 0; i < 4U; ++i) out->bytes[out->size++] = (uint8_t)((value >> (8U * i)) & 0xffU);
}

static void hhs_put_u64(HHSGameCanonicalState* out, uint64_t value) {
    size_t i;
    for (i = 0; i < 8U; ++i) out->bytes[out->size++] = (uint8_t)((value >> (8U * i)) & 0xffU);
}

static void hhs_put_i32(HHSGameCanonicalState* out, int32_t value) {
    hhs_put_u32(out, (uint32_t)value);
}

static void hhs_put_bytes(HHSGameCanonicalState* out, const uint8_t* bytes, size_t count) {
    memcpy(out->bytes + out->size, bytes, count);
    out->size += count;
}

static void hhs_canonicalize_state(const HHSVM81GameState* state, HHSGameCanonicalState* out) {
    memset(out, 0, sizeof(*out));
    hhs_put_u32(out, state->abi_version);
    hhs_put_u32(out, state->generation);
    hhs_put_u64(out, state->step);
    hhs_put_u64(out, state->frame);
    hhs_put_u32(out, state->pc);
    hhs_put_u32(out, state->max_frames);
    hhs_put_u32(out, state->input_count);
    hhs_put_u32(out, state->receipt_count);
    hhs_put_u32(out, state->camera_x_px);
    hhs_put_u32(out, state->opcode_coverage);
    hhs_put_u32(out, state->constraint_strength);
    out->bytes[out->size++] = state->phase;
    out->bytes[out->size++] = state->lo_shu_set;
    out->bytes[out->size++] = state->halted;
    out->bytes[out->size++] = state->closure_valid;
    out->bytes[out->size++] = state->current_input;
    out->bytes[out->size++] = state->qbranch_mode;
    out->bytes[out->size++] = state->gate_apb_valid;
    out->bytes[out->size++] = state->gate_closure_valid;
    hhs_put_i32(out, state->accumulator);
    hhs_put_i32(out, state->ordered_xy);
    hhs_put_i32(out, state->ordered_yx);
    hhs_put_i32(out, state->xyzw[0]);
    hhs_put_i32(out, state->xyzw[1]);
    hhs_put_i32(out, state->xyzw[2]);
    hhs_put_i32(out, state->xyzw[3]);
    hhs_put_i32(out, state->player.x_subpx);
    hhs_put_i32(out, state->player.y_subpx);
    hhs_put_i32(out, state->player.vx_subpx);
    hhs_put_i32(out, state->player.vy_subpx);
    out->bytes[out->size++] = state->player.grounded;
    out->bytes[out->size++] = state->player.facing_right;
    out->bytes[out->size++] = state->player.animation_state;
    out->bytes[out->size++] = state->player.animation_frame;
    hhs_put_bytes(out, state->vm81, HHS_VM81_GAME_VM_CELLS);
    hhs_put_bytes(out, &state->level[0][0], HHS_VM81_GAME_LEVEL_TILES_X * HHS_VM81_GAME_LEVEL_TILES_Y);
}

static void hhs_refresh_hashes(HHSVM81GameState* state) {
    HHSGameCanonicalState canonical;
    hhs_canonicalize_state(state, &canonical);
    hhs_hash216_compute(canonical.bytes, canonical.size, &state->latest_state_identity_hash216);
}

static int hhs_tile_solid(const HHSVM81GameState* state, int tile_x, int tile_y) {
    if (tile_x < 0 || tile_x >= HHS_VM81_GAME_LEVEL_TILES_X) return 1;
    if (tile_y < 0) return 0;
    if (tile_y >= HHS_VM81_GAME_LEVEL_TILES_Y) return 1;
    return state->level[tile_y][tile_x] != 0U;
}

static int hhs_rect_collides(const HHSVM81GameState* state, int32_t x_subpx, int32_t y_subpx) {
    int32_t x_px = x_subpx / HHS_VM81_GAME_SUBPIXELS;
    int32_t y_px = y_subpx / HHS_VM81_GAME_SUBPIXELS;
    int left = x_px / HHS_VM81_GAME_TILE_SIZE;
    int right = (x_px + HHS_VM81_GAME_PLAYER_WIDTH - 1) / HHS_VM81_GAME_TILE_SIZE;
    int top = y_px / HHS_VM81_GAME_TILE_SIZE;
    int bottom = (y_px + HHS_VM81_GAME_PLAYER_HEIGHT - 1) / HHS_VM81_GAME_TILE_SIZE;
    int tx, ty;
    for (ty = top; ty <= bottom; ++ty) {
        for (tx = left; tx <= right; ++tx) {
            if (hhs_tile_solid(state, tx, ty)) return 1;
        }
    }
    return 0;
}

static void hhs_move_horizontal(HHSVM81GameState* state) {
    int32_t remaining = state->player.vx_subpx;
    int32_t direction = remaining < 0 ? -1 : 1;
    while (remaining != 0) {
        int32_t delta = remaining;
        int32_t next_x;
        if (delta > HHS_VM81_GAME_SUBPIXELS) delta = HHS_VM81_GAME_SUBPIXELS;
        if (delta < -HHS_VM81_GAME_SUBPIXELS) delta = -HHS_VM81_GAME_SUBPIXELS;
        next_x = state->player.x_subpx + delta;
        if (hhs_rect_collides(state, next_x, state->player.y_subpx)) {
            state->player.vx_subpx = 0;
            break;
        }
        state->player.x_subpx = next_x;
        remaining -= delta;
        if ((direction > 0 && remaining < 0) || (direction < 0 && remaining > 0)) break;
    }
}

static void hhs_move_vertical(HHSVM81GameState* state) {
    int32_t remaining = state->player.vy_subpx;
    state->player.grounded = 0U;
    while (remaining != 0) {
        int32_t delta = remaining;
        int32_t next_y;
        if (delta > HHS_VM81_GAME_SUBPIXELS) delta = HHS_VM81_GAME_SUBPIXELS;
        if (delta < -HHS_VM81_GAME_SUBPIXELS) delta = -HHS_VM81_GAME_SUBPIXELS;
        next_y = state->player.y_subpx + delta;
        if (hhs_rect_collides(state, state->player.x_subpx, next_y)) {
            if (delta > 0) state->player.grounded = 1U;
            state->player.vy_subpx = 0;
            break;
        }
        state->player.y_subpx = next_y;
        remaining -= delta;
    }
    if (!state->player.grounded && hhs_rect_collides(
            state, state->player.x_subpx, state->player.y_subpx + 1)) {
        state->player.grounded = 1U;
    }
}

static void hhs_update_animation(HHSVM81GameState* state) {
    if (!state->player.grounded) {
        state->player.animation_state = state->player.vy_subpx < 0 ? HHS_GAME_ANIM_JUMP : HHS_GAME_ANIM_FALL;
        state->player.animation_frame = 0U;
    } else if (state->player.vx_subpx != 0) {
        state->player.animation_state = HHS_GAME_ANIM_WALK;
        state->player.animation_frame = (uint8_t)((state->frame / 6U) % 4U);
    } else {
        state->player.animation_state = HHS_GAME_ANIM_IDLE;
        state->player.animation_frame = (uint8_t)((state->frame / 30U) % 2U);
    }
}

static void hhs_update_camera(HHSVM81GameState* state) {
    int32_t player_center_px = state->player.x_subpx / HHS_VM81_GAME_SUBPIXELS + HHS_VM81_GAME_PLAYER_WIDTH / 2;
    int32_t desired = player_center_px - HHS_VM81_GAME_SCREEN_WIDTH / 2;
    int32_t max_camera = HHS_VM81_GAME_LEVEL_TILES_X * HHS_VM81_GAME_TILE_SIZE - HHS_VM81_GAME_SCREEN_WIDTH;
    if (desired < 0) desired = 0;
    if (desired > max_camera) desired = max_camera;
    state->camera_x_px = (uint32_t)desired;
}

static void hhs_project_vm81(HHSVM81GameState* state) {
    size_t i;
    uint8_t x = hhs_wrap72_i64(state->player.x_subpx);
    uint8_t y = hhs_wrap72_i64(state->player.y_subpx);
    uint8_t z = hhs_wrap72_i64(state->player.vx_subpx);
    uint8_t w = hhs_wrap72_i64((int64_t)x + y - z);
    state->xyzw[0] = x;
    state->xyzw[1] = y;
    state->xyzw[2] = z;
    state->xyzw[3] = w;
    state->closure_valid = (uint8_t)(hhs_wrap72_i64((int64_t)x + y - z - w) == 0U);

    for (i = 0; i < HHS_VM81_GAME_VISIBLE_CELLS; ++i) {
        uint32_t tile_x = (state->camera_x_px / HHS_VM81_GAME_TILE_SIZE + (uint32_t)(i % 20U)) % HHS_VM81_GAME_LEVEL_TILES_X;
        uint32_t tile_y = ((uint32_t)(i / 20U) + 10U) % HHS_VM81_GAME_LEVEL_TILES_Y;
        uint32_t source = state->level[tile_y][tile_x] ? 17U : 0U;
        source += (uint32_t)state->phase + (uint32_t)i + (uint32_t)state->lo_shu_set;
        state->vm81[i] = (uint8_t)(source % 72U);
    }
    for (i = 0; i < HHS_VM81_GAME_LOSHU_CELLS; ++i) {
        state->vm81[HHS_VM81_GAME_VISIBLE_CELLS + i] = HHS_LO_SHU[i];
